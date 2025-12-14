from fastapi import APIRouter
from app.services.db_service import (
  get_roster_from_db,
  search_players_by_name,
)
from app.services.NFL_service import get_player_info  # optional fallback, not used by default
from app.tasks.periodic_tasks import update_packers_roster

router = APIRouter()

# GET /packers/player/{player_name}
@router.get("/player/{player_name}")
async def player_info(player_name: str, season: int | None = None, fallback_api: bool = False):
  """Search for a player in our database. Optionally filter by season.
  Set fallback_api=true to query API Sports if not found (disabled by default).
  """
  players = await search_players_by_name(player_name, season=season)
  if isinstance(players, dict) and players.get("error"):
    return players

  if players:
    return {
      "source": "database",
      "query": player_name,
      "count": len(players),
      "players": players,
    }

  if fallback_api:
    api_result = await get_player_info(player_name, season=season or 2025)
    return {
      "source": "api",
      "query": player_name,
      "result": api_result,
    }

  return {
    "source": "database",
    "query": player_name,
    "count": 0,
    "players": [],
    "message": "No players found"
  }

# GET /packers/roster - Get current roster from database
@router.get("/roster")
async def get_roster(season: int = 2025):
  """Retrieve the current Packers roster from the database."""
  roster = await get_roster_from_db(season=season)
  return {
    "team": "Green Bay Packers",
    "season": season,
    "player_count": len(roster),
    "players": roster
  }

# POST /packers/roster/update - Manually trigger roster update
@router.post("/roster/update")
async def trigger_roster_update(season: int = 2025):
  """Manually trigger a roster update task."""
  task = update_packers_roster.delay(season=season)
  return {
    "message": "Roster update task triggered",
    "task_id": task.id,
    "season": season,
    "status": "Task queued for processing"
  }

# GET /packers/roster/task/{task_id} - Check task status
@router.get("/roster/task/{task_id}")
async def check_task_status(task_id: str):
  """Check the status of a roster update task."""
  from app.celery_app import celery_app
  task = celery_app.AsyncResult(task_id)
  
  return {
    "task_id": task_id,
    "status": task.state,
    "result": task.result if task.ready() else None
  }

