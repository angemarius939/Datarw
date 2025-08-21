import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { 
  FileText, 
  Download, 
  Calendar, 
  BarChart3, 
  TrendingUp, 
  Brain, 
  Image as ImageIcon, 
  Plus, 
  Settings,
  Clock,
  CheckCircle,
  AlertCircle,
  Upload,
  Eye,
  Trash2,
  Sparkles,
  PieChart,
  Activity,
  Users,
  DollarSign,
  Target,
  Loader2
} from 'lucide-react';
import { reportsAPI, projectsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const EnhancedReporting = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Data state
  const [projects, setProjects] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [generatedReports, setGeneratedReports] = useState([]);
  const [projectImages, setProjectImages] = useState([]);
  
  // UI state
  const [activeTab, setActiveTab] = useState('templates');
  const [selectedProject, setSelectedProject] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showImagesModal, setShowImagesModal] = useState(false);
  const [generatingReport, setGeneratingReport] = useState(false);
  
  // Form state
  const [reportForm, setReportForm] = useState({
    project_id: '',
    report_type: 'Monthly Report',
    period_start: '',
    period_end: '',
    include_images: true,
    ai_narrative: true,
    custom_title: ''
  });
  
  const [imageFiles, setImageFiles] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [projectsRes, templatesRes, reportsRes] = await Promise.allSettled([
        projectsAPI.getProjects(),
        reportsAPI.getTemplates(),
        reportsAPI.getGeneratedReports()
      ]);

      if (projectsRes.status === 'fulfilled') {
        setProjects(projectsRes.value.data || []);
      }

      if (templatesRes.status === 'fulfilled') {
        const templatesData = templatesRes.value.data;
        setTemplates(Array.isArray(templatesData) ? templatesData : []);
      } else {
        setTemplates([]);
      }

      if (reportsRes.status === 'fulfilled') {
        setGeneratedReports(reportsRes.value.data || []);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to load reporting data');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async (quickType = null, projectId = null) => {
    try {
      setGeneratingReport(true);
      setError('');
      
      let reportData = {};
      
      if (quickType && projectId) {
        // Quick report generation
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth();
        
        switch (quickType) {
          case 'monthly':
            reportData = {
              project_id: projectId,
              report_type: 'Monthly Report',
              period_start: new Date(currentYear, currentMonth - 1, 1).toISOString(),
              period_end: new Date(currentYear, currentMonth, 0).toISOString(),
              include_images: true,
              ai_narrative: true
            };
            break;
          case 'quarterly':
            const currentQuarter = Math.floor(currentMonth / 3) + 1;
            const quarterStartMonth = (currentQuarter - 1) * 3;
            reportData = {
              project_id: projectId,
              report_type: 'Quarterly Report',
              period_start: new Date(currentYear, quarterStartMonth, 1).toISOString(),
              period_end: new Date(currentYear, quarterStartMonth + 3, 0).toISOString(),
              include_images: true,
              ai_narrative: true
            };
            break;
          case 'annual':
            reportData = {
              project_id: projectId,
              report_type: 'Annual Report',
              period_start: new Date(currentYear - 1, 0, 1).toISOString(),
              period_end: new Date(currentYear - 1, 11, 31).toISOString(),
              include_images: true,
              ai_narrative: true
            };
            break;
        }
      } else {
        // Custom report from form
        reportData = { ...reportForm };
      }
      
      const response = await reportsAPI.generateReport(reportData);
      
      if (response.data.success) {
        setSuccess(`Report generated successfully! Report ID: ${response.data.data.report_id}`);
        setShowCreateModal(false);
        fetchData(); // Refresh the reports list
      }
    } catch (error) {
      console.error('Error generating report:', error);
      setError(error.response?.data?.detail || 'Failed to generate report');
    } finally {
      setGeneratingReport(false);
    }
  };

  const handleDownloadReport = async (reportId, reportType, projectId) => {
    try {
      setLoading(true);
      const response = await reportsAPI.downloadReport(reportId);
      
      // Create download link
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${reportType}_${projectId}_${reportId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      setSuccess('Report downloaded successfully');
    } catch (error) {
      console.error('Error downloading report:', error);
      setError('Failed to download report');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadImages = async () => {
    if (!selectedProject || imageFiles.length === 0) {
      setError('Please select a project and images to upload');
      return;
    }

    try {
      setLoading(true);
      const response = await reportsAPI.uploadImages(selectedProject, imageFiles);
      
      if (response.data.success) {
        setSuccess(`Uploaded ${response.data.data.length} images successfully`);
        setImageFiles([]);
        setShowImagesModal(false);
        // Refresh images
        if (selectedProject) {
          const imagesRes = await reportsAPI.getProjectImages(selectedProject);
          setProjectImages(imagesRes.data.data || []);
        }
      }
    } catch (error) {
      console.error('Error uploading images:', error);
      setError('Failed to upload images');
    } finally {
      setLoading(false);
    }
  };

  const fetchProjectImages = async (projectId) => {
    try {
      const response = await reportsAPI.getProjectImages(projectId);
      setProjectImages(response.data.data || []);
    } catch (error) {
      console.error('Error fetching images:', error);
    }
  };

  const getReportStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const StatCard = ({ title, value, icon, color = "blue", description, onClick }) => (
    <Card className={`hover:shadow-lg transition-shadow duration-300 ${onClick ? 'cursor-pointer' : ''}`} onClick={onClick}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">{title}</CardTitle>
        <div className={`p-2 rounded-lg bg-${color}-100`}>
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-gray-900">{value}</div>
        {description && (
          <p className="text-xs text-gray-500 mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  );

  const TemplateCard = ({ template, onGenerate }) => (
    <Card className="hover:shadow-lg transition-all duration-300 border-dashed border-2 hover:border-solid hover:border-blue-400">
      <CardContent className="p-6">
        <div className="text-center">
          <div className="mb-4">
            {template.id === 'monthly' && <Calendar className="h-12 w-12 text-blue-600 mx-auto" />}
            {template.id === 'quarterly' && <BarChart3 className="h-12 w-12 text-green-600 mx-auto" />}
            {template.id === 'annual' && <TrendingUp className="h-12 w-12 text-purple-600 mx-auto" />}
            {template.id === 'donor' && <DollarSign className="h-12 w-12 text-orange-600 mx-auto" />}
          </div>
          
          <h3 className="text-lg font-semibold mb-2">{template.name}</h3>
          <p className="text-sm text-gray-600 mb-4">{template.description}</p>
          
          <div className="mb-4">
            <Badge variant="outline" className="text-xs">
              {template.frequency}
            </Badge>
          </div>
          
          <div className="space-y-2">
            <Select onValueChange={(projectId) => onGenerate(template.id, projectId)}>
              <SelectTrigger>
                <SelectValue placeholder="Select project" />
              </SelectTrigger>
              <SelectContent>
                {projects.map(project => (
                  <SelectItem key={project.id} value={project.id}>
                    {project.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Brain className="h-8 w-8 mr-3 text-blue-600" />
            AI-Enhanced Reporting
          </h1>
          <p className="text-gray-600 mt-1">Generate comprehensive reports with AI narratives and visualizations</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowImagesModal(true)}>
            <ImageIcon className="h-4 w-4 mr-2" />
            Manage Images
          </Button>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Create Custom Report
          </Button>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Available Projects"
          value={projects.length}
          icon={<Activity className="h-5 w-5 text-blue-600" />}
          color="blue"
          description="Projects ready for reporting"
        />
        <StatCard
          title="Report Templates"
          value={templates.length}
          icon={<FileText className="h-5 w-5 text-green-600" />}
          color="green"
          description="Available report types"
        />
        <StatCard
          title="Generated Reports"
          value={generatedReports.length}
          icon={<BarChart3 className="h-5 w-5 text-purple-600" />}
          color="purple"
          description="Total reports created"
        />
        <StatCard
          title="AI Features"
          value="Active"
          icon={<Sparkles className="h-5 w-5 text-yellow-600" />}
          color="yellow"
          description="AI narrative generation"
        />
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="templates">Report Templates</TabsTrigger>
          <TabsTrigger value="generated">Generated Reports</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Report Templates Tab */}
        <TabsContent value="templates" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="h-5 w-5 mr-2 text-blue-600" />
                Quick Report Generation
              </CardTitle>
              <CardDescription>
                Generate reports instantly using pre-configured templates
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {templates.map(template => (
                  <TemplateCard
                    key={template.id}
                    template={template}
                    onGenerate={(templateType, projectId) => {
                      if (projectId) {
                        handleGenerateReport(templateType, projectId);
                      }
                    }}
                  />
                ))}
              </div>
              
              {generatingReport && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center">
                    <Loader2 className="h-5 w-5 text-blue-600 animate-spin mr-3" />
                    <div>
                      <p className="font-medium text-blue-900">Generating Report...</p>
                      <p className="text-sm text-blue-700">This may take a few minutes. AI is analyzing project data and creating visualizations.</p>
                    </div>
                  </div>
                  <Progress value={50} className="mt-3" />
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Generated Reports Tab */}
        <TabsContent value="generated" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2 text-green-600" />
                Generated Reports ({generatedReports.length})
              </CardTitle>
              <CardDescription>
                Download and manage your generated reports
              </CardDescription>
            </CardHeader>
            <CardContent>
              {generatedReports.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No reports generated yet</h3>
                  <p className="text-gray-600 mb-4">Start by creating your first report using the templates above</p>
                  <Button onClick={() => setActiveTab('templates')}>
                    <Plus className="h-4 w-4 mr-2" />
                    Generate Report
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {generatedReports.map(report => (
                    <div key={report.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3">
                            <h4 className="font-medium text-gray-900">{report.report_type}</h4>
                            <Badge className={getReportStatusColor(report.status)}>
                              {report.status}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            Project ID: {report.project_id} • Generated: {new Date(report.generated_at).toLocaleDateString()}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            File size: {report.file_size || 'Unknown'}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDownloadReport(report.id, report.report_type, report.project_id)}
                          >
                            <Download className="h-4 w-4 mr-1" />
                            Download
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" className="text-red-600">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Report Generation Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Monthly Reports</span>
                    <Badge variant="outline">
                      {generatedReports.filter(r => r.report_type === 'Monthly Report').length}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Quarterly Reports</span>
                    <Badge variant="outline">
                      {generatedReports.filter(r => r.report_type === 'Quarterly Report').length}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Annual Reports</span>
                    <Badge variant="outline">
                      {generatedReports.filter(r => r.report_type === 'Annual Report').length}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>AI Features Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">AI Narratives Generated</span>
                    <Badge className="bg-blue-100 text-blue-800">
                      {generatedReports.length}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Charts Generated</span>
                    <Badge className="bg-green-100 text-green-800">
                      {generatedReports.length * 4} {/* Approximate */}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Images Included</span>
                    <Badge className="bg-purple-100 text-purple-800">
                      {projectImages.length}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="h-5 w-5 mr-2" />
                Reporting Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert>
                <Brain className="h-4 w-4" />
                <AlertDescription>
                  <strong>AI Features:</strong> Narrative generation is powered by advanced language models. 
                  Reports include intelligent insights, trend analysis, and actionable recommendations.
                </AlertDescription>
              </Alert>
              
              <Alert>
                <BarChart3 className="h-4 w-4" />
                <AlertDescription>
                  <strong>Visualizations:</strong> Charts are automatically generated from your project data 
                  including budget utilization, activity progress, KPI achievements, and beneficiary demographics.
                </AlertDescription>
              </Alert>
              
              <Alert>
                <ImageIcon className="h-4 w-4" />
                <AlertDescription>
                  <strong>Images:</strong> Upload project photos, charts, and documentation to be included 
                  in your reports for enhanced visual storytelling.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Custom Report Creation Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center">
              <Plus className="h-5 w-5 mr-2" />
              Create Custom Report
            </DialogTitle>
            <DialogDescription>
              Generate a custom report with specific parameters and date ranges
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Project</Label>
                <Select value={reportForm.project_id} onValueChange={(value) => setReportForm(prev => ({ ...prev, project_id: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select project" />
                  </SelectTrigger>
                  <SelectContent>
                    {projects.map(project => (
                      <SelectItem key={project.id} value={project.id}>
                        {project.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label>Report Type</Label>
                <Select value={reportForm.report_type} onValueChange={(value) => setReportForm(prev => ({ ...prev, report_type: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Monthly Report">Monthly Report</SelectItem>
                    <SelectItem value="Quarterly Report">Quarterly Report</SelectItem>
                    <SelectItem value="Annual Report">Annual Report</SelectItem>
                    <SelectItem value="Donor Report">Donor Report</SelectItem>
                    <SelectItem value="Custom Report">Custom Report</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Period Start</Label>
                <Input
                  type="date"
                  value={reportForm.period_start}
                  onChange={(e) => setReportForm(prev => ({ ...prev, period_start: e.target.value }))}
                />
              </div>
              
              <div className="space-y-2">
                <Label>Period End</Label>
                <Input
                  type="date"
                  value={reportForm.period_end}
                  onChange={(e) => setReportForm(prev => ({ ...prev, period_end: e.target.value }))}
                />
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="include_images"
                  checked={reportForm.include_images}
                  onChange={(e) => setReportForm(prev => ({ ...prev, include_images: e.target.checked }))}
                  className="rounded border-gray-300"
                />
                <Label htmlFor="include_images">Include uploaded images in report</Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="ai_narrative"
                  checked={reportForm.ai_narrative}
                  onChange={(e) => setReportForm(prev => ({ ...prev, ai_narrative: e.target.checked }))}
                  className="rounded border-gray-300"
                />
                <Label htmlFor="ai_narrative">Generate AI-powered narrative analysis</Label>
              </div>
            </div>
            
            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                Cancel
              </Button>
              <Button 
                onClick={() => handleGenerateReport()}
                disabled={!reportForm.project_id || !reportForm.period_start || !reportForm.period_end || generatingReport}
              >
                {generatingReport ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Generating...</>
                ) : (
                  <><Sparkles className="h-4 w-4 mr-2" /> Generate Report</>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Image Management Modal */}
      <Dialog open={showImagesModal} onOpenChange={setShowImagesModal}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle className="flex items-center">
              <ImageIcon className="h-5 w-5 mr-2" />
              Manage Report Images
            </DialogTitle>
            <DialogDescription>
              Upload and manage images to be included in your reports
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Select Project</Label>
              <Select value={selectedProject} onValueChange={(value) => {
                setSelectedProject(value);
                fetchProjectImages(value);
              }}>
                <SelectTrigger>
                  <SelectValue placeholder="Select project" />
                </SelectTrigger>
                <SelectContent>
                  {projects.map(project => (
                    <SelectItem key={project.id} value={project.id}>
                      {project.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label>Upload Images</Label>
              <Input
                type="file"
                multiple
                accept="image/*"
                onChange={(e) => setImageFiles(Array.from(e.target.files))}
              />
              <p className="text-sm text-gray-500">
                Select multiple images (PNG, JPG, GIF). Maximum 10MB per file.
              </p>
            </div>
            
            {imageFiles.length > 0 && (
              <div className="space-y-2">
                <Label>Selected Files ({imageFiles.length})</Label>
                <div className="space-y-1">
                  {imageFiles.map((file, index) => (
                    <div key={index} className="text-sm text-gray-600 flex justify-between items-center">
                      <span>{file.name}</span>
                      <span>{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {projectImages.length > 0 && (
              <div className="space-y-2">
                <Label>Existing Images ({projectImages.length})</Label>
                <div className="grid grid-cols-3 gap-4 max-h-48 overflow-y-auto">
                  {projectImages.map(image => (
                    <div key={image.id} className="border rounded p-2">
                      <p className="text-xs font-medium truncate">{image.original_name}</p>
                      <p className="text-xs text-gray-500">{(image.size / 1024).toFixed(1)} KB</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={() => setShowImagesModal(false)}>
                Close
              </Button>
              <Button 
                onClick={handleUploadImages}
                disabled={!selectedProject || imageFiles.length === 0 || loading}
              >
                {loading ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Uploading...</>
                ) : (
                  <><Upload className="h-4 w-4 mr-2" /> Upload Images</>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default EnhancedReporting;