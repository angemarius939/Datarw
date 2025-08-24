import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [organization, setOrganization] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check for existing auth data on mount
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user');
    const orgData = localStorage.getItem('organization');

    if (token && userData && orgData) {
      try {
        setUser(JSON.parse(userData));
        setOrganization(JSON.parse(orgData));
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error parsing stored auth data:', error);
        logout();
      }
    }
    setLoading(false);
  }, []);

  const postAuthRedirect = (tab = 'budgets') => {
    // Simple page reload to ensure authentication state is properly loaded
    window.location.reload();
  };

  const login = async (credentials) => {
    try {
      console.log('AuthContext: Login starting with credentials:', credentials);
      const response = await authAPI.login(credentials);
      console.log('AuthContext: Login response received:', response);
      const { access_token, user: userData, organization: orgData } = response.data;

      // Store auth data
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      localStorage.setItem('organization', JSON.stringify(orgData));

      setUser(userData);
      setOrganization(orgData);
      setIsAuthenticated(true);

      // Ensure dashboard becomes visible and deep link to budgets by default
      postAuthRedirect('budgets');

      return { success: true };
    } catch (error) {
      console.error('AuthContext: Login error:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData);
      const { access_token, user: newUser, organization: orgData } = response.data;

      // Store auth data
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(newUser));
      localStorage.setItem('organization', JSON.stringify(orgData));

      setUser(newUser);
      setOrganization(orgData);
      setIsAuthenticated(true);

      // Ensure dashboard becomes visible and deep link to budgets by default
      postAuthRedirect('budgets');

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed'
      };
    }
  };

  const logout = () => {
    authAPI.logout();
    setUser(null);
    setOrganization(null);
    setIsAuthenticated(false);
  };

  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const updateOrganization = (orgData) => {
    setOrganization(orgData);
    localStorage.setItem('organization', JSON.stringify(orgData));
  };

  const value = {
    user,
    organization,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
    updateUser,
    updateOrganization,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};