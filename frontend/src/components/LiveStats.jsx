import { useState, useEffect, useRef } from "react";
import api from "../api/client";
import "./LiveStats.css";

export default function LiveStats({ favorites, isGameLive }) {
  const [liveStats, setLiveStats] = useState({});
  const [loading, setLoading] = useState(false);
  const pollingInterval = useRef(null);

  useEffect(() => {
    // Start polling when game is live and there are favorites
    if (isGameLive && favorites.length > 0) {
      fetchLiveStats();
      pollingInterval.current = setInterval(fetchLiveStats, 30000); // Poll every 30 seconds
    } else {
      // Clear polling when game is not live
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
    }

    return () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
    };
  }, [isGameLive, favorites]);

  const fetchLiveStats = async () => {
    if (favorites.length === 0) return;

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
      if (stats && stats.stats) {
        statsMap[playerId] = stats;
      }
    });

    setLiveStats(statsMap);
    setLoading(false);
  };

  const getPositionStats = (stats, position) => {
    if (!stats || !stats.stats) return null;

    const s = stats.stats;

    // QB Stats
    if (position === "QB" && s.passing) {
      return [
        { label: "Pass Yds", value: s.passing.yards || 0 },
        { label: "Pass TDs", value: s.passing.touchdowns || 0 },
        { label: "INTs", value: s.passing.interceptions || 0 },
        {
          label: "Comp/Att",
          value: `${s.passing.completions || 0}/${s.passing.attempts || 0}`,
        },
      ];
    }

    // RB Stats
    if (["RB", "FB"].includes(position)) {
      const rushing = s.rushing || {};
      const receiving = s.receiving || {};
      return [
        { label: "Rush Yds", value: rushing.yards || 0 },
        { label: "Rush TDs", value: rushing.touchdowns || 0 },
        { label: "Rec Yds", value: receiving.yards || 0 },
        { label: "Rec TDs", value: receiving.touchdowns || 0 },
      ];
    }

    // WR/TE Stats
    if (["WR", "TE"].includes(position) && s.receiving) {
      return [
        { label: "Receptions", value: s.receiving.receptions || 0 },
        { label: "Rec Yds", value: s.receiving.yards || 0 },
        { label: "Rec TDs", value: s.receiving.touchdowns || 0 },
        { label: "Targets", value: s.receiving.targets || 0 },
      ];
    }

    // Defensive Stats
    if (
      ["LB", "DE", "DT", "CB", "S", "SS", "FS"].includes(position) &&
      s.defense
    ) {
      return [
        { label: "Tackles", value: s.defense.tackles || 0 },
        { label: "Sacks", value: s.defense.sacks || 0 },
        { label: "INTs", value: s.defense.interceptions || 0 },
        { label: "FF", value: s.defense.forced_fumbles || 0 },
      ];
    }

    // Kicker Stats
    if (position === "K" && s.kicking) {
      return [
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
      ];
    }

    return null;
  };

  if (favorites.length === 0) {
    return (
      <div className="live-stats">
        <h2 className="section-title">⚡ Live Stats</h2>
        <div className="empty-state">
          <div className="empty-icon">⭐</div>
          <p>Add favorite players to see their live stats during games</p>
        </div>
      </div>
    );
  }

  return (
    <div className="live-stats">
      <h2 className="section-title">
        ⚡ Live Stats
        {isGameLive && <span className="live-indicator">🔴 LIVE</span>}
        {loading && <span className="updating">↻</span>}
      </h2>

      {!isGameLive && (
        <div className="not-live-message">
          Game not currently in progress. Stats will update automatically when
          game starts.
        </div>
      )}

      <div className="live-stats-list">
        {favorites.map((fav) => {
          const player = fav.player;
          const stats = liveStats[player.id];
          const positionStats = getPositionStats(stats, player.position);

          return (
            <div key={player.id} className="live-stat-card">
              <div className="live-player-header">
                <div>
                  <div className="live-player-name">{player.name}</div>
                  <div className="live-player-position">{player.position}</div>
                </div>
                {stats && (
                  <div className="last-updated">
                    Updated {new Date(stats.last_updated).toLocaleTimeString()}
                  </div>
                )}
              </div>

              {positionStats ? (
                <div className="live-stats-grid">
                  {positionStats.map((stat, idx) => (
                    <div key={idx} className="live-stat-item">
                      <div className="stat-label">{stat.label}</div>
                      <div className="stat-value">{stat.value}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-stats">
                  {stats ? "No stats available yet" : "Loading stats..."}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
