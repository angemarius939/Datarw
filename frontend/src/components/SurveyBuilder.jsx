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
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
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
  Loader2,
  Sparkles,
  Upload,
  Languages,
  Brain
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
  const [aiGenerating, setAiGenerating] = useState(false);
  const [aiModalOpen, setAiModalOpen] = useState(false);
  const [documentModalOpen, setDocumentModalOpen] = useState(false);
  const [translateModalOpen, setTranslateModalOpen] = useState(false);
  const [aiRequest, setAiRequest] = useState({
    description: '',
    target_audience: '',
    survey_purpose: '',
    question_count: 10,
    include_demographics: false
  });
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [translating, setTranslating] = useState(false);
  const [previewModalOpen, setPreviewModalOpen] = useState(false);

  // Survey Preview Component
  const SurveyPreview = () => {
    if (survey.questions.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
          <p>No questions to preview. Add questions to see the preview.</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        <div className="border-b pb-4">
          <h2 className="text-2xl font-bold text-gray-900">
            {survey.title || "Untitled Survey"}
          </h2>
          {survey.description && (
            <p className="text-gray-600 mt-2">{survey.description}</p>
          )}
        </div>

        {survey.questions.map((question, index) => (
          <div key={question.id} className="border rounded-lg p-4 bg-gray-50">
            <div className="flex items-start space-x-2 mb-3">
              <span className="text-sm font-medium text-gray-500 min-w-[2rem]">
                {index + 1}.
              </span>
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">
                  {question.question || "Question text"}
                  {question.required && <span className="text-red-500 ml-1">*</span>}
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  {questionTypes.find(qt => qt.type === question.type)?.name || question.type}
                </p>
              </div>
            </div>

            <div className="ml-8">
              {/* Multiple Choice Preview */}
              {['multiple_choice_single', 'multiple_choice_multiple', 'dropdown'].includes(question.type) && (
                <div className="space-y-2">
                  {question.options.map((option, optionIndex) => (
                    <div key={optionIndex} className="flex items-center space-x-2">
                      <input
                        type={question.type === 'multiple_choice_multiple' ? 'checkbox' : 'radio'}
                        disabled
                        className="opacity-50"
                      />
                      <span className="text-sm text-gray-700">{option}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Text Input Preview */}
              {['short_text', 'long_text'].includes(question.type) && (
                <div>
                  {question.type === 'short_text' ? (
                    <input
                      type="text"
                      disabled
                      placeholder="Short text answer..."
                      className="w-full p-2 border rounded bg-white opacity-50"
                    />
                  ) : (
                    <textarea
                      disabled
                      placeholder="Long text answer..."
                      rows={3}
                      className="w-full p-2 border rounded bg-white opacity-50 resize-none"
                    />
                  )}
                </div>
              )}

              {/* Rating Scale Preview */}
              {['rating_scale', 'slider', 'numeric_scale'].includes(question.type) && (
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">
                      {question.scale_min || 1}
                    </span>
                    <input
                      type="range"
                      min={question.scale_min || 1}
                      max={question.scale_max || 5}
                      disabled
                      className="flex-1 opacity-50"
                    />
                    <span className="text-sm text-gray-500">
                      {question.scale_max || 5}
                    </span>
                  </div>
                </div>
              )}

              {/* Likert Scale Preview */}
              {question.type === 'likert_scale' && (
                <div className="space-y-2">
                  {question.scale_labels.map((label, labelIndex) => (
                    <div key={labelIndex} className="flex items-center space-x-2">
                      <input type="radio" disabled className="opacity-50" />
                      <span className="text-sm text-gray-700">{label}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Matrix Grid Preview */}
              {question.type === 'matrix_grid' && (
                <div className="overflow-x-auto">
                  <table className="min-w-full border">
                    <thead>
                      <tr>
                        <th className="border p-2 text-left text-xs font-medium text-gray-500"></th>
                        {question.matrix_columns.map((column, colIndex) => (
                          <th key={colIndex} className="border p-2 text-center text-xs font-medium text-gray-500">
                            {column}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {question.matrix_rows.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                          <td className="border p-2 text-sm text-gray-700 font-medium">{row}</td>
                          {question.matrix_columns.map((_, colIndex) => (
                            <td key={colIndex} className="border p-2 text-center">
                              <input type="radio" disabled className="opacity-50" />
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Yes/No Preview */}
              {question.type === 'yes_no' && (
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <input type="radio" disabled className="opacity-50" />
                    <span className="text-sm text-gray-700">Yes</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="radio" disabled className="opacity-50" />
                    <span className="text-sm text-gray-700">No</span>
                  </div>
                </div>
              )}

              {/* File Upload Preview */}
              {question.type === 'file_upload' && (
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center opacity-50">
                  <Upload className="h-8 w-8 mx-auto text-gray-400" />
                  <p className="text-sm text-gray-500 mt-1">Click to upload files</p>
                  {question.file_types_allowed.length > 0 && (
                    <p className="text-xs text-gray-400 mt-1">
                      Allowed: {question.file_types_allowed.join(', ').toUpperCase()}
                    </p>
                  )}
                </div>
              )}

              {/* Date/Time Picker Preview */}
              {['date_picker', 'time_picker', 'datetime_picker'].includes(question.type) && (
                <input
                  type={question.type.includes('date') && question.type.includes('time') ? 'datetime-local' : 
                        question.type.includes('date') ? 'date' : 'time'}
                  disabled
                  className="p-2 border rounded bg-white opacity-50"
                />
              )}

              {/* Ranking Preview */}
              {question.type === 'ranking' && (
                <div className="space-y-2">
                  <p className="text-xs text-gray-500 mb-2">Drag to reorder by preference:</p>
                  {question.options.map((option, optionIndex) => (
                    <div key={optionIndex} className="flex items-center space-x-2 p-2 border rounded bg-white opacity-50">
                      <GripVertical className="h-4 w-4 text-gray-400" />
                      <span className="text-sm text-gray-700">{option}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Signature Preview */}
              {question.type === 'signature' && (
                <div className="border-2 border-gray-300 rounded-lg p-8 text-center opacity-50">
                  <p className="text-sm text-gray-500">Signature area</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  // AI Generation Functions
  const handleGenerateWithAI = async () => {
    if (!aiRequest.description.trim()) {
      toast({
        title: "Validation Error",
        description: "Please provide a survey description.",
        variant: "destructive",
      });
      return;
    }

    setAiGenerating(true);
    
    try {
      const { aiAPI } = await import('../services/api');
      const response = await aiAPI.generateSurvey(aiRequest);
      
      if (response.data.success) {
        const { survey_data } = response.data;
        
        setSurvey({
          title: survey_data.title,
          description: survey_data.description,
          questions: survey_data.questions.map(q => ({
            ...q,
            id: `q_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
          }))
        });
        
        toast({
          title: "Success!",
          description: "AI has generated your survey. Review and modify as needed.",
          variant: "default",
        });
        
        setAiModalOpen(false);
      }
    } catch (error) {
      console.error('AI generation error:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to generate survey with AI.",
        variant: "destructive",
      });
    } finally {
      setAiGenerating(false);
    }
  };

  const handleUploadDocuments = async () => {
    if (uploadedFiles.length === 0) {
      toast({
        title: "No Files",
        description: "Please select files to upload.",
        variant: "destructive",
      });
      return;
    }

    try {
      const { aiAPI } = await import('../services/api');
      const response = await aiAPI.uploadContext(uploadedFiles);
      
      if (response.data.success) {
        toast({
          title: "Success!",
          description: `Uploaded ${response.data.documents_processed} documents for AI context.`,
          variant: "default",
        });
        
        setDocumentModalOpen(false);
        setUploadedFiles([]);
      }
    } catch (error) {
      console.error('Document upload error:', error);
      toast({
        title: "Error", 
        description: error.response?.data?.detail || "Failed to upload documents.",
        variant: "destructive",
      });
    }
  };

  const handleTranslateSurvey = async (language) => {
    if (survey.questions.length === 0) {
      toast({
        title: "No Survey",
        description: "Create a survey first before translating.",
        variant: "destructive",
      });
      return;
    }

    setTranslating(true);
    
    try {
      // For now, we'll simulate translation by creating a translated version
      // In practice, you'd save the survey first, then translate it
      const translatedSurvey = {
        ...survey,
        title: `${survey.title} (${language})`,
        description: `${survey.description} (Translated to ${language})`
      };
      
      setSurvey(translatedSurvey);
      
      toast({
        title: "Translation Complete",
        description: `Survey translated to ${language}. This is a demo - full translation requires a saved survey.`,
        variant: "default",
      });
      
      setTranslateModalOpen(false);
    } catch (error) {
      console.error('Translation error:', error);
      toast({
        title: "Error",
        description: "Failed to translate survey.",
        variant: "destructive",
      });
    } finally {
      setTranslating(false);
    }
  };

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
      
      // Multiple choice validation
      if (['multiple_choice_single', 'multiple_choice_multiple', 'dropdown', 'ranking'].includes(question.type)) {
        if (question.options.length < 2) {
          newErrors[`question_${index}_options`] = 'This question type needs at least 2 options';
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
      
      // Scale validation  
      if (['rating_scale', 'slider', 'numeric_scale'].includes(question.type)) {
        if (!question.scale_min && !question.scale_max) {
          newErrors[`question_${index}_scale`] = 'Please set minimum and maximum values';
        } else if (question.scale_min >= question.scale_max) {
          newErrors[`question_${index}_scale`] = 'Maximum value must be greater than minimum value';
        }
      }
      
      // Matrix validation
      if (question.type === 'matrix_grid') {
        if (question.matrix_rows.length < 2) {
          newErrors[`question_${index}_matrix`] = 'Matrix questions need at least 2 rows';
        }
        if (question.matrix_columns.length < 2) {
          newErrors[`question_${index}_matrix`] = 'Matrix questions need at least 2 columns';
        }
      }
      
      // File upload validation
      if (question.type === 'file_upload') {
        if (question.file_types_allowed.length === 0) {
          newErrors[`question_${index}_files`] = 'Please select at least one allowed file type';
        }
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

        {/* Multiple Choice (Single/Multiple) */}
        {['multiple_choice_single', 'multiple_choice_multiple', 'dropdown', 'ranking'].includes(question.type) && (
          <div>
            <div className="flex items-center justify-between">
              <Label>Answer Options</Label>
              {question.type === 'multiple_choice_multiple' && (
                <Badge variant="secondary">Multiple Selection</Badge>
              )}
            </div>
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

        {/* Rating Scale */}
        {['rating_scale', 'slider', 'numeric_scale'].includes(question.type) && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor={`scale-min-${question.id}`}>Minimum Value</Label>
              <Input
                id={`scale-min-${question.id}`}
                type="number"
                value={question.scale_min || ''}
                onChange={(e) => updateQuestion(question.id, { scale_min: parseInt(e.target.value) || null })}
                placeholder="1"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor={`scale-max-${question.id}`}>Maximum Value</Label>
              <Input
                id={`scale-max-${question.id}`}
                type="number"
                value={question.scale_max || ''}
                onChange={(e) => updateQuestion(question.id, { scale_max: parseInt(e.target.value) || null })}
                placeholder="5"
                className="mt-1"
              />
            </div>
            {question.type === 'slider' && (
              <div className="col-span-2">
                <Label htmlFor={`step-${question.id}`}>Step Size</Label>
                <Input
                  id={`step-${question.id}`}
                  type="number"
                  step="0.1"
                  value={question.slider_step || ''}
                  onChange={(e) => updateQuestion(question.id, { slider_step: parseFloat(e.target.value) || null })}
                  placeholder="1"
                  className="mt-1 w-32"
                />
              </div>
            )}
          </div>
        )}

        {/* Likert Scale */}
        {question.type === 'likert_scale' && (
          <div>
            <Label>Scale Labels</Label>
            <div className="grid grid-cols-1 gap-2 mt-2">
              {question.scale_labels.map((label, labelIndex) => (
                <Input
                  key={labelIndex}
                  value={label}
                  onChange={(e) => {
                    const newLabels = [...question.scale_labels];
                    newLabels[labelIndex] = e.target.value;
                    updateQuestion(question.id, { scale_labels: newLabels });
                  }}
                  placeholder={`Label ${labelIndex + 1}`}
                />
              ))}
            </div>
          </div>
        )}

        {/* Matrix Grid */}
        {question.type === 'matrix_grid' && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Row Labels</Label>
              <div className="space-y-2 mt-2">
                {question.matrix_rows.map((row, rowIndex) => (
                  <div key={rowIndex} className="flex items-center space-x-2">
                    <Input
                      value={row}
                      onChange={(e) => {
                        const newRows = [...question.matrix_rows];
                        newRows[rowIndex] = e.target.value;
                        updateQuestion(question.id, { matrix_rows: newRows });
                      }}
                      placeholder={`Row ${rowIndex + 1}`}
                    />
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        const newRows = question.matrix_rows.filter((_, i) => i !== rowIndex);
                        updateQuestion(question.id, { matrix_rows: newRows });
                      }}
                      className="text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    const newRows = [...question.matrix_rows, `Row ${question.matrix_rows.length + 1}`];
                    updateQuestion(question.id, { matrix_rows: newRows });
                  }}
                  className="w-full"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Row
                </Button>
              </div>
            </div>
            <div>
              <Label>Column Labels</Label>
              <div className="space-y-2 mt-2">
                {question.matrix_columns.map((column, columnIndex) => (
                  <div key={columnIndex} className="flex items-center space-x-2">
                    <Input
                      value={column}
                      onChange={(e) => {
                        const newColumns = [...question.matrix_columns];
                        newColumns[columnIndex] = e.target.value;
                        updateQuestion(question.id, { matrix_columns: newColumns });
                      }}
                      placeholder={`Column ${columnIndex + 1}`}
                    />
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        const newColumns = question.matrix_columns.filter((_, i) => i !== columnIndex);
                        updateQuestion(question.id, { matrix_columns: newColumns });
                      }}
                      className="text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    const newColumns = [...question.matrix_columns, `Column ${question.matrix_columns.length + 1}`];
                    updateQuestion(question.id, { matrix_columns: newColumns });
                  }}
                  className="w-full"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Column
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* File Upload Settings */}
        {question.type === 'file_upload' && (
          <div className="space-y-3">
            <div>
              <Label>File Types Allowed</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {['PDF', 'DOC', 'DOCX', 'JPG', 'PNG', 'GIF', 'MP4', 'MP3'].map(type => (
                  <div key={type} className="flex items-center space-x-2">
                    <Checkbox 
                      id={`${question.id}-${type}`}
                      checked={question.file_types_allowed.includes(type.toLowerCase())}
                      onCheckedChange={(checked) => {
                        const types = question.file_types_allowed || [];
                        const newTypes = checked 
                          ? [...types, type.toLowerCase()]
                          : types.filter(t => t !== type.toLowerCase());
                        updateQuestion(question.id, { file_types_allowed: newTypes });
                      }}
                    />
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
                value={question.max_file_size_mb || ''}
                onChange={(e) => updateQuestion(question.id, { max_file_size_mb: parseInt(e.target.value) || null })}
                placeholder="10"
                className="mt-1 w-32"
              />
            </div>
          </div>
        )}

        {/* Date/Time Picker Settings */}
        {['date_picker', 'time_picker', 'datetime_picker'].includes(question.type) && (
          <div>
            <Label htmlFor={`date-format-${question.id}`}>Date/Time Format</Label>
            <Select
              value={question.date_format || ''}
              onValueChange={(value) => updateQuestion(question.id, { date_format: value })}
            >
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Select format" />
              </SelectTrigger>
              <SelectContent>
                {question.type === 'date_picker' && (
                  <>
                    <SelectItem value="yyyy-mm-dd">YYYY-MM-DD</SelectItem>
                    <SelectItem value="dd/mm/yyyy">DD/MM/YYYY</SelectItem>
                    <SelectItem value="mm/dd/yyyy">MM/DD/YYYY</SelectItem>
                  </>
                )}
                {question.type === 'time_picker' && (
                  <>
                    <SelectItem value="hh:mm">HH:MM (24-hour)</SelectItem>
                    <SelectItem value="hh:mm am/pm">HH:MM AM/PM</SelectItem>
                  </>
                )}
                {question.type === 'datetime_picker' && (
                  <>
                    <SelectItem value="yyyy-mm-dd hh:mm">YYYY-MM-DD HH:MM</SelectItem>
                    <SelectItem value="dd/mm/yyyy hh:mm">DD/MM/YYYY HH:MM</SelectItem>
                  </>
                )}
              </SelectContent>
            </Select>
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
          <Dialog open={aiModalOpen} onOpenChange={setAiModalOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
                <Sparkles className="h-4 w-4 mr-2 text-purple-600" />
                Generate with AI
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle className="flex items-center">
                  <Brain className="h-5 w-5 mr-2 text-purple-600" />
                  AI Survey Generation
                </DialogTitle>
                <DialogDescription>
                  Describe your survey needs and let AI create a comprehensive questionnaire for you.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <Label htmlFor="ai-description">Survey Description *</Label>
                  <Textarea
                    id="ai-description"
                    value={aiRequest.description}
                    onChange={(e) => setAiRequest(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="e.g., 'Create a customer satisfaction survey for a restaurant focusing on food quality, service, and ambiance...'"
                    className="mt-1 min-h-[80px]"
                    rows={3}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="target-audience">Target Audience</Label>
                    <Input
                      id="target-audience"
                      value={aiRequest.target_audience}
                      onChange={(e) => setAiRequest(prev => ({ ...prev, target_audience: e.target.value }))}
                      placeholder="e.g., Restaurant customers"
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="survey-purpose">Survey Purpose</Label>
                    <Input
                      id="survey-purpose"
                      value={aiRequest.survey_purpose}
                      onChange={(e) => setAiRequest(prev => ({ ...prev, survey_purpose: e.target.value }))}
                      placeholder="e.g., Improve service quality"
                      className="mt-1"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="question-count">Number of Questions</Label>
                    <Input
                      id="question-count"
                      type="number"
                      min="5"
                      max="50"
                      value={aiRequest.question_count}
                      onChange={(e) => setAiRequest(prev => ({ ...prev, question_count: parseInt(e.target.value) || 10 }))}
                      className="mt-1"
                    />
                  </div>
                  <div className="flex items-center space-x-2 mt-6">
                    <Checkbox
                      id="include-demographics"
                      checked={aiRequest.include_demographics}
                      onCheckedChange={(checked) => setAiRequest(prev => ({ ...prev, include_demographics: checked }))}
                    />
                    <Label htmlFor="include-demographics" className="text-sm">Include demographic questions</Label>
                  </div>
                </div>
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setAiModalOpen(false)}>Cancel</Button>
                  <Button onClick={handleGenerateWithAI} disabled={aiGenerating}>
                    {aiGenerating ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4 mr-2" />
                        Generate Survey
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={documentModalOpen} onOpenChange={setDocumentModalOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
                <Upload className="h-4 w-4 mr-2 text-green-600" />
                Upload Documents
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Upload Context Documents</DialogTitle>
                <DialogDescription>
                  Upload business plans, policies, participant profiles, or strategic documents to help AI generate more relevant surveys.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <Label>Select Files</Label>
                  <Input
                    type="file"
                    multiple
                    accept=".txt,.doc,.docx,.pdf"
                    onChange={(e) => setUploadedFiles(Array.from(e.target.files))}
                    className="mt-1"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Supported formats: TXT, DOC, DOCX, PDF (up to 10MB each)
                  </p>
                </div>
                {uploadedFiles.length > 0 && (
                  <div>
                    <Label>Selected Files:</Label>
                    <ul className="text-sm text-gray-600 mt-1">
                      {uploadedFiles.map((file, index) => (
                        <li key={index}>{file.name} ({Math.round(file.size / 1024)} KB)</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setDocumentModalOpen(false)}>Cancel</Button>
                  <Button onClick={handleUploadDocuments}>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Documents
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={translateModalOpen} onOpenChange={setTranslateModalOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200">
                <Languages className="h-4 w-4 mr-2 text-blue-600" />
                Translate
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Translate Survey</DialogTitle>
                <DialogDescription>
                  Translate your survey to different languages for broader accessibility.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <Button
                    variant="outline"
                    onClick={() => handleTranslateSurvey('Kinyarwanda')}
                    disabled={translating}
                    className="h-16 flex-col"
                  >
                    <Languages className="h-6 w-6 mb-1" />
                    Kinyarwanda
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleTranslateSurvey('French')}
                    disabled={translating}
                    className="h-16 flex-col"
                  >
                    <Languages className="h-6 w-6 mb-1" />
                    French
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleTranslateSurvey('Swahili')}
                    disabled={translating}
                    className="h-16 flex-col"
                  >
                    <Languages className="h-6 w-6 mb-1" />
                    Swahili
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleTranslateSurvey('Spanish')}
                    disabled={translating}
                    className="h-16 flex-col"
                  >
                    <Languages className="h-6 w-6 mb-1" />
                    Spanish
                  </Button>
                </div>
                {translating && (
                  <div className="flex items-center justify-center py-4">
                    <Loader2 className="h-6 w-6 animate-spin mr-2" />
                    <span>Translating survey...</span>
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={previewModalOpen} onOpenChange={setPreviewModalOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Eye className="h-4 w-4 mr-2" />
                Preview
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Survey Preview</DialogTitle>
                <DialogDescription>
                  This is how your survey will appear to respondents.
                </DialogDescription>
              </DialogHeader>
              <div className="py-4">
                <SurveyPreview />
              </div>
            </DialogContent>
          </Dialog>
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