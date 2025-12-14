// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://sharpshop-api-10a2006ad1b4.herokuapp.com';

export const apiClient = {
  async fetch(endpoint: string, options?: RequestInit) {
    const url = `${API_BASE_URL}${endpoint}`;
    return fetch(url, {
      ...options,
      credentials: 'include',
    });
  }
};
