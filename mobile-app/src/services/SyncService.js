import {ApiService} from './ApiService';
import {DatabaseService} from './DatabaseService';

class SyncServiceClass {
  async uploadResponses(enumeratorId, responses) {
    try {
      const result = await ApiService.uploadSurveyResponses(enumeratorId, responses);
      
      if (result.success) {
        return {
          success: true,
          uploadedCount: result.data.processed_responses,
          message: `Successfully uploaded ${result.data.processed_responses} responses`
        };
      } else {
        return {
          success: false,
          error: result.error
        };
      }
    } catch (error) {
      console.error('Upload responses error:', error);
      return {
        success: false,
        error: 'Upload failed. Please try again later.'
      };
    }
  }

  async downloadSurveys(enumeratorId) {
    try {
      const result = await ApiService.downloadAssignedSurveys(enumeratorId);
      
      if (result.success) {
        return {
          success: true,
          data: result.data
        };
      } else {
        return {
          success: false,
          error: result.error
        };
      }
    } catch (error) {
      console.error('Download surveys error:', error);
      return {
        success: false,
        error: 'Download failed. Please try again later.'
      };
    }
  }

  async performFullSync(enumeratorId) {
    try {
      // Step 1: Upload pending responses
      const pendingResponses = await DatabaseService.getPendingResponses();
      
      if (pendingResponses.length > 0) {
        const uploadResult = await this.uploadResponses(enumeratorId, pendingResponses);
        
        if (!uploadResult.success) {
          return uploadResult;
        }

        // Mark responses as synced
        await DatabaseService.markResponsesAsSynced(
          pendingResponses.map(r => r.id)
        );
      }

      // Step 2: Download latest survey assignments
      const downloadResult = await this.downloadSurveys(enumeratorId);
      
      if (downloadResult.success) {
        // Update local database with new surveys
        await DatabaseService.storeSurveys(downloadResult.data.surveys);
      }

      // Step 3: Update sync timestamp
      const currentTime = new Date().toISOString();
      await DatabaseService.updateLastSyncTime(currentTime);

      return {
        success: true,
        uploadedResponses: pendingResponses.length,
        downloadedSurveys: downloadResult.success ? downloadResult.data.surveys.length : 0,
        message: `Sync completed: ${pendingResponses.length} responses uploaded, ${downloadResult.success ? downloadResult.data.surveys.length : 0} surveys downloaded`
      };

    } catch (error) {
      console.error('Full sync error:', error);
      return {
        success: false,
        error: 'Sync failed. Please try again later.'
      };
    }
  }

  async checkConnectivity() {
    try {
      const result = await ApiService.checkServerHealth();
      return result.success && result.online;
    } catch (error) {
      return false;
    }
  }
}

export const SyncService = new SyncServiceClass();