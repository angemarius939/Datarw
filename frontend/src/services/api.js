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

// AI Survey Generation API
export const aiAPI = {
  generateSurvey: (request) => api.post('/surveys/generate-ai', request),
  uploadContext: (files) => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    return api.post('/surveys/upload-context', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  translateSurvey: (surveyId, targetLanguage) => api.post(`/surveys/${surveyId}/translate`, null, {
    params: { target_language: targetLanguage }
  }),
  getSurveyContext: (organizationId) => api.get(`/surveys/context/${organizationId}`),
};

// Project Management API
export const projectsAPI = {
  getDashboard: () => api.get('/projects/dashboard'),
  getProjects: (status) => api.get('/projects', status ? { params: { status } } : {}),
  createProject: (projectData) => api.post('/projects', projectData),
  getProject: (projectId) => api.get(`/projects/${projectId}`),
  updateProject: (projectId, data) => api.put(`/projects/${projectId}`, data),
  deleteProject: (projectId) => api.delete(`/projects/${projectId}`),
  
  // Activities
  getActivities: (projectId) => api.get('/activities', projectId ? { params: { project_id: projectId } } : {}),
  createActivity: (activityData) => api.post('/activities', activityData),
  updateActivity: (activityId, data) => api.put(`/activities/${activityId}`, data),
  
  // Budget
  getBudgetItems: (projectId) => api.get('/budget', projectId ? { params: { project_id: projectId } } : {}),
  createBudgetItem: (budgetData) => api.post('/budget', budgetData),
  getBudgetSummary: (projectId) => api.get('/budget/summary', projectId ? { params: { project_id: projectId } } : {}),
  
  // KPIs
  getKPIs: (projectId) => api.get('/kpis', projectId ? { params: { project_id: projectId } } : {}),
  createKPI: (kpiData) => api.post('/kpis', kpiData),
  updateKPIValue: (indicatorId, currentValue) => api.put(`/kpis/${indicatorId}/value`, { current_value: currentValue }),
  
  // Beneficiaries
  getBeneficiaries: (projectId) => api.get('/beneficiaries', projectId ? { params: { project_id: projectId } } : {}),
  createBeneficiary: (beneficiaryData) => api.post('/beneficiaries', beneficiaryData),
  getBeneficiaryDemographics: (projectId) => api.get('/beneficiaries/demographics', projectId ? { params: { project_id: projectId } } : {}),
};

// Admin Panel API
export const adminAPI = {
  // Advanced User Management
  createUserAdvanced: (userData) => api.post('/admin/users/create-advanced', userData),
  bulkCreateUsers: (usersData, sendEmails = true) => api.post('/admin/users/bulk-create', usersData, {
    params: { send_emails: sendEmails }
  }),
  
  // Organization Branding
  getBranding: () => api.get('/admin/branding'),
  updateBranding: (brandingData) => api.put('/admin/branding', brandingData),
  
  // Email System
  getEmailLogs: (limit = 50) => api.get('/admin/email-logs', { params: { limit } }),
};

// Partners API
export const partnersAPI = {
  getPartners: (status) => api.get('/admin/partners', status ? { params: { status } } : {}),
  createPartner: (partnerData) => api.post('/admin/partners', partnerData),
  updatePartner: (partnerId, data) => api.put(`/admin/partners/${partnerId}`, data),
  
  // Performance Tracking
  createPerformance: (performanceData) => api.post('/admin/partners/performance', performanceData),
  getPerformanceSummary: (partnerId) => api.get('/admin/partners/performance/summary', partnerId ? { params: { partner_id: partnerId } } : {}),
};

export default api;