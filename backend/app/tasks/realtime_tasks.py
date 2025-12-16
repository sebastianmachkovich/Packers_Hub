from datetime import datetime, timezone
from app.celery_app import celery_app
from app.services.NFL_service import get_live_games_sync, get_game_player_statistics_sync
from app.services.db_service import get_sync_database, upsert_live_stats_sync, get_next_game_sync

PACKERS_TEAM_ID = 15

@celery_app.task(name="app.tasks.realtime_tasks.update_packers_live_stats")
def update_packers_live_stats(season: int = 2025):
	"""
	Poll live games; if Packers are playing, fetch and upsert player stats in near real-time.
	Checks game status/times first. This task reschedules itself every 30 seconds.
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
		print(f"[INFO] No live Packers game, will check again in 5 minutes")
		return {"success": True, "status": "no-live-packers-game", "timestamp": datetime.utcnow().isoformat()}

	print(f"[INFO] Live Packers game detected! Updating stats and rescheduling in 30 seconds...")

	# Get the game ID from the live game
	game_id = packers_live[0].get("game", {}).get("id")
	if not game_id:
		return {"success": False, "error": "Could not extract game ID from live game"}

	# Fetch live player stats for this game (returns stats for ALL players in the game)
	game_stats_resp = get_game_player_statistics_sync(game_id)
	if not game_stats_resp or "error" in game_stats_resp:
		return {"success": False, "error": game_stats_resp.get("error") if isinstance(game_stats_resp, dict) else "Unknown error"}

	# Extract player stats from response
	player_stats_list = game_stats_resp.get("response", [])
	if not isinstance(player_stats_list, list):
		return {"success": False, "error": "Invalid game stats response format"}

	# Filter to only Packers players and upsert their stats
	updated = 0
	errors = []

	# The API returns: [{team: {...}, groups: [{name: "Passing", players: [{player: {...}, statistics: [...]}]}]}]
	# Collect all stat groups for each player before upserting
	players_by_id = {}  # {player_id: {player_info, team_info, groups: [...]}}
	
	for team_data in player_stats_list:
		if not isinstance(team_data, dict):
			continue
		
		team_info = team_data.get("team", {})
		team_id = team_info.get("id")
		
		# Check if this is Packers team data
		if team_id != PACKERS_TEAM_ID:
			continue
		
		print(f"[INFO] Processing Packers stats with {len(team_data.get('groups', []))} stat groups")
		
		# Iterate through stat groups (Passing, Rushing, Receiving, etc.)
		for group in team_data.get("groups", []):
			group_name = group.get("name", "Unknown")
			players = group.get("players", [])
			
			# Iterate through players in this group
			for player_item in players:
				player_info = player_item.get("player", {})
				player_id = player_info.get("id")
				
				if not player_id:
					print(f"[WARN] Missing player ID in {group_name} group")
					errors.append({"error": "missing player id", "group": group_name})
					continue
				
				# Collect this group for this player
				if player_id not in players_by_id:
					players_by_id[player_id] = {
						"player_info": player_info,
						"team_info": team_info,
						"groups": []
					}
				
				players_by_id[player_id]["groups"].append({
					"name": group_name,
					"statistics": player_item.get("statistics", [])
				})
	
	# Now upsert each player with ALL their stat groups
	for player_id, player_data in players_by_id.items():
		upsert_result = upsert_live_stats_sync(
			game_id=game_id,
			player_id=player_id,
			player_stat={
				"team": player_data["team_info"],
				"player": player_data["player_info"],
				"groups": player_data["groups"]  # Array of all stat groups
			},
			season=season
		)
		
		if upsert_result.get("success"):
			updated += 1
		else:
			errors.append({
				"player_id": player_id,
				"player_name": player_data["player_info"].get("name"),
				"error": upsert_result.get("error")
			})

	# Reschedule this task to run again in 30 seconds since game is still live
	update_packers_live_stats.apply_async(args=[season], countdown=30)

	return {
		"success": True,
		"updated_count": updated,
		"errors": errors,
		"rescheduled_in": "30s",
		"timestamp": datetime.utcnow().isoformat(),
	}

