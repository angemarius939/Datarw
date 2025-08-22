import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Calendar,
  Users,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  Clock,
  CheckCircle,
  Edit,
  Eye,
  Filter,
  Search,
  ArrowUp,
  ArrowDown,
  Minus,
  Flag,
  Target,
  BarChart3,
  Activity,
  Timer,
  User,
  FileText,
  Save,
  X
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';

const EnhancedActivityTracker = ({ dashboardData, onDataRefresh }) => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [activities, setActivities] = useState([]);
  const [flaggedActivities, setFlaggedActivities] = useState([]);
  const [portfolioSummary, setPortfolioSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editingActivity, setEditingActivity] = useState(null);
  const [showVarianceAnalysis, setShowVarianceAnalysis] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchEnhancedActivityData();
  }, []);

  const fetchEnhancedActivityData = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      // Fetch activities, flagged activities, and portfolio summary in parallel
      const [activitiesResponse, flaggedResponse, portfolioResponse] = await Promise.all([
        fetch(`${backendUrl}/api/activities`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${backendUrl}/api/activities/flagged`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${backendUrl}/api/projects/portfolio-summary`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (activitiesResponse.ok) {
        const activitiesData = await activitiesResponse.json();
        setActivities(Array.isArray(activitiesData) ? activitiesData : []);
      }

      if (flaggedResponse.ok) {
        const flaggedData = await flaggedResponse.json();
        setFlaggedActivities(flaggedData.data || []);
      }

      if (portfolioResponse.ok) {
        const portfolioData = await portfolioResponse.json();
        setPortfolioSummary(portfolioData.data || null);
      }

    } catch (error) {
      console.error('Enhanced activity data fetch error:', error);
      toast({
        title: "Error",
        description: "Failed to load enhanced activity data",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const updateActivityProgress = async (activityId, progressData) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${backendUrl}/api/activities/${activityId}/progress`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(progressData)
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Activity progress updated successfully"
        });
        fetchEnhancedActivityData();
        onDataRefresh?.();
      } else {
        throw new Error('Failed to update progress');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update activity progress",
        variant: "destructive"
      });
    }
  };

  const getVarianceAnalysis = async (activityId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${backendUrl}/api/activities/${activityId}/variance`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setShowVarianceAnalysis(data.data);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load variance analysis",
        variant: "destructive"
      });
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'completed': 'bg-green-100 text-green-800 border-green-200',
      'in_progress': 'bg-blue-100 text-blue-800 border-blue-200',
      'delayed': 'bg-red-100 text-red-800 border-red-200',
      'not_started': 'bg-gray-100 text-gray-800 border-gray-200'
    };
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getRiskColor = (riskLevel) => {
    const colors = {
      'low': 'bg-green-100 text-green-800',
      'medium': 'bg-yellow-100 text-yellow-800',
      'high': 'bg-red-100 text-red-800',
      'critical': 'bg-purple-100 text-purple-800'
    };
    return colors[riskLevel] || 'bg-gray-100 text-gray-800';
  };

  const getVarianceColor = (variance) => {
    if (variance > 0) return 'text-green-600';
    if (variance < -10) return 'text-red-600';
    if (variance < 0) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const getVarianceIcon = (variance) => {
    if (variance > 0) return <ArrowUp className="h-4 w-4" />;
    if (variance < 0) return <ArrowDown className="h-4 w-4" />;
    return <Minus className="h-4 w-4" />;
  };

  const filteredActivities = activities.filter(activity => {
    const matchesStatus = filterStatus === 'all' || activity.status === filterStatus;
    const matchesSearch = activity.name?.toLowerCase().includes(searchTerm.toLowerCase()) || false;
    return matchesStatus && matchesSearch;
  });

  const ActivityEditModal = ({ activity, onClose, onSave }) => {
    const [editData, setEditData] = useState({
      progress_percentage: activity.progress_percentage || 0,
      actual_output: activity.actual_output || '',
      achieved_quantity: activity.achieved_quantity || 0,
      status_notes: activity.status_notes || '',
      milestone_completed: ''
    });

    const handleSave = () => {
      onSave(activity.id, editData);
      onClose();
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Update Activity Progress</h3>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Progress %</label>
              <input
                type="number"
                min="0"
                max="100"
                className="w-full p-2 border rounded"
                value={editData.progress_percentage}
                onChange={(e) => setEditData({...editData, progress_percentage: parseFloat(e.target.value)})}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Actual Output</label>
              <textarea
                className="w-full p-2 border rounded"
                rows={3}
                value={editData.actual_output}
                onChange={(e) => setEditData({...editData, actual_output: e.target.value})}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Achieved Quantity</label>
              <input
                type="number"
                className="w-full p-2 border rounded"
                value={editData.achieved_quantity}
                onChange={(e) => setEditData({...editData, achieved_quantity: parseFloat(e.target.value)})}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Status Notes</label>
              <textarea
                className="w-full p-2 border rounded"
                rows={2}
                value={editData.status_notes}
                onChange={(e) => setEditData({...editData, status_notes: e.target.value})}
              />
            </div>
          </div>
          
          <div className="flex justify-end space-x-2 mt-6">
            <Button variant="outline" onClick={onClose}>Cancel</Button>
            <Button onClick={handleSave}>
              <Save className="h-4 w-4 mr-1" />
              Update Progress
            </Button>
          </div>
        </div>
      </div>
    );
  };

  const VarianceAnalysisModal = ({ analysis, onClose }) => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Variance Analysis: {analysis.activity_name}</h3>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="p-3 bg-gray-50 rounded">
            <div className="text-sm font-medium text-gray-600">Schedule Variance</div>
            <div className={`text-lg font-bold ${getVarianceColor(analysis.schedule_variance_days)}`}>
              {analysis.schedule_variance_days} days
            </div>
          </div>
          
          <div className="p-3 bg-gray-50 rounded">
            <div className="text-sm font-medium text-gray-600">Budget Variance</div>
            <div className={`text-lg font-bold ${getVarianceColor(analysis.budget_variance_percentage)}`}>
              {analysis.budget_variance_percentage}%
            </div>
          </div>
          
          <div className="p-3 bg-gray-50 rounded">
            <div className="text-sm font-medium text-gray-600">Output Variance</div>
            <div className={`text-lg font-bold ${getVarianceColor(analysis.output_variance_percentage)}`}>
              {analysis.output_variance_percentage}%
            </div>
          </div>
          
          <div className="p-3 bg-gray-50 rounded">
            <div className="text-sm font-medium text-gray-600">Completion Variance</div>
            <div className={`text-lg font-bold ${getVarianceColor(analysis.completion_variance)}`}>
              {analysis.completion_variance}%
            </div>
          </div>
        </div>
        
        <div className="mb-4">
          <div className="text-sm font-medium text-gray-600 mb-2">Risk Assessment</div>
          <Badge className={getRiskColor(analysis.risk_assessment)}>
            {analysis.risk_assessment.toUpperCase()}
          </Badge>
        </div>
        
        {analysis.risk_factors?.length > 0 && (
          <div>
            <div className="text-sm font-medium text-gray-600 mb-2">Risk Factors</div>
            <ul className="space-y-1">
              {analysis.risk_factors.map((factor, index) => (
                <li key={index} className="text-sm text-red-600 flex items-center">
                  <AlertTriangle className="h-3 w-3 mr-1" />
                  {factor}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading enhanced activity tracker...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Portfolio Summary Cards */}
      {portfolioSummary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Activities</p>
                  <p className="text-2xl font-bold">{portfolioSummary.total_activities}</p>
                </div>
                <Activity className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Completion Rate</p>
                  <p className="text-2xl font-bold">{portfolioSummary.completion_rate}%</p>
                </div>
                <Target className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Overdue Activities</p>
                  <p className="text-2xl font-bold text-red-600">{portfolioSummary.overdue_activities}</p>
                </div>
                <Clock className="h-8 w-8 text-red-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">High Risk</p>
                  <p className="text-2xl font-bold text-orange-600">{portfolioSummary.high_risk_activities}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Flagged Activities Alert */}
      {flaggedActivities.length > 0 && (
        <Alert>
          <Flag className="h-4 w-4" />
          <AlertDescription>
            <div className="flex justify-between items-center">
              <span>
                {flaggedActivities.length} activities need immediate attention
              </span>
              <Button variant="outline" size="sm">
                View Details
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Activity Tracker Main Section */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="flex items-center">
                <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
                Enhanced Activity Tracker
              </CardTitle>
              <CardDescription>
                Comprehensive project activity management with variance analysis
              </CardDescription>
            </div>
            <div className="flex space-x-2">
              <div className="flex items-center space-x-2">
                <Search className="h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search activities..."
                  className="px-3 py-1 border rounded text-sm"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <select
                className="px-3 py-1 border rounded text-sm"
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <option value="all">All Status</option>
                <option value="not_started">Not Started</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="delayed">Delayed</option>
              </select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredActivities.length > 0 ? (
            <div className="space-y-4">
              {filteredActivities.map((activity) => (
                <div key={activity.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="grid grid-cols-12 gap-4 items-center">
                    {/* Activity Name & Status */}
                    <div className="col-span-3">
                      <h4 className="font-medium text-gray-900">{activity.name}</h4>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge className={getStatusColor(activity.status)}>
                          {activity.status?.replace('_', ' ')}
                        </Badge>
                        {activity.risk_level && (
                          <Badge className={getRiskColor(activity.risk_level)}>
                            {activity.risk_level}
                          </Badge>
                        )}
                      </div>
                    </div>
                    
                    {/* Assigned & Timeline */}
                    <div className="col-span-2">
                      <div className="text-sm text-gray-600">
                        <User className="h-3 w-3 inline mr-1" />
                        {activity.assigned_to || 'Unassigned'}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {new Date(activity.end_date).toLocaleDateString()}
                      </div>
                    </div>
                    
                    {/* Progress */}
                    <div className="col-span-2">
                      <div className="text-sm text-gray-600 mb-1">
                        {activity.progress_percentage || 0}% Complete
                      </div>
                      <Progress value={activity.progress_percentage || 0} className="h-2" />
                    </div>
                    
                    {/* Variance Indicators */}
                    <div className="col-span-2">
                      <div className="flex items-center space-x-2 text-xs">
                        {activity.schedule_variance_days !== undefined && (
                          <div className={`flex items-center ${getVarianceColor(activity.schedule_variance_days)}`}>
                            {getVarianceIcon(activity.schedule_variance_days)}
                            <span className="ml-1">{Math.abs(activity.schedule_variance_days)}d</span>
                          </div>
                        )}
                        {activity.completion_variance !== undefined && (
                          <div className={`flex items-center ${getVarianceColor(activity.completion_variance)}`}>
                            <Target className="h-3 w-3" />
                            <span className="ml-1">{activity.completion_variance > 0 ? '+' : ''}{activity.completion_variance}%</span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {/* Target vs Achieved */}
                    <div className="col-span-2">
                      {activity.target_quantity && (
                        <div className="text-xs text-gray-600">
                          <div>Target: {activity.target_quantity}{activity.measurement_unit ? ` ${activity.measurement_unit}` : ''}</div>
                          <div>Achieved: {activity.achieved_quantity || 0}{activity.measurement_unit ? ` ${activity.measurement_unit}` : ''}</div>
                        </div>
                      )}
                    </div>
                    
                    {/* Actions */}
                    <div className="col-span-1">
                      <div className="flex space-x-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditingActivity(activity)}
                        >
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => getVarianceAnalysis(activity.id)}
                        >
                          <Eye className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                  
                  {/* Additional Info Row */}
                  {(activity.actual_output || activity.status_notes) && (
                    <div className="mt-3 pt-3 border-t">
                      {activity.actual_output && (
                        <div className="text-sm text-gray-600 mb-1">
                          <strong>Output:</strong> {activity.actual_output}
                        </div>
                      )}
                      {activity.status_notes && (
                        <div className="text-sm text-gray-600">
                          <strong>Notes:</strong> {activity.status_notes}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Activity className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No activities found</p>
              <p className="text-sm">Create activities to start tracking progress</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modals */}
      {editingActivity && (
        <ActivityEditModal
          activity={editingActivity}
          onClose={() => setEditingActivity(null)}
          onSave={updateActivityProgress}
        />
      )}

      {showVarianceAnalysis && (
        <VarianceAnalysisModal
          analysis={showVarianceAnalysis}
          onClose={() => setShowVarianceAnalysis(null)}
        />
      )}
    </div>
  );
};

export default EnhancedActivityTracker;