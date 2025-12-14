from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Dict, Any, List
from app.config import MONGO_URL, DATABASE_NAME
from datetime import datetime

client = None
database = None

async def connect_db():
    global client, database
    client = AsyncIOMotorClient(MONGO_URL)
    database = client[DATABASE_NAME] # type: ignore
    print(f"Connected to MongoDB: {DATABASE_NAME}")

async def close_db():
    global client, database
    if client:
        client.close()
        print("Closed MongoDB connection")

def get_database():
    return database

# Synchronous database operations for Celery tasks
def get_sync_database():
    """Get synchronous MongoDB client for Celery tasks."""
    if not MONGO_URL or not DATABASE_NAME:
        raise RuntimeError("MONGO_URL or DATABASE_NAME not configured")
    sync_client = MongoClient(MONGO_URL)
    return sync_client[DATABASE_NAME]

def save_roster_to_db_sync(roster_data: List[Dict[str, Any]], season: int = 2025):
    """
    Synchronously saves the Packers roster to MongoDB.
    Replaces the existing roster for the given season.
    """
    try:
        db = get_sync_database()
        collection = db["players"]
        
        # Clear existing roster for this season
        collection.delete_many({"season": season})
        
        # Add metadata to each player
        players_with_metadata = []
        for player in roster_data:
            player_doc = {
                **player,
                "season": season,
                "last_updated": datetime.utcnow(),
                "team": "Green Bay Packers",
                "team_id": 15
            }
            players_with_metadata.append(player_doc)
        
        # Insert new roster
        if players_with_metadata:
            result = collection.insert_many(players_with_metadata)
            return {
                "success": True,
                "inserted_count": len(result.inserted_ids),
                "season": season,
                "updated_at": datetime.utcnow()
            }
        else:
            return {
                "success": False,
                "error": "No players to insert"
            }
    except Exception as e:
        print(f"Error saving roster to database: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def get_roster_from_db(season: int = 2025):
    """Asynchronously retrieves the Packers roster from MongoDB."""
    db = get_database()
    if db is None:
        return {"error": "Database not connected"}
    
    collection = db["players"]
    roster = await collection.find({"season": season}).to_list(length=None)
    
    # Convert ObjectId to string for JSON serialization
    for player in roster:
        if "_id" in player:
            player["_id"] = str(player["_id"])
    
    return roster

async def search_players_by_name(name: str, season: int | None = None):
    """Search players in our MongoDB by name (case-insensitive).
    Tries common fields from API Sports payload: top-level 'name' or nested 'player.name'.
    Optionally filter by season.
    """
    db = get_database()
    if db is None:
        return {"error": "Database not connected"}

    query: Dict[str, Any] = {
        "$or": [
            {"name": {"$regex": name, "$options": "i"}},
            {"player.name": {"$regex": name, "$options": "i"}},
        ]
    }
    if season is not None:
        query["season"] = season

    collection = db["players"]
    players = await collection.find(query).to_list(length=None)

    for p in players:
        if "_id" in p:
            p["_id"] = str(p["_id"])

    return players

