// API configuration - use empty string for relative paths since Express serves both frontend and API
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const apiClient = {
  async fetch(endpoint: string, options?: RequestInit) {
    const url = `${API_BASE_URL}${endpoint}`;
    return fetch(url, {
      ...options,
      credentials: 'include',
    });
  }
};
