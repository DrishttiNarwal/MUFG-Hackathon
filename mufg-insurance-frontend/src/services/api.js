import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
  withCredentials: false, // Important for CORS
});

export const insuranceService = {
  // Get insurance recommendations based on user inputs
  getRecommendations: async (policyType, country, formData) => {
    try {
      console.log('Making recommendation request:', { policyType, country, formData });
      
      const requestData = {
        country: country,
        policy_type: policyType.toUpperCase(),
        ...formData,
      };

      // Convert diseases array to string for health insurance
      if (policyType.toUpperCase() === 'HEALTH' && Array.isArray(formData.diseases)) {
        requestData.diseases = formData.diseases.join(',');
        requestData.num_diseases = formData.diseases.length;
      }

      // Convert smoker_drinker to proper format
      if (requestData.smoker_drinker) {
        requestData.smoker_drinker = requestData.smoker_drinker === 'yes' ? 'Yes' : 'No';
      }

      console.log('Sending request to API:', requestData);
      const response = await api.post('/recommend', requestData);
      console.log('API Response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error getting recommendations:', error);
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('Error response from server:', {
          data: error.response.data,
          status: error.response.status,
          headers: error.response.headers
        });
        throw new Error(error.response.data?.detail || 'Server error occurred');
      } else if (error.request) {
        // The request was made but no response was received
        console.error('No response received:', error.request);
        throw new Error('Could not connect to server. Please try again later.');
      } else {
        // Something happened in setting up the request
        console.error('Error setting up request:', error.message);
        throw error;
      }
    }
  },

  // Get health check status
  healthCheck: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking API health:', error);
      throw error;
    }
  },

  // Get recommendations for multiple policies
  getMultipleRecommendations: async (policies) => {
    try {
      const response = await api.post('/recommend_multiple', { policies });
      return response.data;
    } catch (error) {
      console.error('Error getting multiple recommendations:', error);
      throw error;
    }
  },
};

export default insuranceService;
