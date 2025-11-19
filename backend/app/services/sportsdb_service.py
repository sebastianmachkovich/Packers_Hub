import aiohttp
import os
import asyncio

API_BASE = "https://www.thesportsdb.com/api/v1/json/3" # Free tier API key

async def fetch_json(url: str):
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      return await response.json()

# Async: get team info
async def get_team_info(team_name: str):
  url = f"{API_BASE}/searchteams.php?t={team_name}"
  return await fetch_json(url)

# Async: get events
async def get_team_events(team_name: str):
  team_info = await get_team_info(team_name)
  if not team_info or "teams" not in team_info:
    return {"error": "Team not found"}
  team_id = team_info["teams"][0]["idTeam"]
  url = f"{API_BASE}/eventslast.php?id={team_id}"
  return await fetch_json(url)

# Async: get player info
async def get_player_info(player_name: str):
  url = f"{API_BASE}/searchplayers.php?p={player_name}"
  return await fetch_json(url)
