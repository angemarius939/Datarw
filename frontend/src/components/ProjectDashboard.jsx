import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Plus,
  Calendar,
  Users,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  Clock,
  CheckCircle,
  Loader2
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';
import CreateProjectModal from './CreateProjectModal';

const ProjectDashboard = () => {
  const { user, organization } = useAuth();
  const { toast } = useToast();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Get backend URL from environment
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('token');
      
      console.log('🔍 Dashboard Debug Info:', {
        backendUrl,
        hasToken: !!token,
        tokenPrefix: token ? token.substring(0, 20) + '...' : 'No token'
      });

      const response = await fetch(`${backendUrl}/api/projects/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('📊 Dashboard Response:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok
      });

      if (response.ok) {
        const data = await response.json();
        console.log('📊 Dashboard Data:', data);
        setDashboardData(data.data);
      } else {
        const errorText = await response.text();
        console.error('📊 Dashboard Error Response:', errorText);
        throw new Error(`Server responded with ${response.status}: ${errorText}`);
      }
    } catch (error) {
      console.error('Dashboard fetch error:', error);
      setError(`Failed to load dashboard data: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading project dashboard...</p>
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

  const handleProjectCreated = (newProject) => {
    // Refresh dashboard data when a new project is created
    fetchDashboardData();
    toast({
      title: "Success!",
      description: `Project "${newProject.title}" was created successfully.`,
      variant: "default",
    });
  };

  const StatCard = ({ title, value, icon, subtitle, trend, color = "blue" }) => (
    <Card className="hover:shadow-md transition-shadow duration-200">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {subtitle && (
              <p className="text-sm text-gray-500">{subtitle}</p>
            )}
          </div>
          <div className={`w-12 h-12 rounded-full bg-${color}-100 flex items-center justify-center`}>
            {React.cloneElement(icon, { className: `h-6 w-6 text-${color}-600` })}
          </div>
        </div>
        {trend && (
          <div className="mt-4 flex items-center">
            <TrendingUp className={`h-4 w-4 mr-1 ${trend > 0 ? 'text-green-500' : 'text-red-500'}`} />
            <span className={`text-sm ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trend > 0 ? '+' : ''}{trend}% from last month
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );

  const getStatusColor = (status) => {
    const colors = {
      'completed': 'bg-green-100 text-green-800 border-green-200',
      'in_progress': 'bg-blue-100 text-blue-800 border-blue-200',
      'delayed': 'bg-red-100 text-red-800 border-red-200',
      'not_started': 'bg-gray-100 text-gray-800 border-gray-200'
    };
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Project Dashboard</h1>
          <p className="text-gray-600">Monitor and manage your organization's projects</p>
        </div>
        <Button 
          className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
          onClick={() => {/* TODO: Navigate to create project */}}
        >
          <Plus className="h-4 w-4 mr-2" />
          New Project
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Projects"
          value={dashboardData?.total_projects || 0}
          icon={<Calendar />}
          color="blue"
        />
        <StatCard
          title="Active Projects"
          value={dashboardData?.active_projects || 0}
          icon={<CheckCircle />}
          color="green"
        />
        <StatCard
          title="Budget Utilization"
          value={`${Math.round(dashboardData?.budget_utilization || 0)}%`}
          icon={<DollarSign />}
          subtitle="of total budget used"
          color="purple"
        />
        <StatCard
          title="Overdue Activities"
          value={dashboardData?.overdue_activities || 0}
          icon={<AlertTriangle />}
          color={dashboardData?.overdue_activities > 0 ? "red" : "gray"}
        />
      </div>

      {/* Warning for overdue activities */}
      {dashboardData?.overdue_activities > 0 && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            You have {dashboardData.overdue_activities} overdue activities that need attention.
          </AlertDescription>
        </Alert>
      )}

      {/* KPI Performance */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
            KPI Performance Overview
          </CardTitle>
          <CardDescription>
            Average achievement rate across all indicators
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Overall Achievement</span>
                <span>{Math.round(dashboardData?.kpi_performance?.average_achievement || 0)}%</span>
              </div>
              <Progress 
                value={dashboardData?.kpi_performance?.average_achievement || 0} 
                className="h-2" 
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activities */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Clock className="h-5 w-5 mr-2 text-green-600" />
            Recent Activities
          </CardTitle>
          <CardDescription>
            Latest updates from your projects
          </CardDescription>
        </CardHeader>
        <CardContent>
          {dashboardData?.recent_activities?.length > 0 ? (
            <div className="space-y-4">
              {dashboardData.recent_activities.map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{activity.title}</h4>
                    <div className="flex items-center space-x-4 mt-1">
                      <Badge className={getStatusColor(activity.status)}>
                        {activity.status.replace('_', ' ')}
                      </Badge>
                      <span className="text-sm text-gray-500">
                        {activity.progress}% complete
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="w-16">
                      <Progress value={activity.progress} className="h-1" />
                    </div>
                    <span className="text-xs text-gray-500 mt-1">
                      {new Date(activity.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Clock className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No recent activities found</p>
              <p className="text-sm">Activities will appear here once you start working on projects</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks to get you started
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
              <Plus className="h-6 w-6 text-blue-600" />
              <span className="text-sm">New Project</span>
            </Button>
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
              <Calendar className="h-6 w-6 text-green-600" />
              <span className="text-sm">Add Activity</span>
            </Button>
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
              <Users className="h-6 w-6 text-purple-600" />
              <span className="text-sm">Add Beneficiary</span>
            </Button>
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
              <TrendingUp className="h-6 w-6 text-orange-600" />
              <span className="text-sm">Add KPI</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProjectDashboard;