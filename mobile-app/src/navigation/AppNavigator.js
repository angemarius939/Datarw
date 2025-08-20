import React, {useContext} from 'react';
import {createStackNavigator} from '@react-navigation/stack';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import {AuthContext} from '../context/AuthContext';
import LoginScreen from '../screens/LoginScreen';
import SurveyListScreen from '../screens/SurveyListScreen';
import SurveyFormScreen from '../screens/SurveyFormScreen';
import SyncScreen from '../screens/SyncScreen';
import SettingsScreen from '../screens/SettingsScreen';
import LoadingScreen from '../screens/LoadingScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

const MainTabs = () => {
  return (
    <Tab.Navigator
      screenOptions={({route}) => ({
        tabBarIcon: ({focused, color, size}) => {
          let iconName;

          if (route.name === 'Surveys') {
            iconName = focused ? 'clipboard-list' : 'clipboard-list-outline';
          } else if (route.name === 'Sync') {
            iconName = focused ? 'sync' : 'sync-off';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'cog' : 'cog-outline';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#2563eb',
        tabBarInactiveTintColor: '#6b7280',
        headerStyle: {
          backgroundColor: '#2563eb',
        },
        headerTintColor: '#ffffff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}>
      <Tab.Screen name="Surveys" component={SurveyListScreen} />
      <Tab.Screen name="Sync" component={SyncScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
};

const AppNavigator = () => {
  const {isAuthenticated, loading} = useContext(AuthContext);

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <Stack.Navigator screenOptions={{headerShown: false}}>
      {isAuthenticated ? (
        <>
          <Stack.Screen name="Main" component={MainTabs} />
          <Stack.Screen 
            name="SurveyForm" 
            component={SurveyFormScreen}
            options={{
              headerShown: true,
              title: 'Survey Form',
              headerStyle: {backgroundColor: '#2563eb'},
              headerTintColor: '#ffffff',
            }}
          />
        </>
      ) : (
        <Stack.Screen name="Login" component={LoginScreen} />
      )}
    </Stack.Navigator>
  );
};

export default AppNavigator;