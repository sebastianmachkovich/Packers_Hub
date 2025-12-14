from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Dict, Any, List, Optional
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

def upsert_player_stats_sync(player_id: int, season: int, stats_payload: Dict[str, Any] | list):
    """Upsert player season stats into 'player_stats' collection.
    Extracts relevant football stats from API response and stores them in a structured format.
    """
    try:
        db = get_sync_database()
        collection = db["player_stats"]
        
        # Extract player info and stats from the API response
        # API Sports returns response as array, we want first item if it exists
        if isinstance(stats_payload, list) and len(stats_payload) > 0:
            player_data = stats_payload[0]
        elif isinstance(stats_payload, dict):
            player_data = stats_payload
        else:
            player_data = {}
        
        # Extract player info
        player_info = player_data.get("player", {})
        player_name = player_info.get("name", "")
        position = player_info.get("position", "")
        
        # API response groups stats by teams - filter to only Green Bay Packers (team_id: 15)
        teams = player_data.get("teams", [])
        packers_team = None
        for team in teams:
            if isinstance(team, dict) and team.get("team", {}).get("id") == 15:
                packers_team = team
                break
        
        # If no Packers stats found, skip this player
        if not packers_team:
            return {"success": False, "error": "No stats for Packers team"}
        
        # Extract groups (stat categories) from Packers team
        groups = packers_team.get("groups", [])
        
        # Create filtered raw response with only Packers data
        filtered_raw_response = {
            "player": player_data.get("player", {}),
            "team": packers_team
        }
        
        # Aggregate stats from all games
        aggregated_stats = {
            "passing": {"yards": 0, "touchdowns": 0, "interceptions": 0, "completions": 0, "attempts": 0},
            "rushing": {"yards": 0, "touchdowns": 0, "carries": 0},
            "receiving": {"yards": 0, "touchdowns": 0, "receptions": 0, "targets": 0},
            "defense": {"tackles": 0, "sacks": 0.0, "interceptions": 0, "forced_fumbles": 0},
            "kicking": {"field_goals_made": 0, "field_goals_attempts": 0, "extra_points_made": 0, "extra_points_attempts": 0},
            "punting": {"punts": 0, "yards": 0, "avg": 0.0, "inside_20": 0, "touchbacks": 0},
            "returning": {"kick_returns": 0, "kick_return_yards": 0, "punt_returns": 0, "punt_return_yards": 0, "touchdowns": 0},
            "scoring": {"touchdowns": 0, "two_point_conversions": 0, "points": 0},
        }
        
        # Helper to safely parse integer from string (handles "1,653" format)
        def safe_int(val):
            if not val:
                return 0
            return int(str(val).replace(",", ""))
        
        def safe_float(val):
            if not val:
                return 0.0
            return float(str(val).replace(",", ""))
        
        # Parse stats from groups (each group is a category like Rushing, Receiving, etc.)
        for group in groups:
            if not isinstance(group, dict):
                continue
            
            group_name = group.get("name", "")
            statistics = group.get("statistics", [])
            
            # Convert statistics array to dict for easier lookup
            stats_dict = {}
            for stat in statistics:
                if isinstance(stat, dict):
                    stats_dict[stat.get("name", "")] = stat.get("value", "0")
            
            # Parse based on group name
            if group_name == "Passing":
                aggregated_stats["passing"]["yards"] += safe_int(stats_dict.get("yards"))
                aggregated_stats["passing"]["touchdowns"] += safe_int(stats_dict.get("passing touchdowns"))
                aggregated_stats["passing"]["interceptions"] += safe_int(stats_dict.get("interceptions thrown"))
                aggregated_stats["passing"]["completions"] += safe_int(stats_dict.get("completions"))
                aggregated_stats["passing"]["attempts"] += safe_int(stats_dict.get("passing attempts"))
            
            elif group_name == "Rushing":
                aggregated_stats["rushing"]["yards"] += safe_int(stats_dict.get("yards"))
                aggregated_stats["rushing"]["touchdowns"] += safe_int(stats_dict.get("rushing touchdowns"))
                aggregated_stats["rushing"]["carries"] += safe_int(stats_dict.get("rushing attempts"))
            
            elif group_name == "Receiving":
                aggregated_stats["receiving"]["yards"] += safe_int(stats_dict.get("receiving yards"))
                aggregated_stats["receiving"]["touchdowns"] += safe_int(stats_dict.get("receiving touchdowns"))
                aggregated_stats["receiving"]["receptions"] += safe_int(stats_dict.get("receptions"))
                aggregated_stats["receiving"]["targets"] += safe_int(stats_dict.get("receiving targets"))
            
            elif group_name == "Defense":
                aggregated_stats["defense"]["tackles"] += safe_int(stats_dict.get("total tackles"))
                aggregated_stats["defense"]["sacks"] += safe_float(stats_dict.get("sacks"))
                aggregated_stats["defense"]["interceptions"] += safe_int(stats_dict.get("interceptions"))
                aggregated_stats["defense"]["forced_fumbles"] += safe_int(stats_dict.get("forced fumbles"))
            
            elif group_name == "Kicking":
                aggregated_stats["kicking"]["field_goals_made"] += safe_int(stats_dict.get("field goals made"))
                aggregated_stats["kicking"]["field_goals_attempts"] += safe_int(stats_dict.get("field goal attempts"))
                aggregated_stats["kicking"]["extra_points_made"] += safe_int(stats_dict.get("extra points made"))
                aggregated_stats["kicking"]["extra_points_attempts"] += safe_int(stats_dict.get("extra point attempts"))
            
            elif group_name == "Punting":
                aggregated_stats["punting"]["punts"] += safe_int(stats_dict.get("punts"))
                aggregated_stats["punting"]["yards"] += safe_int(stats_dict.get("gross punt yards"))
                aggregated_stats["punting"]["avg"] = safe_float(stats_dict.get("yards per punt avg"))
                aggregated_stats["punting"]["inside_20"] += safe_int(stats_dict.get("punts inside 20"))
                aggregated_stats["punting"]["touchbacks"] += safe_int(stats_dict.get("touchbacks"))
            
            elif group_name == "Returning":
                aggregated_stats["returning"]["kick_returns"] += safe_int(stats_dict.get("kick returns"))
                aggregated_stats["returning"]["kick_return_yards"] += safe_int(stats_dict.get("kick return yards"))
                aggregated_stats["returning"]["punt_returns"] += safe_int(stats_dict.get("punt returns"))
                aggregated_stats["returning"]["punt_return_yards"] += safe_int(stats_dict.get("punt return yards"))
                aggregated_stats["returning"]["touchdowns"] += safe_int(stats_dict.get("return touchdowns"))
            
            elif group_name == "Scoring":
                aggregated_stats["scoring"]["touchdowns"] += safe_int(stats_dict.get("total touchdowns"))
                aggregated_stats["scoring"]["two_point_conversions"] += safe_int(stats_dict.get("two point conversions"))
                aggregated_stats["scoring"]["points"] += safe_int(stats_dict.get("total points"))
        
        result = collection.update_one(
            {"player_id": player_id, "season": season},
            {
                "$set": {
                    "player_id": player_id,
                    "player_name": player_name,
                    "position": position,
                    "season": season,
                    "stats": aggregated_stats,
                    "raw_response": filtered_raw_response,  # Only store Packers team data
                    "last_updated": datetime.utcnow(),
                }
            },
            upsert=True,
        )
        return {
            "success": True,
            "matched": result.matched_count,
            "modified": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None,
        }
    except Exception as e:
        print(f"Error upserting player stats: {e}")
        return {"success": False, "error": str(e)}

