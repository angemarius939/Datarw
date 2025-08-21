import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { Plus, Loader2, Calendar, User } from 'lucide-react';
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
    start_date: '',
    end_date: '',
    budget_allocated: '',
    deliverables: [],
    dependencies: [],
    results_framework_link: '',
    notes: ''
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
        start_date: new Date(activity.start_date).toISOString(),
        end_date: new Date(activity.end_date).toISOString(),
        budget_allocated: activity.budget_allocated ? parseFloat(activity.budget_allocated) : 0,
        deliverables: activity.deliverables.filter(d => d.trim() !== ''),
        dependencies: activity.dependencies.filter(d => d.trim() !== '')
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
          title: "Success!",
          description: "Activity created successfully.",
          variant: "default",
        });
        
        setOpen(false);
        setActivity({
          project_id: '',
          name: '',
          description: '',
          assigned_to: '',
          start_date: '',
          end_date: '',
          budget_allocated: '',
          deliverables: [],
          dependencies: [],
          results_framework_link: '',
          notes: ''
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
          title: "Error",
          description: errorMessage,
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Create activity error:', error);
      toast({
        title: "Error",
        description: `Failed to create activity: ${error.message}`,
        variant: "destructive",
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
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Plus className="h-5 w-5 mr-2 text-green-600" />
            Create New Activity
          </DialogTitle>
          <DialogDescription>
            Add a new activity to track project implementation and progress.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
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
            <Label htmlFor="title">Activity Title *</Label>
            <Input
              id="title"
              value={activity.title}
              onChange={(e) => setActivity(prev => ({ ...prev, title: e.target.value }))}
              placeholder="Enter activity title..."
              className={`mt-1 ${errors.title ? 'border-red-500' : ''}`}
            />
            {errors.title && (
              <div className="text-xs text-red-600 mt-1">{errors.title}</div>
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
              Responsible Person *
            </Label>
            <Select value={activity.responsible_user_id} onValueChange={(value) => setActivity(prev => ({ ...prev, responsible_user_id: value }))}>
              <SelectTrigger className={`mt-1 ${errors.responsible_user_id ? 'border-red-500' : ''}`}>
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
            {errors.responsible_user_id && (
              <div className="text-xs text-red-600 mt-1">{errors.responsible_user_id}</div>
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
              className="mt-1"
            />
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