import { useState, useEffect, useRef } from "react";
import api from "../api/client";
import "./LiveStats.css";

export default function LiveStats({ favorites, isGameLive }) {
  const [liveStats, setLiveStats] = useState({});
  const [loading, setLoading] = useState(false);
  const pollingInterval = useRef(null);

  useEffect(() => {
    // Fetch stats immediately when favorites change
    if (favorites.length > 0) {
      fetchLiveStats();
    }

    // Start polling when game is live and there are favorites
    if (isGameLive && favorites.length > 0) {
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
    try {
      const playerIds = favorites.map((fav) => fav.player.id);
      const data = await api.getLiveStats(playerIds);

      // Convert array of stats to map by player_id
      const statsMap = {};
      (data.stats || []).forEach((stat) => {
        if (stat.player_id) {
          statsMap[stat.player_id] = stat;
        }
      });

      setLiveStats(statsMap);
    } catch (error) {
      console.error("Failed to fetch live stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const getPositionStats = (liveStatDoc, position) => {
    if (!liveStatDoc || !liveStatDoc.groups) return null;

    // Live stats now have groups array: [{name: "Passing", statistics: [...]}, ...]
    const groups = liveStatDoc.groups;
    if (!Array.isArray(groups)) return null;

    // Helper to find a stat value from a specific group
    const getStatFromGroup = (groupName, statName) => {
      const group = groups.find((g) => g.name === groupName);
      if (!group || !group.statistics) return null;

      const stat = group.statistics.find((s) => s.name === statName);
      return stat ? stat.value : null;
    };

    // QB Stats - get from Passing group
    if (position === "QB") {
      const compAtt = getStatFromGroup("Passing", "comp att");

      return [
        {
          label: "Pass Yds",
          value: getStatFromGroup("Passing", "yards") || 0,
        },
        {
          label: "Pass TDs",
          value: getStatFromGroup("Passing", "passing touch downs") || 0,
        },
        {
          label: "INTs",
          value: getStatFromGroup("Passing", "interceptions") || 0,
        },
        {
          label: "Comp/Att",
          value: compAtt || "0/0",
        },
      ];
    }

    // RB Stats - get from Rushing and Receiving groups
    if (["RB", "FB"].includes(position)) {
      return [
        {
          label: "Rush Yds",
          value: getStatFromGroup("Rushing", "yards") || 0,
        },
        {
          label: "Rush TDs",
          value: getStatFromGroup("Rushing", "rushing touch downs") || 0,
        },
        {
          label: "Rec Yds",
          value: getStatFromGroup("Receiving", "yards") || 0,
        },
        {
          label: "Rec TDs",
          value: getStatFromGroup("Receiving", "receiving touch downs") || 0,
        },
      ];
    }

    // WR/TE Stats - get from Receiving group
    if (["WR", "TE"].includes(position)) {
      return [
        {
          label: "Receptions",
          value: getStatFromGroup("Receiving", "total receptions") || 0,
        },
        {
          label: "Rec Yds",
          value: getStatFromGroup("Receiving", "yards") || 0,
        },
        {
          label: "Rec TDs",
          value: getStatFromGroup("Receiving", "receiving touch downs") || 0,
        },
        {
          label: "Targets",
          value: getStatFromGroup("Receiving", "targets") || 0,
        },
      ];
    }

    // K/P Stats - get from Kicking/Punting groups
    if (["K", "P"].includes(position)) {
      const fgMade = getStatFromGroup("Kicking", "field goals");

      return [
        {
          label: "FG Made/Att",
          value: fgMade || "0/0",
        },
        {
          label: "XP Made/Att",
          value: getStatFromGroup("Kicking", "extra point") || "0/0",
        },
        {
          label: "Points",
          value: getStatFromGroup("Kicking", "points") || 0,
        },
      ];
    }

    // Defensive Stats - get from Defensive group
    const tackles = getStatFromGroup("Defensive", "tackles");
    const sacks = getStatFromGroup("Defensive", "sacks");
    const forcedFumbles = getStatFromGroup("Defensive", "ff");

    const defaultStats = [];
    if (tackles) defaultStats.push({ label: "Tackles", value: tackles });
    if (sacks) defaultStats.push({ label: "Sacks", value: sacks });
    if (forcedFumbles) defaultStats.push({ label: "FF", value: forcedFumbles });

    return defaultStats.length > 0 ? defaultStats : null;
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
