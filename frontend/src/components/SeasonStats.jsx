import { useState, useEffect } from "react";
import api from "../api/client";
import "./SeasonStats.css";

export default function SeasonStats({ favorites }) {
  const [seasonStats, setSeasonStats] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (favorites.length > 0) {
      fetchSeasonStats();
    } else {
      setSeasonStats({});
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
        title: "🦶 Kicking",
        stats: [
          {
            label: "FG",
            value: `${s.kicking.field_goals_made || 0}/${
              s.kicking.field_goals_attempts || 0
            }`,
          },
          {
            label: "XP",
            value: `${s.kicking.extra_points_made || 0}/${
              s.kicking.extra_points_attempts || 0
            }`,
          },
        ],
      });
    }

    return sections;
  };

  if (favorites.length === 0) {
    return (
      <div className="season-stats">
        <h2 className="section-title">📊 Season Stats</h2>
        <div className="empty-state">
          <div className="empty-icon">⭐</div>
          <p>Add favorite players to see their season stats</p>
        </div>
      </div>
    );
  }

  return (
    <div className="season-stats">
      <h2 className="section-title">
        📊 Season Stats
        <span className="season-label">2025</span>
      </h2>

      {loading && <div className="loading-stats">Loading season stats...</div>}

      <div className="season-stats-list">
        {favorites.map((fav) => {
          const player = fav.player;
          const stats = seasonStats[player.id];
          const statSections = stats
            ? getSeasonStats(stats, player.position)
            : null;

          return (
            <div key={player.id} className="season-stat-card">
              <div className="season-player-header">
                <div className="season-player-name">{player.name}</div>
                <div className="season-player-meta">
                  <span className="season-player-position">
                    {player.position}
                  </span>
                  {player.age && (
                    <span className="season-player-age">Age {player.age}</span>
                  )}
                </div>
              </div>

              {statSections && statSections.length > 0 ? (
                <div className="season-stats-sections">
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
                !loading && (
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
