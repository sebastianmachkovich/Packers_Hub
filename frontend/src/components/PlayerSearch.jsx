import { useState, useEffect, useCallback } from "react";
import api from "../api/client";
import "./PlayerSearch.css";

export default function PlayerSearch({ onAddFavorite, favorites }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);

  // Debounced search
  useEffect(() => {
    if (searchTerm.trim().length < 2) {
      setSearchResults([]);
      setShowResults(false);
      return;
    }

    setIsSearching(true);
    const timer = setTimeout(async () => {
      try {
        const data = await api.searchPlayers(searchTerm);
        setSearchResults(data.players || []);
        setShowResults(true);
        setIsSearching(false);
      } catch (error) {
        console.error("Search error:", error);
        setSearchResults([]);
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  const handleAddFavorite = (player) => {
    onAddFavorite(player);
    setSearchTerm("");
    setShowResults(false);
  };

  const isFavorited = useCallback(
    (playerId) => {
      return favorites.some((fav) => fav.player.id === playerId);
    },
    [favorites]
  );

  return (
    <div className="player-search">
      <div className="search-container">
        <input
          type="text"
          className="search-input"
          placeholder="🔍 Search Packers players..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onFocus={() => searchResults.length > 0 && setShowResults(true)}
        />
        {isSearching && <div className="search-spinner">⏳</div>}
      </div>

      {showResults && searchResults.length > 0 && (
        <div className="search-results">
          {searchResults.map((playerData) => {
            const player = playerData.player;
            const favorited = isFavorited(player.id);

            return (
              <div key={player.id} className="search-result-item">
                <div className="player-info">
                  <span className="player-name">{player.name}</span>
                  <span className="player-position">{player.position}</span>
                  {player.age && (
                    <span className="player-age">Age: {player.age}</span>
                  )}
                </div>
                <button
                  className={`favorite-btn ${favorited ? "favorited" : ""}`}
                  onClick={() => !favorited && handleAddFavorite(playerData)}
                  disabled={favorited}
                >
                  {favorited ? "⭐ Favorited" : "☆ Favorite"}
                </button>
              </div>
            );
          })}
        </div>
      )}

      {showResults &&
        searchResults.length === 0 &&
        searchTerm.trim().length >= 2 &&
        !isSearching && (
          <div className="search-results">
            <div className="no-results">No players found</div>
          </div>
        )}
    </div>
  );
}