async def get_player_stats_from_db(player_id: int, season: Optional[int] = None):
    db = get_database()
    if db is None:
        return {"error": "Database not connected"}

    query: Dict[str, Any] = {"player_id": player_id}
    if season is not None:
        query["season"] = season

    collection = db["player_stats"]
    doc = await collection.find_one(query)
    if not doc:
        return None
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

# --- Games storage and retrieval ---

def save_games_to_db_sync(games_data: List[Dict[str, Any]], season: int = 2025):
    """Save Packers games to MongoDB, replacing existing games for the season."""
    try:
        db = get_sync_database()
        collection = db["games"]
        
        # Clear existing games for this season and team
        collection.delete_many({"season": season, "team_id": 15})
        
        games_with_metadata = []
        for game in games_data:
            game_doc = {
                **game,
                "season": season,
                "team_id": 15,
                "last_updated": datetime.utcnow(),
            }
            games_with_metadata.append(game_doc)
        
        if games_with_metadata:
            result = collection.insert_many(games_with_metadata)
            return {
                "success": True,
                "inserted_count": len(result.inserted_ids),
                "season": season,
            }
        return {"success": False, "error": "No games to insert"}
    except Exception as e:
        print(f"Error saving games: {e}")
        return {"success": False, "error": str(e)}

async def get_games_from_db(season: int = 2025, team_id: int = 15):
    """Retrieve games from MongoDB."""
    db = get_database()
    if db is None:
        return {"error": "Database not connected"}
    
    collection = db["games"]
    games = await collection.find({"season": season, "team_id": team_id}).to_list(length=None)
    
    for game in games:
        if "_id" in game:
            game["_id"] = str(game["_id"])
    
    return games

def get_next_game_sync(season: int = 2025, team_id: int = 15):
    """Get the next upcoming or live game for the team (sync)."""
    try:
        db = get_sync_database()
        collection = db["games"]
        
        # Find games that are not finished, sorted by date
        game = collection.find_one(
            {
                "season": season,
                "team_id": team_id,
                "game.status.short": {"$nin": ["FT", "AOT"]},  # Not finished
            },
            sort=[("game.date.date", 1), ("game.date.time", 1)]
        )
        return game
    except Exception as e:
        print(f"Error getting next game: {e}")
        return None

# ============================================
# Favorites Management
# ============================================





