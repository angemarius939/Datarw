import React, {createContext, useState, useEffect} from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {DatabaseService} from '../services/DatabaseService';
import {ApiService} from '../services/ApiService';

export const AuthContext = createContext();

export const AuthProvider = ({children}) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [enumerator, setEnumerator] = useState(null);
  const [assignedSurveys, setAssignedSurveys] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const storedEnumerator = await AsyncStorage.getItem('enumerator');
      const storedSurveys = await AsyncStorage.getItem('assignedSurveys');
      
      if (storedEnumerator) {
        setEnumerator(JSON.parse(storedEnumerator));
        setAssignedSurveys(storedSurveys ? JSON.parse(storedSurveys) : []);
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('Auth check error:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (enumeratorId, accessPassword) => {
    try {
      setLoading(true);
      
      // First try to authenticate with the server
      const authResponse = await ApiService.authenticateEnumerator(
        enumeratorId,
        accessPassword
      );
      
      if (authResponse.success) {
        const {enumerator: authEnumerator, assigned_surveys} = authResponse.data;
        
        // Store authentication data
        await AsyncStorage.setItem('enumerator', JSON.stringify(authEnumerator));
        await AsyncStorage.setItem('assignedSurveys', JSON.stringify(assigned_surveys));
        
        // Store surveys in local database for offline access
        await DatabaseService.storeSurveys(assigned_surveys);
        
        setEnumerator(authEnumerator);
        setAssignedSurveys(assigned_surveys);
        setIsAuthenticated(true);
        
        return {success: true};
      } else {
        return {success: false, error: 'Invalid credentials'};
      }
    } catch (error) {
      console.error('Login error:', error);
      return {success: false, error: 'Network error. Please try again.'};
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await AsyncStorage.multiRemove(['enumerator', 'assignedSurveys']);
      await DatabaseService.clearAllData();
      
      setEnumerator(null);
      setAssignedSurveys([]);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const updateAssignedSurveys = async (surveys) => {
    try {
      await AsyncStorage.setItem('assignedSurveys', JSON.stringify(surveys));
      await DatabaseService.storeSurveys(surveys);
      setAssignedSurveys(surveys);
    } catch (error) {
      console.error('Update surveys error:', error);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        enumerator,
        assignedSurveys,
        loading,
        login,
        logout,
        updateAssignedSurveys,
      }}>
      {children}
    </AuthContext.Provider>
  );
};