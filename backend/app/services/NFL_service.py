import aiohttp
import asyncio
from datetime import datetime
import json
import os
import requests  # For synchronous requests in Celery tasks
from typing import Optional, Dict, Any
from app.config import API_SPORTS_KEY

BASE_URL = "https://v1.american-football.api-sports.io"

def _get_headers():
    """Get headers with API key. Validates key is set when called."""
    if not API_SPORTS_KEY:
        raise RuntimeError("API_KEY environment variable is not set. Please set it in your .env file.")
    return {"x-apisports-key": API_SPORTS_KEY}

HEADERS = None  # Will be initialized on first use

# --- Module-level aiohttp ClientSession ---
_session: Optional[aiohttp.ClientSession] = None

async def init_session():
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(headers=_get_headers())

async def close_session():
    global _session
    if _session is not None and not _session.closed:
        await _session.close()
        _session = None

# --- Core Async Fetch Function ---
async def fetch_json(url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
    """
    Asynchronously fetches a JSON response from a given URL with optional parameters and headers.
    """
    global _session
    if headers is None:
        headers = _get_headers()
    if _session is None or _session.closed:
        raise RuntimeError("aiohttp ClientSession is not initialized. Call init_session() before making requests.")
    try:
        async with _session.get(url, params=params) as response:
            
            # Check for HTTP status code errors
            if response.status != 200:
                print(f"Error: {response.status} for URL: {url} with params: {params}")
                print(f"Response Text: {await response.text()}")
                return {"error": f"HTTP Error {response.status}"}
                
            # aiohttp handles JSON decoding
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"Aiohttp Client Error: {e}")
        return {"error": f"Client Error: {e}"}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": f"Unexpected Error: {e}"}

# --- American Football API Async Functions ---

# Async: get all NFL teams
async def get_nfl_teams(season: int = 2025, league_id: int = 1):
    """Fetches a list of NFL teams for a specific season."""
    url = f"{BASE_URL}/teams"
    params = {
        "league": league_id, # NFL league ID
        "season": season     # Season
    }
    return await fetch_json(url, params=params)

# Async: get a team's games
async def get_team_games(team_id: int, season: int = 2025):
    """Fetches games for a specific team and season."""
    url = f"{BASE_URL}/games"
    params = {
        "team": team_id,
        "season": season
    }
    return await fetch_json(url, params=params)

# Async: get currently live games
async def get_live_games(league_id: int = 1, season: int = 2025):
    """Fetches currently live NFL games."""
    url = f"{BASE_URL}/games"
    params = {
        "live": "all", # Filter for all currently live games
        "league": league_id,
        "season": season
    }
    return await fetch_json(url, params=params)

# Async: get player info
async def get_player_info(player_name: str, season: int = 2025):
    """Fetches player statistics for a specific player name and season."""
    url = f"{BASE_URL}/players"
    params = {
        "search": player_name,
        "league": 1, # Assuming NFL
        "season": season
    }
    # Note: The search endpoint might return a list of players.
    return await fetch_json(url, params=params)

# Async: get team roster
async def get_team_roster(team_id: int, season: int = 2025):
    """Fetches the roster for a specific team and season."""
    url = f"{BASE_URL}/players"
    params = {
        "team": team_id,
        "season": season
    }
    return await fetch_json(url, params=params)

