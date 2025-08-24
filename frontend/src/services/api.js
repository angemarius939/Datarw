import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
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

// Payment Processing API
export const paymentsAPI = {
  createInvoice: (invoiceData) => api.post('/payments/create-invoice', invoiceData),
  initiatePayment: (paymentData) => api.post('/payments/initiate', paymentData),
  createSubscriptionPayment: (subscriptionData) => api.post('/payments/subscription', subscriptionData),
  getPaymentStatus: (invoiceNumber) => api.get(`/payments/status/${invoiceNumber}`),
  getPaymentHistory: (limit = 10, offset = 0) => api.get(`/payments/history?limit=${limit}&offset=${offset}`),
  getPricingPlans: () => api.get('/payments/plans'),
  subscribeToBasic: (userData) => paymentsAPI.createSubscriptionPayment({
    ...userData,
    plan_name: 'Basic',
    payment_method: userData.payment_method || 'MTN'
  }),
  subscribeToProfessional: (userData) => paymentsAPI.createSubscriptionPayment({
    ...userData,
    plan_name: 'Professional', 
    payment_method: userData.payment_method || 'MTN'
  }),
  subscribeToEnterprise: (userData) => paymentsAPI.createSubscriptionPayment({
    ...userData,
    plan_name: 'Enterprise',
    payment_method: userData.payment_method || 'MTN'
  })
};

// Project Management API
export const projectsAPI = {
  getDashboard: () => api.get('/projects/dashboard'),
  getProjects: (status) => api.get('/projects', status ? { params: { status } } : {}),
  createProject: (projectData) => api.post('/projects', projectData),
  getProject: (projectId) => api.get(`/projects/${projectId}`),
  updateProject: (projectId, data) => api.put(`/projects/${projectId}`, data),
  deleteProject: (projectId) => api.delete(`/projects/${projectId}`),
  getActivities: (projectId) => api.get('/activities', projectId ? { params: { project_id: projectId } } : {}),
  createActivity: (activityData) => api.post('/activities', activityData),
  updateActivity: (activityId, data) => api.put(`/activities/${activityId}`, data),
  getBudgetItems: (projectId) => api.get('/budget', projectId ? { params: { project_id: projectId } } : {}),
  createBudgetItem: (budgetData) => api.post('/budget', budgetData),
  getBudgetSummary: (projectId) => api.get('/budget/summary', projectId ? { params: { project_id: projectId } } : {}),
  getKPIs: (projectId) => api.get('/kpis', projectId ? { params: { project_id: projectId } } : {}),
  createKPI: (kpiData) => api.post('/kpis', kpiData),
  updateKPIValue: (indicatorId, currentValue) => api.put(`/kpis/${indicatorId}/value`, { current_value: currentValue }),
  getBeneficiaries: (projectId) => api.get('/beneficiaries', projectId ? { params: { project_id: projectId } } : {}),
  createBeneficiary: (beneficiaryData) => api.post('/beneficiaries', beneficiaryData),
  getBeneficiaryDemographics: (projectId) => api.get('/beneficiaries/demographics', projectId ? { params: { project_id: projectId } } : {}),
};

// Admin Panel API
export const adminAPI = {
  createUserAdvanced: (userData) => api.post('/admin/users/create-advanced', userData),
  bulkCreateUsers: (usersData, sendEmails = true) => api.post('/admin/users/bulk-create', usersData, {
    params: { send_emails: sendEmails }
  }),
  getBranding: () => api.get('/admin/branding'),
  updateBranding: (brandingData) => api.put('/admin/branding', brandingData),
  getEmailLogs: (limit = 50) => api.get('/admin/email-logs', { params: { limit } }),
};

