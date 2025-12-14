import "./Favorites.css";

export default function Favorites({ favorites, onRemoveFavorite, loading }) {
  if (loading) {
    return (
      <div className="favorites">
        <h2 className="section-title">⭐ Favorites</h2>
        <div className="loading-favorites">Loading favorites...</div>
      </div>
    );
  }

  if (favorites.length === 0) {
    return (
      <div className="favorites">
        <h2 className="section-title">⭐ Favorites</h2>
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <p>
            Search and add your favorite Packers players to track their season
            stats
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="favorites">
      <h2 className="section-title">
        ⭐ Favorites
        <span className="favorites-count">({favorites.length})</span>
      </h2>

      <div className="favorites-list">
        {favorites.map((fav) => {
          const player = fav.player;

          return (
            <div key={player.id} className="favorite-card">
              <div className="favorite-header">
                <div className="player-details">
                  <div className="favorite-name">{player.name}</div>
                  <div className="favorite-meta">
                    <span className="favorite-position">{player.position}</span>
                    {player.age && (
                      <span className="favorite-age">Age {player.age}</span>
                    )}
                  </div>
                </div>
                <button
                  className="remove-btn"
                  onClick={() => onRemoveFavorite(player.id)}
                  title="Remove from favorites"
                >
                  ✕
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
