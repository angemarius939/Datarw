import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Mail, 
  Shield, 
  ShieldCheck, 
  Eye,
  MoreHorizontal,
  UserPlus
} from 'lucide-react';
import { mockUsers } from '../mock/mockData';

const UserManagement = () => {
  const [users, setUsers] = useState(mockUsers);
  const [isAddUserOpen, setIsAddUserOpen] = useState(false);
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    role: 'Viewer'
  });

  const roles = [
    { 
      value: 'Admin', 
      label: 'Admin', 
      description: 'Full access to all features',
      icon: <ShieldCheck className="h-4 w-4 text-red-600" />,
      color: 'bg-red-100 text-red-800 border-red-200'
    },
    { 
      value: 'Editor', 
      label: 'Editor', 
      description: 'Can create and edit surveys',
      icon: <Edit className="h-4 w-4 text-blue-600" />,
      color: 'bg-blue-100 text-blue-800 border-blue-200'
    },
    { 
      value: 'Viewer', 
      label: 'Viewer', 
      description: 'View-only access to data',
      icon: <Eye className="h-4 w-4 text-green-600" />,
      color: 'bg-green-100 text-green-800 border-green-200'
    }
  ];

  const handleAddUser = () => {
    const user = {
      id: `user_${Date.now()}`,
      ...newUser,
      status: 'pending',
      lastLogin: null,
      surveysCreated: 0
    };
    
    setUsers(prev => [...prev, user]);
    setNewUser({ name: '', email: '', role: 'Viewer' });
    setIsAddUserOpen(false);
  };

  const handleUpdateUserRole = (userId, newRole) => {
    setUsers(prev => prev.map(user => 
      user.id === userId ? { ...user, role: newRole } : user
    ));
  };

  const handleDeleteUser = (userId) => {
    setUsers(prev => prev.filter(user => user.id !== userId));
  };

  const getRoleInfo = (role) => {
    return roles.find(r => r.value === role) || roles[2];
  };

  const UserCard = ({ user }) => {
    const roleInfo = getRoleInfo(user.role);
    
    return (
      <Card className="hover:shadow-md transition-shadow duration-200">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Avatar>
                <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.name}`} />
                <AvatarFallback>{user.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
              </Avatar>
              <div>
                <CardTitle className="text-lg">{user.name}</CardTitle>
                <CardDescription className="flex items-center space-x-1">
                  <Mail className="h-3 w-3" />
                  <span>{user.email}</span>
                </CardDescription>
              </div>
            </div>
            <Badge className={roleInfo.color}>
              {roleInfo.icon}
              <span className="ml-1">{user.role}</span>
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Status:</span>
              <Badge 
                variant={user.status === 'active' ? 'default' : 'secondary'}
                className="ml-2"
              >
                {user.status}
              </Badge>
            </div>
            <div>
              <span className="text-gray-600">Surveys Created:</span>
              <span className="ml-2 font-medium">{user.surveysCreated}</span>
            </div>
            <div className="col-span-2">
              <span className="text-gray-600">Last Login:</span>
              <span className="ml-2">
                {user.lastLogin 
                  ? new Date(user.lastLogin).toLocaleDateString()
                  : 'Never'
                }
              </span>
            </div>
          </div>
          <div className="flex gap-2 mt-4">
            <Select
              value={user.role}
              onValueChange={(value) => handleUpdateUserRole(user.id, value)}
            >
              <SelectTrigger className="flex-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {roles.map(role => (
                  <SelectItem key={role.value} value={role.value}>
                    <div className="flex items-center space-x-2">
                      {role.icon}
                      <span>{role.label}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleDeleteUser(user.id)}
              className="text-red-600 hover:text-red-700"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600 mt-1">Manage team members and their access levels</p>
        </div>
        <Dialog open={isAddUserOpen} onOpenChange={setIsAddUserOpen}>
          <DialogTrigger asChild>
            <Button className="bg-gradient-to-r from-blue-600 to-purple-600">
              <UserPlus className="h-4 w-4 mr-2" />
              Add User
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New User</DialogTitle>
              <DialogDescription>
                Invite a new team member to your organization
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="user-name">Full Name</Label>
                <Input
                  id="user-name"
                  value={newUser.name}
                  onChange={(e) => setNewUser(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter user's full name"
                />
              </div>
              <div>
                <Label htmlFor="user-email">Email Address</Label>
                <Input
                  id="user-email"
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="Enter user's email"
                />
              </div>
              <div>
                <Label htmlFor="user-role">Role</Label>
                <Select
                  value={newUser.role}
                  onValueChange={(value) => setNewUser(prev => ({ ...prev, role: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {roles.map(role => (
                      <SelectItem key={role.value} value={role.value}>
                        <div className="flex items-center space-x-2">
                          {role.icon}
                          <div>
                            <span className="font-medium">{role.label}</span>
                            <p className="text-xs text-gray-500">{role.description}</p>
                          </div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex justify-end space-x-2 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setIsAddUserOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleAddUser}
                  disabled={!newUser.name || !newUser.email}
                >
                  Add User
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Role Overview */}
      <div className="grid md:grid-cols-3 gap-4">
        {roles.map(role => (
          <Card key={role.value}>
            <CardHeader>
              <div className="flex items-center space-x-2">
                {role.icon}
                <CardTitle className="text-lg">{role.label}</CardTitle>
              </div>
              <CardDescription>{role.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {users.filter(user => user.role === role.value).length}
              </div>
              <p className="text-sm text-gray-600">users with this role</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Users Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {users.map(user => (
          <UserCard key={user.id} user={user} />
        ))}
      </div>

      {/* Users Table (Alternative View) */}
      <Card>
        <CardHeader>
          <CardTitle>All Users</CardTitle>
          <CardDescription>Complete list of team members</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Surveys</TableHead>
                <TableHead>Last Login</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map(user => {
                const roleInfo = getRoleInfo(user.role);
                return (
                  <TableRow key={user.id}>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <Avatar className="h-8 w-8">
                          <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.name}`} />
                          <AvatarFallback className="text-xs">
                            {user.name.split(' ').map(n => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium">{user.name}</div>
                          <div className="text-sm text-gray-600">{user.email}</div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={roleInfo.color}>
                        {roleInfo.icon}
                        <span className="ml-1">{user.role}</span>
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                        {user.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{user.surveysCreated}</TableCell>
                    <TableCell>
                      {user.lastLogin 
                        ? new Date(user.lastLogin).toLocaleDateString()
                        : 'Never'
                      }
                    </TableCell>
                    <TableCell>
                      <Button size="sm" variant="outline">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default UserManagement;