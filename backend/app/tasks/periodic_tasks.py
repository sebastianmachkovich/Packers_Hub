from app.celery_app import celery_app
from app.services.NFL_service import get_team_roster_sync
from app.services.db_service import save_roster_to_db_sync
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
