from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any
from app.config import MONGO_URL, DATABASE_NAME

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

async def save_player_to_db(player: Dict[str, Any]):
    db = get_database()
    if db is None:
        return {"error": "Database not connected"}
    
    collection = db["players"]
    result = await collection.insert_one(player)
    return {"inserted_id": str(result.inserted_id)}
