import { useState, useEffect } from "react";
import api from "../api/client";
import "./UpcomingGame.css";

export default function UpcomingGame({ games = [], onRefresh }) {
  const [currentGameIndex, setCurrentGameIndex] = useState(0);

  // Find current/upcoming game when games prop changes
  useEffect(() => {
    if (games.length === 0) return;

    const now = new Date();
    const upcomingGameIndex = games.findIndex((g) => {
      const gameDate = new Date(g.game.date.date);
      return gameDate >= now || g.game.status.short === "NS";
    });

    if (upcomingGameIndex !== -1) {
      setCurrentGameIndex(upcomingGameIndex);
    } else if (games.length > 0) {
      setCurrentGameIndex(games.length - 1);
    }
  }, [games]);

  const currentGame = games[currentGameIndex];
  const loading = games.length === 0;

  const goToPrevGame = () => {
    if (currentGameIndex > 0) {
      setCurrentGameIndex(currentGameIndex - 1);
    }
  };

  const goToNextGame = () => {
    if (currentGameIndex < games.length - 1) {
      setCurrentGameIndex(currentGameIndex + 1);
    }
  };

  const formatDate = (dateStr, timeStr) => {
    const date = new Date(`${dateStr}T${timeStr}`);
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  const getStatusDisplay = (status) => {
    const statusMap = {
      NS: "Not Started",
      Q1: "1st Quarter",
      Q2: "2nd Quarter",
      Q3: "3rd Quarter",
      Q4: "4th Quarter",
      HT: "Halftime",
      OT: "Overtime",
      FT: "Final",
      AOT: "Final/OT",
      PST: "Postponed",
      CANC: "Cancelled",
    };
    return statusMap[status.short] || status.long;
  };

  const isLive = (status) => {
    return ["Q1", "Q2", "Q3", "Q4", "HT", "OT"].includes(status.short);
  };

  if (loading) {
    return (
      <div className="upcoming-game loading">
        <div className="spinner">Loading games...</div>
      </div>
    );
  }

  if (!currentGame) {
    return (
      <div className="upcoming-game">
        <div className="no-game">No game data available</div>
      </div>
    );
  }

  const { game, teams, scores } = currentGame;
  const isPackersHome = teams.home.id === 15;
  const opponent = isPackersHome ? teams.away : teams.home;
  const packersScore = isPackersHome ? scores.home.total : scores.away.total;
  const opponentScore = isPackersHome ? scores.away.total : scores.home.total;

  return (
    <div className="upcoming-game">
      <div className="week-navigation">
        <button
          className="nav-arrow"
          onClick={goToPrevGame}
          disabled={currentGameIndex === 0}
        >
          ‹
        </button>

        <div className="game-header">
          <div className="week-label">{game.week}</div>
          {isLive(game.status) && <span className="live-badge">🔴 LIVE</span>}
        </div>

        <button
          className="nav-arrow"
          onClick={goToNextGame}
          disabled={currentGameIndex === games.length - 1}
        >
          ›
        </button>
      </div>

      <div className="game-content">
        <div className="teams">
          <div className="team packers">
            <div className="team-name">Green Bay Packers</div>
            <div className="team-logo">🏈</div>
            {game.status.short !== "NS" && (
              <div className="team-score">{packersScore}</div>
            )}
          </div>

          <div className="vs-separator">
            {game.status.short === "NS" ? "VS" : "@"}
          </div>

          <div className="team opponent">
            <div className="team-name">{opponent.name}</div>
            <div className="team-logo">🏈</div>
            {game.status.short !== "NS" && (
              <div className="team-score">{opponentScore}</div>
            )}
          </div>
        </div>

        <div className="game-info">
          <div className="game-date">
            {formatDate(game.date.date, game.date.time)}
          </div>
          <div className={`game-status ${isLive(game.status) ? "live" : ""}`}>
            {getStatusDisplay(game.status)}
            {game.status.timer && ` - ${game.status.timer}`}
          </div>
          {game.stage && <div className="game-stage">{game.stage}</div>}
        </div>
      </div>
    </div>
  );
}
