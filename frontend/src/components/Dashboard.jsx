import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
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
  Download
} from 'lucide-react';
import { mockOrganizations, mockSurveys, mockUsers, mockAnalytics } from '../mock/mockData';
import SurveyBuilder from './SurveyBuilder';
import UserManagement from './UserManagement';

const Dashboard = ({ onLogout }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [currentOrg] = useState(mockOrganizations[0]);

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
            <span className="font-medium">{survey.responses}</span> responses
          </div>
          <div className="text-sm text-gray-600">
            Updated {new Date(survey.updatedAt).toLocaleDateString()}
          </div>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" className="flex-1">
            <Eye className="h-4 w-4 mr-2" />
            View
          </Button>
          <Button size="sm" variant="outline" className="flex-1">
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button size="sm" variant="outline" className="text-red-600 hover:text-red-700">
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );

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
                <p className="text-sm text-gray-600">{currentOrg.name}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge className="bg-green-100 text-green-800 border-green-200">
                {currentOrg.plan} Plan
              </Badge>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <Button variant="outline" size="sm" onClick={onLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r min-h-screen">
          <nav className="p-4 space-y-2">
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
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
                <Button className="bg-gradient-to-r from-blue-600 to-purple-600">
                  <Plus className="h-4 w-4 mr-2" />
                  New Survey
                </Button>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                  title="Total Surveys"
                  value={currentOrg.surveyCount}
                  icon={<FileText className="h-5 w-5 text-blue-600" />}
                  trend="up"
                  trendValue={12}
                  color="blue"
                />
                <StatCard
                  title="Total Responses"
                  value={mockAnalytics.totalResponses.toLocaleString()}
                  icon={<BarChart3 className="h-5 w-5 text-green-600" />}
                  trend="up"
                  trendValue={mockAnalytics.monthlyGrowth}
                  color="green"
                />
                <StatCard
                  title="Response Rate"
                  value={`${mockAnalytics.responseRate}%`}
                  icon={<TrendingUp className="h-5 w-5 text-purple-600" />}
                  trend="up"
                  trendValue={8}
                  color="purple"
                />
                <StatCard
                  title="Storage Used"
                  value={`${currentOrg.storageUsed}/${currentOrg.storageLimit} GB`}
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
                      {currentOrg.surveyCount} of {currentOrg.plan === 'Basic' ? 4 : 10} surveys used
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Progress 
                      value={(currentOrg.surveyCount / (currentOrg.plan === 'Basic' ? 4 : 10)) * 100} 
                      className="h-2"
                    />
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Storage Usage</CardTitle>
                    <CardDescription>
                      {currentOrg.storageUsed} GB of {currentOrg.storageLimit} GB used
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Progress 
                      value={(currentOrg.storageUsed / currentOrg.storageLimit) * 100} 
                      className="h-2"
                    />
                  </CardContent>
                </Card>
              </div>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Survey Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {mockAnalytics.responsesByMonth.slice(-3).map((data, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <span className="font-medium">{data.month}</span>
                          <span className="text-gray-600 ml-2">{data.responses} responses</span>
                        </div>
                        <Badge variant="outline">{data.responses > 250 ? 'High' : 'Normal'} Activity</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === 'surveys' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">Surveys</h1>
                <Button onClick={() => setActiveTab('builder')} className="bg-gradient-to-r from-blue-600 to-purple-600">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Survey
                </Button>
              </div>

              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {mockSurveys.map((survey) => (
                  <SurveyCard key={survey.id} survey={survey} />
                ))}
              </div>
            </div>
          )}

          {activeTab === 'builder' && <SurveyBuilder />}
          {activeTab === 'users' && <UserManagement />}

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
                {mockSurveys.map((survey) => (
                  <Card key={survey.id} className="hover:shadow-md transition-shadow">
                    <CardHeader>
                      <CardTitle className="text-lg">{survey.title}</CardTitle>
                      <CardDescription>{survey.responses} responses</CardDescription>
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
        </main>
      </div>
    </div>
  );
};

export default Dashboard;