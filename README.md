# 🏈 Packers Hub

A full-stack web application for tracking Green Bay Packers player statistics, live game updates, and season data.

## Project Overview

Packers Hub is a real-time sports tracking application featuring:

- **Player Search & Favorites**: Search and track your favorite Packers players
- **Live Game Stats**: Real-time updates during games (auto-polling every 30 seconds)
- **Season Statistics**: Comprehensive player stats across all categories
- **Game Schedule**: Week-by-week navigation with live scores
- **Background Jobs**: Automated data updates via Celery

## Architecture

```
Packers_Hub/
├── backend/          # FastAPI + Celery + MongoDB
├── frontend/         # React + Vite
└── redis/            # Redis configuration for Celery
```

### Backend Stack

- **FastAPI**: REST API server
- **Celery**: Background task processing
- **MongoDB**: Data persistence
- **Redis**: Message broker for Celery
- **API-Sports.io**: External NFL data source

### Frontend Stack

- **React 18**: UI framework
- **Vite**: Build tool
- **Vanilla CSS**: Component styling
- **LocalStorage**: Favorites persistence

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB (running on default port 27017)
- Redis (running on default port 6379)
- API-Sports.io API key ([Get one here](https://api-sports.io/))

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd Packers_Hub
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
MONGO_URL=mongodb://localhost:27017/
DATABASE_NAME=packers_hub
API_KEY=your_api_sports_key_here
REDIS_URL=redis://localhost:6379/0
EOF

# Start FastAPI server
uvicorn app.main:app --reload
```

Backend will run on `http://localhost:8000`

### 3. Start Celery Workers (in separate terminals)

```bash
# Terminal 2: Celery Worker
cd backend
source venv/bin/activate
celery -A app.celery_app.celery_app worker --loglevel=info

# Terminal 3: Celery Beat (scheduler)
cd backend
source venv/bin/activate
celery -A app.celery_app.celery_app beat --loglevel=info
```

### 4. Frontend Setup

```bash
# New terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on `http://localhost:5173`

### 5. Access the Application

Open `http://localhost:5173` in your browser

## Features in Detail

### 🔍 Player Search

- Type player name in search bar
- Results appear in real-time below search input
- Click "Favorite" to add to your tracking list
- Click x to dismiss search results
- Search results persist until manually dismissed

### ⭐ Favorites Panel (Right Side)

- Lightweight list of favorited players
- Shows player name, position, and age
- Click x to remove from favorites
- Favorites stored in browser localStorage (no backend required)
- Persists across page refreshes
- Auto-stretches to show all favorited players

### ⚡ Live Stats Panel (Left Side)

- **Only appears when game is LIVE** (🔴 LIVE indicator)
- Automatically updates every 30 seconds during active games
- Shows position-specific live stats for favorited players only:
  - **QB**: Pass Yds, Pass TDs, INTs, Comp/Att
  - **RB/FB**: Rush Yds, Rush TDs, Rec Yds, Rec TDs
  - **WR/TE**: Receptions, Rec Yds, Rec TDs, Targets
  - **Defense**: Tackles, Sacks, Forced Fumbles
  - **K/P**: FG Made/Att, XP Made/Att, Points
- Fetches data from separate `live_stats` collection
- Auto-stretches to show all players
- Stats grouped by position group (Passing, Rushing, Receiving, Defensive, etc.)

### 📊 Season Stats Section (Full Width Below)

- Comprehensive season statistics for all favorited players
- Displays complete stat categories:
  - Passing (QB)
  - Rushing (RB, FB)
  - Receiving (WR, TE)
  - Defense (all defensive positions)
  - Kicking (K)
  - Punting (P)
  - Scoring (all positions)
- Fetches data from `player_stats` collection
- Updated post-game, not real-time

### 🏈 Upcoming Game Section

- Navigate weeks with ◄ ► arrows
- Shows next scheduled Packers game
- Live game indicator (🔴 LIVE) when game is active
- Real-time scores during game
- Date, time, opponent, and venue information
- Checks game status every 30 seconds

## API Endpoints

### Player Endpoints

- `GET /packers/roster?season=2025` - Get full roster
- `GET /packers/player/{name}` - Search players by name
- `GET /packers/player/{id}/stats?season=2025` - Get player season statistics
- `POST /packers/live-stats` - Get live stats for multiple players (body: `{player_ids: [1049, 6], season: 2025}`)

### Game Endpoints

- `GET /packers/games?season=2025` - Get game schedule
- `GET /packers/next-game?season=2025` - Get next scheduled game

### Admin Endpoints (Manual Triggers)

- `POST /packers/update-roster` - Refresh roster
- `POST /packers/update-stats` - Refresh player stats
- `POST /packers/update-games` - Refresh game schedule

## Automated Tasks

### Periodic Tasks (Celery Beat)

1. **Live Stats Update**: Runs **every 30 seconds**
   - Checks for active Packers games
   - When game is live -> fetches all player stats from API
   - Stores stats in separate `live_stats` MongoDB collection
   - Groups stats by position (Passing, Rushing, Receiving, Defensive, etc.)
   - Auto-reschedules every 30 seconds while game is active
2. **Weekly Roster Update**: Every Monday at 2:00 AM CST
   - Refreshes team roster from API-Sports
3. **Post-Game Stats Refresh**: Every 15 minutes on Sunday/Monday
   - Updates season statistics in `player_stats` collection

Create `backend/.env`:

```bash
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/  # Or localhost
DATABASE_NAME=PackersHub
API_KEY=your_api_sports_key_here
REDIS_URL=redis://localhost:6379/0
```

**Note**: The project uses MongoDB Atlas in production. For local development, you can use:

```bash
MONGO_URL=mongodb://localhost:27017/
DATABASE_NAME=packers_hub
```

### Frontend Configuration

Located in `frontend/src/api/client.js`:

```javascript
const BASE_URL = "http://localhost:8000";
```

### MongoDB Collections

- `players` - Team roster
- `player_stats` - Season statistics
- `games` - Game schedule
- `live_stats` - Real-time game statistics (updated every 30s during games) - Used by Season Stats section

## Configuration

### Backend Environment Variables

```bash
MONGO_URL=mongodb://localhost:27017/
DATABASE_NAME=packers_hub
API_KEY=your_api_sports_key
REDIS_URL=redis://localhost:6379/0
```

### Frontend API Configuration

Located in `frontend/src/api/client.js`:

```javascript
const BASE_URL = "http://localhost:8000";
```

## Development

### Backend Development

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Check Logs

- **FastAPI**: Terminal output where uvicorn is running
- **Celery Worker**: Terminal output where celery worker is running
- **Celery Beat**: Terminal output where celery beat is running
- **Frontend**: Browser console + Vite terminal

## Troubleshooting

### Backend won't start

- Ensure MongoDB is running: `mo (status must be "1", "2", "3", "4", or "HT")
- Verify Celery worker and beat are running in separate terminals
- Check Celery logs for errors (should show "Live Packers game detected!")
- Ensure `live_stats` collection has recent data in MongoDB
- Check browser console for API errors
- Verify favorited players are actually playing in the game

### Frontend API errors

- Ensure backend is running on port 8000
- Check CORS settings in `backend/app/main.py` (should allow `http://localhost:5173`)
- Check browser Network tab for failed requests
- Verify MongoDB connection is working

### Stats showing zeros or wrong values

- **Live Stats**: Make sure you're looking at stats during an active game
- **Passing yards showing rushing yards**: Each stat group (Passing, Rushing, etc.) is now parsed separately
- **Player appearing in wrong stats group**: Players can appear in multiple groups (e.g., Jordan Love has both Passing and Rushing stats)
- Clear browser cache and refresh if seeing stale datackers/update-roster
  curl -X POST http://localhost:8000/packers/update-stats
  curl -X POST http://localhost:8000/packers/update-games
  ```

  ```

### Live stats not updating

- Check if game is actually live
- Verify Celery worker and beat are running
- Check browser console for errors

### Frontend API errors

- Ensure backend is running on port 8000
- Check CORS settings if running on different domain
- Verify Vite proxy in `vite.config.js`

## Tech Stack Summary

| Component          | Technology     |
| ------------------ | -------------- |
| Frontend Framework | React 18       |
| Build Tool         | Vite 5         |
| Backend Framework  | FastAPI        |
| Task Queue         | Celery + Redis |
| Database           | MongoDB        |
| External API       | API-Sports.io  |
| Styling            | CSS Modules    |

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Support

For issues and questions, please open an issue on GitHub.

---

**Go Pack Go! 🧀**
