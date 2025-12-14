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
- Results appear in real-time (debounced)
- Click "Favorite" to add to your tracking list

### ⭐ Favorites Panel (Right Side)

- View complete season stats for favorited players
- Stats organized by category:
  - Passing (QB)
  - Rushing (RB, FB)
  - Receiving (WR, TE)
  - Defense (LB, DE, DT, CB, S)
  - Kicking (K)
  - Scoring (all positions)
- Click ✕ to remove from favorites
- Persists across page refreshes

### ⚡ Live Stats Panel (Left Side)

- Automatically updates when game is LIVE
- Shows real-time performance for favorited players
- Position-specific stats displayed
- 30-second polling during active games

### 🏈 Upcoming Game Section

- Navigate weeks with ◄ ► arrows
- Live game indicator (🔴 LIVE)
- Real-time scores when game is active
- Date, time, and opponent information

## API Endpoints

### Player Endpoints

- `GET /packers/roster?season=2025` - Get full roster
- `GET /packers/search?player=name` - Search players
- `GET /packers/stats?player_id=X` - Get player statistics

### Game Endpoints

- `GET /packers/games?season=2025` - Get game schedule

### Admin Endpoints (Manual Triggers)

- `POST /packers/update-roster` - Refresh roster
- `POST /packers/update-stats` - Refresh player stats
- `POST /packers/update-games` - Refresh game schedule

## Automated Tasks

### Periodic Tasks (Celery Beat)

1. **Weekly Roster Update**: Every Monday at 2:00 AM CST
2. **Post-Game Stats Refresh**: Every 15 minutes on Sunday/Monday (game days)

### Real-Time Task

- **Live Stats Polling**: Checks for live games every 5 minutes
  - When game is live → polls every 30 seconds
  - When no live game → waits 5 minutes

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

## Production Build

### Frontend

```bash
cd frontend
npm run build
npm run preview  # Test production build
```

### Backend

Use production ASGI server:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Troubleshooting

### Backend won't start

- Ensure MongoDB is running: `mongosh`
- Ensure Redis is running: `redis-cli ping`
- Check .env file exists with correct values

### No data showing

- Trigger manual updates:
  ```bash
  curl -X POST http://localhost:8000/packers/update-roster
  curl -X POST http://localhost:8000/packers/update-stats
  curl -X POST http://localhost:8000/packers/update-games
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

## License

MIT

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
