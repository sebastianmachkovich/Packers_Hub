import { useState, useEffect } from "react";
import PlayerSearch from "./components/PlayerSearch";
import SearchResults from "./components/SearchResults";
import UpcomingGame from "./components/UpcomingGame";
import LiveStats from "./components/LiveStats";
import SeasonStats from "./components/SeasonStats";
import Favorites from "./components/Favorites";
import api from "./api/client";
import "./App.css";

function App() {
  const [favorites, setFavorites] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [isGameLive, setIsGameLive] = useState(false);
  const [loading, setLoading] = useState(true);
  const [games, setGames] = useState([]);

  // Load favorites from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("packers-favorites");
    if (saved) {
      try {
        setFavorites(JSON.parse(saved));
      } catch (error) {
        console.error("Failed to parse favorites:", error);
      }
    }
    setLoading(false);
  }, []);

  // Load games and check for live games periodically
  useEffect(() => {
    loadGames();
    const interval = setInterval(loadGames, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadGames = async () => {
    try {
      const data = await api.getGames(2025);
      const sortedGames = (data.games || []).sort(
        (a, b) => a.game.week - b.game.week
      );
      setGames(sortedGames);

      // Check if any game is live
      const liveGame = sortedGames.find((game) =>
        ["Q1", "Q2", "Q3", "Q4", "HT", "OT"].includes(game.game.status.short)
      );
      setIsGameLive(!!liveGame);
    } catch (error) {
      console.error("Failed to load games:", error);
    }
  };

  const handleSearch = (results) => {
    setSearchResults(results);
  };

  const handleAddFavorite = (playerData) => {
    const player = playerData.player || playerData;
    const playerId = player.id;

    if (
      favorites.some((fav) => {
        const favId = fav.player?.id || fav.id;
        return favId === playerId;
      })
    ) {
      return; // Already favorited
    }

    const newFavorites = [...favorites, { player }];
    setFavorites(newFavorites);
    localStorage.setItem("packers-favorites", JSON.stringify(newFavorites));
  };

  const handleRemoveFavorite = (playerId) => {
    const newFavorites = favorites.filter((fav) => {
      const favId = fav.player?.id || fav.id;
      return favId !== playerId;
    });
    setFavorites(newFavorites);
    localStorage.setItem("packers-favorites", JSON.stringify(newFavorites));
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
          <PlayerSearch onSearch={handleSearch} />
          <SearchResults
            results={searchResults}
            onAddFavorite={handleAddFavorite}
            onDismiss={() => setSearchResults([])}
            favorites={favorites}
          />
        </div>

        <div className="game-section">
          <UpcomingGame games={games} onRefresh={loadGames} />
        </div>

        <div className="stats-section">
          <div className="stats-left">
            <LiveStats favorites={favorites} isGameLive={isGameLive} />
          </div>

          <div className="stats-right">
            <Favorites
              favorites={favorites}
              onRemoveFavorite={handleRemoveFavorite}
              loading={loading}
            />
          </div>
        </div>

        <div className="season-section">
          <SeasonStats favorites={favorites} />
        </div>
      </main>

      <footer className="app-footer">
        <p>Data updates automatically during games • Season: 2025</p>
      </footer>
    </div>
  );
}

export default App;
