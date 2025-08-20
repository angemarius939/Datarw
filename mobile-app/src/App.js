import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {Provider as PaperProvider} from 'react-native-paper';
import {GestureHandlerRootView} from 'react-native-gesture-handler';
import {SafeAreaProvider} from 'react-native-safe-area-context';
import AppNavigator from './navigation/AppNavigator';
import {AuthProvider} from './context/AuthContext';
import {DatabaseProvider} from './context/DatabaseContext';
import {SyncProvider} from './context/SyncContext';
import {theme} from './styles/theme';

const App = () => {
  return (
    <GestureHandlerRootView style={{flex: 1}}>
      <SafeAreaProvider>
        <PaperProvider theme={theme}>
          <DatabaseProvider>
            <AuthProvider>
              <SyncProvider>
                <NavigationContainer>
                  <AppNavigator />
                </NavigationContainer>
              </SyncProvider>
            </AuthProvider>
          </DatabaseProvider>
        </PaperProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
};

export default App;