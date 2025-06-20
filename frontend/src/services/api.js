import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      localStorage.removeItem('organization');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('organization');
  }
};

// Organization API
export const organizationAPI = {
  getMyOrganization: () => api.get('/organizations/me'),
  updateMyOrganization: (data) => api.put('/organizations/me', data),
};

// Users API
export const usersAPI = {
  getUsers: () => api.get('/users'),
  createUser: (userData) => api.post('/users', userData),
  updateUser: (userId, data) => api.put(`/users/${userId}`, data),
  deleteUser: (userId) => api.delete(`/users/${userId}`),
};

// Surveys API
export const surveysAPI = {
  getSurveys: () => api.get('/surveys'),
  createSurvey: (surveyData) => api.post('/surveys', surveyData),
  getSurvey: (surveyId) => api.get(`/surveys/${surveyId}`),
  updateSurvey: (surveyId, data) => api.put(`/surveys/${surveyId}`, data),
  deleteSurvey: (surveyId) => api.delete(`/surveys/${surveyId}`),
  getSurveyResponses: (surveyId) => api.get(`/surveys/${surveyId}/responses`),
  submitResponse: (surveyId, responseData) => api.post(`/surveys/${surveyId}/responses`, responseData),
};

// Analytics API
export const analyticsAPI = {
  getAnalytics: () => api.get('/analytics'),
};

// Payment API
export const paymentAPI = {
  createCheckoutSession: (plan) => api.post('/payments/checkout/session', null, { params: { plan } }),
  getCheckoutStatus: (sessionId) => api.get(`/payments/checkout/status/${sessionId}`),
  getPaymentHistory: () => api.get('/payments/history'),
  getPaymentPlans: () => api.get('/payments/plans'),
};

export default api;