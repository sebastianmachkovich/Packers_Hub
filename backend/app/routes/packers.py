from fastapi import APIRouter
from app.services.sportsdb_service import *
from app.services.db_service import *

router = APIRouter()
  
# GET /packers/info
@router.get("/info")
async def packers_info():
  return await get_team_info("Green Bay Packers")

# GET /packers/events
@router.get("/events")
async def packers_events():
  return await get_team_events("Green Bay Packers")

# GET /packers/player/{player_name}
@router.get("/player/{player_name}")
async def player_info(player_name: str):
  return await get_player_info(player_name)

# POST /packers/player/save/{player_name}
@router.post("/player/save/{player_name}")
async def save_player_by_name(player_name: str):
  # Fetch player data from SportsDB API
  player_data = await get_player_info(player_name)
  
  if not player_data or "player" not in player_data or not player_data["player"]:
    return {"error": "Player not found"}
  
  # Get the first player from the result
  player = player_data["player"][0]
  
  # Save to MongoDB
  result = await save_player_to_db(player)
  return result
