import React, { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { Plus, Loader2, Calendar, DollarSign } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';

const CreateProjectModal = ({ onProjectCreated }) => {
  const { user, organization } = useAuth();
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [project, setProject] = useState({
    name: '',
    description: '',
    sector: '',
    donor_organization: '',
    start_date: '',
    end_date: '',
    budget_total: '',
    budget_currency: 'RWF',
    location: '',
    beneficiaries_target: '',
    team_members: [],
    project_manager_id: user?.id || '', // Set current user as default project manager
    me_officer_id: ''
  });

  const sectors = [
    'Education', 'Health', 'Agriculture', 'Infrastructure', 'Technology',
    'Environment', 'Social Services', 'Economic Development', 'Governance',
    'Emergency Response', 'Other'
  ];

  const validateProject = () => {
    const newErrors = {};
    
    if (!project.name.trim()) {
      newErrors.name = 'Project name is required';
    }
    
    if (!project.description.trim()) {
      newErrors.description = 'Project description is required';
    }
    
    if (!project.sector) {
      newErrors.sector = 'Sector is required';
    }
    
    if (!project.donor_organization.trim()) {
      newErrors.donor_organization = 'Donor is required';
    }
    
    if (!project.start_date) {
      newErrors.start_date = 'Start date is required';
    }
    
    if (!project.end_date) {
      newErrors.end_date = 'End date is required';
    }
    
    if (!project.budget_total || parseFloat(project.budget_total) <= 0) {
      newErrors.budget_total = 'Valid budget amount is required';
    }
    
    if (!project.project_manager_id) {
      newErrors.project_manager_id = 'Project manager is required';
    }
    
    // Validate date range
    if (project.start_date && project.end_date) {
      if (new Date(project.start_date) >= new Date(project.end_date)) {
        newErrors.end_date = 'End date must be after start date';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreateProject = async () => {
    if (!validateProject()) {
      return;
    }

    setLoading(true);
    
    try {
      // Get backend URL from environment
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token'); // Fixed: use 'access_token' not 'token'
      
      const projectData = {
        name: project.name,
        description: project.description,
        project_manager_id: project.project_manager_id,
        start_date: new Date(project.start_date).toISOString(),
        end_date: new Date(project.end_date).toISOString(),
        budget_total: parseFloat(project.budget_total),
        beneficiaries_target: project.beneficiaries_target ? parseInt(project.beneficiaries_target) : 0,
        location: project.location || null,
        donor_organization: project.donor_organization || null,
        implementing_partners: [],
        tags: []
      };

      console.log('🚀 Creating project:', projectData);

      const response = await fetch(`${backendUrl}/api/projects`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(projectData)
      });

      console.log('📊 Create Project Response:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok
      });

      if (response.ok) {
        const createdProject = await response.json();
        console.log('✅ Project created:', createdProject);
        
        toast({
          title: "Success!",
          description: "Project created successfully.",
          variant: "default",
        });
        
        setOpen(false);
        setProject({
          name: '',
          description: '',
          sector: '',
          donor_organization: '',
          start_date: '',
          end_date: '',
          budget_total: '',
          budget_currency: 'RWF',
          location: '',
          beneficiaries_target: '',
          team_members: [],
          project_manager_id: user?.id || '',
          me_officer_id: ''
        });
        
        if (onProjectCreated) {
          onProjectCreated(createdProject);
        }
      } else {
        const errorText = await response.text();
        console.error('❌ Create Project Error:', errorText);
        
        let errorMessage = 'Failed to create project';
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
      console.error('Create project error:', error);
      toast({
        title: "Error",
        description: `Failed to create project: ${error.message}`,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
          <Plus className="h-4 w-4 mr-2" />
          New Project
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Plus className="h-5 w-5 mr-2 text-purple-600" />
            Create New Project
          </DialogTitle>
          <DialogDescription>
            Set up a new project with timeline, budget, and team information.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          {/* Basic Information */}
          <div className="grid grid-cols-1 gap-4">
            <div>
              <Label htmlFor="name">Project Name *</Label>
              <Input
                id="name"
                value={project.name}
                onChange={(e) => setProject(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Enter project name..."
                className={`mt-1 ${errors.name ? 'border-red-500' : ''}`}
              />
              {errors.name && (
                <Alert variant="destructive" className="mt-2">
                  <AlertDescription>{errors.name}</AlertDescription>
                </Alert>
              )}
            </div>
            
            <div>
              <Label htmlFor="description">Description *</Label>
              <Textarea
                id="description"
                value={project.description}
                onChange={(e) => setProject(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe the project objectives and scope..."
                className={`mt-1 ${errors.description ? 'border-red-500' : ''}`}
                rows={3}
              />
              {errors.description && (
                <Alert variant="destructive" className="mt-2">
                  <AlertDescription>{errors.description}</AlertDescription>
                </Alert>
              )}
            </div>
          </div>

          {/* Sector and Donor */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="sector">Sector *</Label>
              <Select value={project.sector} onValueChange={(value) => setProject(prev => ({ ...prev, sector: value }))}>
                <SelectTrigger className={`mt-1 ${errors.sector ? 'border-red-500' : ''}`}>
                  <SelectValue placeholder="Select sector" />
                </SelectTrigger>
                <SelectContent>
                  {sectors.map(sector => (
                    <SelectItem key={sector} value={sector}>{sector}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.sector && (
                <div className="text-xs text-red-600 mt-1">{errors.sector}</div>
              )}
            </div>
            
            <div>
              <Label htmlFor="donor_organization">Donor/Funder *</Label>
              <Input
                id="donor_organization"
                value={project.donor_organization}
                onChange={(e) => setProject(prev => ({ ...prev, donor_organization: e.target.value }))}
                placeholder="e.g., World Bank, USAID..."
                className={`mt-1 ${errors.donor_organization ? 'border-red-500' : ''}`}
              />
              {errors.donor_organization && (
                <div className="text-xs text-red-600 mt-1">{errors.donor_organization}</div>
              )}
            </div>
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
                value={project.implementation_start}
                onChange={(e) => setProject(prev => ({ ...prev, implementation_start: e.target.value }))}
                className={`mt-1 ${errors.implementation_start ? 'border-red-500' : ''}`}
              />
              {errors.implementation_start && (
                <div className="text-xs text-red-600 mt-1">{errors.implementation_start}</div>
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
                value={project.implementation_end}
                onChange={(e) => setProject(prev => ({ ...prev, implementation_end: e.target.value }))}
                className={`mt-1 ${errors.implementation_end ? 'border-red-500' : ''}`}
              />
              {errors.implementation_end && (
                <div className="text-xs text-red-600 mt-1">{errors.implementation_end}</div>
              )}
            </div>
          </div>

          {/* Budget */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="budget" className="flex items-center">
                <DollarSign className="h-4 w-4 mr-1" />
                Total Budget *
              </Label>
              <Input
                id="budget"
                type="number"
                value={project.total_budget}
                onChange={(e) => setProject(prev => ({ ...prev, total_budget: e.target.value }))}
                placeholder="0.00"
                className={`mt-1 ${errors.total_budget ? 'border-red-500' : ''}`}
              />
              {errors.total_budget && (
                <div className="text-xs text-red-600 mt-1">{errors.total_budget}</div>
              )}
            </div>
            
            <div>
              <Label htmlFor="currency">Currency</Label>
              <Select value={project.budget_currency} onValueChange={(value) => setProject(prev => ({ ...prev, budget_currency: value }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="RWF">RWF (Rwandan Franc)</SelectItem>
                  <SelectItem value="USD">USD (US Dollar)</SelectItem>
                  <SelectItem value="EUR">EUR (Euro)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Additional Information */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                value={project.location}
                onChange={(e) => setProject(prev => ({ ...prev, location: e.target.value }))}
                placeholder="e.g., Kigali, Rwanda"
                className="mt-1"
              />
            </div>
            
            <div>
              <Label htmlFor="beneficiaries">Target Beneficiaries</Label>
              <Input
                id="beneficiaries"
                type="number"
                value={project.target_beneficiaries}
                onChange={(e) => setProject(prev => ({ ...prev, target_beneficiaries: e.target.value }))}
                placeholder="Number of people"
                className="mt-1"
              />
            </div>
          </div>
        </div>
        
        <div className="flex justify-end space-x-2 pt-4 border-t">
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleCreateProject} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Plus className="h-4 w-4 mr-2" />
                Create Project
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default CreateProjectModal;