from fastapi import APIRouter
from app.services.sportsdb_service import *

router = APIRouter()
  
# GET /packers/info
@router.get("/info")
async def packers_info():
  return await get_team_info("Green Bay Packers")

# GET /packers/events
@router.get("/events")
async def packers_events():
  return await get_team_events("Green Bay Packers")

@router.get("/player/{player_name}")
async def player_info(player_name: str):
  return await get_player_info(player_name)
