import { useState } from "react";
import api from "../api/client";
import "./PlayerSearch.css";

export default function PlayerSearch({ onSearch }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async () => {
    if (searchTerm.trim().length < 2) {
      return;
    }

    setIsSearching(true);
    try {
      const data = await api.searchPlayers(searchTerm);
      onSearch(data.players || []);
    } catch (error) {
      console.error("Search error:", error);
      onSearch([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="player-search">
      <div className="search-container">
        <input
          type="text"
          className="search-input"
          placeholder="🔍 Search Packers players... (Press Enter)"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        {isSearching && <div className="search-spinner">⏳</div>}
        <button
          className="search-button"
          onClick={handleSearch}
          disabled={isSearching || searchTerm.trim().length < 2}
        >
          Search
        </button>
      </div>
    </div>
  );
}
