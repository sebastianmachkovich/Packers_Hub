import "./SearchResults.css";

export default function SearchResults({
  results,
  onAddFavorite,
  onDismiss,
  favorites,
}) {
  const isFavorited = (playerId) => {
    return favorites.some((fav) => {
      const favPlayerId = fav.player?.id || fav.id;
      return favPlayerId === playerId;
    });
  };

  if (!results || results.length === 0) {
    return null;
  }

  return (
    <div className="search-results-panel">
      <div className="search-results-header">
        <h3 className="search-results-title">
          Search Results ({results.length})
        </h3>
        <button
          className="dismiss-btn"
          onClick={onDismiss}
          title="Dismiss search results"
        >
          ✕
        </button>
      </div>
      <div className="search-results-list">
        {results.map((playerData) => {
          // Handle both nested and flat player data structures
          const player = playerData.player || playerData;
          const playerId = player.id;
          const favorited = isFavorited(playerId);

          return (
            <div key={playerId} className="search-result-card">
              <div className="search-result-info">
                <div className="search-result-name">{player.name}</div>
                <div className="search-result-meta">
                  <span className="search-result-position">
                    {player.position || "N/A"}
                  </span>
                  {player.age && (
                    <span className="search-result-age">Age {player.age}</span>
                  )}
                </div>
              </div>
              <button
                className={`star-btn ${favorited ? "favorited" : ""}`}
                onClick={() => !favorited && onAddFavorite(playerData)}
                disabled={favorited}
                title={favorited ? "Already in favorites" : "Add to favorites"}
              >
                {favorited ? "⭐" : "☆"}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
