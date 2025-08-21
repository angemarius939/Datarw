import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Checkbox } from './ui/checkbox';
import { Switch } from './ui/switch';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { 
  Users, 
  UserPlus, 
  Building2, 
  Plus, 
  Settings, 
  Shield, 
  Mail, 
  Edit,
  Trash2,
  Eye,
  AlertCircle,
  CheckCircle,
  Clock,
  Search,
  Filter,
  Download,
  Upload,
  Key,
  Globe,
  Palette,
  FileText,
  BarChart3
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { adminAPI, usersAPI, partnersAPI } from '../services/api';

const AdminPanel = () => {
  const { user, organization } = useAuth();
  const [activeTab, setActiveTab] = useState('users');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Users State
  const [users, setUsers] = useState([]);
  const [userSearch, setUserSearch] = useState('');
  const [userFilter, setUserFilter] = useState('all');
  const [selectedUsers, setSelectedUsers] = useState([]);
  
  // Partners State
  const [partners, setPartners] = useState([]);
  const [partnerSearch, setPartnerSearch] = useState('');
  const [partnerFilter, setPartnerFilter] = useState('all');
  
  // Modals State
  const [showCreateUserModal, setShowCreateUserModal] = useState(false);
  const [showBulkCreateModal, setShowBulkCreateModal] = useState(false);
  const [showCreatePartnerModal, setShowCreatePartnerModal] = useState(false);
  const [showBrandingModal, setShowBrandingModal] = useState(false);
  const [showEmailLogsModal, setShowEmailLogsModal] = useState(false);
  
  // Form Data State
  const [userFormData, setUserFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'Viewer',
    partner_organization_id: '',
    department: '',
    position: '',
    supervisor_id: '',
    access_level: 'standard',
    permissions: {},
    send_credentials_email: true,
    temporary_password: true
  });
  
  const [partnerFormData, setPartnerFormData] = useState({
    name: '',
    description: '',
    contact_person: '',
    contact_email: '',
    contact_phone: '',
    address: '',
    organization_type: 'NGO',
    partnership_start_date: '',
    partnership_end_date: '',
    website: '',
    capabilities: []
  });
  
  const [brandingData, setBrandingData] = useState({
    logo_url: '',
    primary_color: '#3B82F6',
    secondary_color: '#10B981',
    accent_color: '#8B5CF6',
    background_color: '#FFFFFF',
    text_color: '#1F2937',
    custom_css: '',
    white_label_enabled: false
  });
  
  const [emailLogs, setEmailLogs] = useState([]);
  const [bulkUsersData, setBulkUsersData] = useState([]);

  // User Roles and Permissions
  const userRoles = [
    'Admin', 'Editor', 'Viewer', 'Project Manager', 'M&E Officer', 
    'Donor Viewer', 'Director', 'Officer', 'Field Staff', 'Partner Staff', 'System Admin'
  ];
  
  const accessLevels = ['standard', 'elevated', 'restricted'];
  const organizationTypes = ['NGO', 'Government', 'Private', 'International'];
  
  const defaultPermissions = {
    view_dashboard: true,
    view_projects: true,
    view_activities: true,
    view_kpis: true,
    view_beneficiaries: true,
    view_documents: true,
    view_reports: true,
    create_projects: false,
    edit_projects: false,
    delete_projects: false,
    create_activities: false,
    edit_activities: false,
    delete_activities: false,
    create_users: false,
    edit_users: false,
    delete_users: false,
    manage_partners: false,
    view_financial_data: false,
    edit_financial_data: false,
    generate_reports: false,
    export_data: false,
    system_admin: false
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [usersRes, partnersRes] = await Promise.allSettled([
        usersAPI.getUsers(),
        partnersAPI.getPartners()
      ]);

      if (usersRes.status === 'fulfilled') {
        setUsers(usersRes.value.data);
      }

      if (partnersRes.status === 'fulfilled') {
        setPartners(partnersRes.value.data);
      }
    } catch (error) {
      console.error('Error fetching admin data:', error);
      setError('Failed to load admin panel data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (formData) => {
    try {
      setLoading(true);
      const response = await adminAPI.createUserAdvanced(formData);
      
      if (response.data.success) {
        setUsers(prev => [...prev, response.data.data.user]);
        setSuccess(`User created successfully. ${formData.send_credentials_email ? 'Credentials sent via email.' : `Password: ${response.data.data.password}`}`);
        setShowCreateUserModal(false);
        resetUserForm();
      }
    } catch (error) {
      console.error('Error creating user:', error);
      setError(error.response?.data?.detail || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  const handleBulkCreateUsers = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.bulkCreateUsers(bulkUsersData, true);
      
      if (response.data.success) {
        const { created_count, failed_count, created_users, failed_users } = response.data.data;
        setUsers(prev => [...prev, ...created_users.map(u => u.user)]);
        setSuccess(`Successfully created ${created_count} users. ${failed_count > 0 ? `${failed_count} failed.` : ''}`);
        
        if (failed_count > 0) {
          console.log('Failed users:', failed_users);
        }
        
        setShowBulkCreateModal(false);
        setBulkUsersData([]);
      }
    } catch (error) {
      console.error('Error bulk creating users:', error);
      setError(error.response?.data?.detail || 'Failed to create users');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePartner = async (formData) => {
    try {
      setLoading(true);
      const response = await partnersAPI.createPartner(formData);
      
      setPartners(prev => [...prev, response.data]);
      setSuccess('Partner organization created successfully');
      setShowCreatePartnerModal(false);
      resetPartnerForm();
    } catch (error) {
      console.error('Error creating partner:', error);
      setError(error.response?.data?.detail || 'Failed to create partner organization');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateBranding = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.updateBranding(brandingData);
      
      if (response.data.success) {
        setSuccess('Organization branding updated successfully');
        setShowBrandingModal(false);
      }
    } catch (error) {
      console.error('Error updating branding:', error);
      setError(error.response?.data?.detail || 'Failed to update branding');
    } finally {
      setLoading(false);
    }
  };

  const fetchEmailLogs = async () => {
    try {
      const response = await adminAPI.getEmailLogs();
      if (response.data.success) {
        setEmailLogs(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching email logs:', error);
      setError('Failed to fetch email logs');
    }
  };

  const resetUserForm = () => {
    setUserFormData({
      name: '',
      email: '',
      password: '',
      role: 'Viewer',
      partner_organization_id: '',
      department: '',
      position: '',
      supervisor_id: '',
      access_level: 'standard',
      permissions: {},
      send_credentials_email: true,
      temporary_password: true
    });
  };

  const resetPartnerForm = () => {
    setPartnerFormData({
      name: '',
      description: '',
      contact_person: '',
      contact_email: '',
      contact_phone: '',
      address: '',
      organization_type: 'NGO',
      partnership_start_date: '',
      partnership_end_date: '',
      website: '',
      capabilities: []
    });
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(userSearch.toLowerCase()) ||
                         user.email.toLowerCase().includes(userSearch.toLowerCase());
    const matchesFilter = userFilter === 'all' || user.role === userFilter;
    return matchesSearch && matchesFilter;
  });

  const filteredPartners = partners.filter(partner => {
    const matchesSearch = partner.name.toLowerCase().includes(partnerSearch.toLowerCase());
    const matchesFilter = partnerFilter === 'all' || partner.status === partnerFilter;
    return matchesSearch && matchesFilter;
  });

  // Permission update helper
  const updatePermission = (permission, value) => {
    setUserFormData(prev => ({
      ...prev,
      permissions: {
        ...prev.permissions,
        [permission]: value
      }
    }));
  };

  const StatCard = ({ title, value, icon, color = "blue", description }) => (
    <Card className="hover:shadow-lg transition-shadow duration-300">
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

  if (!user || !['Admin', 'Director', 'System Admin'].includes(user.role)) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Access denied. You need Admin, Director, or System Admin privileges to access this panel.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
          <p className="text-gray-600 mt-1">Manage users, partners, and system settings</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchData} disabled={loading}>
            {loading ? <Clock className="h-4 w-4 mr-2" /> : <BarChart3 className="h-4 w-4 mr-2" />}
            Refresh Data
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
          title="Total Users"
          value={users.length}
          icon={<Users className="h-5 w-5 text-blue-600" />}
          color="blue"
          description="Active system users"
        />
        <StatCard
          title="Partner Organizations"
          value={partners.length}
          icon={<Building2 className="h-5 w-5 text-green-600" />}
          color="green"
          description="Registered partners"
        />
        <StatCard
          title="Admin Users"
          value={users.filter(u => ['Admin', 'Director', 'System Admin'].includes(u.role)).length}
          icon={<Shield className="h-5 w-5 text-purple-600" />}
          color="purple"
          description="Privileged accounts"
        />
        <StatCard
          title="Active Partners"
          value={partners.filter(p => p.status === 'active').length}
          icon={<CheckCircle className="h-5 w-5 text-emerald-600" />}
          color="emerald"
          description="Currently active"
        />
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="users">User Management</TabsTrigger>
          <TabsTrigger value="partners">Partner Organizations</TabsTrigger>
          <TabsTrigger value="permissions">Roles & Permissions</TabsTrigger>
          <TabsTrigger value="branding">Organization Branding</TabsTrigger>
          <TabsTrigger value="system">System Settings</TabsTrigger>
        </TabsList>

        {/* User Management Tab */}
        <TabsContent value="users" className="space-y-6">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="flex gap-4 items-center flex-1">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search users..."
                  value={userSearch}
                  onChange={(e) => setUserSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={userFilter} onValueChange={setUserFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filter by role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Roles</SelectItem>
                  {userRoles.map(role => (
                    <SelectItem key={role} value={role}>{role}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2">
              <Dialog open={showBulkCreateModal} onOpenChange={setShowBulkCreateModal}>
                <DialogTrigger asChild>
                  <Button variant="outline">
                    <Upload className="h-4 w-4 mr-2" />
                    Bulk Create
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Bulk Create Users</DialogTitle>
                    <DialogDescription>
                      Create multiple users at once. Enter user data separated by new lines.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <Textarea
                      placeholder="Format: Name, Email, Role&#10;John Doe, john@example.com, Editor&#10;Jane Smith, jane@example.com, Viewer"
                      value={bulkUsersData.map(u => `${u.name}, ${u.email}, ${u.role}`).join('\n')}
                      onChange={(e) => {
                        const lines = e.target.value.split('\n').filter(line => line.trim());
                        const users = lines.map(line => {
                          const [name, email, role] = line.split(',').map(s => s.trim());
                          return { name, email, role: role || 'Viewer' };
                        });
                        setBulkUsersData(users);
                      }}
                      rows={8}
                    />
                    <div className="flex justify-between">
                      <Badge variant="outline">{bulkUsersData.length} users ready</Badge>
                      <div className="flex gap-2">
                        <Button variant="outline" onClick={() => setShowBulkCreateModal(false)}>
                          Cancel
                        </Button>
                        <Button onClick={handleBulkCreateUsers} disabled={bulkUsersData.length === 0 || loading}>
                          Create {bulkUsersData.length} Users
                        </Button>
                      </div>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>

              <Dialog open={showCreateUserModal} onOpenChange={setShowCreateUserModal}>
                <DialogTrigger asChild>
                  <Button>
                    <UserPlus className="h-4 w-4 mr-2" />
                    Create User
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>Create New User</DialogTitle>
                    <DialogDescription>
                      Create a new user with advanced settings and permissions.
                    </DialogDescription>
                  </DialogHeader>
                  <CreateUserForm
                    formData={userFormData}
                    setFormData={setUserFormData}
                    onSubmit={handleCreateUser}
                    partners={partners}
                    users={users}
                    loading={loading}
                    defaultPermissions={defaultPermissions}
                    updatePermission={updatePermission}
                  />
                </DialogContent>
              </Dialog>
            </div>
          </div>

          {/* Users Table */}
          <Card>
            <CardHeader>
              <CardTitle>Users ({filteredUsers.length})</CardTitle>
              <CardDescription>
                Manage user accounts and permissions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>User</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Last Login</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredUsers.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{user.name}</div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{user.role}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                          {user.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" className="text-red-600">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Partner Organizations Tab */}
        <TabsContent value="partners" className="space-y-6">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="flex gap-4 items-center flex-1">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search partners..."
                  value={partnerSearch}
                  onChange={(e) => setPartnerSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={partnerFilter} onValueChange={setPartnerFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                  <SelectItem value="suspended">Suspended</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Dialog open={showCreatePartnerModal} onOpenChange={setShowCreatePartnerModal}>
              <DialogTrigger asChild>
                <Button>
                  <Building2 className="h-4 w-4 mr-2" />
                  Add Partner
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Add Partner Organization</DialogTitle>
                  <DialogDescription>
                    Register a new partner organization for collaboration.
                  </DialogDescription>
                </DialogHeader>
                <CreatePartnerForm
                  formData={partnerFormData}
                  setFormData={setPartnerFormData}
                  onSubmit={handleCreatePartner}
                  loading={loading}
                />
              </DialogContent>
            </Dialog>
          </div>

          {/* Partners Table */}
          <Card>
            <CardHeader>
              <CardTitle>Partner Organizations ({filteredPartners.length})</CardTitle>
              <CardDescription>
                Manage partner organizations and collaborations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Organization</TableHead>
                    <TableHead>Contact</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPartners.map((partner) => (
                    <TableRow key={partner.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{partner.name}</div>
                          <div className="text-sm text-gray-500">{partner.description}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">{partner.contact_person}</div>
                          <div className="text-sm text-gray-500">{partner.contact_email}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{partner.organization_type}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={partner.status === 'active' ? 'default' : 'secondary'}>
                          {partner.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" className="text-red-600">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Roles & Permissions Tab */}
        <TabsContent value="permissions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Role-Based Access Control</CardTitle>
              <CardDescription>
                Configure permissions for different user roles
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Alert>
                  <Shield className="h-4 w-4" />
                  <AlertDescription>
                    Permission management is available for individual users during creation. 
                    Global role permissions are managed at the system level.
                  </AlertDescription>
                </Alert>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {userRoles.map(role => (
                    <Card key={role}>
                      <CardHeader>
                        <CardTitle className="text-lg">{role}</CardTitle>
                        <CardDescription>
                          {users.filter(u => u.role === role).length} users
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <Badge variant="outline">
                          System Managed
                        </Badge>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Organization Branding Tab */}
        <TabsContent value="branding" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Organization Branding</CardTitle>
              <CardDescription>
                Customize your organization's visual identity
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button onClick={() => setShowBrandingModal(true)}>
                  <Palette className="h-4 w-4 mr-2" />
                  Update Branding
                </Button>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-8 h-8 rounded border"
                      style={{ backgroundColor: brandingData.primary_color }}
                    />
                    <span className="text-sm">Primary Color</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-8 h-8 rounded border"
                      style={{ backgroundColor: brandingData.secondary_color }}
                    />
                    <span className="text-sm">Secondary Color</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-8 h-8 rounded border"
                      style={{ backgroundColor: brandingData.accent_color }}
                    />
                    <span className="text-sm">Accent Color</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Dialog open={showBrandingModal} onOpenChange={setShowBrandingModal}>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Update Organization Branding</DialogTitle>
                <DialogDescription>
                  Customize colors, logos, and visual elements
                </DialogDescription>
              </DialogHeader>
              <BrandingForm
                brandingData={brandingData}
                setBrandingData={setBrandingData}
                onSubmit={handleUpdateBranding}
                loading={loading}
              />
            </DialogContent>
          </Dialog>
        </TabsContent>

        {/* System Settings Tab */}
        <TabsContent value="system" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Email System</CardTitle>
                <CardDescription>
                  Monitor email delivery and logs
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={() => {
                  setShowEmailLogsModal(true);
                  fetchEmailLogs();
                }}>
                  <Mail className="h-4 w-4 mr-2" />
                  View Email Logs
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>System Health</CardTitle>
                <CardDescription>
                  Monitor system performance and status
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Database</span>
                    <Badge className="bg-green-100 text-green-800">Healthy</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">API Services</span>
                    <Badge className="bg-green-100 text-green-800">Running</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Storage</span>
                    <Badge className="bg-yellow-100 text-yellow-800">85% Used</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Dialog open={showEmailLogsModal} onOpenChange={setShowEmailLogsModal}>
            <DialogContent className="max-w-4xl">
              <DialogHeader>
                <DialogTitle>Email Logs</DialogTitle>
                <DialogDescription>
                  Recent email delivery history
                </DialogDescription>
              </DialogHeader>
              <div className="max-h-96 overflow-y-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Recipient</TableHead>
                      <TableHead>Subject</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Sent</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {emailLogs.map((log) => (
                      <TableRow key={log.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{log.recipient_name}</div>
                            <div className="text-sm text-gray-500">{log.recipient_email}</div>
                          </div>
                        </TableCell>
                        <TableCell>{log.subject}</TableCell>
                        <TableCell>
                          <Badge variant={log.status === 'sent' ? 'default' : 'destructive'}>
                            {log.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {log.sent_at ? new Date(log.sent_at).toLocaleString() : '-'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </DialogContent>
          </Dialog>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Create User Form Component
const CreateUserForm = ({ 
  formData, 
  setFormData, 
  onSubmit, 
  partners, 
  users, 
  loading, 
  defaultPermissions, 
  updatePermission 
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const supervisors = users.filter(u => 
    ['Admin', 'Director', 'Project Manager', 'M&E Officer'].includes(u.role)
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="name">Full Name *</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">Email Address *</Label>
          <Input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="role">Role *</Label>
          <Select value={formData.role} onValueChange={(value) => setFormData(prev => ({ ...prev, role: value }))}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {['Admin', 'Editor', 'Viewer', 'Project Manager', 'M&E Officer', 'Donor Viewer', 'Director', 'Officer', 'Field Staff', 'Partner Staff'].map(role => (
                <SelectItem key={role} value={role}>{role}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="access_level">Access Level</Label>
          <Select value={formData.access_level} onValueChange={(value) => setFormData(prev => ({ ...prev, access_level: value }))}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="standard">Standard</SelectItem>
              <SelectItem value="elevated">Elevated</SelectItem>
              <SelectItem value="restricted">Restricted</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="department">Department</Label>
          <Input
            id="department"
            value={formData.department}
            onChange={(e) => setFormData(prev => ({ ...prev, department: e.target.value }))}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="position">Position</Label>
          <Input
            id="position"
            value={formData.position}
            onChange={(e) => setFormData(prev => ({ ...prev, position: e.target.value }))}
          />
        </div>
      </div>

      {partners.length > 0 && (
        <div className="space-y-2">
          <Label htmlFor="partner_organization_id">Partner Organization</Label>
          <Select value={formData.partner_organization_id} onValueChange={(value) => setFormData(prev => ({ ...prev, partner_organization_id: value }))}>
            <SelectTrigger>
              <SelectValue placeholder="Select partner (optional)" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">None</SelectItem>
              {partners.map(partner => (
                <SelectItem key={partner.id} value={partner.id}>{partner.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      {supervisors.length > 0 && (
        <div className="space-y-2">
          <Label htmlFor="supervisor_id">Supervisor</Label>
          <Select value={formData.supervisor_id} onValueChange={(value) => setFormData(prev => ({ ...prev, supervisor_id: value }))}>
            <SelectTrigger>
              <SelectValue placeholder="Select supervisor (optional)" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">None</SelectItem>
              {supervisors.map(supervisor => (
                <SelectItem key={supervisor.id} value={supervisor.id}>{supervisor.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor="password">Password (leave empty for auto-generated)</Label>
        <Input
          id="password"
          type="password"
          value={formData.password}
          onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
          placeholder="Auto-generated if empty"
        />
      </div>

      <div className="flex items-center space-x-2">
        <Checkbox
          id="send_credentials_email"
          checked={formData.send_credentials_email}
          onCheckedChange={(checked) => setFormData(prev => ({ ...prev, send_credentials_email: checked }))}
        />
        <Label htmlFor="send_credentials_email">Send credentials via email</Label>
      </div>

      <div className="flex items-center space-x-2">
        <Checkbox
          id="temporary_password"
          checked={formData.temporary_password}
          onCheckedChange={(checked) => setFormData(prev => ({ ...prev, temporary_password: checked }))}
        />
        <Label htmlFor="temporary_password">Force password change on first login</Label>
      </div>

      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" onClick={() => setFormData(prev => ({ ...prev, name: '', email: '', password: '' }))}>
          Reset
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? <Clock className="h-4 w-4 mr-2" /> : <UserPlus className="h-4 w-4 mr-2" />}
          Create User
        </Button>
      </div>
    </form>
  );
};

// Create Partner Form Component
const CreatePartnerForm = ({ formData, setFormData, onSubmit, loading }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="name">Organization Name *</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="organization_type">Organization Type *</Label>
          <Select value={formData.organization_type} onValueChange={(value) => setFormData(prev => ({ ...prev, organization_type: value }))}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="NGO">NGO</SelectItem>
              <SelectItem value="Government">Government</SelectItem>
              <SelectItem value="Private">Private</SelectItem>
              <SelectItem value="International">International</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          rows={3}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="contact_person">Contact Person *</Label>
          <Input
            id="contact_person"
            value={formData.contact_person}
            onChange={(e) => setFormData(prev => ({ ...prev, contact_person: e.target.value }))}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="contact_email">Contact Email *</Label>
          <Input
            id="contact_email"
            type="email"
            value={formData.contact_email}
            onChange={(e) => setFormData(prev => ({ ...prev, contact_email: e.target.value }))}
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="contact_phone">Contact Phone</Label>
          <Input
            id="contact_phone"
            value={formData.contact_phone}
            onChange={(e) => setFormData(prev => ({ ...prev, contact_phone: e.target.value }))}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="website">Website</Label>
          <Input
            id="website"
            value={formData.website}
            onChange={(e) => setFormData(prev => ({ ...prev, website: e.target.value }))}
            placeholder="https://"
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="address">Address</Label>
        <Textarea
          id="address"
          value={formData.address}
          onChange={(e) => setFormData(prev => ({ ...prev, address: e.target.value }))}
          rows={2}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="partnership_start_date">Partnership Start Date *</Label>
          <Input
            id="partnership_start_date"
            type="date"
            value={formData.partnership_start_date}
            onChange={(e) => setFormData(prev => ({ ...prev, partnership_start_date: e.target.value }))}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="partnership_end_date">Partnership End Date</Label>
          <Input
            id="partnership_end_date"
            type="date"
            value={formData.partnership_end_date}
            onChange={(e) => setFormData(prev => ({ ...prev, partnership_end_date: e.target.value }))}
          />
        </div>
      </div>

      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" onClick={() => setFormData({
          name: '', description: '', contact_person: '', contact_email: '', 
          contact_phone: '', address: '', organization_type: 'NGO', 
          partnership_start_date: '', partnership_end_date: '', website: '', capabilities: []
        })}>
          Reset
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? <Clock className="h-4 w-4 mr-2" /> : <Building2 className="h-4 w-4 mr-2" />}
          Create Partner
        </Button>
      </div>
    </form>
  );
};

// Branding Form Component
const BrandingForm = ({ brandingData, setBrandingData, onSubmit, loading }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="logo_url">Logo URL</Label>
          <Input
            id="logo_url"
            value={brandingData.logo_url}
            onChange={(e) => setBrandingData(prev => ({ ...prev, logo_url: e.target.value }))}
            placeholder="https://example.com/logo.png"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="primary_color">Primary Color</Label>
          <Input
            id="primary_color"
            type="color"
            value={brandingData.primary_color}
            onChange={(e) => setBrandingData(prev => ({ ...prev, primary_color: e.target.value }))}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="secondary_color">Secondary Color</Label>
          <Input
            id="secondary_color"
            type="color"
            value={brandingData.secondary_color}
            onChange={(e) => setBrandingData(prev => ({ ...prev, secondary_color: e.target.value }))}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="accent_color">Accent Color</Label>
          <Input
            id="accent_color"
            type="color"
            value={brandingData.accent_color}
            onChange={(e) => setBrandingData(prev => ({ ...prev, accent_color: e.target.value }))}
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="custom_css">Custom CSS</Label>
        <Textarea
          id="custom_css"
          value={brandingData.custom_css}
          onChange={(e) => setBrandingData(prev => ({ ...prev, custom_css: e.target.value }))}
          rows={4}
          placeholder="/* Custom CSS styles */"
        />
      </div>

      <div className="flex items-center space-x-2">
        <Switch
          id="white_label_enabled"
          checked={brandingData.white_label_enabled}
          onCheckedChange={(checked) => setBrandingData(prev => ({ ...prev, white_label_enabled: checked }))}
        />
        <Label htmlFor="white_label_enabled">Enable White Label Mode</Label>
      </div>

      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" onClick={() => setShowBrandingModal(false)}>
          Cancel
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? <Clock className="h-4 w-4 mr-2" /> : <Palette className="h-4 w-4 mr-2" />}
          Update Branding
        </Button>
      </div>
    </form>
  );
};

export default AdminPanel;