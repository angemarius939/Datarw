import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { 
  BarChart3, 
  Users, 
  FileText, 
  Database, 
  TrendingUp, 
  Settings,
  Plus,
  Eye,
  Edit,
  Trash2,
  Download,
  CreditCard,
  Calendar,
  DollarSign,
  Loader2
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { surveysAPI, analyticsAPI, usersAPI, organizationAPI } from '../services/api';
import SurveyBuilder from './SurveyBuilder';
import UserManagement from './UserManagement';
import ProjectDashboard from './ProjectDashboard';
import AdminPanel from './AdminPanel';
import EnhancedReporting from './EnhancedReporting';
import CreateProjectModal from './CreateProjectModal';
import CreateActivityModal from './CreateActivityModal';
import CreateBeneficiaryModal from './CreateBeneficiaryModal';
import CreateKPIModal from './CreateKPIModal';
import CreateBudgetItemModal from './CreateBudgetItemModal';
import ActivitiesTable from './ActivitiesTable';

const Dashboard = ({ onUpgrade }) => {
  const { user, organization, logout, updateOrganization } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [surveys, setSurveys] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [surveysRes, analyticsRes, usersRes, orgRes] = await Promise.allSettled([
        surveysAPI.getSurveys(),
        analyticsAPI.getAnalytics(),
        usersAPI.getUsers(),
        organizationAPI.getMyOrganization()
      ]);

      if (surveysRes.status === 'fulfilled') {
        setSurveys(surveysRes.value.data);
      }

      if (analyticsRes.status === 'fulfilled') {
        setAnalytics(analyticsRes.value.data);
      }

      if (usersRes.status === 'fulfilled') {
        setUsers(usersRes.value.data);
      }

      if (orgRes.status === 'fulfilled') {
        updateOrganization(orgRes.value.data);
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSurvey = async (surveyId) => {
    if (!window.confirm('Are you sure you want to delete this survey?')) return;
    
    try {
      await surveysAPI.deleteSurvey(surveyId);
      setSurveys(prev => prev.filter(s => s.id !== surveyId));
    } catch (error) {
      console.error('Error deleting survey:', error);
      setError('Failed to delete survey');
    }
  };

  const StatCard = ({ title, value, icon, trend, trendValue, color = "blue" }) => (
    <Card className="relative overflow-hidden hover:shadow-lg transition-shadow duration-300">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">{title}</CardTitle>
        <div className={`p-2 rounded-lg bg-${color}-100`}>
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-gray-900">{value}</div>
        {trend && (
          <div className={`flex items-center text-sm mt-1 ${
            trend === 'up' ? 'text-green-600' : 'text-red-600'
          }`}>
            <TrendingUp className="h-4 w-4 mr-1" />
            {trendValue}% from last month
          </div>
        )}
      </CardContent>
    </Card>
  );

  const SurveyCard = ({ survey }) => (
    <Card className="hover:shadow-md transition-shadow duration-200">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{survey.title}</CardTitle>
          <Badge variant={survey.status === 'active' ? 'default' : 'secondary'}>
            {survey.status}
          </Badge>
        </div>
        <CardDescription>{survey.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between mb-4">
          <div className="text-sm text-gray-600">
            <span className="font-medium">{survey.responses_count || 0}</span> responses
          </div>
          <div className="text-sm text-gray-600">
            Updated {new Date(survey.updated_at).toLocaleDateString()}
          </div>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" className="flex-1">
            <Eye className="h-4 w-4 mr-2" />
            View
          </Button>
          <Button 
            size="sm" 
            variant="outline" 
            className="flex-1"
            onClick={() => setActiveTab('builder')}
          >
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          {user?.role === 'Admin' && (
            <Button 
              size="sm" 
              variant="outline" 
              className="text-red-600 hover:text-red-700"
              onClick={() => handleDeleteSurvey(survey.id)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );

  const isAtLimit = (current, limit) => {
    if (limit === -1) return false; // Unlimited
    return current >= limit;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">D</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">DataRW</h1>
                <p className="text-sm text-gray-600">{organization?.name}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge className="bg-green-100 text-green-800 border-green-200">
                {organization?.plan} Plan
              </Badge>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => onUpgrade && onUpgrade()}
                className="text-blue-600 border-blue-200 hover:bg-blue-50"
              >
                <CreditCard className="h-4 w-4 mr-2" />
                Upgrade
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <Button variant="outline" size="sm" onClick={logout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {error && (
        <div className="px-6 py-4">
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      )}

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r min-h-screen">
          <nav className="p-4 space-y-2">
            {/* DataRW Surveys Section */}
            <div className="pb-2 border-b mb-4">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                DataRW Surveys
              </h3>
            </div>
            <Button
              variant={activeTab === 'overview' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('overview')}
              className="w-full justify-start"
            >
              <BarChart3 className="h-4 w-4 mr-3" />
              Overview
            </Button>
            <Button
              variant={activeTab === 'surveys' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('surveys')}
              className="w-full justify-start"
            >
              <FileText className="h-4 w-4 mr-3" />
              Surveys
            </Button>
            <Button
              variant={activeTab === 'builder' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('builder')}
              className="w-full justify-start"
              disabled={isAtLimit(surveys.length, organization?.survey_limit)}
            >
              <Plus className="h-4 w-4 mr-3" />
              Survey Builder
            </Button>
            <Button
              variant={activeTab === 'data' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('data')}
              className="w-full justify-start"
            >
              <Database className="h-4 w-4 mr-3" />
              Data Management
            </Button>
            <Button
              variant={activeTab === 'users' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('users')}
              className="w-full justify-start"
            >
              <Users className="h-4 w-4 mr-3" />
              User Management
            </Button>

            {/* DataRW Projects Section */}
            <div className="pt-4 border-t mt-4">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                DataRW Projects
              </h3>
            </div>
            <Button
              variant={activeTab === 'projects-overview' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('projects-overview')}
              className="w-full justify-start"
            >
              <BarChart3 className="h-4 w-4 mr-3" />
              Project Dashboard
            </Button>
            <Button
              variant={activeTab === 'projects' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('projects')}
              className="w-full justify-start"
            >
              <FileText className="h-4 w-4 mr-3" />
              Projects & Activities
            </Button>
            <Button
              variant={activeTab === 'budgets' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('budgets')}
              className="w-full justify-start"
            >
              <Database className="h-4 w-4 mr-3" />
              Budget Tracking
            </Button>
            <Button
              variant={activeTab === 'kpis' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('kpis')}
              className="w-full justify-start"
            >
              <TrendingUp className="h-4 w-4 mr-3" />
              KPI Dashboard
            </Button>
            <Button
              variant={activeTab === 'beneficiaries' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('beneficiaries')}
              className="w-full justify-start"
            >
              <Users className="h-4 w-4 mr-3" />
              Beneficiaries
            </Button>
            <Button
              variant={activeTab === 'documents' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('documents')}
              className="w-full justify-start"
            >
              <FileText className="h-4 w-4 mr-3" />
              Document Repository
            </Button>
            <Button
              variant={activeTab === 'reports' ? 'default' : 'ghost'}
              onClick={() => setActiveTab('reports')}
              className="w-full justify-start"
            >
              <BarChart3 className="h-4 w-4 mr-3" />
              Automated Reporting
            </Button>

            {/* Admin Panel Section - Only for Admin/Director users */}
            {user && ['Admin', 'Director', 'System Admin'].includes(user.role) && (
              <>
                <div className="pt-4 border-t mt-4">
                  <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                    Administration
                  </h3>
                </div>
                <Button
                  variant={activeTab === 'admin-panel' ? 'default' : 'ghost'}
                  onClick={() => setActiveTab('admin-panel')}
                  className="w-full justify-start"
                >
                  <Settings className="h-4 w-4 mr-3" />
                  Admin Panel
                </Button>
              </>
            )}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
                <Button 
                  className="bg-gradient-to-r from-blue-600 to-purple-600"
                  onClick={() => setActiveTab('builder')}
                  disabled={isAtLimit(surveys.length, organization?.survey_limit)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  {isAtLimit(surveys.length, organization?.survey_limit) ? 'Limit Reached' : 'New Survey'}
                </Button>
              </div>

              {/* Usage Warnings */}
              {isAtLimit(surveys.length, organization?.survey_limit) && (
                <Alert>
                  <AlertDescription>
                    You've reached your survey limit. <Button variant="link" className="p-0" onClick={() => onUpgrade && onUpgrade()}>Upgrade your plan</Button> to create more surveys.
                  </AlertDescription>
                </Alert>
              )}

              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                  title="Total Surveys"
                  value={surveys.length}
                  icon={<FileText className="h-5 w-5 text-blue-600" />}
                  trend="up"
                  trendValue={12}
                  color="blue"
                />
                <StatCard
                  title="Total Responses"
                  value={analytics?.total_responses?.toLocaleString() || '0'}
                  icon={<BarChart3 className="h-5 w-5 text-green-600" />}
                  trend="up"
                  trendValue={analytics?.monthly_growth || 0}
                  color="green"
                />
                <StatCard
                  title="Response Rate"
                  value={`${analytics?.response_rate?.toFixed(1) || 0}%`}
                  icon={<TrendingUp className="h-5 w-5 text-purple-600" />}
                  trend="up"
                  trendValue={8}
                  color="purple"
                />
                <StatCard
                  title="Storage Used"
                  value={`${organization?.storage_used || 0}/${organization?.storage_limit === -1 ? '∞' : organization?.storage_limit} GB`}
                  icon={<Database className="h-5 w-5 text-orange-600" />}
                  color="orange"
                />
              </div>

              {/* Usage Progress */}
              <div className="grid md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Survey Usage</CardTitle>
                    <CardDescription>
                      {surveys.length} of {organization?.survey_limit === -1 ? 'unlimited' : organization?.survey_limit} surveys used
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Progress 
                      value={organization?.survey_limit === -1 ? 0 : (surveys.length / organization?.survey_limit) * 100} 
                      className="h-2"
                    />
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Storage Usage</CardTitle>
                    <CardDescription>
                      {organization?.storage_used || 0} GB of {organization?.storage_limit === -1 ? 'unlimited' : `${organization?.storage_limit} GB`} used
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Progress 
                      value={organization?.storage_limit === -1 ? 0 : ((organization?.storage_used || 0) / organization?.storage_limit) * 100} 
                      className="h-2"
                    />
                  </CardContent>
                </Card>
              </div>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Surveys</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {surveys.slice(0, 3).map((survey) => (
                      <div key={survey.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <span className="font-medium">{survey.title}</span>
                          <span className="text-gray-600 ml-2">{survey.responses_count || 0} responses</span>
                        </div>
                        <Badge variant="outline">
                          {survey.status}
                        </Badge>
                      </div>
                    ))}
                    {surveys.length === 0 && (
                      <p className="text-gray-500 text-center py-4">No surveys yet. Create your first survey!</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === 'surveys' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">Surveys</h1>
                <Button 
                  onClick={() => setActiveTab('builder')} 
                  className="bg-gradient-to-r from-blue-600 to-purple-600"
                  disabled={isAtLimit(surveys.length, organization?.survey_limit)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Create Survey
                </Button>
              </div>

              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {surveys.map((survey) => (
                  <SurveyCard key={survey.id} survey={survey} />
                ))}
                {surveys.length === 0 && (
                  <div className="col-span-full text-center py-12">
                    <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No surveys yet</h3>
                    <p className="text-gray-600 mb-4">Create your first survey to start collecting data.</p>
                    <Button onClick={() => setActiveTab('builder')}>
                      <Plus className="h-4 w-4 mr-2" />
                      Create Survey
                    </Button>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'builder' && <SurveyBuilder onSurveyCreated={fetchDashboardData} />}
          {activeTab === 'users' && <UserManagement users={users} onUsersChange={setUsers} />}

          {activeTab === 'data' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">Data Management</h1>
                <Button className="bg-gradient-to-r from-green-600 to-blue-600">
                  <Download className="h-4 w-4 mr-2" />
                  Export All Data
                </Button>
              </div>

              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {surveys.map((survey) => (
                  <Card key={survey.id} className="hover:shadow-md transition-shadow">
                    <CardHeader>
                      <CardTitle className="text-lg">{survey.title}</CardTitle>
                      <CardDescription>{survey.responses_count || 0} responses</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <Button size="sm" variant="outline" className="w-full">
                          <Download className="h-4 w-4 mr-2" />
                          Export CSV
                        </Button>
                        <Button size="sm" variant="outline" className="w-full">
                          <Download className="h-4 w-4 mr-2" />
                          Export Excel
                        </Button>
                        <Button size="sm" variant="outline" className="w-full">
                          <Eye className="h-4 w-4 mr-2" />
                          View Analytics
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Project Management Content Areas */}
          {activeTab === 'projects-overview' && <ProjectDashboard />}
          
          {activeTab === 'projects' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">Projects &amp; Activities</h1>
                <div className="flex space-x-2">
                  <CreateProjectModal onProjectCreated={() => {
                    console.log('Project created successfully');
                  }} />
                  <CreateActivityModal onActivityCreated={() => {
                    console.log('Activity created successfully');
                  }} />
                </div>
              </div>
              <ActivitiesTable />
            </div>
          )}

          {activeTab === 'budgets' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">Budget Tracking</h1>
                <CreateBudgetItemModal onBudgetItemCreated={() => {
                  console.log('Budget item created successfully');
                }} />
              </div>
              <div className="text-center py-12 text-gray-500">
                <Database className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium mb-2">Financial Management</p>
                <p>Track project budgets, expenditures, and financial performance in real-time</p>
              </div>
            </div>
          )}

          {activeTab === 'kpis' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">KPI Dashboard</h1>
                <CreateKPIModal onKPICreated={() => {
                  console.log('KPI created successfully');
                }} />
              </div>
              <div className="text-center py-12 text-gray-500">
                <TrendingUp className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium mb-2">Performance Monitoring</p>
                <p>Define indicators, track progress, and visualize organizational performance</p>
              </div>
            </div>
          )}

          {activeTab === 'beneficiaries' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">Beneficiary Management</h1>
                <CreateBeneficiaryModal onBeneficiaryCreated={() => {
                  console.log('Beneficiary created successfully');
                }} />
              </div>
              <div className="text-center py-12 text-gray-500">
                <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium mb-2">Stakeholder Profiles</p>
                <p>Manage beneficiary information, demographics, and program participation</p>
              </div>
            </div>
          )}

          {activeTab === 'documents' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">Document Repository</h1>
                <Button className="bg-gradient-to-r from-indigo-600 to-blue-600">
                  <Plus className="h-4 w-4 mr-2" />
                  Upload Document
                </Button>
              </div>
              <div className="text-center py-12 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium mb-2">Secure File Management</p>
                <p>Store project documents, reports, agreements with version control and access permissions</p>
              </div>
            </div>
          )}

          {activeTab === 'reports' && <EnhancedReporting />}

          {/* Admin Panel Content */}
          {activeTab === 'admin-panel' && <AdminPanel />}
        </main>
      </div>
    </div>
  );
};

export default Dashboard;