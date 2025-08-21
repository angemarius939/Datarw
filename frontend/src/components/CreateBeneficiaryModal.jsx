import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { Plus, Loader2, User, Phone, Mail, MapPin } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';

const CreateBeneficiaryModal = ({ onBeneficiaryCreated, trigger }) => {
  const { user, organization } = useAuth();
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [beneficiary, setBeneficiary] = useState({
    unique_id: '',
    first_name: '',
    last_name: '',
    date_of_birth: '',
    gender: '',
    location: '',
    contact_phone: '',
    contact_email: '',
    household_size: '',
    income_level: '',
    education_level: '',
    employment_status: '',
    disability_status: '',
    custom_fields: {},
    geographical_coordinates: null
  });

  const genderOptions = ['Male', 'Female', 'Other', 'Prefer not to say'];
  const educationLevels = ['None', 'Primary', 'Secondary', 'Vocational', 'University', 'Graduate'];
  const employmentStatuses = ['Employed', 'Unemployed', 'Self-employed', 'Student', 'Retired', 'Other'];
  const incomeLevels = ['Very Low', 'Low', 'Medium', 'High', 'Very High'];
  const disabilityStatuses = ['None', 'Physical', 'Visual', 'Hearing', 'Cognitive', 'Multiple', 'Other'];

  useEffect(() => {
    if (open && !beneficiary.unique_id) {
      // Generate unique ID
      const timestamp = Date.now();
      const randomNum = Math.floor(Math.random() * 1000);
      setBeneficiary(prev => ({ ...prev, unique_id: `BEN-${timestamp}-${randomNum}` }));
    }
  }, [open]);

  const validateBeneficiary = () => {
    const newErrors = {};
    
    if (!beneficiary.unique_id.trim()) {
      newErrors.unique_id = 'Unique ID is required';
    }
    
    if (!beneficiary.first_name.trim()) {
      newErrors.first_name = 'First name is required';
    }
    
    if (!beneficiary.last_name.trim()) {
      newErrors.last_name = 'Last name is required';
    }
    
    // Validate email format if provided
    if (beneficiary.contact_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(beneficiary.contact_email)) {
      newErrors.contact_email = 'Invalid email format';
    }
    
    // Validate household size
    if (beneficiary.household_size && (parseInt(beneficiary.household_size) < 1 || parseInt(beneficiary.household_size) > 50)) {
      newErrors.household_size = 'Household size must be between 1 and 50';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreateBeneficiary = async () => {
    if (!validateBeneficiary()) {
      return;
    }

    setLoading(true);
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');
      
      const beneficiaryData = {
        ...beneficiary,
        household_size: beneficiary.household_size ? parseInt(beneficiary.household_size) : null,
        date_of_birth: beneficiary.date_of_birth ? new Date(beneficiary.date_of_birth).toISOString() : null
      };

      console.log('🚀 Creating beneficiary:', beneficiaryData);

      const response = await fetch(`${backendUrl}/api/beneficiaries`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(beneficiaryData)
      });

      if (response.ok) {
        const createdBeneficiary = await response.json();
        
        toast({
          title: "Success!",
          description: "Beneficiary profile created successfully.",
          variant: "default",
        });
        
        setOpen(false);
        setBeneficiary({
          unique_id: '',
          first_name: '',
          last_name: '',
          date_of_birth: '',
          gender: '',
          location: '',
          contact_phone: '',
          contact_email: '',
          household_size: '',
          income_level: '',
          education_level: '',
          employment_status: '',
          disability_status: '',
          custom_fields: {},
          geographical_coordinates: null
        });
        
        if (onBeneficiaryCreated) {
          onBeneficiaryCreated(createdBeneficiary);
        }
      } else {
        const errorText = await response.text();
        console.error('❌ Create Beneficiary Error:', errorText);
        
        let errorMessage = 'Failed to create beneficiary';
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
      console.error('Create beneficiary error:', error);
      toast({
        title: "Error",
        description: `Failed to create beneficiary: ${error.message}`,
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
          <Button className="bg-gradient-to-r from-pink-600 to-purple-600">
            <Plus className="h-4 w-4 mr-2" />
            Add Beneficiary
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <User className="h-5 w-5 mr-2 text-pink-600" />
            Add New Beneficiary
          </DialogTitle>
          <DialogDescription>
            Create a new beneficiary profile for project participation tracking.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          {/* Unique ID */}
          <div>
            <Label htmlFor="unique_id">Unique ID *</Label>
            <Input
              id="unique_id"
              value={beneficiary.unique_id}
              onChange={(e) => setBeneficiary(prev => ({ ...prev, unique_id: e.target.value }))}
              placeholder="BEN-XXXXXXXXX"
              className={`mt-1 ${errors.unique_id ? 'border-red-500' : ''}`}
            />
            {errors.unique_id && (
              <div className="text-xs text-red-600 mt-1">{errors.unique_id}</div>
            )}
          </div>

          {/* Basic Information */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="first_name">First Name *</Label>
              <Input
                id="first_name"
                value={beneficiary.first_name}
                onChange={(e) => setBeneficiary(prev => ({ ...prev, first_name: e.target.value }))}
                placeholder="Enter first name..."
                className={`mt-1 ${errors.first_name ? 'border-red-500' : ''}`}
              />
              {errors.first_name && (
                <div className="text-xs text-red-600 mt-1">{errors.first_name}</div>
              )}
            </div>
            
            <div>
              <Label htmlFor="last_name">Last Name *</Label>
              <Input
                id="last_name"
                value={beneficiary.last_name}
                onChange={(e) => setBeneficiary(prev => ({ ...prev, last_name: e.target.value }))}
                placeholder="Enter last name..."
                className={`mt-1 ${errors.last_name ? 'border-red-500' : ''}`}
              />
              {errors.last_name && (
                <div className="text-xs text-red-600 mt-1">{errors.last_name}</div>
              )}
            </div>
          </div>

          {/* Demographics */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <Label htmlFor="date_of_birth">Date of Birth</Label>
              <Input
                id="date_of_birth"
                type="date"
                value={beneficiary.date_of_birth}
                onChange={(e) => setBeneficiary(prev => ({ ...prev, date_of_birth: e.target.value }))}
                className="mt-1"
              />
            </div>
            
            <div>
              <Label htmlFor="gender">Gender</Label>
              <Select value={beneficiary.gender} onValueChange={(value) => setBeneficiary(prev => ({ ...prev, gender: value }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  {genderOptions.map(gender => (
                    <SelectItem key={gender} value={gender}>{gender}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="household_size">Household Size</Label>
              <Input
                id="household_size"
                type="number"
                value={beneficiary.household_size}
                onChange={(e) => setBeneficiary(prev => ({ ...prev, household_size: e.target.value }))}
                placeholder="Number of people"
                className={`mt-1 ${errors.household_size ? 'border-red-500' : ''}`}
              />
              {errors.household_size && (
                <div className="text-xs text-red-600 mt-1">{errors.household_size}</div>
              )}
            </div>
          </div>

          {/* Contact Information */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="contact_phone" className="flex items-center">
                <Phone className="h-4 w-4 mr-1" />
                Phone Number
              </Label>
              <Input
                id="contact_phone"
                value={beneficiary.contact_phone}
                onChange={(e) => setBeneficiary(prev => ({ ...prev, contact_phone: e.target.value }))}
                placeholder="+250 xxx xxx xxx"
                className="mt-1"
              />
            </div>
            
            <div>
              <Label htmlFor="contact_email" className="flex items-center">
                <Mail className="h-4 w-4 mr-1" />
                Email
              </Label>
              <Input
                id="contact_email"
                type="email"
                value={beneficiary.contact_email}
                onChange={(e) => setBeneficiary(prev => ({ ...prev, contact_email: e.target.value }))}
                placeholder="email@example.com"
                className={`mt-1 ${errors.contact_email ? 'border-red-500' : ''}`}
              />
              {errors.contact_email && (
                <div className="text-xs text-red-600 mt-1">{errors.contact_email}</div>
              )}
            </div>
          </div>

          {/* Location */}
          <div>
            <Label htmlFor="location" className="flex items-center">
              <MapPin className="h-4 w-4 mr-1" />
              Location
            </Label>
            <Input
              id="location"
              value={beneficiary.location}
              onChange={(e) => setBeneficiary(prev => ({ ...prev, location: e.target.value }))}
              placeholder="District, Sector, Cell, Village"
              className="mt-1"
            />
          </div>

          {/* Socioeconomic Information */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="education_level">Education Level</Label>
              <Select value={beneficiary.education_level} onValueChange={(value) => setBeneficiary(prev => ({ ...prev, education_level: value }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select education level" />
                </SelectTrigger>
                <SelectContent>
                  {educationLevels.map(level => (
                    <SelectItem key={level} value={level}>{level}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="employment_status">Employment Status</Label>
              <Select value={beneficiary.employment_status} onValueChange={(value) => setBeneficiary(prev => ({ ...prev, employment_status: value }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select employment status" />
                </SelectTrigger>
                <SelectContent>
                  {employmentStatuses.map(status => (
                    <SelectItem key={status} value={status}>{status}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="income_level">Income Level</Label>
              <Select value={beneficiary.income_level} onValueChange={(value) => setBeneficiary(prev => ({ ...prev, income_level: value }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select income level" />
                </SelectTrigger>
                <SelectContent>
                  {incomeLevels.map(level => (
                    <SelectItem key={level} value={level}>{level}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="disability_status">Disability Status</Label>
              <Select value={beneficiary.disability_status} onValueChange={(value) => setBeneficiary(prev => ({ ...prev, disability_status: value }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select disability status" />
                </SelectTrigger>
                <SelectContent>
                  {disabilityStatuses.map(status => (
                    <SelectItem key={status} value={status}>{status}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
        
        <div className="flex justify-end space-x-2 pt-4 border-t">
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleCreateBeneficiary} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Plus className="h-4 w-4 mr-2" />
                Add Beneficiary
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default CreateBeneficiaryModal;