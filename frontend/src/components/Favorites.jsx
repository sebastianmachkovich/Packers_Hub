import { useState, useEffect } from "react";
import api from "../api/client";
import "./Favorites.css";

export default function Favorites({ favorites, onRemoveFavorite }) {
  const [seasonStats, setSeasonStats] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (favorites.length > 0) {
      fetchSeasonStats();
    }
  }, [favorites]);

  const fetchSeasonStats = async () => {
    setLoading(true);
    const statsPromises = favorites.map(async (fav) => {
      try {
        const stats = await api.getPlayerStats(fav.player.id, fav.player.name);
        return { playerId: fav.player.id, stats };
      } catch (error) {
        console.error(`Failed to fetch stats for ${fav.player.name}:`, error);
        return { playerId: fav.player.id, stats: null };
      }
    });

    const results = await Promise.all(statsPromises);
    const statsMap = {};
    results.forEach(({ playerId, stats }) => {
      if (stats) {
        statsMap[playerId] = stats;
      }
    });

    setSeasonStats(statsMap);
    setLoading(false);
  };

  const getSeasonStats = (stats, position) => {
    if (!stats || !stats.stats) return null;

    const s = stats.stats;
    const sections = [];

    // Passing Stats
    if (s.passing && (s.passing.attempts > 0 || position === "QB")) {
      sections.push({
        title: "🎯 Passing",
        stats: [
          { label: "Yards", value: s.passing.yards || 0 },
          { label: "TDs", value: s.passing.touchdowns || 0 },
          { label: "INTs", value: s.passing.interceptions || 0 },
          {
            label: "Comp/Att",
            value: `${s.passing.completions || 0}/${s.passing.attempts || 0}`,
          },
        ],
      });
    }

    // Rushing Stats
    if (s.rushing && s.rushing.carries > 0) {
      sections.push({
        title: "🏃 Rushing",
        stats: [
          { label: "Yards", value: s.rushing.yards || 0 },
          { label: "TDs", value: s.rushing.touchdowns || 0 },
          { label: "Carries", value: s.rushing.carries || 0 },
          {
            label: "YPC",
            value: s.rushing.carries
              ? (s.rushing.yards / s.rushing.carries).toFixed(1)
              : "0.0",
          },
        ],
      });
    }

    // Receiving Stats
    if (s.receiving && s.receiving.targets > 0) {
      sections.push({
        title: "🙌 Receiving",
        stats: [
          { label: "Yards", value: s.receiving.yards || 0 },
          { label: "TDs", value: s.receiving.touchdowns || 0 },
          { label: "Receptions", value: s.receiving.receptions || 0 },
          { label: "Targets", value: s.receiving.targets || 0 },
        ],
      });
    }

    // Defense Stats
    if (s.defense && s.defense.tackles > 0) {
      sections.push({
        title: "🛡️ Defense",
        stats: [
          { label: "Tackles", value: s.defense.tackles || 0 },
          { label: "Sacks", value: s.defense.sacks || 0 },
          { label: "INTs", value: s.defense.interceptions || 0 },
          { label: "FF", value: s.defense.forced_fumbles || 0 },
        ],
      });
    }

    // Kicking Stats
    if (s.kicking && (s.kicking.field_goals_attempts > 0 || position === "K")) {
      sections.push({
        title: "⚽ Kicking",
        stats: [
          { label: "FG Made", value: s.kicking.field_goals_made || 0 },
          { label: "FG Att", value: s.kicking.field_goals_attempts || 0 },
          { label: "XP Made", value: s.kicking.extra_points_made || 0 },
          { label: "XP Att", value: s.kicking.extra_points_attempts || 0 },
        ],
      });
    }

    // Scoring Stats (always show if points > 0)
    if (s.scoring && s.scoring.points > 0) {
      sections.push({
        title: "🏆 Scoring",
        stats: [
          { label: "Total TDs", value: s.scoring.touchdowns || 0 },
          { label: "2PT Conv", value: s.scoring.two_point_conversions || 0 },
          { label: "Points", value: s.scoring.points || 0 },
        ],
      });
    }

    return sections;
  };

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
          const stats = seasonStats[player.id];
          const statSections = stats
            ? getSeasonStats(stats, player.position)
            : null;

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

              {loading && !stats && (
                <div className="loading-stats">Loading season stats...</div>
              )}

              {statSections && statSections.length > 0 ? (
                <div className="season-stats">
                  {statSections.map((section, idx) => (
                    <div key={idx} className="stat-section">
                      <div className="stat-section-title">{section.title}</div>
                      <div className="stat-grid">
                        {section.stats.map((stat, statIdx) => (
                          <div key={statIdx} className="stat-item">
                            <div className="stat-item-label">{stat.label}</div>
                            <div className="stat-item-value">{stat.value}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                stats && (
                  <div className="no-season-stats">
                    No season stats available for this player yet
                  </div>
                )
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
