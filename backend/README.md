# Packers Hub Backend

A FastAPI-based backend service for managing Green Bay Packers team information with automated weekly roster updates using Celery and Redis.

## Features

- 🏈 Fetch Green Bay Packers team information via API Sports
- 📅 Get team games and schedules
- 👤 Player information and statistics
- 🔄 **Automated weekly roster updates** using Celery Beat
- ⚡ Async API endpoints for better performance
- 💾 MongoDB integration for roster storage
- 🔴 Redis-backed task queue for background jobs
- 📊 Built with FastAPI for automatic API documentation

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- MongoDB (local or cloud instance)
- Redis (for Celery task queue)
- API Sports API key ([get one here](https://api-sports.io/))

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/sebastianmachkovich/Packers_Hub.git
cd Packers_Hub/backend
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```
:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# MongoInstall and Start Redis

**macOS:**
```bash
brew install redis
redis-server
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo service redis-server start
```

### 6. Run the Application

You need to run multiple processes:

**Terminal 1 - FastAPI Server:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
celery -A app.celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat (Scheduler):**
```bash
celery -A app.celery_app beat --loglevel=info
```

The server will start at `http://127.0.0.1:8000`

📖 **For detailed Celery setup instructions, see [CELERY_SETUP.md](CELERY_SETUP.md)**
# Redis Configuration
REDIS_URL=redis://localhost:6379/0optional, as the project uses a free API):

```bash
# No API key required for TheSportsDB free tier
```

### 5. Run the Application

```bash
uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`

## API Endpoints

### Base URL

`http://127.0.0.1:8000`

### Available Endpoints

| Method | Endpoint                        | Description                            |
| ------ | ------------------------------- | -------------------------------------- |
| GET    | `/`                             | Health check - returns backend status  |
| GET    | `/packers/info`                 | Get Green Bay Packers team information |
| GET    | `/packers/events`               | Get recent Packers events/games        |
| GET    | `/packers/player/{player_name}` | Search for player by name              |

### Example Requests

```bash
# Get team info
curl http://127.0.0.1:8000/packers/info

# Get recent events
curl http://127.0.0.1:8000/packers/events

# Search for a player
curl http://127.0.0.1:8000/packers/player/Aaron%20Rodgers
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── celery_app.py        # Celery configuration (planned)
│   ├── routes/
│   │   └── packers.py       # Packers API routes
│   ├── services/
│   │   └── sportsdb_service.py  # TheSportsDB API integration
│   └── tasks/
│       ├── periodic_tasks.py    # Scheduled tasks (planned)
│       └── realtime_tasks.py    # Real-time tasks (planned)
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration (planned)
├── docker-compose.yml      # Docker compose setup (planned)
└── README.md
```

## Development

### Running in Development Mode

The `--reload` flag enables auto-reload on code changes:

```bash
uvicorn app.main:app --reload
```

### Adding New Routes

1. Create or modify route files in `app/routes/`
2. Import and include the router in `app/main.py`
3. The API documentation will update automatically

## Tech Stack

- **FastAPI** - Modern web framework for building APIs
- **uvicorn** - ASGI server
- **aiohttp** - Async HTTP client for external API calls
- **python-dotenv** - Environment variable management

## Planned Features

- [ ] Celery integration for background tasks
- [ ] Redis for caching and task queue
- [ ] Docker containerization
- [ ] Real-time game updates
- [ ] Database integration for data persistence
