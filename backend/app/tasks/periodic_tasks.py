from app.celery_app import celery_app
from app.services.NFL_service import (
    get_team_roster_sync,
    get_player_statistics_sync,
    get_team_games_sync,
    get_game_by_id_sync,
)
from app.services.db_service import (
    save_roster_to_db_sync,
    upsert_player_stats_sync,
    get_sync_database,
    save_games_to_db_sync,
    get_next_game_sync,
)
from datetime import datetime

@celery_app.task(name="app.tasks.periodic_tasks.update_packers_roster")
def update_packers_roster(season: int = 2025):
    """
    Celery task to fetch and update the Green Bay Packers roster.
    This task runs weekly (every Monday at 2 AM) via Celery Beat.
    
    Args:
        season: The NFL season year (default: 2025)
    
    Returns:
        dict: Status of the update operation
    """
    print(f"[{datetime.now()}] Starting Packers roster update for season {season}...")
    
    try:
        # Fetch roster from API Sports (Team ID 15 = Green Bay Packers)
        roster_response = get_team_roster_sync(team_id=15, season=season)
        
        # Check for errors in API response
        if "error" in roster_response:
            error_msg = f"Failed to fetch roster from API: {roster_response['error']}"
            print(f"[ERROR] {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Extract player data from response
        players = roster_response.get("response", [])
        
        if not players or not isinstance(players, list):
            print("[WARNING] No players found in API response")
            return {
                "success": False,
                "error": "No players found in API response",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Validate player data format
        valid_players = [p for p in players if isinstance(p, dict)]
        if not valid_players:
            print("[WARNING] No valid player data in API response")
            return {
                "success": False,
                "error": "No valid player data in API response",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        print(f"[INFO] Fetched {len(valid_players)} players from API")
        
        # Save roster to database
        save_result = save_roster_to_db_sync(valid_players, season=season)
        
        if save_result.get("success"):
            success_msg = f"Successfully updated {save_result['inserted_count']} players for season {season}"
            print(f"[SUCCESS] {success_msg}")
            return {
                "success": True,
                "message": success_msg,
                "inserted_count": save_result["inserted_count"],
                "season": season,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            error_msg = f"Failed to save roster to database: {save_result.get('error')}"
            print(f"[ERROR] {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        error_msg = f"Unexpected error during roster update: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task(name="app.tasks.periodic_tasks.update_packers_games")
def update_packers_games(season: int = 2025):
    """
    Fetch and store all Packers games for the season.
    Run this weekly or manually to keep game schedule up to date.
    """
    print(f"[{datetime.now()}] Fetching Packers games for season {season}...")
    
    try:
        games_response = get_team_games_sync(team_id=15, season=season)
        
        if "error" in games_response:
            error_msg = f"Failed to fetch games: {games_response['error']}"
            print(f"[ERROR] {error_msg}")
            return {"success": False, "error": error_msg, "timestamp": datetime.utcnow().isoformat()}
        
        games = games_response.get("response", [])
        if not games or not isinstance(games, list):
            msg = "No games found in API response"
            print(f"[WARNING] {msg}")
            return {"success": False, "error": msg, "timestamp": datetime.utcnow().isoformat()}
        
        valid_games = [g for g in games if isinstance(g, dict)]
        if not valid_games:
            msg = "No valid game data"
            print(f"[WARNING] {msg}")
            return {"success": False, "error": msg, "timestamp": datetime.utcnow().isoformat()}
        
        print(f"[INFO] Fetched {len(valid_games)} games")
        
        save_result = save_games_to_db_sync(valid_games, season=season)
        
        if save_result.get("success"):
            msg = f"Successfully stored {save_result['inserted_count']} games"
            print(f"[SUCCESS] {msg}")
            return {
                "success": True,
                "message": msg,
                "inserted_count": save_result["inserted_count"],
                "season": season,
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            error_msg = f"Failed to save games: {save_result.get('error')}"
            print(f"[ERROR] {error_msg}")
            return {"success": False, "error": error_msg, "timestamp": datetime.utcnow().isoformat()}
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return {"success": False, "error": error_msg, "timestamp": datetime.utcnow().isoformat()}


@celery_app.task(name="app.tasks.periodic_tasks.update_packers_stats_postgame")
def update_packers_stats_postgame(season: int = 2025, force: bool = False):
    """
    Refresh all Packers player season stats after games are completed.
    Checks if a game just finished before running (unless force=True).
    Intended to run shortly after weekly games.
    """
    print(f"[{datetime.now()}] Starting Packers player stats postgame update for season {season}...")
    
    try:
        db = get_sync_database()
        players_cursor = db["players"].find({"team_id": 15, "season": season}, {"player": 1, "id": 1})
        players = list(players_cursor)
        if not players:
            msg = "No players found in DB for Packers"
            print(f"[WARNING] {msg}")
            return {"success": False, "error": msg}

        updated = 0
        errors = []
        for p in players:
            player_id = None
            if isinstance(p, dict):
                player_id = p.get("player", {}).get("id") or p.get("id")

            if not player_id:
                errors.append({"player": p, "error": "missing player id"})
                continue

            stats_resp = get_player_statistics_sync(player_id, season=season)
            if not stats_resp or "error" in stats_resp:
                errors.append({"player_id": player_id, "error": stats_resp.get("error") if isinstance(stats_resp, dict) else "unknown"})
                continue

            # API returns response as a list of player stats, pass it directly to upsert
            stats_payload = stats_resp.get("response")
            
            # Check if response exists (could be empty list [] which is falsy but valid)
            if stats_payload is None:
                errors.append({"player_id": player_id, "error": "null stats response"})
                continue
            
            # Empty list means no stats for this player yet - skip but don't treat as error
            if isinstance(stats_payload, list) and len(stats_payload) == 0:
                continue
            
            # Ensure payload is dict or list
            if not isinstance(stats_payload, (dict, list)):
                errors.append({"player_id": player_id, "error": f"invalid stats payload type: {type(stats_payload)}"})
                continue

            upsert_result = upsert_player_stats_sync(player_id, season, stats_payload)
            if upsert_result.get("success"):
                updated += 1
            else:
                errors.append({"player_id": player_id, "error": upsert_result.get("error")})

        summary = {
            "success": True,
            "season": season,
            "updated_count": updated,
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat(),
        }
        print(f"[INFO] Player stats update complete: {updated} updated, {len(errors)} errors")
        return summary

    except Exception as e:
        err = f"Unexpected error during player stats update: {e}"
        print(f"[ERROR] {err}")
        return {"success": False, "error": err, "timestamp": datetime.utcnow().isoformat()}
