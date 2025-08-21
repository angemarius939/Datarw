import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { Plus, Loader2, TrendingUp, Target, BarChart3, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';

const CreateKPIModal = ({ onKPICreated, trigger }) => {
  const { user, organization } = useAuth();
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState([]);
  const [users, setUsers] = useState([]);
  const [errors, setErrors] = useState({});
  const [kpi, setKPI] = useState({
    project_id: '',
    name: '',
    description: '',
    indicator_type: 'quantitative',
    level: 'output',
    baseline_value: '',
    target_value: '',
    unit_of_measurement: '',
    frequency: 'monthly',
    responsible_user_id: '',
    data_source: '',
    collection_method: '',
    disaggregation: {}
  });

  const indicatorTypes = [
    { value: 'quantitative', label: 'Quantitative (Numbers)' },
    { value: 'qualitative', label: 'Qualitative (Text/Categories)' }
  ];

  const levels = [
    { value: 'output', label: 'Output (Direct results of activities)' },
    { value: 'outcome', label: 'Outcome (Medium-term effects)' },
    { value: 'impact', label: 'Impact (Long-term changes)' }
  ];

  const frequencies = [
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'quarterly', label: 'Quarterly' },
    { value: 'semi-annually', label: 'Semi-Annually' },
    { value: 'annually', label: 'Annually' }
  ];

  useEffect(() => {
    if (open) {
      fetchProjects();
      fetchUsers();
    }
  }, [open]);

  const fetchProjects = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${backendUrl}/api/projects`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const projectsData = await response.json();
        setProjects(projectsData);
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${backendUrl}/api/users`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const usersData = await response.json();
        setUsers(usersData);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const validateKPI = () => {
    const newErrors = {};
    
    if (!kpi.project_id) {
      newErrors.project_id = 'Project is required';
    }
    
    if (!kpi.name.trim()) {
      newErrors.name = 'KPI name is required';
    }
    
    if (!kpi.description.trim()) {
      newErrors.description = 'Description is required';
    }
    
    if (kpi.indicator_type === 'quantitative') {
      if (kpi.baseline_value && isNaN(parseFloat(kpi.baseline_value))) {
        newErrors.baseline_value = 'Baseline value must be a number';
      }
      
      if (!kpi.target_value || isNaN(parseFloat(kpi.target_value))) {
        newErrors.target_value = 'Target value is required and must be a number';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreateKPI = async () => {
    if (!validateKPI()) {
      return;
    }

    setLoading(true);
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');
      
      const kpiData = {
        ...kpi,
        baseline_value: kpi.baseline_value ? parseFloat(kpi.baseline_value) : null,
        target_value: kpi.target_value ? parseFloat(kpi.target_value) : null,
      };

      console.log('🚀 Creating KPI:', kpiData);

      const response = await fetch(`${backendUrl}/api/kpis`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(kpiData)
      });

      if (response.ok) {
        const createdKPI = await response.json();
        
        toast({
          title: "Success!",
          description: "KPI indicator created successfully.",
          variant: "default",
        });
        
        setOpen(false);
        setKPI({
          project_id: '',
          name: '',
          description: '',
          indicator_type: 'quantitative',
          level: 'output',
          baseline_value: '',
          target_value: '',
          unit_of_measurement: '',
          frequency: 'monthly',
          responsible_user_id: '',
          data_source: '',
          collection_method: '',
          disaggregation: {}
        });
        
        if (onKPICreated) {
          onKPICreated(createdKPI);
        }
      } else {
        const errorText = await response.text();
        console.error('❌ Create KPI Error:', errorText);
        
        let errorMessage = 'Failed to create KPI';
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          errorMessage = `Server error: ${response.status}`;
        }
        
        toast({
          title: "Error",
          description: errorMessage,
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Create KPI error:', error);
      toast({
        title: "Error",
        description: `Failed to create KPI: ${error.message}`,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button className="bg-gradient-to-r from-blue-600 to-purple-600">
            <Plus className="h-4 w-4 mr-2" />
            Define KPI
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
            Define New KPI Indicator
          </DialogTitle>
          <DialogDescription>
            Create a Key Performance Indicator to track project progress and success.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          {/* Project Selection */}
          <div>
            <Label htmlFor="project">Project *</Label>
            <Select value={kpi.project_id} onValueChange={(value) => setKPI(prev => ({ ...prev, project_id: value }))}>
              <SelectTrigger className={`mt-1 ${errors.project_id ? 'border-red-500' : ''}`}>
                <SelectValue placeholder="Select project" />
              </SelectTrigger>
              <SelectContent>
                {projects.map(project => (
                  <SelectItem key={project._id || project.id} value={project._id || project.id}>
                    {project.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.project_id && (
              <div className="text-xs text-red-600 mt-1">{errors.project_id}</div>
            )}
          </div>

          {/* Basic Information */}
          <div>
            <Label htmlFor="name">KPI Name *</Label>
            <Input
              id="name"
              value={kpi.name}
              onChange={(e) => setKPI(prev => ({ ...prev, name: e.target.value }))}
              placeholder="e.g., Number of students trained, Customer satisfaction rate..."
              className={`mt-1 ${errors.name ? 'border-red-500' : ''}`}
            />
            {errors.name && (
              <div className="text-xs text-red-600 mt-1">{errors.name}</div>
            )}
          </div>
          
          <div>
            <Label htmlFor="description">Description *</Label>
            <Textarea
              id="description"
              value={kpi.description}
              onChange={(e) => setKPI(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Detailed description of what this indicator measures and why it's important..."
              className={`mt-1 ${errors.description ? 'border-red-500' : ''}`}
              rows={3}
            />
            {errors.description && (
              <div className="text-xs text-red-600 mt-1">{errors.description}</div>
            )}
          </div>

          {/* Indicator Configuration */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="type" className="flex items-center">
                <BarChart3 className="h-4 w-4 mr-1" />
                Indicator Type *
              </Label>
              <Select value={kpi.indicator_type} onValueChange={(value) => setKPI(prev => ({ ...prev, indicator_type: value }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {indicatorTypes.map(type => (
                    <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="level" className="flex items-center">
                <Target className="h-4 w-4 mr-1" />
                Result Level *
              </Label>
              <Select value={kpi.level} onValueChange={(value) => setKPI(prev => ({ ...prev, level: value }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {levels.map(level => (
                    <SelectItem key={level.value} value={level.value}>{level.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Quantitative Values */}
          {kpi.indicator_type === 'quantitative' && (
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="baseline">Baseline Value</Label>
                <Input
                  id="baseline"
                  type="number"
                  value={kpi.baseline_value}
                  onChange={(e) => setKPI(prev => ({ ...prev, baseline_value: e.target.value }))}
                  placeholder="Current value"
                  className={`mt-1 ${errors.baseline_value ? 'border-red-500' : ''}`}
                />
                {errors.baseline_value && (
                  <div className="text-xs text-red-600 mt-1">{errors.baseline_value}</div>
                )}
              </div>
              
              <div>
                <Label htmlFor="target">Target Value *</Label>
                <Input
                  id="target"
                  type="number"
                  value={kpi.target_value}
                  onChange={(e) => setKPI(prev => ({ ...prev, target_value: e.target.value }))}
                  placeholder="Desired value"
                  className={`mt-1 ${errors.target_value ? 'border-red-500' : ''}`}
                />
                {errors.target_value && (
                  <div className="text-xs text-red-600 mt-1">{errors.target_value}</div>
                )}
              </div>
              
              <div>
                <Label htmlFor="unit">Unit of Measurement</Label>
                <Input
                  id="unit"
                  value={kpi.unit_of_measurement}
                  onChange={(e) => setKPI(prev => ({ ...prev, unit_of_measurement: e.target.value }))}
                  placeholder="e.g., people, %, hours"
                  className="mt-1"
                />
              </div>
            </div>
          )}

          {/* Data Collection */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="frequency">Reporting Frequency</Label>
              <Select value={kpi.frequency} onValueChange={(value) => setKPI(prev => ({ ...prev, frequency: value }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {frequencies.map(freq => (
                    <SelectItem key={freq.value} value={freq.value}>{freq.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="responsible" className="flex items-center">
                <User className="h-4 w-4 mr-1" />
                Responsible Person
              </Label>
              <Select value={kpi.responsible_user_id} onValueChange={(value) => setKPI(prev => ({ ...prev, responsible_user_id: value }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select responsible person" />
                </SelectTrigger>
                <SelectContent>
                  {users.map(user => (
                    <SelectItem key={user.id} value={user.id}>
                      {user.name} ({user.email})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Data Sources */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="data_source">Data Source</Label>
              <Input
                id="data_source"
                value={kpi.data_source}
                onChange={(e) => setKPI(prev => ({ ...prev, data_source: e.target.value }))}
                placeholder="e.g., Survey data, Reports, Database"
                className="mt-1"
              />
            </div>
            
            <div>
              <Label htmlFor="collection_method">Collection Method</Label>
              <Input
                id="collection_method"
                value={kpi.collection_method}
                onChange={(e) => setKPI(prev => ({ ...prev, collection_method: e.target.value }))}
                placeholder="e.g., Online survey, Field visits, Interviews"
                className="mt-1"
              />
            </div>
          </div>
        </div>
        
        <div className="flex justify-end space-x-2 pt-4 border-t">
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleCreateKPI} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Plus className="h-4 w-4 mr-2" />
                Define KPI
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default CreateKPIModal;