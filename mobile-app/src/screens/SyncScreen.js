import React, {useContext} from 'react';
import {View, StyleSheet, ScrollView} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  List,
  Chip,
  Text,
  ProgressBar,
} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {SyncContext} from '../context/SyncContext';
import {AuthContext} from '../context/AuthContext';

const SyncScreen = () => {
  const {
    isOnline,
    isSyncing,
    pendingResponses,
    lastSyncTime,
    syncStatus,
    syncData,
  } = useContext(SyncContext);

  const {enumerator} = useContext(AuthContext);

  const formatSyncTime = (timestamp) => {
    if (!timestamp) return 'Never';
    
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return 'Never';
    }
  };

  const getSyncStatusColor = () => {
    switch (syncStatus) {
      case 'success':
        return '#059669';
      case 'error':
        return '#dc2626';
      case 'syncing':
        return '#2563eb';
      default:
        return '#64748b';
    }
  };

  const getSyncStatusIcon = () => {
    switch (syncStatus) {
      case 'success':
        return 'check-circle';
      case 'error':
        return 'alert-circle';
      case 'syncing':
        return 'sync';
      default:
        return 'sync-off';
    }
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Connection Status */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.statusHeader}>
            <Title style={styles.cardTitle}>Connection Status</Title>
            <Chip
              icon={isOnline ? 'wifi' : 'wifi-off'}
              style={[
                styles.statusChip,
                {backgroundColor: isOnline ? '#dcfce7' : '#fee2e2'},
              ]}>
              {isOnline ? 'Online' : 'Offline'}
            </Chip>
          </View>
          <Paragraph style={styles.statusDescription}>
            {isOnline
              ? 'Connected to internet. Data can be synced.'
              : 'No internet connection. Working in offline mode.'}
          </Paragraph>
        </Card.Content>
      </Card>

      {/* Sync Status */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.statusHeader}>
            <Title style={styles.cardTitle}>Sync Status</Title>
            <View style={styles.syncStatusContainer}>
              <Icon
                name={getSyncStatusIcon()}
                size={20}
                color={getSyncStatusColor()}
                style={styles.syncStatusIcon}
              />
              <Text style={[styles.syncStatusText, {color: getSyncStatusColor()}]}>
                {syncStatus === 'syncing' ? 'Syncing...' : 
                 syncStatus === 'success' ? 'Success' :
                 syncStatus === 'error' ? 'Error' : 'Idle'}
              </Text>
            </View>
          </View>
          
          {isSyncing && (
            <ProgressBar 
              indeterminate 
              style={styles.progressBar}
              color="#2563eb"
            />
          )}

          <List.Item
            title="Last Sync"
            description={formatSyncTime(lastSyncTime)}
            left={(props) => <List.Icon {...props} icon="clock-outline" />}
          />
          <List.Item
            title="Pending Responses"
            description={`${pendingResponses} responses waiting to sync`}
            left={(props) => <List.Icon {...props} icon="upload" />}
            right={() => (
              <Chip mode="outlined" compact>
                {pendingResponses}
              </Chip>
            )}
          />
        </Card.Content>
      </Card>

      {/* Sync Actions */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.cardTitle}>Sync Actions</Title>
          <View style={styles.actionButtons}>
            <Button
              mode="contained"
              onPress={syncData}
              loading={isSyncing}
              disabled={isSyncing || !isOnline}
              style={styles.syncButton}
              icon="sync">
              {isSyncing ? 'Syncing...' : 'Sync Now'}
            </Button>
            
            {!isOnline && (
              <Text style={styles.offlineNotice}>
                Sync is only available when online
              </Text>
            )}
          </View>
        </Card.Content>
      </Card>

      {/* Enumerator Info */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.cardTitle}>Account Information</Title>
          <List.Item
            title="Enumerator"
            description={enumerator?.name || 'Unknown'}
            left={(props) => <List.Icon {...props} icon="account" />}
          />
          <List.Item
            title="Email"
            description={enumerator?.email || 'Not provided'}
            left={(props) => <List.Icon {...props} icon="email" />}
          />
          <List.Item
            title="Status"
            description={enumerator?.status || 'Active'}
            left={(props) => <List.Icon {...props} icon="shield-check" />}
            right={() => (
              <Chip 
                mode="outlined" 
                compact
                style={{backgroundColor: '#dcfce7'}}>
                Active
              </Chip>
            )}
          />
        </Card.Content>
      </Card>

      {/* Sync Guidelines */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.cardTitle}>Sync Guidelines</Title>
          <View style={styles.guidelinesList}>
            <View style={styles.guidelineItem}>
              <Icon name="information" size={16} color="#2563eb" />
              <Text style={styles.guidelineText}>
                Sync regularly to backup your data
              </Text>
            </View>
            <View style={styles.guidelineItem}>
              <Icon name="wifi" size={16} color="#2563eb" />
              <Text style={styles.guidelineText}>
                WiFi connection recommended for large uploads
              </Text>
            </View>
            <View style={styles.guidelineItem}>
              <Icon name="battery-high" size={16} color="#2563eb" />
              <Text style={styles.guidelineText}>
                Ensure device has sufficient battery
              </Text>
            </View>
            <View style={styles.guidelineItem}>
              <Icon name="shield-check" size={16} color="#2563eb" />
              <Text style={styles.guidelineText}>
                All data is encrypted during transfer
              </Text>
            </View>
          </View>
        </Card.Content>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  card: {
    margin: 16,
    marginBottom: 0,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e40af',
    marginBottom: 8,
  },
  statusHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  statusChip: {
    borderRadius: 12,
  },
  statusDescription: {
    color: '#64748b',
    lineHeight: 20,
    marginBottom: 8,
  },
  syncStatusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  syncStatusIcon: {
    marginRight: 6,
  },
  syncStatusText: {
    fontSize: 14,
    fontWeight: '500',
  },
  progressBar: {
    marginVertical: 12,
    height: 4,
  },
  actionButtons: {
    marginTop: 8,
  },
  syncButton: {
    marginVertical: 8,
  },
  offlineNotice: {
    textAlign: 'center',
    color: '#64748b',
    fontSize: 12,
    fontStyle: 'italic',
    marginTop: 8,
  },
  guidelinesList: {
    marginTop: 8,
  },
  guidelineItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginVertical: 6,
  },
  guidelineText: {
    flex: 1,
    marginLeft: 8,
    fontSize: 14,
    color: '#475569',
    lineHeight: 18,
  },
});

export default SyncScreen;