import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { 
  TrendingUp,
  TrendingDown,
  Activity,
  Target,
  Users,
  DollarSign,
  Clock,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  PieChart,
  Calendar,
  Filter,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Eye,
  ArrowUpRight,
  ArrowDownRight,
  Zap,
  Shield
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';

const KPIDashboard = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  
  // State management
  const [indicatorKPIs, setIndicatorKPIs] = useState(null);
  const [activityKPIs, setActivityKPIs] = useState(null);
  const [projectKPIs, setProjectKPIs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('indicators');
  const [selectedDateRange, setSelectedDateRange] = useState('30d');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [drillDownData, setDrillDownData] = useState(null);
  const [drillDownType, setDrillDownType] = useState('');
  const [expandedCards, setExpandedCards] = useState({});

  // Real-time update interval
  useEffect(() => {
    let interval;
    if (autoRefresh) {
      interval = setInterval(() => {
        fetchKPIData();
        console.log('🔄 Auto-refreshing KPI data...');
      }, 30000); // Refresh every 30 seconds
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  // Initial data fetch
  useEffect(() => {
    fetchKPIData();
  }, [selectedDateRange]);

  const fetchKPIData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');

      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      if (!backendUrl || !token) {
        throw new Error('Missing backend URL or authentication token');
      }

      // Calculate date range
      const endDate = new Date();
      const startDate = new Date();
      switch (selectedDateRange) {
        case '7d':
          startDate.setDate(endDate.getDate() - 7);
          break;
        case '30d':
          startDate.setDate(endDate.getDate() - 30);
          break;
        case '90d':
          startDate.setDate(endDate.getDate() - 90);
          break;
        case '1y':
          startDate.setFullYear(endDate.getFullYear() - 1);
          break;
        default:
          startDate.setDate(endDate.getDate() - 30);
      }

      const dateParams = `?date_from=${startDate.toISOString()}&date_to=${endDate.toISOString()}`;

      // Fetch all KPI data in parallel
      const [indicatorsRes, activitiesRes, projectsRes] = await Promise.all([
        fetch(`${backendUrl}/api/kpi/indicators${dateParams}`, {
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        }),
        fetch(`${backendUrl}/api/kpi/activities`, {
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        }),
        fetch(`${backendUrl}/api/kpi/projects`, {
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        })
      ]);

      if (indicatorsRes.ok) {
        const data = await indicatorsRes.json();
        setIndicatorKPIs(data);
      }

      if (activitiesRes.ok) {
        const data = await activitiesRes.json();
        setActivityKPIs(data);
      }

      if (projectsRes.ok) {
        const data = await projectsRes.json();
        setProjectKPIs(data);
      }

    } catch (error) {
      console.error('KPI fetch error:', error);
      setError(`Failed to load KPI data: ${error.message}`);
      toast({
        title: 'Error',
        description: 'Failed to load KPI data',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  }, [selectedDateRange, toast]);

  // Drill-down functionality
  const handleDrillDown = (type, data, title) => {
    setDrillDownData(data);
    setDrillDownType(type);
    console.log(`🔍 Drilling down into ${type}:`, title);
  };

  const closeDrillDown = () => {
    setDrillDownData(null);
    setDrillDownType('');
  };

  // Card expansion toggle
  const toggleCardExpansion = (cardId) => {
    setExpandedCards(prev => ({
      ...prev,
      [cardId]: !prev[cardId]
    }));
  };

  // Metric card component
  const MetricCard = ({ 
    title, 
    value, 
    icon, 
    trend, 
    subtitle, 
    color = "blue", 
    drillDownData = null,
    drillDownTitle = "",
    cardId = "",
    children 
  }) => {
    const isExpanded = expandedCards[cardId];
    const trendColor = trend > 0 ? 'text-green-600' : trend < 0 ? 'text-red-600' : 'text-gray-600';
    const TrendIcon = trend > 0 ? ArrowUpRight : trend < 0 ? ArrowDownRight : Activity;

    return (
      <Card className="hover:shadow-lg transition-all duration-200 relative">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="space-y-1 flex-1">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-600">{title}</p>
                <div className="flex items-center space-x-2">
                  {drillDownData && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDrillDown(drillDownTitle, drillDownData, title)}
                      className="h-6 w-6 p-0"
                    >
                      <Eye className="h-3 w-3" />
                    </Button>
                  )}
                  {children && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleCardExpansion(cardId)}
                      className="h-6 w-6 p-0"
                    >
                      {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                    </Button>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <p className="text-2xl font-bold text-gray-900">{value}</p>
                {trend !== undefined && (
                  <div className={`flex items-center ${trendColor}`}>
                    <TrendIcon className="h-4 w-4 mr-1" />
                    <span className="text-sm font-medium">{Math.abs(trend)}%</span>
                  </div>
                )}
              </div>
              {subtitle && (
                <p className="text-sm text-gray-500">{subtitle}</p>
              )}
            </div>
            <div className={`w-12 h-12 rounded-full bg-${color}-100 flex items-center justify-center flex-shrink-0`}>
              {React.cloneElement(icon, { className: `h-6 w-6 text-${color}-600` })}
            </div>
          </div>
          
          {/* Expandable content */}
          {isExpanded && children && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              {children}
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  // Progress ring component
  const ProgressRing = ({ percentage, size = 60, strokeWidth = 6, color = "#3B82F6" }) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const strokeDasharray = `${circumference} ${circumference}`;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;

    return (
      <div className="relative inline-flex items-center justify-center">
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#E5E7EB"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-300"
          />
        </svg>
        <span className="absolute text-sm font-semibold text-gray-700">
          {Math.round(percentage)}%
        </span>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading KPI Dashboard...</p>
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
          <h1 className="text-3xl font-bold text-gray-900">KPI Dashboard</h1>
          <p className="text-gray-600">Real-time performance indicators and analytics</p>
        </div>
        
        {/* Controls */}
        <div className="flex items-center space-x-4">
          {/* Date Range Selector */}
          <div className="flex items-center space-x-2">
            <Calendar className="h-4 w-4 text-gray-500" />
            <select
              value={selectedDateRange}
              onChange={(e) => setSelectedDateRange(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
          </div>

          {/* Auto-refresh toggle */}
          <Button
            variant={autoRefresh ? "default" : "outline"}
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className="flex items-center space-x-2"
          >
            <Zap className={`h-4 w-4 ${autoRefresh ? 'text-white' : 'text-gray-500'}`} />
            <span>{autoRefresh ? 'Auto' : 'Manual'}</span>
          </Button>

          {/* Manual refresh */}
          <Button
            variant="outline"
            size="sm"
            onClick={fetchKPIData}
            className="flex items-center space-x-2"
          >
            <Refresh className="h-4 w-4" />
            <span>Refresh</span>
          </Button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'indicators', label: 'Indicators', icon: <Target className="h-4 w-4" /> },
            { id: 'activities', label: 'Activity Level', icon: <Activity className="h-4 w-4" /> },
            { id: 'projects', label: 'Project Level', icon: <BarChart3 className="h-4 w-4" /> }
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

      {/* Indicators Tab */}
      {activeTab === 'indicators' && indicatorKPIs && (
        <div className="space-y-6">
          {/* Key Performance Indicators */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Project Completion Rate"
              value={`${indicatorKPIs.performance_indicators?.project_completion_rate || 0}%`}
              icon={<CheckCircle />}
              trend={5.2}
              subtitle="Overall completion"
              color="green"
              cardId="project-completion"
            >
              <div className="flex justify-center">
                <ProgressRing 
                  percentage={indicatorKPIs.performance_indicators?.project_completion_rate || 0} 
                  color="#10B981"
                />
              </div>
            </MetricCard>

            <MetricCard
              title="Activity Completion Rate"
              value={`${indicatorKPIs.performance_indicators?.activity_completion_rate || 0}%`}
              icon={<Activity />}
              trend={2.8}
              subtitle="Activity progress"
              color="blue"
              cardId="activity-completion"
            >
              <div className="flex justify-center">
                <ProgressRing 
                  percentage={indicatorKPIs.performance_indicators?.activity_completion_rate || 0} 
                  color="#3B82F6"
                />
              </div>
            </MetricCard>

            <MetricCard
              title="Budget Utilization"
              value={`${indicatorKPIs.performance_indicators?.budget_utilization_rate || 0}%`}
              icon={<DollarSign />}
              trend={-1.2}
              subtitle="Budget efficiency"
              color="purple"
              cardId="budget-utilization"
            >
              <div className="flex justify-center">
                <ProgressRing 
                  percentage={indicatorKPIs.performance_indicators?.budget_utilization_rate || 0} 
                  color="#8B5CF6"
                />
              </div>
            </MetricCard>

            <MetricCard
              title="On-Time Delivery"
              value={`${indicatorKPIs.performance_indicators?.on_time_delivery_rate || 0}%`}
              icon={<Clock />}
              trend={3.5}
              subtitle="Timeline adherence"
              color="orange"
              cardId="on-time-delivery"
            >
              <div className="flex justify-center">
                <ProgressRing 
                  percentage={indicatorKPIs.performance_indicators?.on_time_delivery_rate || 0} 
                  color="#F59E0B"
                />
              </div>
            </MetricCard>
          </div>

          {/* Overview Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
            <MetricCard
              title="Total Projects"
              value={indicatorKPIs.overview?.total_projects || 0}
              icon={<BarChart3 />}
              color="blue"
            />
            <MetricCard
              title="Active Projects"
              value={indicatorKPIs.overview?.active_projects || 0}
              icon={<Zap />}
              color="green"
            />
            <MetricCard
              title="Total Activities"
              value={indicatorKPIs.overview?.total_activities || 0}
              icon={<Activity />}
              color="purple"
            />
            <MetricCard
              title="Beneficiaries"
              value={indicatorKPIs.overview?.total_beneficiaries || 0}
              icon={<Users />}
              color="orange"
            />
            <MetricCard
              title="Budget Utilization"
              value={`$${(indicatorKPIs.overview?.utilized_budget || 0).toLocaleString()}`}
              icon={<DollarSign />}
              subtitle={`of $${(indicatorKPIs.overview?.total_budget || 0).toLocaleString()}`}
              color="green"
            />
          </div>

          {/* Trends Chart Placeholder */}
          {indicatorKPIs.trends?.monthly_trends && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Performance Trends</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {indicatorKPIs.trends.monthly_trends.map((trend, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{trend.month}</span>
                      <div className="flex items-center space-x-4">
                        <span className="text-sm text-gray-600">Projects: {trend.projects}</span>
                        <span className="text-sm text-gray-600">Activities: {trend.activities}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Activities Tab */}
      {activeTab === 'activities' && activityKPIs && (
        <div className="space-y-6">
          {/* Activity Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Activities"
              value={activityKPIs.summary?.total_activities || 0}
              icon={<Activity />}
              color="blue"
            />
            <MetricCard
              title="Completion Rate"
              value={`${activityKPIs.summary?.completion_rate || 0}%`}
              icon={<CheckCircle />}
              color="green"
            />
            <MetricCard
              title="Overdue Activities"
              value={activityKPIs.summary?.overdue_activities || 0}
              icon={<AlertTriangle />}
              color="red"
            />
            <MetricCard
              title="High Risk Activities"
              value={activityKPIs.summary?.high_risk_activities || 0}
              icon={<Shield />}
              color="orange"
            />
          </div>

          {/* Activity Analytics */}
          {activityKPIs.analytics && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Status Breakdown */}
              <Card>
                <CardHeader>
                  <CardTitle>Status Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(activityKPIs.analytics.status_breakdown || {}).map(([status, count]) => (
                      <div key={status} className="flex items-center justify-between">
                        <Badge variant="outline" className="capitalize">
                          {status.replace('_', ' ')}
                        </Badge>
                        <span className="font-medium">{count}</span>
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
                    {Object.entries(activityKPIs.analytics.risk_distribution || {}).map(([risk, count]) => (
                      <div key={risk} className="flex items-center justify-between">
                        <Badge 
                          variant="outline" 
                          className={`capitalize ${
                            risk === 'high' ? 'border-red-500 text-red-600' :
                            risk === 'medium' ? 'border-yellow-500 text-yellow-600' :
                            'border-green-500 text-green-600'
                          }`}
                        >
                          {risk} risk
                        </Badge>
                        <span className="font-medium">{count}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Activities List with Drill-down */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Activity Details</span>
                <Badge variant="outline">{activityKPIs.activities?.length || 0} activities</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {(activityKPIs.activities || []).slice(0, 10).map((activity, index) => (
                  <div 
                    key={activity.activity_id || index} 
                    className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => handleDrillDown('activity', activity, activity.name)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{activity.name}</h4>
                        <div className="flex items-center space-x-4 mt-2">
                          <Badge className={`${
                            activity.status === 'completed' ? 'bg-green-100 text-green-800' :
                            activity.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {(activity.status || '').replace('_', ' ')}
                          </Badge>
                          <span className="text-sm text-gray-600">
                            Progress: {activity.progress_percentage}%
                          </span>
                          <Badge className={`${
                            activity.risk_level === 'high' ? 'bg-red-100 text-red-800' :
                            activity.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {activity.risk_level} risk
                          </Badge>
                        </div>
                      </div>
                      <div className="text-right">
                        <Progress value={activity.progress_percentage} className="w-20 mb-2" />
                        <span className="text-sm text-gray-500">
                          {activity.completion_rate.toFixed(1)}% complete
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Projects Tab */}
      {activeTab === 'projects' && projectKPIs && (
        <div className="space-y-6">
          {/* Project Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Projects"
              value={projectKPIs.summary?.total_projects || 0}
              icon={<BarChart3 />}
              color="blue"
            />
            <MetricCard
              title="Completion Rate"
              value={`${projectKPIs.summary?.project_completion_rate || 0}%`}
              icon={<CheckCircle />}
              color="green"
            />
            <MetricCard
              title="Budget Utilization"
              value={`${projectKPIs.summary?.overall_budget_utilization || 0}%`}
              icon={<DollarSign />}
              color="purple"
            />
            <MetricCard
              title="Total Budget"
              value={`$${(projectKPIs.summary?.total_budget || 0).toLocaleString()}`}
              icon={<Target />}
              subtitle={`$${(projectKPIs.summary?.total_expenses || 0).toLocaleString()} spent`}
              color="orange"
            />
          </div>

          {/* Project Analytics */}
          {projectKPIs.analytics && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Status Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle>Project Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(projectKPIs.analytics.status_distribution || {}).map(([status, count]) => (
                      <div key={status} className="flex items-center justify-between">
                        <Badge variant="outline" className="capitalize">
                          {status.replace('_', ' ')}
                        </Badge>
                        <span className="font-medium">{count}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Budget Performance */}
              <Card>
                <CardHeader>
                  <CardTitle>Budget Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(projectKPIs.analytics.budget_performance?.budget_distribution || {}).map(([range, count]) => (
                      <div key={range} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">{range}</span>
                        <span className="font-medium">{count} projects</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Beneficiary Impact */}
              <Card>
                <CardHeader>
                  <CardTitle>Beneficiary Impact</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900">
                        {projectKPIs.analytics.beneficiary_impact?.overall_achievement_rate || 0}%
                      </div>
                      <div className="text-sm text-gray-600">Overall Achievement</div>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Target: {(projectKPIs.analytics.beneficiary_impact?.total_target_beneficiaries || 0).toLocaleString()}</span>
                      <span>Actual: {(projectKPIs.analytics.beneficiary_impact?.total_actual_beneficiaries || 0).toLocaleString()}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Projects List with Drill-down */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Project Details</span>
                <Badge variant="outline">{projectKPIs.projects?.length || 0} projects</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {(projectKPIs.projects || []).slice(0, 10).map((project, index) => (
                  <div 
                    key={project.project_id || index} 
                    className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => handleDrillDown('project', project, project.name)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{project.name}</h4>
                        <div className="flex items-center space-x-4 mt-2">
                          <Badge className={`${
                            project.status === 'completed' ? 'bg-green-100 text-green-800' :
                            project.status === 'active' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {(project.status || '').replace('_', ' ')}
                          </Badge>
                          <span className="text-sm text-gray-600">
                            Activities: {project.total_activities}
                          </span>
                          <span className="text-sm text-gray-600">
                            Budget: ${project.budget?.toLocaleString()}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-semibold text-gray-900">
                          {project.budget_utilization}%
                        </div>
                        <div className="text-sm text-gray-500">Budget Used</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Drill-down Modal */}
      {drillDownData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={closeDrillDown}>
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-96 overflow-y-auto" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Detailed View: {drillDownType}</h3>
              <Button variant="ghost" size="sm" onClick={closeDrillDown}>
                ×
              </Button>
            </div>
            <div className="space-y-4">
              <pre className="bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
                {JSON.stringify(drillDownData, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default KPIDashboard;