import axios from 'axios';
import {Alert} from 'react-native';

// Configure based on your backend URL
const BASE_URL = 'https://datarw-bugfix.preview.emergentagent.com/api';

class ApiServiceClass {
  constructor() {
    this.api = axios.create({
      baseURL: BASE_URL,
      timeout: 30000, // 30 second timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error);
        
        if (error.code === 'NETWORK_ERROR') {
          // Handle offline scenario
          return Promise.resolve({
            success: false,
            error: 'Network error. Operating in offline mode.',
            offline: true
          });
        }

        if (error.response?.status === 401) {
          // Handle authentication error
          return Promise.resolve({
            success: false,
            error: 'Authentication failed. Please check your credentials.',
            status: 401
          });
        }

        return Promise.reject(error);
      }
    );
  }

  async authenticateEnumerator(enumeratorId, accessPassword) {
    try {
      const response = await this.api.post('/enumerators/auth', {
        enumerator_id: enumeratorId,
        access_password: accessPassword,
      });

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Authentication failed'
      };
    }
  }

  async uploadSurveyResponses(enumeratorId, responses) {
    try {
      const response = await this.api.post('/mobile/sync/upload', {
        enumerator_id: enumeratorId,
        responses: responses,
      });

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Upload failed'
      };
    }
  }

  async downloadAssignedSurveys(enumeratorId) {
    try {
      const response = await this.api.get(`/mobile/sync/download/${enumeratorId}`);

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Download failed'
      };
    }
  }

  async submitSurveyResponse(surveyId, responseData) {
    try {
      const response = await this.api.post(`/surveys/${surveyId}/responses`, responseData);

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Submission failed'
      };
    }
  }

  // Health check endpoint
  async checkServerHealth() {
    try {
      const response = await this.api.get('/');
      return {
        success: true,
        online: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        online: false,
        error: 'Server unreachable'
      };
    }
  }
}

export const ApiService = new ApiServiceClass();