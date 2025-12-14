from datetime import datetime, timezone
from app.celery_app import celery_app
from app.services.NFL_service import get_live_games_sync, get_player_statistics_sync
from app.services.db_service import get_sync_database, upsert_player_stats_sync, get_next_game_sync

PACKERS_TEAM_ID = 15

@celery_app.task(name="app.tasks.realtime_tasks.update_packers_live_stats")
def update_packers_live_stats(season: int = 2025):
	"""
	Poll live games; if Packers are playing, fetch and upsert player stats in near real-time.
	Checks game status/times first to avoid unnecessary API calls.
	"""
	print(f"[{datetime.now()}] Checking for active Packers game...")
	
	# First check if there's an active or upcoming game from our DB
	next_game = get_next_game_sync(season=season, team_id=PACKERS_TEAM_ID)
	if not next_game:
		print(f"[INFO] No upcoming games found in DB, skipping stats update")
		return {"success": True, "status": "no-upcoming-game", "timestamp": datetime.utcnow().isoformat()}
	
	# Check game status - only run during live games or shortly after
	game_status = next_game.get("game", {}).get("status", {}).get("short")
	if game_status in ["FT", "AOT", "CANC", "PST"]:
		print(f"[INFO] Game already finished or postponed (status: {game_status}), skipping")
		return {"success": True, "status": "game-not-active", "game_status": game_status, "timestamp": datetime.utcnow().isoformat()}
	
	# Now check live games from API to confirm
	live_resp = get_live_games_sync(season=season)
	if not live_resp or "error" in live_resp:
		return {"success": False, "error": live_resp.get("error") if isinstance(live_resp, dict) else "Unknown error"}

	live_games = live_resp.get("response", []) or []
	# Only keep dicts to satisfy typing/attribute access
	live_games = [g for g in live_games if isinstance(g, dict)]
	packers_live = [
		g for g in live_games
		if g.get("teams", {}).get("home", {}).get("id") == PACKERS_TEAM_ID
		or g.get("teams", {}).get("away", {}).get("id") == PACKERS_TEAM_ID
	]

	if not packers_live:
		return {"success": True, "status": "no-live-packers-game", "timestamp": datetime.utcnow().isoformat()}

	# Fetch players from DB to know whom to update
	db = get_sync_database()
	players = list(db["players"].find({"team_id": PACKERS_TEAM_ID, "season": season}, {"player": 1, "id": 1}))
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

	return {
		"success": True,
		"updated_count": updated,
		"errors": errors,
		"timestamp": datetime.utcnow().isoformat(),
	}

