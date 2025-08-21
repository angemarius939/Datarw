import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Switch } from './ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { 
  Users, 
  Shield, 
  Plus, 
  Mail, 
  Settings, 
  Palette,
  Building,
  UserPlus,
  FileText,
  Loader2,
  Check,
  X,
  Eye,
  EyeOff,
  Upload
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';

const AdminPanel = () => {
  const { user, organization } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);
  const [partners, setPartners] = useState([]);
  const [emailLogs, setEmailLogs] = useState([]);
  const [branding, setBranding] = useState(null);

  // User Creation State
  const [createUserOpen, setCreateUserOpen] = useState(false);
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    role: 'Field Staff',
    department: '',
    position: '',
    send_credentials_email: true,
    temporary_password: true
  });

  // Partner Organization State
  const [createPartnerOpen, setCreatePartnerOpen] = useState(false);
  const [newPartner, setNewPartner] = useState({
    name: '',
    description: '',
    contact_person: '',
    contact_email: '',
    contact_phone: '',
    address: '',
    organization_type: 'NGO',
    partnership_start_date: '',
    website: '',
    capabilities: []
  });

  // Branding State
  const [brandingOpen, setBrandingOpen] = useState(false);
  const [brandingData, setBrandingData] = useState({
    primary_color: '#3B82F6',
    secondary_color: '#10B981',
    accent_color: '#8B5CF6',
    white_label_enabled: false
  });

  const roles = [
    'Director', 'Officer', 'Project Manager', 'M&E Officer', 
    'Field Staff', 'Partner Staff', 'Donor Viewer'
  ];

  const organizationTypes = ['NGO', 'Government', 'Private', 'International'];

  useEffect(() => {
    fetchUsers();
    fetchPartners();
    fetchEmailLogs();
    fetchBranding();
  }, []);

  const fetchUsers = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${backendUrl}/api/users`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const usersData = await response.json();
        setUsers(usersData);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchPartners = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${backendUrl}/api/admin/partners`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const partnersData = await response.json();
        setPartners(partnersData);
      }
    } catch (error) {
      console.error('Error fetching partners:', error);
    }
  };

  const fetchEmailLogs = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${backendUrl}/api/admin/email-logs`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setEmailLogs(data.data || []);
      }
    } catch (error) {
      console.error('Error fetching email logs:', error);
    }
  };

  const fetchBranding = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${backendUrl}/api/admin/branding`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.data) {
          setBranding(data.data);
          setBrandingData(data.data);
        }
      }
    } catch (error) {
      console.error('Error fetching branding:', error);
    }
  };

  const handleCreateUser = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${backendUrl}/api/admin/users/create-advanced`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newUser)
      });

      if (response.ok) {
        const result = await response.json();
        
        toast({
          title: "User Created Successfully!",
          description: `${newUser.name} has been added with role: ${newUser.role}${result.data.credentials_sent ? '. Credentials sent via email.' : ''}`,
          variant: "default",
        });
        
        setCreateUserOpen(false);
        setNewUser({
          name: '',
          email: '',
          role: 'Field Staff',
          department: '',
          position: '',
          send_credentials_email: true,
          temporary_password: true
        });
        
        fetchUsers();
        fetchEmailLogs();
      } else {
        throw new Error('Failed to create user');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create user. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePartner = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');
      
      const partnerData = {
        ...newPartner,
        partnership_start_date: new Date(newPartner.partnership_start_date).toISOString()
      };
      
      const response = await fetch(`${backendUrl}/api/admin/partners`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(partnerData)
      });

      if (response.ok) {
        toast({
          title: "Partner Organization Created!",
          description: `${newPartner.name} has been added as a partner organization.`,
          variant: "default",
        });
        
        setCreatePartnerOpen(false);
        setNewPartner({
          name: '',
          description: '',
          contact_person: '',
          contact_email: '',
          contact_phone: '',
          address: '',
          organization_type: 'NGO',
          partnership_start_date: '',
          website: '',
          capabilities: []
        });
        
        fetchPartners();
      } else {
        throw new Error('Failed to create partner');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create partner organization. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateBranding = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${backendUrl}/api/admin/branding`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(brandingData)
      });

      if (response.ok) {
        toast({
          title: "Branding Updated!",
          description: "Organization branding has been updated successfully.",
          variant: "default",
        });
        
        setBrandingOpen(false);
        fetchBranding();
      } else {
        throw new Error('Failed to update branding');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update branding. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getRoleBadgeColor = (role) => {
    const colors = {
      'Director': 'bg-red-100 text-red-800',
      'Officer': 'bg-blue-100 text-blue-800',
      'Project Manager': 'bg-green-100 text-green-800',
      'M&E Officer': 'bg-purple-100 text-purple-800',
      'Field Staff': 'bg-yellow-100 text-yellow-800',
      'Partner Staff': 'bg-orange-100 text-orange-800',
      'Donor Viewer': 'bg-gray-100 text-gray-800'
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
          <p className="text-gray-600">Manage users, partners, and organization settings</p>
        </div>
        <div className="flex space-x-2">
          <Dialog open={createUserOpen} onOpenChange={setCreateUserOpen}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-blue-600 to-purple-600">
                <UserPlus className="h-4 w-4 mr-2" />
                Create User
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New User</DialogTitle>
                <DialogDescription>
                  Add a new user to your organization with automatic credential generation.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="user-name">Full Name *</Label>
                    <Input
                      id="user-name"
                      value={newUser.name}
                      onChange={(e) => setNewUser(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="Enter full name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="user-email">Email Address *</Label>
                    <Input
                      id="user-email"
                      type="email"
                      value={newUser.email}
                      onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
                      placeholder="user@organization.com"
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="user-role">Role *</Label>
                    <Select value={newUser.role} onValueChange={(value) => setNewUser(prev => ({ ...prev, role: value }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {roles.map(role => (
                          <SelectItem key={role} value={role}>{role}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="user-department">Department</Label>
                    <Input
                      id="user-department"
                      value={newUser.department}
                      onChange={(e) => setNewUser(prev => ({ ...prev, department: e.target.value }))}
                      placeholder="e.g., Operations, M&E, Finance"
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="user-position">Position/Title</Label>
                  <Input
                    id="user-position"
                    value={newUser.position}
                    onChange={(e) => setNewUser(prev => ({ ...prev, position: e.target.value }))}
                    placeholder="e.g., Senior Program Officer"
                  />
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={newUser.send_credentials_email}
                      onCheckedChange={(checked) => setNewUser(prev => ({ ...prev, send_credentials_email: checked }))}
                    />
                    <Label>Send credentials via email</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={newUser.temporary_password}
                      onCheckedChange={(checked) => setNewUser(prev => ({ ...prev, temporary_password: checked }))}
                    />
                    <Label>Require password change</Label>
                  </div>
                </div>
              </div>
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setCreateUserOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateUser} disabled={loading}>
                  {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <UserPlus className="h-4 w-4 mr-2" />}
                  Create User
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Tabs defaultValue="users" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="users">User Management</TabsTrigger>
          <TabsTrigger value="partners">Partner Organizations</TabsTrigger>
          <TabsTrigger value="branding">Branding</TabsTrigger>
          <TabsTrigger value="emails">Email Logs</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* User Management Tab */}
        <TabsContent value="users">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="h-5 w-5 mr-2" />
                Organization Users ({users.length})
              </CardTitle>
              <CardDescription>
                Manage user accounts, roles, and permissions for your organization.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {users.map((user) => (
                  <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <div>
                          <h4 className="font-medium">{user.name}</h4>
                          <p className="text-sm text-gray-600">{user.email}</p>
                        </div>
                        <Badge className={getRoleBadgeColor(user.role)}>
                          {user.role}
                        </Badge>
                        {user.is_active ? (
                          <Badge variant="success">Active</Badge>
                        ) : (
                          <Badge variant="secondary">Inactive</Badge>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button size="sm" variant="outline">
                        Edit
                      </Button>
                      <Button size="sm" variant="outline">
                        {user.is_active ? 'Deactivate' : 'Activate'}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Partner Organizations Tab */}
        <TabsContent value="partners">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center">
                    <Building className="h-5 w-5 mr-2" />
                    Partner Organizations ({partners.length})
                  </CardTitle>
                  <CardDescription>
                    Manage partner organizations and track their performance.
                  </CardDescription>
                </div>
                <Dialog open={createPartnerOpen} onOpenChange={setCreatePartnerOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      Add Partner
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Add Partner Organization</DialogTitle>
                      <DialogDescription>
                        Create a new partner organization for collaboration.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="partner-name">Organization Name *</Label>
                          <Input
                            id="partner-name"
                            value={newPartner.name}
                            onChange={(e) => setNewPartner(prev => ({ ...prev, name: e.target.value }))}
                            placeholder="Partner Organization Name"
                          />
                        </div>
                        <div>
                          <Label htmlFor="partner-type">Organization Type</Label>
                          <Select value={newPartner.organization_type} onValueChange={(value) => setNewPartner(prev => ({ ...prev, organization_type: value }))}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {organizationTypes.map(type => (
                                <SelectItem key={type} value={type}>{type}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      
                      <div>
                        <Label htmlFor="partner-description">Description</Label>
                        <Textarea
                          id="partner-description"
                          value={newPartner.description}
                          onChange={(e) => setNewPartner(prev => ({ ...prev, description: e.target.value }))}
                          placeholder="Brief description of the partner organization..."
                          rows={3}
                        />
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="contact-person">Contact Person *</Label>
                          <Input
                            id="contact-person"
                            value={newPartner.contact_person}
                            onChange={(e) => setNewPartner(prev => ({ ...prev, contact_person: e.target.value }))}
                            placeholder="Primary contact name"
                          />
                        </div>
                        <div>
                          <Label htmlFor="contact-email">Contact Email *</Label>
                          <Input
                            id="contact-email"
                            type="email"
                            value={newPartner.contact_email}
                            onChange={(e) => setNewPartner(prev => ({ ...prev, contact_email: e.target.value }))}
                            placeholder="contact@partner.org"
                          />
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="partnership-start">Partnership Start Date</Label>
                          <Input
                            id="partnership-start"
                            type="date"
                            value={newPartner.partnership_start_date}
                            onChange={(e) => setNewPartner(prev => ({ ...prev, partnership_start_date: e.target.value }))}
                          />
                        </div>
                        <div>
                          <Label htmlFor="partner-website">Website</Label>
                          <Input
                            id="partner-website"
                            value={newPartner.website}
                            onChange={(e) => setNewPartner(prev => ({ ...prev, website: e.target.value }))}
                            placeholder="https://partner.org"
                          />
                        </div>
                      </div>
                    </div>
                    <div className="flex justify-end space-x-2">
                      <Button variant="outline" onClick={() => setCreatePartnerOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={handleCreatePartner} disabled={loading}>
                        {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Plus className="h-4 w-4 mr-2" />}
                        Add Partner
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {partners.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Building className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>No partner organizations yet</p>
                    <p className="text-sm">Add partners to track collaboration and performance</p>
                  </div>
                ) : (
                  partners.map((partner) => (
                    <div key={partner.id || partner._id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">{partner.name}</h4>
                          <p className="text-sm text-gray-600">{partner.organization_type} • {partner.contact_person}</p>
                          <p className="text-sm text-gray-500">{partner.contact_email}</p>
                        </div>
                        <Badge variant={partner.status === 'active' ? 'success' : 'secondary'}>
                          {partner.status}
                        </Badge>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Branding Tab */}
        <TabsContent value="branding">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Palette className="h-5 w-5 mr-2" />
                Organization Branding
              </CardTitle>
              <CardDescription>
                Customize your organization's branding and visual identity.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="primary-color">Primary Color</Label>
                    <div className="flex items-center space-x-2 mt-1">
                      <Input
                        id="primary-color"
                        type="color"
                        value={brandingData.primary_color}
                        onChange={(e) => setBrandingData(prev => ({ ...prev, primary_color: e.target.value }))}
                        className="w-16 h-10"
                      />
                      <Input
                        value={brandingData.primary_color}
                        onChange={(e) => setBrandingData(prev => ({ ...prev, primary_color: e.target.value }))}
                        placeholder="#3B82F6"
                        className="flex-1"
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="secondary-color">Secondary Color</Label>
                    <div className="flex items-center space-x-2 mt-1">
                      <Input
                        id="secondary-color"
                        type="color"
                        value={brandingData.secondary_color}
                        onChange={(e) => setBrandingData(prev => ({ ...prev, secondary_color: e.target.value }))}
                        className="w-16 h-10"
                      />
                      <Input
                        value={brandingData.secondary_color}
                        onChange={(e) => setBrandingData(prev => ({ ...prev, secondary_color: e.target.value }))}
                        placeholder="#10B981"
                        className="flex-1"
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="accent-color">Accent Color</Label>
                    <div className="flex items-center space-x-2 mt-1">
                      <Input
                        id="accent-color"
                        type="color"
                        value={brandingData.accent_color}
                        onChange={(e) => setBrandingData(prev => ({ ...prev, accent_color: e.target.value }))}
                        className="w-16 h-10"
                      />
                      <Input
                        value={brandingData.accent_color}
                        onChange={(e) => setBrandingData(prev => ({ ...prev, accent_color: e.target.value }))}
                        placeholder="#8B5CF6"
                        className="flex-1"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    checked={brandingData.white_label_enabled}
                    onCheckedChange={(checked) => setBrandingData(prev => ({ ...prev, white_label_enabled: checked }))}
                  />
                  <Label>Enable White Label Mode</Label>
                  <p className="text-sm text-gray-500 ml-2">(Remove DataRW branding)</p>
                </div>

                <div className="pt-4 border-t">
                  <Button onClick={handleUpdateBranding} disabled={loading}>
                    {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Palette className="h-4 w-4 mr-2" />}
                    Update Branding
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Email Logs Tab */}
        <TabsContent value="emails">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Mail className="h-5 w-5 mr-2" />
                Email Logs ({emailLogs.length})
              </CardTitle>
              <CardDescription>
                Track all emails sent by the system including user credentials.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {emailLogs.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Mail className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>No emails sent yet</p>
                    <p className="text-sm">Email logs will appear here when users are created</p>
                  </div>
                ) : (
                  emailLogs.map((log, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">{log.subject}</h4>
                          <p className="text-sm text-gray-600">To: {log.recipient_name} ({log.recipient_email})</p>
                          <p className="text-sm text-gray-500">
                            {new Date(log.sent_at || log.created_at).toLocaleString()}
                          </p>
                        </div>
                        <Badge variant={log.status === 'sent' ? 'success' : log.status === 'failed' ? 'destructive' : 'secondary'}>
                          {log.status}
                        </Badge>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="h-5 w-5 mr-2" />
                System Settings
              </CardTitle>
              <CardDescription>
                Configure system-wide settings and preferences.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <Alert>
                  <Shield className="h-4 w-4" />
                  <AlertDescription>
                    Advanced system settings are available. Contact your system administrator for configuration changes.
                  </AlertDescription>
                </Alert>
                
                <div className="text-center py-8 text-gray-500">
                  <Settings className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>Additional settings coming soon</p>
                  <p className="text-sm">More configuration options will be available in future updates</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminPanel;