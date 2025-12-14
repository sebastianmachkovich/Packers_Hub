import { useState, useEffect } from "react";
import PlayerSearch from "./components/PlayerSearch";
import UpcomingGame from "./components/UpcomingGame";
import LiveStats from "./components/LiveStats";
import Favorites from "./components/Favorites";
import api from "./api/client";
import "./App.css";

function App() {
  const [favorites, setFavorites] = useState([]);
  const [isGameLive, setIsGameLive] = useState(false);

  // Load favorites from localStorage on mount
  useEffect(() => {
    const savedFavorites = localStorage.getItem("packers_favorites");
    if (savedFavorites) {
      try {
        setFavorites(JSON.parse(savedFavorites));
      } catch (error) {
        console.error("Failed to load favorites:", error);
      }
    }
  }, []);

  // Save favorites to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem("packers_favorites", JSON.stringify(favorites));
  }, [favorites]);

  // Check for live games periodically
  useEffect(() => {
    checkForLiveGame();
    const interval = setInterval(checkForLiveGame, 60000); // Check every minute
    return () => clearInterval(interval);
  }, []);

  const checkForLiveGame = async () => {
    try {
      const data = await api.getGames(2025);
      const liveGame = data.games?.find((game) =>
        ["Q1", "Q2", "Q3", "Q4", "HT", "OT"].includes(game.game.status.short)
      );
      setIsGameLive(!!liveGame);
    } catch (error) {
      console.error("Failed to check for live game:", error);
    }
  };

  const handleAddFavorite = (playerData) => {
    const playerId = playerData.player.id;
    // Prevent duplicates
    if (!favorites.some((fav) => fav.player.id === playerId)) {
      setFavorites([...favorites, playerData]);
    }
  };

  const handleRemoveFavorite = (playerId) => {
    setFavorites(favorites.filter((fav) => fav.player.id !== playerId));
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">
            <span className="title-icon">🏈</span>
            Packers Hub
          </h1>
          <div className="app-subtitle">
            Green Bay Packers Player Stats & Live Updates
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="search-section">
          <PlayerSearch
            onAddFavorite={handleAddFavorite}
            favorites={favorites}
          />
        </div>

        <div className="game-section">
          <UpcomingGame />
        </div>

        <div className="stats-section">
          <div className="stats-left">
            <LiveStats favorites={favorites} isGameLive={isGameLive} />
          </div>

          <div className="stats-right">
            <Favorites
              favorites={favorites}
              onRemoveFavorite={handleRemoveFavorite}
            />
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <p>Data updates automatically during games • Season: 2025</p>
      </footer>
    </div>
  );
}

export default App;
