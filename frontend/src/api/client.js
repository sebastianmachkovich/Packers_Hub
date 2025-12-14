const BASE_URL = "http://localhost:8000";

/**
 * API Client for Packers Hub Backend
 */

export const api = {
  /**
   * Get Packers roster for a given season
   * @param {number} season - Season year (default: 2025)
   * @returns {Promise<Object>} Roster data with players array
   */
  async getRoster(season = 2025) {
    const response = await fetch(`${BASE_URL}/packers/roster?season=${season}`);
    if (!response.ok) throw new Error("Failed to fetch roster");
    return response.json();
  },

  /**
   * Search for Packers players by name
   * @param {string} playerName - Player name to search
   * @param {boolean} forceRefresh - Force API refresh instead of using DB cache
   * @returns {Promise<Object>} Search results with players array
   */
  async searchPlayers(playerName, forceRefresh = false) {
    const params = new URLSearchParams({
      player: playerName,
      force_refresh: forceRefresh,
    });
    const response = await fetch(`${BASE_URL}/packers/search?${params}`);
    if (!response.ok) throw new Error("Failed to search players");
    return response.json();
  },

  /**
   * Get player statistics
   * @param {number} playerId - Player ID
   * @param {string} playerName - Player name (optional)
   * @returns {Promise<Object>} Player stats object
   */
  async getPlayerStats(playerId, playerName = null) {
    const params = new URLSearchParams();
    if (playerId) params.append("player_id", playerId);
    if (playerName) params.append("player_name", playerName);

    const response = await fetch(`${BASE_URL}/packers/stats?${params}`);
    if (!response.ok) throw new Error("Failed to fetch player stats");
    return response.json();
  },

  /**
   * Get Packers games schedule
   * @param {number} season - Season year (default: 2025)
   * @returns {Promise<Object>} Games data with games array
   */
  async getGames(season = 2025) {
    const response = await fetch(`${BASE_URL}/packers/games?season=${season}`);
    if (!response.ok) throw new Error("Failed to fetch games");
    return response.json();
  },

  /**
   * Manually trigger roster update (admin function)
   * @param {number} season - Season year
   * @returns {Promise<Object>} Task confirmation
   */
  async updateRoster(season = 2025) {
    const response = await fetch(
      `${BASE_URL}/packers/update-roster?season=${season}`,
      {
        method: "POST",
      }
    );
    if (!response.ok) throw new Error("Failed to trigger roster update");
    return response.json();
  },

  /**
   * Manually trigger stats refresh (admin function)
   * @param {number} season - Season year
   * @returns {Promise<Object>} Task confirmation
   */
  async updateStats(season = 2025) {
    const response = await fetch(
      `${BASE_URL}/packers/update-stats?season=${season}`,
      {
        method: "POST",
      }
    );
    if (!response.ok) throw new Error("Failed to trigger stats update");
    return response.json();
  },

  /**
   * Manually trigger games schedule update (admin function)
   * @param {number} season - Season year
   * @returns {Promise<Object>} Task confirmation
   */
  async updateGames(season = 2025) {
    const response = await fetch(
      `${BASE_URL}/packers/update-games?season=${season}`,
      {
        method: "POST",
      }
    );
    if (!response.ok) throw new Error("Failed to trigger games update");
    return response.json();
  },
};

export default api;
