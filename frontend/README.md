# Packers Hub Frontend

A modern, clean React single-page application for tracking Green Bay Packers players, live stats, and game schedules.

## Features

### 🔍 Player Search

- Real-time search for Packers players
- Debounced search (300ms) to reduce API calls
- Click to add players to favorites
- Shows player position and age

### 🏈 Upcoming Game Section

- Week-by-week game navigation (left/right arrows)
- Live game status indicator
- Real-time score updates during games
- Displays opponent, date/time, and game status

### ⚡ Live Stats (Left Panel)

- Automatic polling during live games (every 30 seconds)
- Position-specific stats display:
  - **QB**: Passing yards, TDs, INTs, Completions/Attempts
  - **RB/FB**: Rushing yards/TDs, Receiving yards/TDs
  - **WR/TE**: Receptions, yards, TDs, targets
  - **Defense**: Tackles, sacks, INTs, forced fumbles
  - **K**: Field goals, extra points
- Updates automatically when game is live

### ⭐ Favorites (Right Panel)

- Full season statistics for favorited players
- Organized by stat category (Passing, Rushing, Receiving, Defense, Kicking, Scoring)
- One-click remove from favorites
- Persistent storage (survives page refreshes via localStorage)

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **CSS Modules** - Component-scoped styling
- **Fetch API** - HTTP requests to backend

## Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

## Installation

```bash
# Install dependencies
npm install
```

## Development

```bash
# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

## Build for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## Configuration

### API Endpoint

The API base URL is configured in [src/api/client.js](src/api/client.js):

```javascript
const BASE_URL = "http://localhost:8000";
```

### Vite Proxy

The Vite dev server includes a proxy configuration in [vite.config.js](vite.config.js) to forward `/packers/*` requests to the backend.

## Project Structure

```
frontend/
├── index.html              # HTML entry point
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration
├── src/
│   ├── main.jsx           # React entry point
│   ├── App.jsx            # Main app component
│   ├── App.css            # Global app styles
│   ├── index.css          # Reset and base styles
│   ├── api/
│   │   └── client.js      # API client with all endpoints
│   └── components/
│       ├── PlayerSearch.jsx      # Search bar component
│       ├── PlayerSearch.css
│       ├── UpcomingGame.jsx      # Game display with navigation
│       ├── UpcomingGame.css
│       ├── LiveStats.jsx         # Live player stats
│       ├── LiveStats.css
│       ├── Favorites.jsx         # Season stats for favorites
│       └── Favorites.css
```

## Key Features Implementation

### Local Storage Persistence

Favorites are automatically saved to `localStorage` under the key `packers_favorites` and restored on page load.

### Live Game Detection

The app polls the `/packers/games` endpoint every minute to detect if a game is live (status: Q1, Q2, Q3, Q4, HT, OT).

### Auto-Polling During Games

When a game is detected as live AND there are favorited players:

- Stats are fetched every 30 seconds
- Polling stops when game ends

### Responsive Design

- Desktop: Two-column layout (Live Stats | Favorites)
- Tablet/Mobile: Single-column with Favorites on top

## Color Scheme

The app uses the official Green Bay Packers colors:

- **Dark Green**: `#203731` (primary backgrounds, text)
- **Gold**: `#FFB612` (accents, highlights)
- **White**: `#FFFFFF` (cards, text)

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Troubleshooting

### API Connection Issues

If you see "Failed to fetch" errors:

1. Ensure backend is running on `http://localhost:8000`
2. Check browser console for CORS errors
3. Verify backend health: `curl http://localhost:8000/packers/roster`

### Live Stats Not Updating

1. Verify a game is actually live
2. Check browser console for polling errors
3. Ensure you have players favorited

### Favorites Not Persisting

Check browser's localStorage in DevTools → Application → Local Storage

## License

MIT
