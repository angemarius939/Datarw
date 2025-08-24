import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Users,
  MapPin,
  Phone,
  Mail,
  Calendar,
  Plus,
  Edit,
  Eye,
  Search,
  AlertTriangle,
  CheckCircle,
  Clock,
  Target,
  Activity,
  TrendingUp,
  Map,
  BarChart3,
  RefreshCw,
  Star
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';

const BeneficiaryInterface = () => {
  const { user } = useAuth();
  const { toast } = useToast();

  // State management
  const [activeTab, setActiveTab] = useState('overview');
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Form state
  const [beneficiaryForm, setBeneficiaryForm] = useState({
    name: '',
    gender: '',
    contact_phone: '',
    project_ids: []
  });

  // Fetch data
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');

      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      if (!backendUrl || !token) {
        throw new Error('Missing backend URL or authentication token');
      }

      // Fetch beneficiaries
      const beneficiariesRes = await fetch(`${backendUrl}/api/beneficiaries?page=1&page_size=20`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (beneficiariesRes.ok) {
        const beneficiariesData = await beneficiariesRes.json();
        setBeneficiaries(beneficiariesData.items || []);
      }

      // Fetch analytics if on overview tab
      if (activeTab === 'overview') {
        const analyticsRes = await fetch(`${backendUrl}/api/beneficiaries/analytics`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (analyticsRes.ok) {
          const analyticsData = await analyticsRes.json();
          setAnalytics(analyticsData);
        }
      }

    } catch (error) {
      console.error('Error fetching beneficiary data:', error);
      setError(`Failed to load data: ${error.message}`);
      toast({
        title: 'Error',
        description: 'Failed to load beneficiary data',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  }, [activeTab, toast]);

  // Fetch data on mount
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Create beneficiary
  const handleCreateBeneficiary = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      const beneficiaryData = {
        name: beneficiaryForm.name || 'Test Beneficiary',
        gender: beneficiaryForm.gender || 'female',
        contact_phone: beneficiaryForm.contact_phone || '+250123456789',
        project_ids: [],
        custom_fields: {},
        tags: []
      };

      const response = await fetch(`${backendUrl}/api/beneficiaries`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(beneficiaryData)
      });

      if (response.ok) {
        const result = await response.json();
        toast({
          title: 'Success',
          description: 'Beneficiary created successfully'
        });
        setShowCreateModal(false);
        setBeneficiaryForm({ name: '', gender: '', contact_phone: '', project_ids: [] });
        fetchData();
      } else {
        const errorText = await response.text();
        throw new Error(`Failed to create beneficiary: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('Create beneficiary error:', error);
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive'
      });
    }
  };

  if (loading && beneficiaries.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Beneficiary Interface...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Beneficiary Management</h1>
          <p className="text-gray-600">Comprehensive beneficiary tracking and management</p>
        </div>
        
        {/* Action Buttons */}
        <div className="flex items-center space-x-4">
          <Button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Add Beneficiary</span>
          </Button>
          
          <Button
            variant="outline"
            onClick={fetchData}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: <BarChart3 className="h-4 w-4" /> },
            { id: 'registry', label: 'Beneficiary Registry', icon: <Users className="h-4 w-4" /> },
            { id: 'analytics', label: 'Analytics', icon: <TrendingUp className="h-4 w-4" /> }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {analytics ? (
            <>
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Total Beneficiaries</p>
                        <p className="text-2xl font-bold text-gray-900">{analytics.summary?.total_beneficiaries || 0}</p>
                      </div>
                      <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                        <Users className="h-6 w-6 text-blue-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Active Beneficiaries</p>
                        <p className="text-2xl font-bold text-green-900">{analytics.summary?.active_beneficiaries || 0}</p>
                      </div>
                      <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                        <CheckCircle className="h-6 w-6 text-green-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Graduation Rate</p>
                        <p className="text-2xl font-bold text-blue-900">{analytics.summary?.graduation_rate || 0}%</p>
                      </div>
                      <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                        <Star className="h-6 w-6 text-blue-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Total Services</p>
                        <p className="text-2xl font-bold text-purple-900">{analytics.services?.total_services || 0}</p>
                      </div>
                      <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
                        <Activity className="h-6 w-6 text-purple-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Loading Analytics...</h3>
            </div>
          )}
        </div>
      )}

      {/* Beneficiary Registry Tab */}
      {activeTab === 'registry' && (
        <div className="space-y-6">
          {/* Beneficiaries Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {beneficiaries.map((beneficiary) => (
              <Card key={beneficiary.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                        <Users className="h-6 w-6 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{beneficiary.name}</h3>
                        <p className="text-sm text-gray-600">{beneficiary.system_id}</p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 text-sm">
                    {beneficiary.contact_phone && (
                      <div className="flex items-center space-x-2">
                        <Phone className="h-4 w-4 text-gray-400" />
                        <span>{beneficiary.contact_phone}</span>
                      </div>
                    )}
                    {beneficiary.contact_email && (
                      <div className="flex items-center space-x-2">
                        <Mail className="h-4 w-4 text-gray-400" />
                        <span>{beneficiary.contact_email}</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Empty State */}
          {beneficiaries.length === 0 && !loading && (
            <div className="text-center py-12">
              <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No beneficiaries found</h3>
              <p className="text-gray-600 mb-6">Get started by adding your first beneficiary to the system.</p>
              <Button onClick={() => setShowCreateModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add First Beneficiary
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Create Beneficiary Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Create New Beneficiary</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <Input
                  value={beneficiaryForm.name}
                  onChange={(e) => setBeneficiaryForm({...beneficiaryForm, name: e.target.value})}
                  placeholder="Enter beneficiary name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
                <select
                  value={beneficiaryForm.gender}
                  onChange={(e) => setBeneficiaryForm({...beneficiaryForm, gender: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="">Select Gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Contact Phone</label>
                <Input
                  value={beneficiaryForm.contact_phone}
                  onChange={(e) => setBeneficiaryForm({...beneficiaryForm, contact_phone: e.target.value})}
                  placeholder="+250123456789"
                />
              </div>
            </div>
            
            <div className="flex items-center justify-end space-x-4 mt-6">
              <Button
                variant="outline"
                onClick={() => setShowCreateModal(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleCreateBeneficiary}
              >
                Create Beneficiary
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BeneficiaryInterface;