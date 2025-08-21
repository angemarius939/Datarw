import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { Plus, Loader2, Calendar, User, Flag } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';

const CreateActivityModal = ({ onActivityCreated, trigger }) => {
  const { user, organization } = useAuth();
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState([]);
  const [users, setUsers] = useState([]);
  const [errors, setErrors] = useState({});
  const [activity, setActivity] = useState({
    project_id: '',
    name: '',
    description: '',
    assigned_to: '',
    assigned_team: '',
    start_date: '',
    end_date: '',
    planned_start_date: '',
    planned_end_date: '',
    budget_allocated: '',
    planned_output: '',
    target_quantity: '',
    actual_output: '',
    achieved_quantity: '',
    status_notes: '',
    risk_level: 'low',
    deliverables: [],
    dependencies: [],
    milestones: []
  });

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

  const validateActivity = () => {
    const newErrors = {};
    
    if (!activity.project_id) {
      newErrors.project_id = 'Project is required';
    }
    
    if (!activity.name.trim()) {
      newErrors.name = 'Activity name is required';
    }
    
    if (!activity.description.trim()) {
      newErrors.description = 'Activity description is required';
    }
    
    if (!activity.assigned_to) {
      newErrors.assigned_to = 'Assigned person is required';
    }
    
    if (!activity.start_date) {
      newErrors.start_date = 'Start date is required';
    }
    
    if (!activity.end_date) {
      newErrors.end_date = 'End date is required';
    }
    
    // Validate date range
    if (activity.start_date && activity.end_date) {
      if (new Date(activity.start_date) >= new Date(activity.end_date)) {
        newErrors.end_date = 'End date must be after start date';
      }
    }

    // Validate numbers (non-negative)
    const numericFields = [
      { key: 'budget_allocated', label: 'Budget Allocated' },
      { key: 'target_quantity', label: 'Target Quantity' },
      { key: 'achieved_quantity', label: 'Achieved Quantity' }
    ];
    numericFields.forEach(({ key, label }) => {
      const val = activity[key];
      if (val !== '' && val !== null && val !== undefined) {
        const num = Number(val);
        if (Number.isNaN(num) || num < 0) {
          newErrors[key] = `${label} must be a non-negative number`;
        }
      }
    });

    // Validate milestones (name + date) and ensure dates are within activity timeline if provided
    const milestoneErrors = [];
    activity.milestones.forEach((m, idx) => {
      if (!m.name?.trim()) {
        milestoneErrors.push(`Milestone ${idx + 1}: name is required`);
      }
      if (!m.planned_date) {
        milestoneErrors.push(`Milestone ${idx + 1}: target date is required`);
      } else {
        if (activity.start_date && new Date(m.planned_date) < new Date(activity.start_date)) {
          milestoneErrors.push(`Milestone ${idx + 1}: date before start date`);
        }
        if (activity.end_date && new Date(m.planned_date) > new Date(activity.end_date)) {
          milestoneErrors.push(`Milestone ${idx + 1}: date after end date`);
        }
      }
    });
    if (milestoneErrors.length) newErrors.milestones = milestoneErrors.join(', ');
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreateActivity = async () => {
    if (!validateActivity()) {
      return;
    }

    setLoading(true);
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');
      
      const activityData = {
        project_id: activity.project_id,
        name: activity.name,
        description: activity.description,
        assigned_to: activity.assigned_to,
        assigned_team: activity.assigned_team || null,
        start_date: new Date(activity.start_date).toISOString(),
        end_date: new Date(activity.end_date).toISOString(),
        planned_start_date: activity.planned_start_date ? new Date(activity.planned_start_date).toISOString() : new Date(activity.start_date).toISOString(),
        planned_end_date: activity.planned_end_date ? new Date(activity.planned_end_date).toISOString() : new Date(activity.end_date).toISOString(),
        budget_allocated: activity.budget_allocated ? parseFloat(activity.budget_allocated) : 0,
        planned_output: activity.planned_output || null,
        target_quantity: activity.target_quantity !== '' ? parseFloat(activity.target_quantity) : null,
        status_notes: activity.status_notes || null,
        risk_level: activity.risk_level || 'low',
        deliverables: activity.deliverables.filter(d => d.trim() !== ''),
        dependencies: activity.dependencies.filter(d => d.trim() !== ''),
        milestones: (activity.milestones || []).map(m => ({
          name: m.name,
          planned_date: new Date(m.planned_date).toISOString(),
          status: 'pending'
        })),
        // Extras (accepted by backend if allowed; otherwise safely ignored)
        actual_output: activity.actual_output || undefined,
        achieved_quantity: activity.achieved_quantity !== '' ? parseFloat(activity.achieved_quantity) : undefined
      };

      console.log('🚀 Creating activity:', activityData);

      const response = await fetch(`${backendUrl}/api/activities`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(activityData)
      });

      if (response.ok) {
        const createdActivity = await response.json();
        
        toast({
          title: 'Success!',
          description: 'Activity created successfully.',
        });
        
        setOpen(false);
        setActivity({
          project_id: '',
          name: '',
          description: '',
          assigned_to: '',
          assigned_team: '',
          start_date: '',
          end_date: '',
          planned_start_date: '',
          planned_end_date: '',
          budget_allocated: '',
          planned_output: '',
          target_quantity: '',
          actual_output: '',
          achieved_quantity: '',
          status_notes: '',
          risk_level: 'low',
          deliverables: [],
          dependencies: [],
          milestones: []
        });
        
        if (onActivityCreated) {
          onActivityCreated(createdActivity);
        }
      } else {
        const errorText = await response.text();
        console.error('❌ Create Activity Error:', errorText);
        
        let errorMessage = 'Failed to create activity';
        try {
          const errorData = JSON.parse(errorText);
          
          // Handle FastAPI validation errors
          if (errorData.detail && Array.isArray(errorData.detail)) {
            // Extract validation error messages
            const validationErrors = errorData.detail.map(err => {
              const field = err.loc ? err.loc[err.loc.length - 1] : 'field';
              return `${field}: ${err.msg}`;
            }).join(', ');
            errorMessage = `Validation errors: ${validationErrors}`;
          } else if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (errorData.message) {
            errorMessage = errorData.message;
          }
        } catch (e) {
          errorMessage = `Server error: ${response.status}`;
        }
        
        toast({
          title: 'Error',
          description: errorMessage,
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Create activity error:', error);
      toast({
        title: 'Error',
        description: `Failed to create activity: ${error.message}`,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const addDeliverable = () => {
    setActivity(prev => ({
      ...prev,
      deliverables: [...prev.deliverables, '']
    }));
  };

  const updateDeliverable = (index, value) => {
    setActivity(prev => ({
      ...prev,
      deliverables: prev.deliverables.map((d, i) => i === index ? value : d)
    }));
  };

  const removeDeliverable = (index) => {
    setActivity(prev => ({
      ...prev,
      deliverables: prev.deliverables.filter((_, i) => i !== index)
    }));
  };

  const addMilestone = () => {
    setActivity(prev => ({
      ...prev,
      milestones: [...prev.milestones, { name: '', planned_date: '' }]
    }));
  };

  const updateMilestone = (index, key, value) => {
    setActivity(prev => ({
      ...prev,
      milestones: prev.milestones.map((m, i) => i === index ? { ...m, [key]: value } : m)
    }));
  };

  const removeMilestone = (index) => {
    setActivity(prev => ({
      ...prev,
      milestones: prev.milestones.filter((_, i) => i !== index)
    }));
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button className="bg-gradient-to-r from-green-600 to-blue-600">
            <Plus className="h-4 w-4 mr-2" />
            Add Activity
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Plus className="h-5 w-5 mr-2 text-green-600" />
            Create New Activity
          </DialogTitle>
          <DialogDescription>
            Add a new activity to track project implementation and progress.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-5 py-2">
          {/* Project Selection */}
          <div>
            <Label htmlFor="project">Project *</Label>
            <Select value={activity.project_id} onValueChange={(value) => setActivity(prev => ({ ...prev, project_id: value }))}>
              <SelectTrigger className={`mt-1 ${errors.project_id ? 'border-red-500' : ''}`}>
                <SelectValue placeholder="Select project" />
              </SelectTrigger>
              <SelectContent>
                {projects.map(project => (
                  <SelectItem key={project._id || project.id} value={project._id || project.id}>
                    {project.name || project.title}
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
            <Label htmlFor="name">Activity Name *</Label>
            <Input
              id="name"
              value={activity.name}
              onChange={(e) => setActivity(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Enter activity name..."
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
              value={activity.description}
              onChange={(e) => setActivity(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe the activity objectives and scope..."
              className={`mt-1 ${errors.description ? 'border-red-500' : ''}`}
              rows={3}
            />
            {errors.description && (
              <div className="text-xs text-red-600 mt-1">{errors.description}</div>
            )}
          </div>

          {/* Responsible Person */}
          <div>
            <Label htmlFor="responsible" className="flex items-center">
              <User className="h-4 w-4 mr-1" />
              Assigned Person *
            </Label>
            <Select value={activity.assigned_to} onValueChange={(value) => setActivity(prev => ({ ...prev, assigned_to: value }))}>
              <SelectTrigger className={`mt-1 ${errors.assigned_to ? 'border-red-500' : ''}`}>
                <SelectValue placeholder="Select assigned person" />
              </SelectTrigger>
              <SelectContent>
                {users.map(user => (
                  <SelectItem key={user.id} value={user.id}>
                    {user.name} ({user.email})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.assigned_to && (
              <div className="text-xs text-red-600 mt-1">{errors.assigned_to}</div>
            )}
          </div>

          {/* Timeline */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="start_date" className="flex items-center">
                <Calendar className="h-4 w-4 mr-1" />
                Start Date *
              </Label>
              <Input
                id="start_date"
                type="date"
                value={activity.start_date}
                onChange={(e) => setActivity(prev => ({ ...prev, start_date: e.target.value }))}
                className={`mt-1 ${errors.start_date ? 'border-red-500' : ''}`}
              />
              {errors.start_date && (
                <div className="text-xs text-red-600 mt-1">{errors.start_date}</div>
              )}
            </div>
            
            <div>
              <Label htmlFor="end_date" className="flex items-center">
                <Calendar className="h-4 w-4 mr-1" />
                End Date *
              </Label>
              <Input
                id="end_date"
                type="date"
                value={activity.end_date}
                onChange={(e) => setActivity(prev => ({ ...prev, end_date: e.target.value }))}
                className={`mt-1 ${errors.end_date ? 'border-red-500' : ''}`}
              />
              {errors.end_date && (
                <div className="text-xs text-red-600 mt-1">{errors.end_date}</div>
              )}
            </div>
          </div>

          {/* Budget */}
          <div>
            <Label htmlFor="budget">Budget Allocated</Label>
            <Input
              id="budget"
              type="number"
              value={activity.budget_allocated}
              onChange={(e) => setActivity(prev => ({ ...prev, budget_allocated: e.target.value }))}
              placeholder="0.00"
              className={`mt-1 ${errors.budget_allocated ? 'border-red-500' : ''}`}
            />
            {errors.budget_allocated && (
              <div className="text-xs text-red-600 mt-1">{errors.budget_allocated}</div>
            )}
          </div>

          {/* Output and Quantity */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="planned_output">Planned Output</Label>
              <Input
                id="planned_output"
                value={activity.planned_output}
                onChange={(e) => setActivity(prev => ({ ...prev, planned_output: e.target.value }))}
                placeholder="Expected output description"
                className="mt-1"
              />
            </div>
            
            <div>
              <Label htmlFor="target_quantity">Target Quantity</Label>
              <Input
                id="target_quantity"
                type="number"
                value={activity.target_quantity}
                onChange={(e) => setActivity(prev => ({ ...prev, target_quantity: e.target.value }))}
                placeholder="0"
                className={`mt-1 ${errors.target_quantity ? 'border-red-500' : ''}`}
              />
              {errors.target_quantity && (
                <div className="text-xs text-red-600 mt-1">{errors.target_quantity}</div>
              )}
            </div>
          </div>

          {/* Risk Level */}
          <div>
            <Label htmlFor="risk_level" className="flex items-center">
              <Flag className="h-4 w-4 mr-1" />
              Risk Level
            </Label>
            <Select value={activity.risk_level} onValueChange={(value) => setActivity(prev => ({ ...prev, risk_level: value }))}>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Select risk level" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low Risk</SelectItem>
                <SelectItem value="medium">Medium Risk</SelectItem>
                <SelectItem value="high">High Risk</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Deliverables */}
          <div>
            <Label>Deliverables</Label>
            <div className="space-y-2 mt-2">
              {activity.deliverables.map((deliverable, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <Input
                    value={deliverable}
                    onChange={(e) => updateDeliverable(index, e.target.value)}
                    placeholder={`Deliverable ${index + 1}`}
                  />
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => removeDeliverable(index)}
                    className="text-red-600"
                  >
                    Remove
                  </Button>
                </div>
              ))}
              <Button
                size="sm"
                variant="outline"
                onClick={addDeliverable}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Deliverable
              </Button>
            </div>
          </div>

          {/* Additional Information */}
          <div>
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              value={activity.notes}
              onChange={(e) => setActivity(prev => ({ ...prev, notes: e.target.value }))}
              placeholder="Additional notes or comments..."
              className="mt-1"
              rows={2}
            />
          </div>
        </div>
        
        <div className="flex justify-end space-x-2 pt-4 border-t">
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleCreateActivity} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Plus className="h-4 w-4 mr-2" />
                Create Activity
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default CreateActivityModal;