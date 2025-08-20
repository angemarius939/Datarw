import React, {createContext, useState, useContext, useEffect} from 'react';
import NetInfo from '@react-native-community/netinfo';
import {AuthContext} from './AuthContext';
import {SyncService} from '../services/SyncService';
import {DatabaseService} from '../services/DatabaseService';

export const SyncContext = createContext();

export const SyncProvider = ({children}) => {
  const [isOnline, setIsOnline] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [pendingResponses, setPendingResponses] = useState(0);
  const [lastSyncTime, setLastSyncTime] = useState(null);
  const [syncStatus, setSyncStatus] = useState('idle'); // idle, syncing, success, error

  const {enumerator} = useContext(AuthContext);

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsOnline(state.isConnected);
      
      // Auto-sync when coming online
      if (state.isConnected && enumerator && pendingResponses > 0) {
        syncData();
      }
    });

    loadSyncStatus();

    return () => unsubscribe();
  }, [enumerator]);

  const loadSyncStatus = async () => {
    try {
      const pendingCount = await DatabaseService.getPendingResponsesCount();
      const lastSync = await DatabaseService.getLastSyncTime();
      
      setPendingResponses(pendingCount);
      setLastSyncTime(lastSync);
    } catch (error) {
      console.error('Load sync status error:', error);
    }
  };

  const syncData = async () => {
    if (!isOnline || isSyncing || !enumerator) {
      return {success: false, error: 'Cannot sync at this time'};
    }

    try {
      setIsSyncing(true);
      setSyncStatus('syncing');

      // Get pending responses
      const pendingResponses = await DatabaseService.getPendingResponses();
      
      if (pendingResponses.length === 0) {
        setSyncStatus('success');
        return {success: true, message: 'No data to sync'};
      }

      // Upload responses to server
      const uploadResult = await SyncService.uploadResponses(
        enumerator.id,
        pendingResponses
      );

      if (uploadResult.success) {
        // Mark responses as synced
        await DatabaseService.markResponsesAsSynced(
          pendingResponses.map(r => r.id)
        );

        // Download latest survey assignments
        const downloadResult = await SyncService.downloadSurveys(enumerator.id);
        
        if (downloadResult.success) {
          await DatabaseService.storeSurveys(downloadResult.data.surveys);
        }

        // Update sync status
        const currentTime = new Date().toISOString();
        await DatabaseService.updateLastSyncTime(currentTime);
        
        setLastSyncTime(currentTime);
        setPendingResponses(0);
        setSyncStatus('success');

        return {
          success: true, 
          message: `Synced ${pendingResponses.length} responses successfully`
        };
      } else {
        setSyncStatus('error');
        return {success: false, error: uploadResult.error};
      }
    } catch (error) {
      console.error('Sync error:', error);
      setSyncStatus('error');
      return {success: false, error: 'Sync failed. Please try again.'};
    } finally {
      setIsSyncing(false);
      // Reset status after 3 seconds
      setTimeout(() => setSyncStatus('idle'), 3000);
    }
  };

  const addPendingResponse = async (response) => {
    try {
      await DatabaseService.addSurveyResponse(response);
      const newCount = await DatabaseService.getPendingResponsesCount();
      setPendingResponses(newCount);
    } catch (error) {
      console.error('Add pending response error:', error);
    }
  };

  return (
    <SyncContext.Provider
      value={{
        isOnline,
        isSyncing,
        pendingResponses,
        lastSyncTime,
        syncStatus,
        syncData,
        addPendingResponse,
        loadSyncStatus,
      }}>
      {children}
    </SyncContext.Provider>
  );
};