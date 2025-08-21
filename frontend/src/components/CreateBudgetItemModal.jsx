import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { Plus, Loader2, DollarSign, Calendar, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';

const CreateBudgetItemModal = ({ onBudgetItemCreated, trigger }) => {
  const { user, organization } = useAuth();
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState([]);
  const [users, setUsers] = useState([]);
  const [errors, setErrors] = useState({});
  const [budgetItem, setBudgetItem] = useState({
    project_id: '',
    category: 'administration',
    description: '',
    budgeted_amount: '',
    currency: 'RWF',
    period_start: '',
    period_end: '',
    responsible_user_id: '',
    notes: ''
  });

  const budgetCategories = [
    { value: 'administration', label: 'Administration' },
    { value: 'logistics', label: 'Logistics' },
    { value: 'training', label: 'Training' },
    { value: 'personnel', label: 'Personnel' },
    { value: 'equipment', label: 'Equipment' },
    { value: 'travel', label: 'Travel' },
    { value: 'communications', label: 'Communications' },
    { value: 'monitoring', label: 'Monitoring' },
    { value: 'other', label: 'Other' }
  ];

  const currencies = [
    { value: 'RWF', label: 'RWF (Rwandan Franc)' },
    { value: 'USD', label: 'USD (US Dollar)' },
    { value: 'EUR', label: 'EUR (Euro)' }
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

  const validateBudgetItem = () => {
    const newErrors = {};
    
    if (!budgetItem.project_id) {
      newErrors.project_id = 'Project is required';
    }
    
    if (!budgetItem.description.trim()) {
      newErrors.description = 'Description is required';
    }
    
    if (!budgetItem.budgeted_amount || parseFloat(budgetItem.budgeted_amount) <= 0) {
      newErrors.budgeted_amount = 'Valid budget amount is required';
    }
    
    if (!budgetItem.period_start) {
      newErrors.period_start = 'Start date is required';
    }
    
    if (!budgetItem.period_end) {
      newErrors.period_end = 'End date is required';
    }
    
    // Validate date range
    if (budgetItem.period_start && budgetItem.period_end) {
      if (new Date(budgetItem.period_start) >= new Date(budgetItem.period_end)) {
        newErrors.period_end = 'End date must be after start date';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreateBudgetItem = async () => {
    if (!validateBudgetItem()) {
      return;
    }

    setLoading(true);
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');
      
      const budgetData = {
        ...budgetItem,
        budgeted_amount: parseFloat(budgetItem.budgeted_amount),
        period_start: new Date(budgetItem.period_start).toISOString(),
        period_end: new Date(budgetItem.period_end).toISOString()
      };

      console.log('🚀 Creating budget item:', budgetData);

      const response = await fetch(`${backendUrl}/api/budget`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(budgetData)
      });

      if (response.ok) {
        const createdBudgetItem = await response.json();
        
        toast({
          title: "Success!",
          description: "Budget item created successfully.",
          variant: "default",
        });
        
        setOpen(false);
        setBudgetItem({
          project_id: '',
          category: 'administration',
          description: '',
          budgeted_amount: '',
          currency: 'RWF',
          period_start: '',
          period_end: '',
          responsible_user_id: '',
          notes: ''
        });
        
        if (onBudgetItemCreated) {
          onBudgetItemCreated(createdBudgetItem);
        }
      } else {
        const errorText = await response.text();
        console.error('❌ Create Budget Item Error:', errorText);
        
        let errorMessage = 'Failed to create budget item';
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
      console.error('Create budget item error:', error);
      toast({
        title: "Error",
        description: `Failed to create budget item: ${error.message}`,
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
          <Button className="bg-gradient-to-r from-green-600 to-blue-600">
            <Plus className="h-4 w-4 mr-2" />
            Add Budget Item
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <DollarSign className="h-5 w-5 mr-2 text-green-600" />
            Add Budget Item
          </DialogTitle>
          <DialogDescription>
            Create a new budget line item to track project financial resources.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          {/* Project Selection */}
          <div>
            <Label htmlFor="project">Project *</Label>
            <Select value={budgetItem.project_id} onValueChange={(value) => setBudgetItem(prev => ({ ...prev, project_id: value }))}>
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

          {/* Category and Description */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="category">Budget Category *</Label>
              <Select value={budgetItem.category} onValueChange={(value) => setBudgetItem(prev => ({ ...prev, category: value }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {budgetCategories.map(category => (
                    <SelectItem key={category.value} value={category.value}>{category.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="currency">Currency</Label>
              <Select value={budgetItem.currency} onValueChange={(value) => setBudgetItem(prev => ({ ...prev, currency: value }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {currencies.map(currency => (
                    <SelectItem key={currency.value} value={currency.value}>{currency.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div>
            <Label htmlFor="description">Description *</Label>
            <Textarea
              id="description"
              value={budgetItem.description}
              onChange={(e) => setBudgetItem(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Detailed description of the budget item..."
              className={`mt-1 ${errors.description ? 'border-red-500' : ''}`}
              rows={3}
            />
            {errors.description && (
              <div className="text-xs text-red-600 mt-1">{errors.description}</div>
            )}
          </div>

          {/* Budget Amount */}
          <div>
            <Label htmlFor="amount" className="flex items-center">
              <DollarSign className="h-4 w-4 mr-1" />
              Budgeted Amount *
            </Label>
            <Input
              id="amount"
              type="number"
              value={budgetItem.budgeted_amount}
              onChange={(e) => setBudgetItem(prev => ({ ...prev, budgeted_amount: e.target.value }))}
              placeholder="0.00"
              className={`mt-1 ${errors.budgeted_amount ? 'border-red-500' : ''}`}
            />
            {errors.budgeted_amount && (
              <div className="text-xs text-red-600 mt-1">{errors.budgeted_amount}</div>
            )}
          </div>

          {/* Budget Period */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="period_start" className="flex items-center">
                <Calendar className="h-4 w-4 mr-1" />
                Period Start *
              </Label>
              <Input
                id="period_start"
                type="date"
                value={budgetItem.period_start}
                onChange={(e) => setBudgetItem(prev => ({ ...prev, period_start: e.target.value }))}
                className={`mt-1 ${errors.period_start ? 'border-red-500' : ''}`}
              />
              {errors.period_start && (
                <div className="text-xs text-red-600 mt-1">{errors.period_start}</div>
              )}
            </div>
            
            <div>
              <Label htmlFor="period_end" className="flex items-center">
                <Calendar className="h-4 w-4 mr-1" />
                Period End *
              </Label>
              <Input
                id="period_end"
                type="date"
                value={budgetItem.period_end}
                onChange={(e) => setBudgetItem(prev => ({ ...prev, period_end: e.target.value }))}
                className={`mt-1 ${errors.period_end ? 'border-red-500' : ''}`}
              />
              {errors.period_end && (
                <div className="text-xs text-red-600 mt-1">{errors.period_end}</div>
              )}
            </div>
          </div>

          {/* Responsible Person */}
          <div>
            <Label htmlFor="responsible" className="flex items-center">
              <User className="h-4 w-4 mr-1" />
              Responsible Person
            </Label>
            <Select value={budgetItem.responsible_user_id} onValueChange={(value) => setBudgetItem(prev => ({ ...prev, responsible_user_id: value }))}>
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

          {/* Notes */}
          <div>
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              value={budgetItem.notes}
              onChange={(e) => setBudgetItem(prev => ({ ...prev, notes: e.target.value }))}
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
          <Button onClick={handleCreateBudgetItem} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Plus className="h-4 w-4 mr-2" />
                Add Budget Item
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default CreateBudgetItemModal;