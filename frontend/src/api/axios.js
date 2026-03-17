import axios from 'axios';

const API_BASE_URL = '/api';

const instance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const riskAPI = {
  /**
   * Get top 5 risk food items for a city
   */
  getTopRisks: async (city) => {
    try {
      const response = await instance.get('/risk/', {
        params: { city }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching risks:', error);
      return [];
    }
  },

  /**
   * Get last 20 alerts for a city
   */
  getAlerts: async (city) => {
    try {
      const response = await instance.get('/alerts/', {
        params: { city }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching alerts:', error);
      return [];
    }
  },

  /**
   * Submit a citizen report
   */
  submitReport: async (city, food_item, adulterant, description) => {
    try {
      const response = await instance.post('/report/', {
        city,
        food_item,
        adulterant,
        description,
      });
      return response.data;
    } catch (error) {
      console.error('Error submitting report:', error);
      throw error;
    }
  },

  /**
   * Get all available cities
   */
  getCities: async () => {
    try {
      const response = await instance.get('/cities/');
      return response.data.cities || [];
    } catch (error) {
      console.error('Error fetching cities:', error);
      return [];
    }
  },
};

export default instance;
