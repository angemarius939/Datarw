import React, {useState, useContext} from 'react';
import {
  View,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import {
  TextInput,
  Button,
  Text,
  Card,
  Title,
  Paragraph,
  Snackbar,
  ActivityIndicator,
} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {AuthContext} from '../context/AuthContext';

const LoginScreen = () => {
  const [enumeratorId, setEnumeratorId] = useState('');
  const [accessPassword, setAccessPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showError, setShowError] = useState(false);

  const {login} = useContext(AuthContext);

  const handleLogin = async () => {
    if (!enumeratorId.trim() || !accessPassword.trim()) {
      setError('Please enter both Enumerator ID and Access Password');
      setShowError(true);
      return;
    }

    setLoading(true);
    setError('');

    const result = await login(enumeratorId.trim(), accessPassword.trim());

    if (!result.success) {
      setError(result.error);
      setShowError(true);
    }

    setLoading(false);
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.logoContainer}>
          <View style={styles.logo}>
            <Icon name="clipboard-list" size={60} color="#2563eb" />
          </View>
          <Title style={styles.title}>DataRW Survey</Title>
          <Paragraph style={styles.subtitle}>
            Mobile data collection for enumerators
          </Paragraph>
        </View>

        <Card style={styles.card}>
          <Card.Content>
            <Title style={styles.cardTitle}>Login</Title>
            
            <TextInput
              label="Enumerator ID"
              value={enumeratorId}
              onChangeText={setEnumeratorId}
              mode="outlined"
              style={styles.input}
              left={<TextInput.Icon icon="account" />}
              autoCapitalize="none"
              autoCorrect={false}
            />

            <TextInput
              label="Access Password"
              value={accessPassword}
              onChangeText={setAccessPassword}
              mode="outlined"
              secureTextEntry
              style={styles.input}
              left={<TextInput.Icon icon="lock" />}
              autoCapitalize="none"
              autoCorrect={false}
            />

            <Button
              mode="contained"
              onPress={handleLogin}
              loading={loading}
              disabled={loading}
              style={styles.loginButton}>
              {loading ? 'Authenticating...' : 'Login'}
            </Button>
          </Card.Content>
        </Card>

        <View style={styles.infoContainer}>
          <Card style={styles.infoCard}>
            <Card.Content>
              <Title style={styles.infoTitle}>How to use:</Title>
              <Paragraph style={styles.infoText}>
                1. Get your Enumerator ID and Access Password from your administrator
              </Paragraph>
              <Paragraph style={styles.infoText}>
                2. Login to download assigned surveys
              </Paragraph>
              <Paragraph style={styles.infoText}>
                3. Fill surveys offline and sync when connected
              </Paragraph>
            </Card.Content>
          </Card>
        </View>

        <Snackbar
          visible={showError}
          onDismiss={() => setShowError(false)}
          duration={4000}
          style={styles.snackbar}>
          {error}
        </Snackbar>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  scrollContent: {
    flexGrow: 1,
    padding: 20,
    justifyContent: 'center',
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logo: {
    width: 100,
    height: 100,
    borderRadius: 20,
    backgroundColor: '#dbeafe',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1e40af',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#64748b',
    textAlign: 'center',
  },
  card: {
    marginBottom: 30,
    elevation: 4,
  },
  cardTitle: {
    textAlign: 'center',
    marginBottom: 20,
    color: '#1e40af',
  },
  input: {
    marginBottom: 16,
  },
  loginButton: {
    marginTop: 10,
    paddingVertical: 8,
  },
  infoContainer: {
    marginTop: 20,
  },
  infoCard: {
    backgroundColor: '#f0f9ff',
    elevation: 2,
  },
  infoTitle: {
    fontSize: 18,
    color: '#1e40af',
    marginBottom: 10,
  },
  infoText: {
    color: '#475569',
    marginBottom: 8,
    fontSize: 14,
  },
  snackbar: {
    backgroundColor: '#dc2626',
  },
});

export default LoginScreen;