# Synchronous: get team roster (for Celery tasks)
def get_team_roster_sync(team_id: int = 15, season: int = 2025):
    """
    Synchronously fetches the roster for a specific team and season.
    Used in Celery tasks since they don't support async operations by default.
    Team ID 15 is Green Bay Packers.
    """
    url = f"{BASE_URL}/players"
    params = {
        "team": team_id,
        "season": season
    }
    try:
        response = requests.get(url, headers=_get_headers(), params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching roster: {e}")
        return {"error": str(e)}



# --- Formatting and Execution Functions (Can remain sync or be async for printing) ---

def print_nfl_teams(data):
    """Prints the formatted list of NFL teams."""
    print("=== NFL Teams ===")
    teams = data.get("response", [])
    if data.get("error") or not teams:
        print(f"Could not retrieve teams: {data.get('error', 'No data')}")
        return

    for team in teams:
        team_data = team.get("team", {})
        team_id = team_data.get("id")
        name = team_data.get("name")
        city = team_data.get("city")
        logo = team_data.get("logo")

        print(f"ID: {team_id} | {city} {name}")
        print(f"Logo: {logo}")
        print("-" * 40)

def print_team_games(data, team_name="Green Bay Packers"):
    """Prints the formatted schedule for a team."""
    print(f"=== {team_name} Schedule ===")
    games = data.get("response", [])
    if data.get("error") or not games:
        print(f"Could not retrieve games: {data.get('error', 'No data')}")
        return
    
    for game in games:
        game_info = game.get("game", {})
        teams = game.get("teams", {})
        scores = game.get("scores", {})
        
        # Extract and format date/time
        date_str = game_info.get("date", {}).get("date")
        time_str = game_info.get("date", {}).get("time")
        
        # Convert to a more readable format, assuming UTC input
        try:
            # The API gives date and time separately, we combine them for parsing
            date_time_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            # Format to Month Day, Year @ Hour:Minute (e.g., Aug 9, 2025 @ 20:25 UTC)
            display_date = date_time_obj.strftime("%b %d, %Y @ %H:%M UTC")
        except (ValueError, TypeError):
            display_date = f"{date_str} {time_str}" # Fallback if parsing fails

        home_team = teams.get("home", {}).get("name")
        away_team = teams.get("away", {}).get("name")
        
        # Extract scores
        home_score = scores.get("home", {}).get("total", 'N/A')
        away_score = scores.get("away", {}).get("total", 'N/A')
        
        # Format the game string
        game_display = (
            f"  {display_date} | {game_info.get('stage')} {game_info.get('week')}\n"
            f"  {home_team} vs. {away_team} "
        )
        
        # Add score if the game is finished (or after overtime)
        if game_info.get("status", {}).get("short") in ["FT", "AOT"]:
              game_display += f"  (Final Score: {home_score} - {away_score})"
        else:
              game_display += f"  (Status: {game_info.get('status', {}).get('long', 'TBD')})"
        
        print(game_display)
        print("-" * 60)

def print_live_games(data):
    """Prints the formatted list of live NFL games."""
    print("=== Live NFL Games ===")
    live_games = data.get("response", [])
    
    if data.get("error") or not live_games:
        print(f"No NFL games are currently live or an error occurred: {data.get('error', 'No data')}.")
        return

    for game in live_games:
        teams = game.get("teams", {})
        scores = game.get("scores", {})
        game_status = game.get("game", {}).get("status", {})
        
        home_name = teams.get("home", {}).get("name")
        away_name = teams.get("away", {}).get("name")
        
        # Get the current total score
        home_score = scores.get("home", {}).get("total", 0)
        away_score = scores.get("away", {}).get("total", 0)
        
        # Get live status info
        current_quarter = game_status.get("short")
        time_remaining = game_status.get("timer")
        
        status_text = f"{current_quarter} | {time_remaining} left" if time_remaining else game_status.get("long", "Live")
        
        print(f"  **{away_name} ({away_score}) @ {home_name} ({home_score})**")
        print(f"  Status: {status_text}")
        print("-" * 50)


# --- Main Execution Block ---

async def main():
    """Runs all async functions concurrently and prints the results."""
    
    # Define tasks to run concurrently
    tasks = [
        get_nfl_teams(season=2025), 
        get_team_games(team_id=15, season=2025), # Green Bay Packers ID 15
        get_live_games(season=2025),
    ]

    # Run tasks concurrently
    nfl_teams_data, packers_games_data, live_games_data = await asyncio.gather(*tasks)

    # Print results sequentially (no need for async here)
    print_nfl_teams(nfl_teams_data)
    print("\n")
    print_team_games(packers_games_data, team_name="Green Bay Packers 2025 Schedule")
    print("\n")
    print_live_games(live_games_data)
    print("\n")
    
    # Example of a single player lookup
    player_data = await get_player_info("Aaron Rodgers", season=2025)
    print("=== Aaron Rodgers 2025 Stats (Example) ===")
    if player_data.get("response"):
        print(f"Found {len(player_data['response'])} results for Aaron Rodgers.")
    else:
        print("Player not found or error occurred.")


if __name__ == "__main__":
    print("Starting concurrent API calls with aiohttp...")
    # asyncio.run(main()) is the modern way to run the main async function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted.")
    except Exception as e:
        print(f"An error occurred during execution: {e}")