import React, {createContext, useEffect, useState} from 'react';
import {DatabaseService} from '../services/DatabaseService';

export const DatabaseContext = createContext();

export const DatabaseProvider = ({children}) => {
  const [dbReady, setDbReady] = useState(false);

  useEffect(() => {
    initializeDatabase();
  }, []);

  const initializeDatabase = async () => {
    try {
      await DatabaseService.initialize();
      setDbReady(true);
    } catch (error) {
      console.error('Database initialization failed:', error);
    }
  };

  return (
    <DatabaseContext.Provider value={{dbReady}}>
      {children}
    </DatabaseContext.Provider>
  );
};