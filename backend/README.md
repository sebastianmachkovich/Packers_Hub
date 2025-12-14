# Packers Hub Backend

FastAPI backend for Green Bay Packers data with Celery/Redis workers keeping roster and player stats fresh.

## Features

- Automated weekly roster sync (Celery Beat)
- Postgame player stats refresh (season 2025)
- Realtime player stats polling during live games
- MongoDB persistence for roster and stats
- API endpoints backed by our database (no live API calls for searches)

## Prerequisites

- Python 3.10+
- MongoDB running locally or remote URI
- Redis running locally (for Celery broker/result)
- API Sports NFL key (https://api-sports.io/)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cat > .env <<'EOF'
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=packers_hub
API_KEY=your_api_sports_key
REDIS_URL=redis://localhost:6379/0
EOF
```

Start dependencies (examples):

```bash
# Redis
redis-server

# We are using MongoDB Atlas
```

## Run

Use three terminals:

```bash
# 1) FastAPI
uvicorn app.main:app --reload --port 8000

# 2) Celery worker
celery -A app.celery_app worker --loglevel=info

# 3) Celery beat (schedules)
celery -A app.celery_app beat --loglevel=info
```

## Celery schedules

- `update_packers_roster` — Mondays 02:00 (weekly roster sync)
- `update_packers_stats_postgame` — Sundays 23:30 (season stats refresh after games)
- `update_packers_live_stats` — every 60s (poll live game and upsert stats if Packers are playing)

## API Endpoints (DB-backed)

- `GET /packers/player/{player_name}?season=2025` — search players in DB; optional `fallback_api=true` to call API if missing.
- `GET /packers/player/{player_id}/stats?season=2025` — get stored stats for a player.
- `GET /packers/roster?season=2025` — roster from DB.
- `POST /packers/roster/update?season=2025` — trigger roster refresh task.
- `GET /packers/roster/task/{task_id}` — check Celery task status.

Swagger UI: http://127.0.0.1:8000/docs

## Notes

- Player stats are stored in `player_stats` collection; roster lives in `players` collection.
- Realtime job is lightweight when no Packers game is live; it exits early.

## Quick checks

```bash
curl "http://127.0.0.1:8000/packers/roster?season=2025"
curl "http://127.0.0.1:8000/packers/player/Jordan%20Love?season=2025"
curl "http://127.0.0.1:8000/packers/player/12345/stats?season=2025"
```
