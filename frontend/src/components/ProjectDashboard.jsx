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
  Loader2,
  BarChart3,
  Target,
  Activity,
  Zap,
  TrendingDown,
  Brain,
  Shield
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';
import CreateProjectModal from './CreateProjectModal';
import CreateActivityModal from './CreateActivityModal';
import CreateBeneficiaryModal from './CreateBeneficiaryModal';
import CreateKPIModal from './CreateKPIModal';
import EnhancedActivityTracker from './EnhancedActivityTracker';

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
      const token = localStorage.getItem('access_token'); // Fixed: use 'access_token' not 'token'
      
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
        // Server returns the dashboard object directly (not wrapped)
        setDashboardData(data);
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
      description: `Project "${newProject.name || newProject.title}" was created successfully.`,
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
        <CreateProjectModal onProjectCreated={handleProjectCreated} />
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

      {/* Enhanced Recent Activities with Key Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activities */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Clock className="h-5 w-5 mr-2 text-green-600" />
              Latest Project Updates
            </CardTitle>
            <CardDescription>
              Recent activities with progress insights
            </CardDescription>
          </CardHeader>
          <CardContent>
            {dashboardData?.recent_activities?.length > 0 ? (
              <div className="space-y-4">
                {dashboardData.recent_activities.map((activity, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{activity.name}</h4>
                      <div className="flex items-center space-x-4 mt-1">
                        <Badge className={getStatusColor(activity.status)}>
                          {(activity.status || '').replace('_', ' ') || 'Unknown'}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {activity.progress}% complete
                        </span>
                        {activity.progress > 75 && (
                          <Badge className="bg-green-100 text-green-800 border-green-200">
                            <TrendingUp className="h-3 w-3 mr-1" />
                            On Track
                          </Badge>
                        )}
                        {activity.progress < 30 && (
                          <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">
                            <AlertTriangle className="h-3 w-3 mr-1" />
                            Needs Attention
                          </Badge>
                        )}
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

        {/* Activity Performance Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Brain className="h-5 w-5 mr-2 text-purple-600" />
              Key Performance Insights
            </CardTitle>
            <CardDescription>
              AI-generated insights from your project data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Completion Rate Insight */}
              {dashboardData?.completion_analytics && (
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center mb-2">
                    <Target className="h-4 w-4 text-blue-600 mr-2" />
                    <span className="font-medium text-blue-800">Project Success Rate</span>
                  </div>
                  <p className="text-sm text-blue-700">
                    {dashboardData.completion_analytics.project_success_rate}% of closed projects completed successfully.
                    {dashboardData.completion_analytics.on_time_completion_rate > 80 ? ' Excellent timeline management!' : 
                     dashboardData.completion_analytics.on_time_completion_rate > 60 ? ' Good progress tracking.' : 
                     ' Consider improving project timeline planning.'}
                  </p>
                </div>
              )}

              {/* Activity Efficiency Insight */}
              {dashboardData?.activity_insights && (
                <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center mb-2">
                    <Zap className="h-4 w-4 text-green-600 mr-2" />
                    <span className="font-medium text-green-800">Activity Efficiency</span>
                  </div>
                  <p className="text-sm text-green-700">
                    Average completion time: {dashboardData.activity_insights.avg_completion_days} days.
                    {dashboardData.activity_insights.avg_completion_days < 14 ? ' Your team is highly efficient!' : 
                     dashboardData.activity_insights.avg_completion_days < 30 ? ' Good pace of execution.' : 
                     ' Consider breaking down activities into smaller tasks.'}
                  </p>
                </div>
              )}

              {/* Budget Performance Insight */}
              {dashboardData?.budget_utilization && (
                <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                  <div className="flex items-center mb-2">
                    <DollarSign className="h-4 w-4 text-purple-600 mr-2" />
                    <span className="font-medium text-purple-800">Budget Performance</span>
                  </div>
                  <p className="text-sm text-purple-700">
                    {Math.round(dashboardData.budget_utilization)}% budget utilized.
                    {dashboardData.budget_utilization > 90 ? ' High utilization - monitor spending closely.' : 
                     dashboardData.budget_utilization > 70 ? ' Good budget management.' : 
                     ' Opportunity to accelerate project activities.'}
                  </p>
                </div>
              )}

              {/* Risk Alert */}
              {dashboardData?.risk_indicators && (
                <div className="p-3 bg-red-50 rounded-lg border border-red-200">
                  <div className="flex items-center mb-2">
                    <Shield className="h-4 w-4 text-red-600 mr-2" />
                    <span className="font-medium text-red-800">Risk Alert</span>
                  </div>
                  <p className="text-sm text-red-700">
                    {dashboardData.risk_indicators.timeline_risk?.projects_due_soon || 0} projects due within 30 days,
                    {' '}{dashboardData.risk_indicators.performance_risk?.low_progress_activities || 0} activities need attention.
                    {(dashboardData.risk_indicators.timeline_risk?.projects_due_soon || 0) > 0 ? ' Review project timelines.' : ' All projects on track.'}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Advanced Analytics Section */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Activity Status Analytics */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="h-5 w-5 mr-2 text-blue-600" />
              Activity Analytics
            </CardTitle>
            <CardDescription>
              Breakdown of activity progress and performance
            </CardDescription>
          </CardHeader>
          <CardContent>
            {dashboardData?.activity_insights?.activity_status_breakdown ? (
              <div className="space-y-3">
                {Object.entries(dashboardData.activity_insights.activity_status_breakdown).map(([status, data]) => (
                  <div key={status} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Badge className={getStatusColor(status)}>
                        {status.replace('_', ' ')}
                      </Badge>
                      <span className="text-sm text-gray-600">{data.count} activities</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">{data.avg_progress}%</div>
                      <div className="text-xs text-gray-500">avg progress</div>
                    </div>
                  </div>
                ))}
                <div className="pt-2 border-t">
                  <div className="text-xs text-gray-500">
                    Total: {dashboardData.activity_insights.total_activities} activities
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-4 text-gray-500">
                <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No activity data available</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Performance Trends */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="h-5 w-5 mr-2 text-green-600" />
              Performance Trends
            </CardTitle>
            <CardDescription>
              Recent completion and achievement trends
            </CardDescription>
          </CardHeader>
          <CardContent>
            {dashboardData?.activity_insights?.completion_trend_weekly?.length > 0 ? (
              <div className="space-y-3">
                <div className="text-sm font-medium text-gray-700">Weekly Completions</div>
                {dashboardData.activity_insights.completion_trend_weekly.slice(-4).map((week, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">{week.week}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full" 
                          style={{width: `${Math.min(week.completed * 10, 100)}%`}}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{week.completed}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4 text-gray-500">
                <BarChart3 className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No trend data available</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Risk Indicators */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="h-5 w-5 mr-2 text-red-600" />
              Risk Assessment
            </CardTitle>
            <CardDescription>
              Project and budget risk indicators
            </CardDescription>
          </CardHeader>
          <CardContent>
            {dashboardData?.risk_indicators ? (
              <div className="space-y-4">
                {/* Budget Risk */}
                <div className="flex items-center justify-between p-2 rounded-lg bg-orange-50">
                  <div>
                    <div className="text-sm font-medium text-orange-800">Budget Risk</div>
                    <div className="text-xs text-orange-600">High utilization projects</div>
                  </div>
                  <div className="text-lg font-bold text-orange-800">
                    {dashboardData.risk_indicators.budget_risk?.high_utilization_projects || 0}
                  </div>
                </div>

                {/* Timeline Risk */}
                <div className="flex items-center justify-between p-2 rounded-lg bg-red-50">
                  <div>
                    <div className="text-sm font-medium text-red-800">Timeline Risk</div>
                    <div className="text-xs text-red-600">Due within 30 days</div>
                  </div>
                  <div className="text-lg font-bold text-red-800">
                    {dashboardData.risk_indicators.timeline_risk?.projects_due_soon || 0}
                  </div>
                </div>

                {/* Performance Risk */}
                <div className="flex items-center justify-between p-2 rounded-lg bg-yellow-50">
                  <div>
                    <div className="text-sm font-medium text-yellow-800">Performance Risk</div>
                    <div className="text-xs text-yellow-600">Low progress activities</div>
                  </div>
                  <div className="text-lg font-bold text-yellow-800">
                    {dashboardData.risk_indicators.performance_risk?.low_progress_activities || 0}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-4 text-gray-500">
                <Shield className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No risk data available</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

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
            <CreateProjectModal 
              onProjectCreated={handleProjectCreated}
              trigger={
                <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
                  <Plus className="h-6 w-6 text-blue-600" />
                  <span className="text-sm">New Project</span>
                </Button>
              }
            />
            <CreateActivityModal
              onActivityCreated={() => fetchDashboardData()}
              trigger={
                <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
                  <Calendar className="h-6 w-6 text-green-600" />
                  <span className="text-sm">Add Activity</span>
                </Button>
              }
            />
            <CreateBeneficiaryModal
              onBeneficiaryCreated={() => fetchDashboardData()}
              trigger={
                <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
                  <Users className="h-6 w-6 text-purple-600" />
                  <span className="text-sm">Add Beneficiary</span>
                </Button>
              }
            />
            <CreateKPIModal
              onKPICreated={() => fetchDashboardData()}
              trigger={
                <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
                  <TrendingUp className="h-6 w-6 text-orange-600" />
                  <span className="text-sm">Add KPI</span>
                </Button>
              }
            />
          </div>
        </CardContent>
      </Card>

      {/* Enhanced Activity Tracker Section */}
      <EnhancedActivityTracker 
        dashboardData={dashboardData} 
        onDataRefresh={fetchDashboardData}
      />
    </div>
  );
};

export default ProjectDashboard;