// AI-Enhanced Automated Reporting API
export const reportsAPI = {
  generateReport: (reportData) => api.post('/reports/generate', null, {
    params: reportData
  }),
  getTemplates: () => api.get('/reports/templates'),
  getGeneratedReports: (projectId = null) => api.get('/reports/generated', 
    projectId ? { params: { project_id: projectId } } : {}
  ),
  downloadReport: (reportId) => api.get(`/reports/download/${reportId}`, {
    responseType: 'blob'
  }),
  uploadImages: (projectId, files) => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    return api.post(`/reports/upload-images?project_id=${projectId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getProjectImages: (projectId) => api.get(`/reports/project-images/${projectId}`),
  installDependencies: () => api.post('/reports/install-dependencies'),
  generateMonthlyReport: (projectId, year, month) => reportsAPI.generateReport({
    project_id: projectId,
    report_type: 'Monthly Report',
    period_start: new Date(year, month - 1, 1).toISOString(),
    period_end: new Date(year, month, 0).toISOString(),
    include_images: true,
    ai_narrative: true
  }),
  generateQuarterlyReport: (projectId, year, quarter) => {
    const quarterStartMonth = (quarter - 1) * 3;
    const quarterEndMonth = quarterStartMonth + 3;
    return reportsAPI.generateReport({
      project_id: projectId,
      report_type: 'Quarterly Report',
      period_start: new Date(year, quarterStartMonth, 1).toISOString(),
      period_end: new Date(year, quarterEndMonth, 0).toISOString(),
      include_images: true,
      ai_narrative: true
    });
  },
  generateAnnualReport: (projectId, year) => reportsAPI.generateReport({
    project_id: projectId,
    report_type: 'Annual Report',
    period_start: new Date(year, 0, 1).toISOString(),
    period_end: new Date(year, 11, 31).toISOString(),
    include_images: true,
    ai_narrative: true
  }),
  generateCustomReport: (projectId, reportType, startDate, endDate, options = {}) => reportsAPI.generateReport({
    project_id: projectId,
    report_type: reportType,
    period_start: startDate,
    period_end: endDate,
    include_images: options.include_images !== false,
    ai_narrative: options.ai_narrative !== false
  })
};

// Partners API
export const partnersAPI = {
  getPartners: (status) => api.get('/admin/partners', status ? { params: { status } } : {}),
  createPartner: (partnerData) => api.post('/admin/partners', partnerData),
  updatePartner: (partnerId, data) => api.put(`/admin/partners/${partnerId}`, data),
  createPerformance: (performanceData) => api.post('/admin/partners/performance', performanceData),
  getPerformanceSummary: (partnerId) => api.get('/admin/partners/performance/summary', partnerId ? { params: { partner_id: partnerId } } : {}),
};

// Finance API (Budget Tracking)
export const financeAPI = {
  // Config
  getFinanceConfig: () => api.get('/finance/config'),
  updateFinanceConfig: (data) => api.put('/finance/config', data),

  // Expenses
  listExpenses: (params = {}) => api.get('/finance/expenses', { params }),
  createExpense: (data) => api.post('/finance/expenses', data),
  updateExpense: (expenseId, data) => api.put(`/finance/expenses/${expenseId}`, data),
  deleteExpense: (expenseId) => api.delete(`/finance/expenses/${expenseId}`),

  // CSV Import/Export
  exportExpensesCSV: (params = {}) => api.get('/finance/expenses/export-csv', { params, responseType: 'blob' }),
  importExpensesCSV: (file) => {
    const form = new FormData();
    form.append('file', file);
    return api.post('/finance/expenses/import-csv', form, { headers: { 'Content-Type': 'multipart/form-data' } });
  },

  // Analytics
  getBurnRate: (period = 'monthly') => api.get('/finance/burn-rate', { params: { period } }),
  getVariance: (projectId = null) => api.get('/finance/variance', projectId ? { params: { project_id: projectId } } : {}),
  getForecast: () => api.get('/finance/forecast'),
  getFundingUtilization: (donor = null) => api.get('/finance/funding-utilization', donor ? { params: { donor } } : {}),

  // AI Insights
  getAIInsights: (payload) => api.post('/finance/ai/insights', payload),

  // QuickBooks Online stubs
  qboConnect: () => api.post('/finance/integrations/qbo/connect'),
  qboStatus: () => api.get('/finance/integrations/qbo/status'),
  qboPushExpenses: () => api.post('/finance/integrations/qbo/push-expenses'),

  // Finance CSV Reports
  downloadProjectReportCSV: (projectId, params = {}) => api.get('/finance/reports/project-csv', { params: { project_id: projectId, ...params }, responseType: 'blob' }),
  downloadActivitiesReportCSV: (projectId, params = {}) => api.get('/finance/reports/activities-csv', { params: { project_id: projectId, ...params }, responseType: 'blob' }),
  downloadAllProjectsReportCSV: (params = {}) => api.get('/finance/reports/all-projects-csv', { params, responseType: 'blob' }),
  downloadProjectReportXLSX: (projectId, params = {}) => api.get('/finance/reports/project-xlsx', { params: { project_id: projectId, ...params }, responseType: 'blob' }),
  downloadActivitiesReportXLSX: (projectId, params = {}) => api.get('/finance/reports/activities-xlsx', { params: { project_id: projectId, ...params }, responseType: 'blob' }),
  downloadAllProjectsReportXLSX: (params = {}) => api.get('/finance/reports/all-projects-xlsx', { params, responseType: 'blob' }),
  downloadProjectReportPDF: (projectId, params = {}) => api.get('/finance/reports/project-pdf', { params: { project_id: projectId, ...params }, responseType: 'blob' }),
  downloadActivitiesReportPDF: (projectId, params = {}) => api.get('/finance/reports/activities-pdf', { params: { project_id: projectId, ...params }, responseType: 'blob' }),
  downloadAllProjectsReportPDF: (params = {}) => api.get('/finance/reports/all-projects-pdf', { params, responseType: 'blob' }),
};

export default api;