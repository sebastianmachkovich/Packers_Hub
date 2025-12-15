from fastapi import APIRouter
from pydantic import BaseModel
from app.services.db_service import (
  get_roster_from_db,
  search_players_by_name,
  get_player_stats_from_db,
  get_games_from_db,
  get_live_stats_from_db,
)
from app.services.NFL_service import get_player_info  # optional fallback, not used by default
from app.tasks.periodic_tasks import (
  update_packers_roster,
  update_packers_stats_postgame,
  update_packers_games,
)

router = APIRouter()

# Request model for live stats
class LiveStatsRequest(BaseModel):
  player_ids: list[int]
  season: int = 2025

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


# GET /packers/player/{player_id}/stats
@router.get("/player/{player_id}/stats")
async def player_stats(player_id: int, season: int | None = None):
  """Return stored stats for a player from our DB."""
  stats = await get_player_stats_from_db(player_id, season=season)
  if not stats:
    return {"message": "No stats found", "player_id": player_id, "season": season}
  if isinstance(stats, dict) and stats.get("error"):
    return stats
  return stats

# POST /packers/live-stats - Get live stats for specific player IDs
@router.post("/live-stats")
async def get_live_stats(request: LiveStatsRequest):
  """Get live stats for multiple players by their IDs."""
  stats = await get_live_stats_from_db(request.player_ids, season=request.season)
  if isinstance(stats, dict) and stats.get("error"):
    return stats
  return {
    "player_count": len(stats),
    "stats": stats,
    "season": request.season
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

# POST /packers/stats/update - Trigger a full stats refresh for players in DB
@router.post("/stats/update")
async def trigger_stats_update(season: int = 2025):
  """Trigger a postgame stats refresh for all Packers players in the DB."""
  task = update_packers_stats_postgame.delay(season=season, force=True)
  return {
    "message": "Stats update task triggered",
    "task_id": task.id,
    "season": season,
    "status": "Task queued for processing"
  }

# GET /packers/games - Get games from database
@router.get("/games")
async def get_games(season: int = 2025):
  """Retrieve Packers games from the database."""
  games = await get_games_from_db(season=season, team_id=15)
  if isinstance(games, dict) and games.get("error"):
    return games
  return {
    "team": "Green Bay Packers",
    "team_id": 15,
    "season": season,
    "game_count": len(games),
    "games": games
  }

# POST /packers/games/update - Trigger games fetch and store
@router.post("/games/update")
async def trigger_games_update(season: int = 2025):
  """Manually trigger a games update task to fetch and store Packers schedule."""
  task = update_packers_games.delay(season=season)
  return {
    "message": "Games update task triggered",
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

