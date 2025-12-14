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
    const response = await fetch(
      `${BASE_URL}/packers/player/${encodeURIComponent(
        playerName
      )}?fallback_api=${forceRefresh}`
    );
    if (!response.ok) throw new Error("Failed to search players");
    return response.json();
  },

  /**
   * Get player statistics
   * @param {number} playerId - Player ID
   * @param {string} playerName - Player name (optional, not used in current endpoint)
   * @returns {Promise<Object>} Player stats object
   */
  async getPlayerStats(playerId, playerName = null) {
    const response = await fetch(
      `${BASE_URL}/packers/player/${playerId}/stats`
    );
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

  /**
   * Get user's favorite players
   * @param {string} userId - User ID (default: "default")
   * @returns {Promise<Object>} Favorites data
   */
  async getFavorites(userId = "default") {
    const response = await fetch(
      `${BASE_URL}/packers/favorites?user_id=${userId}`
    );
    if (!response.ok) throw new Error("Failed to fetch favorites");
    return response.json();
  },

  /**
   * Add a player to favorites
   * @param {Object} playerData - Player data to favorite
   * @param {string} userId - User ID (default: "default")
   * @returns {Promise<Object>} Success response
   */
  async addFavorite(playerData, userId = "default") {
    const response = await fetch(
      `${BASE_URL}/packers/favorites?user_id=${userId}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(playerData),
      }
    );
    if (!response.ok) throw new Error("Failed to add favorite");
    return response.json();
  },

  /**
   * Remove a player from favorites
   * @param {number} playerId - Player ID
   * @param {string} userId - User ID (default: "default")
   * @returns {Promise<Object>} Success response
   */
  async removeFavorite(playerId, userId = "default") {
    const response = await fetch(
      `${BASE_URL}/packers/favorites/${playerId}?user_id=${userId}`,
      {
        method: "DELETE",
      }
    );
    if (!response.ok) throw new Error("Failed to remove favorite");
    return response.json();
  },
};

export default api;
