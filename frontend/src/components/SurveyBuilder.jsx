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
import { 
  Plus, 
  Trash2, 
  GripVertical, 
  Settings, 
  Eye, 
  Save,
  ArrowUp,
  ArrowDown
} from 'lucide-react';
import { questionTypes } from '../mock/mockData';

const SurveyBuilder = () => {
  const [survey, setSurvey] = useState({
    title: '',
    description: '',
    questions: []
  });

  const [selectedQuestionType, setSelectedQuestionType] = useState('');

  const addQuestion = (type) => {
    const newQuestion = {
      id: `q_${Date.now()}`,
      type: type,
      question: '',
      required: false,
      options: type === 'multiple_choice' ? ['Option 1', 'Option 2'] : [],
      scale: type === 'rating' ? 5 : null,
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
        <div>
          <Label htmlFor={`question-${question.id}`}>Question Text</Label>
          <Textarea
            id={`question-${question.id}`}
            value={question.question}
            onChange={(e) => updateQuestion(question.id, { question: e.target.value })}
            placeholder="Enter your question here..."
            className="mt-1"
          />
        </div>

        {question.type === 'multiple_choice' && (
          <div>
            <Label>Answer Options</Label>
            <div className="space-y-2 mt-2">
              {question.options.map((option, optionIndex) => (
                <div key={optionIndex} className="flex items-center space-x-2">
                  <Input
                    value={option}
                    onChange={(e) => updateOption(question.id, optionIndex, e.target.value)}
                    placeholder={`Option ${optionIndex + 1}`}
                  />
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => removeOption(question.id, optionIndex)}
                    className="text-red-600"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
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
          <Button className="bg-gradient-to-r from-green-600 to-blue-600">
            <Save className="h-4 w-4 mr-2" />
            Save Survey
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
              <div>
                <Label htmlFor="survey-title">Survey Title</Label>
                <Input
                  id="survey-title"
                  value={survey.title}
                  onChange={(e) => setSurvey(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Enter survey title..."
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="survey-description">Description</Label>
                <Textarea
                  id="survey-description"
                  value={survey.description}
                  onChange={(e) => setSurvey(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe your survey..."
                  className="mt-1"
                />
              </div>
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