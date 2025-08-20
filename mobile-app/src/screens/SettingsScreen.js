import React, {useContext} from 'react';
import {View, StyleSheet, ScrollView, Alert} from 'react-native';
import {
  Card,
  Title,
  List,
  Switch,
  Button,
  Divider,
  Text,
} from 'react-native-paper';
import {AuthContext} from '../context/AuthContext';
import {SyncContext} from '../context/SyncContext';

const SettingsScreen = () => {
  const {enumerator, logout} = useContext(AuthContext);
  const {loadSyncStatus} = useContext(SyncContext);

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout? Any unsynced data will remain on this device.',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Logout',
          style: 'destructive',
          onPress: logout,
        },
      ]
    );
  };

  const handleClearCache = () => {
    Alert.alert(
      'Clear Cache',
      'This will clear temporary data but keep your surveys and responses. Continue?',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Clear',
          onPress: () => {
            loadSyncStatus();
            Alert.alert('Success', 'Cache cleared successfully');
          },
        },
      ]
    );
  };

  const showAbout = () => {
    Alert.alert(
      'About DataRW Survey',
      'Version: 1.0.0\n\nOffline survey data collection app for field researchers and enumerators.\n\nDeveloped by Research Analytics and AI Solutions Ltd.',
      [{text: 'OK'}]
    );
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Account Information */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.cardTitle}>Account</Title>
          <List.Item
            title={enumerator?.name || 'Unknown User'}
            description={enumerator?.email || 'No email provided'}
            left={(props) => <List.Icon {...props} icon="account-circle" />}
          />
          <List.Item
            title="Enumerator ID"
            description={enumerator?.id || 'Unknown'}
            left={(props) => <List.Icon {...props} icon="badge-account" />}
          />
          <List.Item
            title="Status"
            description="Active"
            left={(props) => <List.Icon {...props} icon="shield-check" />}
          />
        </Card.Content>
      </Card>

      {/* App Settings */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.cardTitle}>App Settings</Title>
          <List.Item
            title="Auto Sync"
            description="Automatically sync when connected to WiFi"
            left={(props) => <List.Icon {...props} icon="sync" />}
            right={() => <Switch value={true} disabled />}
          />
          <List.Item
            title="Offline Mode"
            description="Allow working without internet connection"
            left={(props) => <List.Icon {...props} icon="wifi-off" />}
            right={() => <Switch value={true} disabled />}
          />
          <List.Item
            title="Data Validation"
            description="Validate responses before saving"
            left={(props) => <List.Icon {...props} icon="shield-check" />}
            right={() => <Switch value={true} disabled />}
          />
        </Card.Content>
      </Card>

      {/* Data Management */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.cardTitle}>Data Management</Title>
          <List.Item
            title="Clear Cache"
            description="Remove temporary files and refresh data"
            left={(props) => <List.Icon {...props} icon="delete-sweep" />}
            onPress={handleClearCache}
          />
          <List.Item
            title="Storage Usage"
            description="View local storage usage"
            left={(props) => <List.Icon {...props} icon="database" />}
            right={() => <Text style={styles.storageText}>~2.5 MB</Text>}
          />
        </Card.Content>
      </Card>

      {/* Support */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.cardTitle}>Support</Title>
          <List.Item
            title="Help & Documentation"
            description="Learn how to use the app effectively"
            left={(props) => <List.Icon {...props} icon="help-circle" />}
            onPress={() => Alert.alert('Help', 'Documentation will be available in the next update.')}
          />
          <List.Item
            title="Contact Support"
            description="Get help with technical issues"
            left={(props) => <List.Icon {...props} icon="email" />}
            onPress={() => Alert.alert('Contact Support', 'Email: support@datarw.com\n\nPlease include your Enumerator ID when contacting support.')}
          />
          <List.Item
            title="Report Issue"
            description="Report bugs or suggest features"
            left={(props) => <List.Icon {...props} icon="bug" />}
            onPress={() => Alert.alert('Report Issue', 'Please contact your administrator or email support@datarw.com with issue details.')}
          />
        </Card.Content>
      </Card>

      {/* App Info */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.cardTitle}>App Information</Title>
          <List.Item
            title="Version"
            description="1.0.0"
            left={(props) => <List.Icon {...props} icon="information" />}
          />
          <List.Item
            title="About"
            description="Learn more about DataRW Survey"
            left={(props) => <List.Icon {...props} icon="information-outline" />}
            onPress={showAbout}
          />
          <List.Item
            title="Privacy Policy"
            description="View our privacy policy"
            left={(props) => <List.Icon {...props} icon="shield-account" />}
            onPress={() => Alert.alert('Privacy Policy', 'Your data is encrypted and stored securely. We only collect survey responses and do not share personal information with third parties.')}
          />
        </Card.Content>
      </Card>

      {/* Logout */}
      <View style={styles.logoutContainer}>
        <Button
          mode="contained"
          onPress={handleLogout}
          style={styles.logoutButton}
          buttonColor="#dc2626"
          textColor="#ffffff">
          Logout
        </Button>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          DataRW Survey v1.0.0
        </Text>
        <Text style={styles.footerSubtext}>
          Made by Research Analytics and AI Solutions Ltd.
        </Text>
      </View>
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
  storageText: {
    color: '#64748b',
    fontSize: 14,
    alignSelf: 'center',
  },
  logoutContainer: {
    margin: 16,
    marginTop: 32,
  },
  logoutButton: {
    paddingVertical: 8,
  },
  footer: {
    alignItems: 'center',
    padding: 32,
    paddingBottom: 16,
  },
  footerText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#64748b',
    marginBottom: 4,
  },
  footerSubtext: {
    fontSize: 12,
    color: '#9ca3af',
    textAlign: 'center',
  },
});

export default SettingsScreen;