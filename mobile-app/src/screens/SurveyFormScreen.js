import React, {useState, useEffect, useContext} from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import {
  Text,
  Card,
  Title,
  Button,
  TextInput,
  RadioButton,
  Checkbox,
  ProgressBar,
  Snackbar,
} from 'react-native-paper';
import {useRoute, useNavigation} from '@react-navigation/native';
import {SyncContext} from '../context/SyncContext';

const SurveyFormScreen = () => {
  const route = useRoute();
  const navigation = useNavigation();
  const {survey} = route.params;
  const {addPendingResponse} = useContext(SyncContext);

  const [responses, setResponses] = useState({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [startTime] = useState(new Date());
  const [showSnackbar, setShowSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const questions = survey.questions || [];
  const currentQuestion = questions[currentQuestionIndex];
  const progress = questions.length > 0 ? (currentQuestionIndex + 1) / questions.length : 0;

  useEffect(() => {
    navigation.setOptions({
      title: survey.title || 'Survey Form',
      headerLeft: () => (
        <Button onPress={handleGoBack} mode="text">
          Exit
        </Button>
      ),
    });
  }, [navigation, survey.title]);

  const handleGoBack = () => {
    Alert.alert(
      'Exit Survey',
      'Are you sure you want to exit? Your progress will be lost.',
      [
        {text: 'Stay', style: 'cancel'},
        {text: 'Exit', style: 'destructive', onPress: () => navigation.goBack()},
      ]
    );
  };

  const handleResponseChange = (questionId, value) => {
    setResponses(prev => ({
      ...prev,
      [questionId]: value,
    }));
  };

  const isQuestionAnswered = (question) => {
    const response = responses[question.id];
    if (question.required) {
      return response !== undefined && response !== '' && response !== null;
    }
    return true;
  };

  const handleNext = () => {
    if (!isQuestionAnswered(currentQuestion)) {
      setSnackbarMessage('Please answer this required question before continuing.');
      setShowSnackbar(true);
      return;
    }

    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      handleSubmit();
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    // Check if all required questions are answered
    const unansweredRequired = questions.filter(
      q => q.required && !responses[q.id]
    );

    if (unansweredRequired.length > 0) {
      Alert.alert(
        'Incomplete Survey',
        `Please answer all required questions (${unansweredRequired.length} remaining).`
      );
      return;
    }

    try {
      const completionTime = (new Date() - startTime) / (1000 * 60); // in minutes

      const surveyResponse = {
        survey_id: survey.id,
        responses: responses,
        completion_time: completionTime,
      };

      await addPendingResponse(surveyResponse);

      Alert.alert(
        'Survey Completed!',
        'Your responses have been saved and will be synced when you\'re online.',
        [{text: 'OK', onPress: () => navigation.goBack()}]
      );
    } catch (error) {
      console.error('Error saving survey response:', error);
      Alert.alert('Error', 'Failed to save your responses. Please try again.');
    }
  };

  const renderQuestion = (question) => {
    const response = responses[question.id];

    switch (question.type) {
      case 'multiple_choice':
        return (
          <View style={styles.questionContainer}>
            <Text style={styles.questionText}>
              {question.question}
              {question.required && <Text style={styles.required}> *</Text>}
            </Text>
            <RadioButton.Group
              onValueChange={value => handleResponseChange(question.id, value)}
              value={response || ''}>
              {question.options?.map((option, index) => (
                <View key={index} style={styles.radioOption}>
                  <RadioButton value={option} />
                  <Text style={styles.optionText}>{option}</Text>
                </View>
              ))}
            </RadioButton.Group>
          </View>
        );

      case 'text':
        return (
          <View style={styles.questionContainer}>
            <Text style={styles.questionText}>
              {question.question}
              {question.required && <Text style={styles.required}> *</Text>}
            </Text>
            <TextInput
              mode="outlined"
              multiline
              numberOfLines={4}
              value={response || ''}
              onChangeText={value => handleResponseChange(question.id, value)}
              style={styles.textInput}
              placeholder="Enter your answer here..."
            />
          </View>
        );

      case 'rating':
        return (
          <View style={styles.questionContainer}>
            <Text style={styles.questionText}>
              {question.question}
              {question.required && <Text style={styles.required}> *</Text>}
            </Text>
            <Text style={styles.ratingLabel}>
              Rate from 1 to {question.scale || 5}
            </Text>
            <RadioButton.Group
              onValueChange={value => handleResponseChange(question.id, parseInt(value))}
              value={response?.toString() || ''}>
              <View style={styles.ratingContainer}>
                {Array.from({length: question.scale || 5}, (_, i) => i + 1).map(
                  rating => (
                    <View key={rating} style={styles.ratingOption}>
                      <RadioButton value={rating.toString()} />
                      <Text style={styles.ratingText}>{rating}</Text>
                    </View>
                  )
                )}
              </View>
            </RadioButton.Group>
          </View>
        );

      default:
        return (
          <View style={styles.questionContainer}>
            <Text style={styles.questionText}>
              {question.question}
              {question.required && <Text style={styles.required}> *</Text>}
            </Text>
            <TextInput
              mode="outlined"
              value={response || ''}
              onChangeText={value => handleResponseChange(question.id, value)}
              style={styles.textInput}
              placeholder="Enter your answer..."
            />
          </View>
        );
    }
  };

  if (questions.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>This survey has no questions.</Text>
        <Button mode="outlined" onPress={() => navigation.goBack()}>
          Go Back
        </Button>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <View style={styles.header}>
        <Title style={styles.surveyTitle}>{survey.title}</Title>
        <Text style={styles.progressText}>
          Question {currentQuestionIndex + 1} of {questions.length}
        </Text>
        <ProgressBar progress={progress} style={styles.progressBar} />
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <Card style={styles.questionCard}>
          <Card.Content>
            {renderQuestion(currentQuestion)}
          </Card.Content>
        </Card>
      </ScrollView>

      <View style={styles.navigationButtons}>
        <Button
          mode="outlined"
          onPress={handlePrevious}
          disabled={currentQuestionIndex === 0}
          style={styles.navButton}>
          Previous
        </Button>
        <Button
          mode="contained"
          onPress={handleNext}
          style={styles.navButton}>
          {currentQuestionIndex === questions.length - 1 ? 'Submit' : 'Next'}
        </Button>
      </View>

      <Snackbar
        visible={showSnackbar}
        onDismiss={() => setShowSnackbar(false)}
        duration={3000}
        style={styles.snackbar}>
        {snackbarMessage}
      </Snackbar>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    padding: 16,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  surveyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1e40af',
    marginBottom: 8,
  },
  progressText: {
    fontSize: 14,
    color: '#64748b',
    marginBottom: 8,
  },
  progressBar: {
    height: 6,
    backgroundColor: '#e5e7eb',
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  questionCard: {
    marginBottom: 16,
    elevation: 2,
  },
  questionContainer: {
    paddingVertical: 8,
  },
  questionText: {
    fontSize: 18,
    fontWeight: '500',
    color: '#1f2937',
    marginBottom: 16,
    lineHeight: 24,
  },
  required: {
    color: '#dc2626',
    fontSize: 18,
  },
  textInput: {
    marginTop: 8,
  },
  radioOption: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 4,
  },
  optionText: {
    marginLeft: 8,
    fontSize: 16,
    flex: 1,
  },
  ratingLabel: {
    fontSize: 14,
    color: '#64748b',
    marginBottom: 12,
  },
  ratingContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 8,
  },
  ratingOption: {
    alignItems: 'center',
  },
  ratingText: {
    marginTop: 4,
    fontSize: 12,
    color: '#64748b',
  },
  navigationButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  navButton: {
    flex: 1,
    marginHorizontal: 8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    fontSize: 18,
    color: '#64748b',
    marginBottom: 24,
    textAlign: 'center',
  },
  snackbar: {
    backgroundColor: '#dc2626',
  },
});

export default SurveyFormScreen;