import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Checkbox } from './ui/checkbox';
import { Switch } from './ui/switch';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Plus, 
  Trash2, 
  GripVertical, 
  Settings, 
  Eye, 
  Save,
  ArrowUp,
  ArrowDown,
  FileText,
  Loader2
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { surveysAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

// Question types definition
const questionTypes = [
  {
    type: "multiple_choice_single",
    name: "Multiple Choice (Single)",
    icon: "☑️",
    description: "Single selection from multiple options"
  },
  {
    type: "multiple_choice_multiple", 
    name: "Multiple Choice (Multiple)",
    icon: "☰",
    description: "Multiple selections allowed (checkboxes)"
  },
  {
    type: "short_text",
    name: "Short Text",
    icon: "📝",
    description: "Brief text responses (1-2 words)"
  },
  {
    type: "long_text",
    name: "Long Text", 
    icon: "📄",
    description: "Detailed text responses (paragraphs)"
  },
  {
    type: "rating_scale",
    name: "Rating Scale",
    icon: "⭐",
    description: "Numeric rating (1-5, 1-10, etc.)"
  },
  {
    type: "likert_scale",
    name: "Likert Scale",
    icon: "📊",
    description: "Agreement scale (Strongly Disagree to Strongly Agree)"
  },
  {
    type: "ranking",
    name: "Ranking Question",
    icon: "🔢",
    description: "Rank options in order of preference"
  },
  {
    type: "dropdown",
    name: "Dropdown",
    icon: "🔽",
    description: "Select one option from dropdown"
  },
  {
    type: "matrix_grid",
    name: "Matrix/Grid",
    icon: "⚏",
    description: "Grid of questions with same response options"
  },
  {
    type: "file_upload",
    name: "File Upload",
    icon: "📎",
    description: "Allow respondents to upload files"
  },
  {
    type: "date_picker",
    name: "Date Picker", 
    icon: "📅",
    description: "Select a specific date"
  },
  {
    type: "time_picker",
    name: "Time Picker",
    icon: "🕐",
    description: "Select a specific time"
  },
  {
    type: "datetime_picker", 
    name: "Date & Time Picker",
    icon: "📅",
    description: "Select both date and time"
  },
  {
    type: "slider",
    name: "Slider",
    icon: "🎚️", 
    description: "Visual slider for numeric input"
  },
  {
    type: "numeric_scale",
    name: "Numeric Scale",
    icon: "🔢",
    description: "Enter numeric value within range"
  },
  {
    type: "image_choice",
    name: "Image Choice",
    icon: "🖼️",
    description: "Choose from images"
  },
  {
    type: "yes_no", 
    name: "Yes/No",
    icon: "✅",
    description: "Simple yes/no question"
  },
  {
    type: "signature",
    name: "Signature Capture",
    icon: "✍️",
    description: "Digital signature capture"
  }
];

const SurveyBuilder = ({ onSurveyCreated }) => {
  const { toast } = useToast();
  const { user, organization } = useAuth();
  const [survey, setSurvey] = useState({
    title: '',
    description: '',
    questions: []
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const validateSurvey = () => {
    const newErrors = {};
    
    if (!survey.title.trim()) {
      newErrors.title = 'Survey title is required';
    } else if (survey.title.length > 200) {
      newErrors.title = 'Survey title must be 200 characters or less';
    }
    
    if (survey.description.length > 2000) {
      newErrors.description = 'Survey description must be 2000 characters or less';
    }
    
    if (survey.questions.length === 0) {
      newErrors.questions = 'At least one question is required';
    }
    
    // Validate each question
    survey.questions.forEach((question, index) => {
      if (!question.question.trim()) {
        newErrors[`question_${index}`] = 'Question text is required';
      } else if (question.question.length > 1000) {
        newErrors[`question_${index}`] = 'Question text must be 1000 characters or less';
      }
      
      if (question.type === 'multiple_choice') {
        if (question.options.length < 2) {
          newErrors[`question_${index}_options`] = 'Multiple choice questions need at least 2 options';
        }
        
        // Validate each option
        question.options.forEach((option, optionIndex) => {
          if (!option.trim()) {
            newErrors[`question_${index}_option_${optionIndex}`] = `Option ${optionIndex + 1} cannot be empty`;
          } else if (option.length > 500) {
            newErrors[`question_${index}_option_${optionIndex}`] = `Option ${optionIndex + 1} must be 500 characters or less`;
          }
        });
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSaveSurvey = async () => {
    if (!validateSurvey()) {
      toast({
        title: "Validation Error",
        description: "Please fix the errors before saving.",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    
    try {
      const surveyData = {
        title: survey.title.trim(),
        description: survey.description.trim(),
        questions: survey.questions.map(q => ({
          ...q,
          id: undefined // Let backend generate IDs
        }))
      };

      await surveysAPI.createSurvey(surveyData);
      
      toast({
        title: "Success!",
        description: "Survey created successfully.",
        variant: "default",
      });

      // Reset form
      setSurvey({
        title: '',
        description: '',
        questions: []
      });
      setErrors({});

      // Notify parent component
      if (onSurveyCreated) {
        onSurveyCreated();
      }

    } catch (error) {
      console.error('Error creating survey:', error);
      
      let errorMessage = 'Failed to create survey. Please try again.';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const addQuestion = (type) => {
    const newQuestion = {
      id: `q_${Date.now()}`,
      type: type,
      question: '',
      required: false,
      options: ['multiple_choice_single', 'multiple_choice_multiple', 'dropdown', 'ranking', 'image_choice'].includes(type) 
        ? ['Option 1', 'Option 2'] : [],
      scale_min: ['rating_scale', 'likert_scale', 'slider', 'numeric_scale'].includes(type) ? 1 : null,
      scale_max: ['rating_scale', 'likert_scale', 'slider', 'numeric_scale'].includes(type) ? 5 : null,
      scale_labels: type === 'likert_scale' 
        ? ['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'] : [],
      matrix_rows: type === 'matrix_grid' ? ['Row 1', 'Row 2'] : [],
      matrix_columns: type === 'matrix_grid' ? ['Column 1', 'Column 2'] : [],
      file_types_allowed: type === 'file_upload' ? ['pdf', 'doc', 'jpg', 'png'] : [],
      max_file_size_mb: type === 'file_upload' ? 10 : null,
      multiple_selection: type === 'multiple_choice_multiple',
      date_format: ['date_picker', 'datetime_picker'].includes(type) ? 'yyyy-mm-dd' : null,
      slider_step: type === 'slider' ? 1 : null,
      image_urls: type === 'image_choice' ? [] : [],
      validation_rules: {},
      skipLogic: null,
      calculation: null
    };

    setSurvey(prev => ({
      ...prev,
      questions: [...prev.questions, newQuestion]
    }));
  };

  const updateQuestion = (questionId, updates) => {
    setSurvey(prev => ({
      ...prev,
      questions: prev.questions.map(q => 
        q.id === questionId ? { ...q, ...updates } : q
      )
    }));
  };

  const removeQuestion = (questionId) => {
    setSurvey(prev => ({
      ...prev,
      questions: prev.questions.filter(q => q.id !== questionId)
    }));
  };

  const moveQuestion = (questionId, direction) => {
    setSurvey(prev => {
      const questions = [...prev.questions];
      const index = questions.findIndex(q => q.id === questionId);
      
      if (direction === 'up' && index > 0) {
        [questions[index], questions[index - 1]] = [questions[index - 1], questions[index]];
      } else if (direction === 'down' && index < questions.length - 1) {
        [questions[index], questions[index + 1]] = [questions[index + 1], questions[index]];
      }
      
      return { ...prev, questions };
    });
  };

  const addOption = (questionId) => {
    updateQuestion(questionId, {
      options: [...survey.questions.find(q => q.id === questionId).options, `Option ${survey.questions.find(q => q.id === questionId).options.length + 1}`]
    });
  };

  const updateOption = (questionId, optionIndex, value) => {
    const question = survey.questions.find(q => q.id === questionId);
    const newOptions = [...question.options];
    newOptions[optionIndex] = value;
    updateQuestion(questionId, { options: newOptions });
  };

  const removeOption = (questionId, optionIndex) => {
    const question = survey.questions.find(q => q.id === questionId);
    const newOptions = question.options.filter((_, index) => index !== optionIndex);
    updateQuestion(questionId, { options: newOptions });
  };

  const QuestionEditor = ({ question, index }) => (
    <Card className="relative border-l-4 border-l-blue-500">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <GripVertical className="h-4 w-4 text-gray-400 cursor-move" />
            <Badge variant="outline">
              {questionTypes.find(qt => qt.type === question.type)?.icon} {questionTypes.find(qt => qt.type === question.type)?.name}
            </Badge>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => moveQuestion(question.id, 'up')}
              disabled={index === 0}
            >
              <ArrowUp className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => moveQuestion(question.id, 'down')}
              disabled={index === survey.questions.length - 1}
            >
              <ArrowDown className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => removeQuestion(question.id)}
              className="text-red-600 hover:text-red-700"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {errors[`question_${index}`] && (
          <Alert variant="destructive">
            <AlertDescription>{errors[`question_${index}`]}</AlertDescription>
          </Alert>
        )}
        
        <div>
          <Label htmlFor={`question-${question.id}`}>Question Text</Label>
          <Textarea
            id={`question-${question.id}`}
            value={question.question}
            onChange={(e) => updateQuestion(question.id, { question: e.target.value })}
            placeholder="Enter your question here... You can write longer, more detailed questions as needed."
            className={`mt-1 min-h-[80px] resize-y ${errors[`question_${index}`] ? 'border-red-500' : ''}`}
            rows={3}
          />
          <div className="text-xs text-gray-500 mt-1 flex justify-between">
            <span>{question.question.length}/1000 characters</span>
            <span>Tip: Be clear and specific for better responses</span>
          </div>
        </div>

        {question.type === 'multiple_choice' && (
          <div>
            <Label>Answer Options</Label>
            {errors[`question_${index}_options`] && (
              <Alert variant="destructive" className="mt-2">
                <AlertDescription>{errors[`question_${index}_options`]}</AlertDescription>
              </Alert>
            )}
            <div className="space-y-2 mt-2">
              {question.options.map((option, optionIndex) => (
                <div key={optionIndex} className="space-y-1">
                  <div className="flex items-start space-x-2">
                    <div className="flex-1">
                      <Textarea
                        value={option}
                        onChange={(e) => updateOption(question.id, optionIndex, e.target.value)}
                        placeholder={`Option ${optionIndex + 1} - Enter your option text here...`}
                        rows={2}
                        className={`min-h-[60px] resize-y ${errors[`question_${index}_option_${optionIndex}`] ? 'border-red-500' : ''}`}
                      />
                      <div className="text-xs text-gray-500 mt-1">
                        {option.length}/500 characters
                      </div>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => removeOption(question.id, optionIndex)}
                      className="text-red-600 mt-1 flex-shrink-0"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                  {errors[`question_${index}_option_${optionIndex}`] && (
                    <div className="text-xs text-red-600 ml-2">
                      {errors[`question_${index}_option_${optionIndex}`]}
                    </div>
                  )}
                </div>
              ))}
              <Button
                size="sm"
                variant="outline"
                onClick={() => addOption(question.id)}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Option
              </Button>
            </div>
          </div>
        )}

        {question.type === 'rating' && (
          <div>
            <Label htmlFor={`scale-${question.id}`}>Rating Scale</Label>
            <Select
              value={question.scale?.toString()}
              onValueChange={(value) => updateQuestion(question.id, { scale: parseInt(value) })}
            >
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Select scale" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">1 to 5</SelectItem>
                <SelectItem value="10">1 to 10</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}

        {question.type === 'file_upload' && (
          <div className="space-y-3">
            <div>
              <Label>File Types Allowed</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {['PDF', 'Images', 'Documents', 'Spreadsheets'].map(type => (
                  <div key={type} className="flex items-center space-x-2">
                    <Checkbox id={`${question.id}-${type}`} />
                    <Label htmlFor={`${question.id}-${type}`} className="text-sm">{type}</Label>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <Label htmlFor={`max-size-${question.id}`}>Max File Size (MB)</Label>
              <Input
                id={`max-size-${question.id}`}
                type="number"
                placeholder="10"
                className="mt-1 w-32"
              />
            </div>
          </div>
        )}

        <div className="flex items-center justify-between pt-4 border-t">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Switch
                id={`required-${question.id}`}
                checked={question.required}
                onCheckedChange={(checked) => updateQuestion(question.id, { required: checked })}
              />
              <Label htmlFor={`required-${question.id}`} className="text-sm">Required</Label>
            </div>
          </div>
          <Button size="sm" variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            Advanced Settings
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Survey Builder</h1>
        <div className="flex space-x-2">
          <Button variant="outline">
            <Eye className="h-4 w-4 mr-2" />
            Preview
          </Button>
          <Button 
            className="bg-gradient-to-r from-green-600 to-blue-600"
            onClick={handleSaveSurvey}
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save Survey
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Question Types Panel */}
        <div className="lg:col-span-1">
          <Card className="sticky top-6">
            <CardHeader>
              <CardTitle className="text-lg">Question Types</CardTitle>
              <CardDescription>Drag or click to add questions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {questionTypes.map((type) => (
                  <Button
                    key={type.type}
                    variant="outline"
                    size="sm"
                    onClick={() => addQuestion(type.type)}
                    className="w-full justify-start text-left h-auto p-3"
                  >
                    <div>
                      <div className="flex items-center space-x-2">
                        <span>{type.icon}</span>
                        <span className="font-medium">{type.name}</span>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">{type.description}</p>
                    </div>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Survey Builder */}
        <div className="lg:col-span-3 space-y-6">
          {/* Survey Info */}
          <Card>
            <CardHeader>
              <CardTitle>Survey Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {errors.title && (
                <Alert variant="destructive">
                  <AlertDescription>{errors.title}</AlertDescription>
                </Alert>
              )}
              
              {errors.description && (
                <Alert variant="destructive">
                  <AlertDescription>{errors.description}</AlertDescription>
                </Alert>
              )}
              
              <div>
                <Label htmlFor="survey-title">Survey Title</Label>
                <Textarea
                  id="survey-title"
                  value={survey.title}
                  onChange={(e) => {
                    setSurvey(prev => ({ ...prev, title: e.target.value }));
                    if (errors.title) {
                      setErrors(prev => ({ ...prev, title: undefined }));
                    }
                  }}
                  placeholder="Enter a clear, descriptive title for your survey..."
                  className={`mt-1 min-h-[60px] resize-y ${errors.title ? 'border-red-500' : ''}`}
                  rows={2}
                />
                <div className="text-xs text-gray-500 mt-1 flex justify-between">
                  <span>{survey.title.length}/200 characters</span>
                  <span>Keep it concise but descriptive</span>
                </div>
              </div>
              
              <div>
                <Label htmlFor="survey-description">Description</Label>
                <Textarea
                  id="survey-description"
                  value={survey.description}
                  onChange={(e) => setSurvey(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe your survey purpose, target audience, and any important instructions for respondents..."
                  className="mt-1 min-h-[100px] resize-y"
                  rows={4}
                />
                <div className="text-xs text-gray-500 mt-1 flex justify-between">
                  <span>{survey.description.length}/2000 characters</span>
                  <span>A good description helps respondents understand your survey</span>
                </div>
              </div>
              
              {errors.questions && (
                <Alert variant="destructive">
                  <AlertDescription>{errors.questions}</AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Questions */}
          <div className="space-y-4">
            {survey.questions.length === 0 ? (
              <Card className="border-dashed border-2 border-gray-300">
                <CardContent className="text-center py-12">
                  <div className="text-gray-500 mb-4">
                    <FileText className="h-12 w-12 mx-auto mb-2" />
                    <p className="text-lg font-medium">No questions yet</p>
                    <p className="text-sm">Start building your survey by adding questions from the panel on the left.</p>
                  </div>
                </CardContent>
              </Card>
            ) : (
              survey.questions.map((question, index) => (
                <QuestionEditor key={question.id} question={question} index={index} />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SurveyBuilder;