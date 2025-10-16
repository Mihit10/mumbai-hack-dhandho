// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// API Service
const api = {
  async fetchUpcomingResults() {
    try {
      const response = await fetch(`${API_BASE_URL}/upcoming-results`);
      if (!response.ok) throw new Error('Failed to fetch upcoming results');
      const data = await response.json();
      // The backend returns the results directly, not nested under a 'results' key.
      return data || [];
    } catch (error) {
      console.error('API Error:', error);
      return [];
    }
  },

  async fetchLatestResults() {
    try {
      const response = await fetch(`${API_BASE_URL}/latest-results`);
      if (!response.ok) throw new Error('Failed to fetch latest results');
      const data = await response.json();
      // The backend returns the results directly, not nested under a 'results' key.
      return data || [];
    } catch (error) {
      console.error('API Error:', error);
      return [];
    }
  },

  async sendChatMessage(question) {
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      if (!response.ok) throw new Error('Failed to send message');
      const data = await response.json();
      // The backend returns the answer under the 'response' key.
      return data.response || 'Sorry, I could not process that.';
    } catch (error) {
      console.error('API Error:', error);
      return 'Error connecting to server. Please check if the backend is running.';
    }
  },

  async triggerResultProcessing(company, ticker) {
    try {
      // The endpoint is /api/analyze/{symbol}, not /api/process-result
      const response = await fetch(`${API_BASE_URL}/analyze/${ticker}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) throw new Error('Failed to process result');
      const data = await response.json();
      return { status: 'success', data }; // We'll wrap the data for consistency
    } catch (error) {
      console.error('API Error:', error);
      return { status: 'error', error: error.message };
    }
  }
};

export default api;