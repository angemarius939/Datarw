import SQLite from 'react-native-sqlite-storage';

SQLite.DEBUG(true);
SQLite.enablePromise(true);

class DatabaseServiceClass {
  constructor() {
    this.db = null;
  }

  async initialize() {
    try {
      this.db = await SQLite.openDatabase({
        name: 'datarw.db',
        location: 'default',
      });

      await this.createTables();
      console.log('Database initialized successfully');
    } catch (error) {
      console.error('Database initialization error:', error);
      throw error;
    }
  }

  async createTables() {
    const createSurveysTable = `
      CREATE TABLE IF NOT EXISTS surveys (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        questions TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `;

    const createResponsesTable = `
      CREATE TABLE IF NOT EXISTS survey_responses (
        id TEXT PRIMARY KEY,
        survey_id TEXT NOT NULL,
        responses TEXT NOT NULL,
        completion_time REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        synced INTEGER DEFAULT 0,
        FOREIGN KEY (survey_id) REFERENCES surveys (id)
      )
    `;

    const createSyncLogTable = `
      CREATE TABLE IF NOT EXISTS sync_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        last_sync_time DATETIME,
        status TEXT
      )
    `;

    await this.db.executeSql(createSurveysTable);
    await this.db.executeSql(createResponsesTable);
    await this.db.executeSql(createSyncLogTable);
  }

  async storeSurveys(surveys) {
    try {
      // Clear existing surveys
      await this.db.executeSql('DELETE FROM surveys');

      // Insert new surveys
      for (const survey of surveys) {
        await this.db.executeSql(
          'INSERT OR REPLACE INTO surveys (id, title, description, questions, status) VALUES (?, ?, ?, ?, ?)',
          [
            survey.id,
            survey.title,
            survey.description || '',
            JSON.stringify(survey.questions || []),
            survey.status || 'active'
          ]
        );
      }
    } catch (error) {
      console.error('Store surveys error:', error);
      throw error;
    }
  }

  async getSurveys() {
    try {
      const [results] = await this.db.executeSql('SELECT * FROM surveys ORDER BY title');
      const surveys = [];

      for (let i = 0; i < results.rows.length; i++) {
        const row = results.rows.item(i);
        surveys.push({
          ...row,
          questions: JSON.parse(row.questions)
        });
      }

      return surveys;
    } catch (error) {
      console.error('Get surveys error:', error);
      return [];
    }
  }

  async getSurvey(surveyId) {
    try {
      const [results] = await this.db.executeSql(
        'SELECT * FROM surveys WHERE id = ?',
        [surveyId]
      );

      if (results.rows.length > 0) {
        const row = results.rows.item(0);
        return {
          ...row,
          questions: JSON.parse(row.questions)
        };
      }

      return null;
    } catch (error) {
      console.error('Get survey error:', error);
      return null;
    }
  }

  async addSurveyResponse(response) {
    try {
      const responseId = `resp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      await this.db.executeSql(
        'INSERT INTO survey_responses (id, survey_id, responses, completion_time) VALUES (?, ?, ?, ?)',
        [
          responseId,
          response.survey_id,
          JSON.stringify(response.responses),
          response.completion_time || null
        ]
      );

      return responseId;
    } catch (error) {
      console.error('Add survey response error:', error);
      throw error;
    }
  }

  async getPendingResponses() {
    try {
      const [results] = await this.db.executeSql(
        'SELECT * FROM survey_responses WHERE synced = 0 ORDER BY created_at'
      );

      const responses = [];
      for (let i = 0; i < results.rows.length; i++) {
        const row = results.rows.item(i);
        responses.push({
          id: row.id,
          survey_id: row.survey_id,
          responses: JSON.parse(row.responses),
          completion_time: row.completion_time,
          created_at: row.created_at
        });
      }

      return responses;
    } catch (error) {
      console.error('Get pending responses error:', error);
      return [];
    }
  }

  async getPendingResponsesCount() {
    try {
      const [results] = await this.db.executeSql(
        'SELECT COUNT(*) as count FROM survey_responses WHERE synced = 0'
      );

      return results.rows.item(0).count;
    } catch (error) {
      console.error('Get pending responses count error:', error);
      return 0;
    }
  }

  async markResponsesAsSynced(responseIds) {
    try {
      const placeholders = responseIds.map(() => '?').join(',');
      await this.db.executeSql(
        `UPDATE survey_responses SET synced = 1 WHERE id IN (${placeholders})`,
        responseIds
      );
    } catch (error) {
      console.error('Mark responses as synced error:', error);
      throw error;
    }
  }

  async updateLastSyncTime(timestamp) {
    try {
      await this.db.executeSql('DELETE FROM sync_log');
      await this.db.executeSql(
        'INSERT INTO sync_log (last_sync_time, status) VALUES (?, ?)',
        [timestamp, 'success']
      );
    } catch (error) {
      console.error('Update last sync time error:', error);
      throw error;
    }
  }

  async getLastSyncTime() {
    try {
      const [results] = await this.db.executeSql(
        'SELECT last_sync_time FROM sync_log ORDER BY id DESC LIMIT 1'
      );

      if (results.rows.length > 0) {
        return results.rows.item(0).last_sync_time;
      }

      return null;
    } catch (error) {
      console.error('Get last sync time error:', error);
      return null;
    }
  }

  async clearAllData() {
    try {
      await this.db.executeSql('DELETE FROM surveys');
      await this.db.executeSql('DELETE FROM survey_responses');
      await this.db.executeSql('DELETE FROM sync_log');
    } catch (error) {
      console.error('Clear all data error:', error);
      throw error;
    }
  }

  async getResponsesForSurvey(surveyId) {
    try {
      const [results] = await this.db.executeSql(
        'SELECT * FROM survey_responses WHERE survey_id = ? ORDER BY created_at DESC',
        [surveyId]
      );

      const responses = [];
      for (let i = 0; i < results.rows.length; i++) {
        const row = results.rows.item(i);
        responses.push({
          id: row.id,
          survey_id: row.survey_id,
          responses: JSON.parse(row.responses),
          completion_time: row.completion_time,
          created_at: row.created_at,
          synced: row.synced === 1
        });
      }

      return responses;
    } catch (error) {
      console.error('Get responses for survey error:', error);
      return [];
    }
  }
}

export const DatabaseService = new DatabaseServiceClass();