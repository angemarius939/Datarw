import React, {useState, useEffect, useContext} from 'react';
import {View, StyleSheet, FlatList, RefreshControl} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Chip,
  Text,
  FAB,
  Searchbar,
} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {AuthContext} from '../context/AuthContext';
import {SyncContext} from '../context/SyncContext';
import {DatabaseService} from '../services/DatabaseService';

const SurveyListScreen = ({navigation}) => {
  const [surveys, setSurveys] = useState([]);
  const [filteredSurveys, setFilteredSurveys] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  const {enumerator} = useContext(AuthContext);
  const {syncData, isSyncing} = useContext(SyncContext);

  useEffect(() => {
    loadSurveys();
  }, []);

  useEffect(() => {
    filterSurveys();
  }, [surveys, searchQuery]);

  const loadSurveys = async () => {
    try {
      setLoading(true);
      const localSurveys = await DatabaseService.getSurveys();
      setSurveys(localSurveys);
    } catch (error) {
      console.error('Load surveys error:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterSurveys = () => {
    if (!searchQuery.trim()) {
      setFilteredSurveys(surveys);
    } else {
      const filtered = surveys.filter(survey =>
        survey.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        survey.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredSurveys(filtered);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadSurveys();
    setRefreshing(false);
  };

  const handleSurveyPress = (survey) => {
    navigation.navigate('SurveyForm', {survey});
  };

  const getQuestionCount = (survey) => {
    return survey.questions ? survey.questions.length : 0;
  };

  const getSurveyResponses = async (surveyId) => {
    try {
      const responses = await DatabaseService.getResponsesForSurvey(surveyId);
      return responses.length;
    } catch (error) {
      return 0;
    }
  };

  const SurveyCard = ({item}) => {
    const [responseCount, setResponseCount] = useState(0);

    useEffect(() => {
      getSurveyResponses(item.id).then(setResponseCount);
    }, [item.id]);

    return (
      <Card style={styles.surveyCard} onPress={() => handleSurveyPress(item)}>
        <Card.Content>
          <View style={styles.surveyHeader}>
            <Title style={styles.surveyTitle}>{item.title}</Title>
            <Chip
              icon="clipboard-list"
              mode="outlined"
              compact
              style={[
                styles.statusChip,
                item.status === 'active' ? styles.activeChip : styles.draftChip,
              ]}>
              {item.status}
            </Chip>
          </View>

          <Paragraph style={styles.surveyDescription} numberOfLines={3}>
            {item.description || 'No description available'}
          </Paragraph>

          <View style={styles.surveyStats}>
            <View style={styles.stat}>
              <Icon name="help-circle" size={16} color="#64748b" />
              <Text style={styles.statText}>
                {getQuestionCount(item)} questions
              </Text>
            </View>
            <View style={styles.stat}>
              <Icon name="chart-line" size={16} color="#64748b" />
              <Text style={styles.statText}>
                {responseCount} responses
              </Text>
            </View>
          </View>

          <Button
            mode="contained"
            onPress={() => handleSurveyPress(item)}
            style={styles.startButton}>
            Start Survey
          </Button>
        </Card.Content>
      </Card>
    );
  };

  const EmptyState = () => (
    <View style={styles.emptyState}>
      <Icon name="clipboard-outline" size={80} color="#cbd5e1" />
      <Title style={styles.emptyTitle}>No Surveys Available</Title>
      <Paragraph style={styles.emptyText}>
        No surveys have been assigned to you yet. Please sync with the server or
        contact your administrator.
      </Paragraph>
      <Button
        mode="outlined"
        onPress={syncData}
        loading={isSyncing}
        disabled={isSyncing}
        style={styles.syncButton}>
        {isSyncing ? 'Syncing...' : 'Sync Now'}
      </Button>
    </View>
  );

  return (
    <View style={styles.container}>
      <Searchbar
        placeholder="Search surveys..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchbar}
      />

      {filteredSurveys.length === 0 && !loading ? (
        <EmptyState />
      ) : (
        <FlatList
          data={filteredSurveys}
          renderItem={({item}) => <SurveyCard item={item} />}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          showsVerticalScrollIndicator={false}
        />
      )}

      <FAB
        style={styles.fab}
        icon="sync"
        onPress={syncData}
        loading={isSyncing}
        disabled={isSyncing}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  searchbar: {
    margin: 16,
    elevation: 2,
  },
  listContent: {
    padding: 16,
    paddingTop: 0,
  },
  surveyCard: {
    marginBottom: 16,
    elevation: 2,
  },
  surveyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  surveyTitle: {
    flex: 1,
    fontSize: 18,
    marginRight: 8,
    color: '#1e40af',
  },
  statusChip: {
    height: 28,
  },
  activeChip: {
    backgroundColor: '#dcfce7',
  },
  draftChip: {
    backgroundColor: '#fef3c7',
  },
  surveyDescription: {
    color: '#64748b',
    marginBottom: 12,
    lineHeight: 20,
  },
  surveyStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  stat: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statText: {
    marginLeft: 4,
    fontSize: 14,
    color: '#64748b',
  },
  startButton: {
    marginTop: 8,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyTitle: {
    marginTop: 16,
    marginBottom: 8,
    color: '#475569',
  },
  emptyText: {
    textAlign: 'center',
    color: '#64748b',
    marginBottom: 24,
    lineHeight: 20,
  },
  syncButton: {
    paddingHorizontal: 16,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#2563eb',
  },
});

export default SurveyListScreen;