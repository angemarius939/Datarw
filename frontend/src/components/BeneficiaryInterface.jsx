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
  Camera,
  Upload,
  Search,
  Filter,
  Plus,
  Edit,
  Trash2,
  Eye,
  Download,
  AlertTriangle,
  CheckCircle,
  Clock,
  Target,
  Activity,
  TrendingUp,
  TrendingDown,
  Map,
  BarChart3,
  PieChart,
  RefreshCw,
  FileText,
  Star,
  Heart,
  Shield,
  Zap
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';

const BeneficiaryInterface = () => {
  const { user } = useAuth();
  const { toast } = useToast();

  // State management
  const [activeTab, setActiveTab] = useState('overview');
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [serviceRecords, setServiceRecords] = useState([]);
  const [beneficiaryKPIs, setBeneficiaryKPIs] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [mapData, setMapData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Filter and search states
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [projectFilter, setProjectFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showServiceModal, setShowServiceModal] = useState(false);
  const [showKPIModal, setShowKPIModal] = useState(false);
  const [showBatchServiceModal, setShowBatchServiceModal] = useState(false);
  const [selectedBeneficiary, setSelectedBeneficiary] = useState(null);
  const [selectedBeneficiaries, setSelectedBeneficiaries] = useState([]);

  // Form states
  const [beneficiaryForm, setBeneficiaryForm] = useState({
    name: '',
    first_name: '',
    last_name: '',
    gender: '',
    age: '',
    contact_phone: '',
    contact_email: '',
    national_id: '',
    address: '',
    gps_latitude: '',
    gps_longitude: '',
    project_ids: [],
    custom_fields: {},
    tags: []
  });

  // Fetch data on component mount and tab changes
  useEffect(() => {
    fetchData();
  }, [activeTab, searchTerm, statusFilter, riskFilter, projectFilter, currentPage]);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');

      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      if (!backendUrl || !token) {
        throw new Error('Missing backend URL or authentication token');
      }

      // Fetch beneficiaries with filters
      const beneficiaryParams = new URLSearchParams({
        page: currentPage.toString(),
        page_size: pageSize.toString(),
        ...(searchTerm && { search: searchTerm }),
        ...(statusFilter && { status: statusFilter }),
        ...(riskFilter && { risk_level: riskFilter }),
        ...(projectFilter && { project_id: projectFilter })
      });

      const beneficiariesRes = await fetch(`${backendUrl}/api/beneficiaries?${beneficiaryParams}`, {
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

        // Fetch map data
        const mapRes = await fetch(`${backendUrl}/api/beneficiaries/map-data`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (mapRes.ok) {
          const mapDataRes = await mapRes.json();
          setMapData(mapDataRes.map_points || []);
        }
      }

      // Fetch service records if on services tab
      if (activeTab === 'services') {
        const serviceParams = new URLSearchParams({
          page: '1',
          page_size: '50'
        });

        const servicesRes = await fetch(`${backendUrl}/api/service-records?${serviceParams}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (servicesRes.ok) {
          const servicesData = await servicesRes.json();
          setServiceRecords(servicesData.items || []);
        }
      }

      // Fetch KPIs if on KPIs tab
      if (activeTab === 'kpis') {
        const kpisRes = await fetch(`${backendUrl}/api/beneficiary-kpis`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (kpisRes.ok) {
          const kpisData = await kpisRes.json();
          setBeneficiaryKPIs(kpisData.kpis || []);
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
  }, [activeTab, searchTerm, statusFilter, riskFilter, projectFilter, currentPage, pageSize, toast]);

  // Create beneficiary
  const handleCreateBeneficiary = async (formData) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${backendUrl}/api/beneficiaries`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Beneficiary created successfully'
        });
        setShowCreateModal(false);
        fetchData();
      } else {
        throw new Error(`Failed to create beneficiary: ${response.statusText}`);
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive'
      });
    }
  };

  // Update beneficiary
  const handleUpdateBeneficiary = async (beneficiaryId, formData) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${backendUrl}/api/beneficiaries/${beneficiaryId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Beneficiary updated successfully'
        });
        setShowEditModal(false);
        fetchData();
      } else {
        throw new Error(`Failed to update beneficiary: ${response.statusText}`);
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive'
      });
    }
  };

  // Create service record
  const handleCreateServiceRecord = async (serviceData) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${backendUrl}/api/service-records`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(serviceData)
      });

      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Service record created successfully'
        });
        setShowServiceModal(false);
        fetchData();
      } else {
        throw new Error(`Failed to create service record: ${response.statusText}`);
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive'
      });
    }
  };

  // Risk level color coding
  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'low': return 'bg-green-100 text-green-800 border-green-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  // Status color coding
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      case 'graduated': return 'bg-blue-100 text-blue-800';
      case 'dropped_out': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
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

  if (error) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Beneficiary Management</h1>
          <p className="text-gray-600">Comprehensive beneficiary tracking, service records, and KPI management</p>
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

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: <BarChart3 className="h-4 w-4" /> },
            { id: 'registry', label: 'Beneficiary Registry', icon: <Users className="h-4 w-4" /> },
            { id: 'services', label: 'Service Records', icon: <Activity className="h-4 w-4" /> },
            { id: 'kpis', label: 'KPI Tracking', icon: <Target className="h-4 w-4" /> },
            { id: 'map', label: 'Geographic View', icon: <Map className="h-4 w-4" /> },
            { id: 'analytics', label: 'Analytics & Insights', icon: <TrendingUp className="h-4 w-4" /> }
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
      {activeTab === 'overview' && analytics && (
        <div className="space-y-6">
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

          {/* Demographics and Risk Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gender Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Gender Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(analytics.demographics?.gender_distribution || {}).map(([gender, count]) => (
                    <div key={gender} className="flex items-center justify-between">
                      <span className="text-sm font-medium capitalize">{gender}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full"
                            style={{
                              width: `${(count / analytics.summary?.total_beneficiaries * 100) || 0}%`
                            }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Risk Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Risk Level Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(analytics.demographics?.risk_distribution || {}).map(([risk, count]) => (
                    <div key={risk} className="flex items-center justify-between">
                      <Badge className={getRiskColor(risk)}>{risk.toUpperCase()}</Badge>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              risk === 'low' ? 'bg-green-500' :
                              risk === 'medium' ? 'bg-yellow-500' :
                              risk === 'high' ? 'bg-orange-500' : 'bg-red-500'
                            }`}
                            style={{
                              width: `${(count / analytics.summary?.total_beneficiaries * 100) || 0}%`
                            }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Beneficiary Registry Tab */}
      {activeTab === 'registry' && (
        <div className="space-y-6">
          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search beneficiaries by name, ID, or phone..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="graduated">Graduated</option>
              <option value="dropped_out">Dropped Out</option>
            </select>

            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="">All Risk Levels</option>
              <option value="low">Low Risk</option>
              <option value="medium">Medium Risk</option>
              <option value="high">High Risk</option>
              <option value="critical">Critical Risk</option>
            </select>
          </div>

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
                    <div className="flex items-center space-x-2">
                      <Badge className={getStatusColor(beneficiary.status)}>
                        {beneficiary.status}
                      </Badge>
                      <Badge className={getRiskColor(beneficiary.risk_level)}>
                        {beneficiary.risk_level}
                      </Badge>
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
                    {beneficiary.address && (
                      <div className="flex items-center space-x-2">
                        <MapPin className="h-4 w-4 text-gray-400" />
                        <span className="truncate">{beneficiary.address}</span>
                      </div>
                    )}
                    {beneficiary.enrollment_date && (
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4 text-gray-400" />
                        <span>Enrolled: {new Date(beneficiary.enrollment_date).toLocaleDateString()}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
                    <div className="flex items-center space-x-2">
                      {beneficiary.gps_latitude && beneficiary.gps_longitude && (
                        <Badge variant="outline" className="text-xs">
                          <MapPin className="h-3 w-3 mr-1" />
                          GPS
                        </Badge>
                      )}
                      {beneficiary.tags?.map((tag, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setSelectedBeneficiary(beneficiary);
                          setShowEditModal(true);
                        }}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setSelectedBeneficiary(beneficiary);
                          setShowServiceModal(true);
                        }}
                      >
                        <Plus className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
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

      {/* Service Records Tab */}
      {activeTab === 'services' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Service Records</h2>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                onClick={() => setShowBatchServiceModal(true)}
              >
                <Upload className="h-4 w-4 mr-2" />
                Batch Entry
              </Button>
              <Button onClick={() => setShowServiceModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add Service
              </Button>
            </div>
          </div>

          {/* Service Records List */}
          <div className="space-y-4">
            {serviceRecords.map((record) => (
              <Card key={record.id}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-2">
                        <Badge className="capitalize">{record.service_type}</Badge>
                        <span className="font-medium">{record.service_name}</span>
                        <span className="text-sm text-gray-500">
                          {new Date(record.service_date).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{record.service_description}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        {record.service_location && (
                          <span><MapPin className="h-3 w-3 inline mr-1" />{record.service_location}</span>
                        )}
                        {record.staff_name && (
                          <span>Staff: {record.staff_name}</span>
                        )}
                        {record.satisfaction_score && (
                          <span>Satisfaction: {record.satisfaction_score}/5</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {record.follow_up_required && (
                        <Badge variant="outline" className="text-orange-600 border-orange-300">
                          <Clock className="h-3 w-3 mr-1" />
                          Follow-up
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* KPI Tracking Tab */}
      {activeTab === 'kpis' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">KPI Tracking</h2>
            <Button onClick={() => setShowKPIModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add KPI
            </Button>
          </div>

          {/* KPI Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {beneficiaryKPIs.map((kpi) => (
              <Card key={kpi.id}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900">{kpi.kpi_name}</h3>
                    <Badge className={kpi.is_on_track ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {kpi.is_on_track ? 'On Track' : 'Off Track'}
                    </Badge>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span>Progress</span>
                        <span>{kpi.progress_percentage?.toFixed(1) || 0}%</span>
                      </div>
                      <Progress value={kpi.progress_percentage || 0} className="h-2" />
                    </div>
                    
                    <div className="grid grid-cols-3 gap-2 text-sm">
                      <div>
                        <p className="text-gray-500">Baseline</p>
                        <p className="font-medium">{kpi.baseline_value}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Current</p>
                        <p className="font-medium">{kpi.current_value}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Target</p>
                        <p className="font-medium">{kpi.target_value}</p>
                      </div>
                    </div>
                    
                    {kpi.unit_of_measure && (
                      <p className="text-xs text-gray-500">Unit: {kpi.unit_of_measure}</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Empty State */}
          {beneficiaryKPIs.length === 0 && (
            <div className="text-center py-12">
              <Target className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No KPIs tracked yet</h3>
              <p className="text-gray-600 mb-6">Start tracking beneficiary progress with custom KPIs.</p>
              <Button onClick={() => setShowKPIModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create First KPI
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Geographic View Tab */}
      {activeTab === 'map' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Map className="h-5 w-5" />
                <span>Beneficiary Locations</span>
              </CardTitle>
              <CardDescription>
                Interactive map showing beneficiary household and service locations
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Map Placeholder - Integration with mapping library would go here */}
              <div className="w-full h-96 bg-gray-100 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <Map className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">Interactive Map</h3>
                  <p className="text-gray-500 mb-4">
                    {mapData.length} beneficiaries with GPS coordinates
                  </p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    {mapData.slice(0, 8).map((point, index) => (
                      <div key={index} className="bg-white p-3 rounded border">
                        <div className="font-medium truncate">{point.name}</div>
                        <div className="text-gray-500">{point.status}</div>
                        <div className="text-xs text-gray-400">
                          {point.latitude?.toFixed(4)}, {point.longitude?.toFixed(4)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Analytics & Insights Tab */}
      {activeTab === 'analytics' && analytics && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Service Statistics */}
            <Card>
              <CardHeader>
                <CardTitle>Service Statistics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Average Services per Beneficiary</span>
                    <span className="font-bold">{analytics.services?.avg_services_per_beneficiary || 0}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Recent Services (30 days)</span>
                    <span className="font-bold">{analytics.services?.recent_services || 0}</span>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Service Type Distribution</p>
                    {Object.entries(analytics.services?.service_type_distribution || {}).map(([type, count]) => (
                      <div key={type} className="flex items-center justify-between text-sm">
                        <span className="capitalize">{type.replace('_', ' ')}</span>
                        <span>{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Age Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Age Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(analytics.demographics?.age_distribution || {}).map(([range, count]) => (
                    <div key={range} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{range} years</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-purple-600 h-2 rounded-full"
                            style={{
                              width: `${(count / analytics.summary?.total_beneficiaries * 100) || 0}%`
                            }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Modals would be added here - Create Beneficiary, Edit Beneficiary, Service Record, KPI, etc. */}
      {/* For brevity, modal implementations are not shown but would follow similar patterns */}
    </div>
  );
};

export default BeneficiaryInterface;