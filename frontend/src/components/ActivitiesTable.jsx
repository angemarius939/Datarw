import React, { useEffect, useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Checkbox } from './ui/checkbox';
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from './ui/pagination';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { projectsAPI, usersAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { Calendar, Filter, Download, RefreshCcw, Search } from 'lucide-react';
import { format } from 'date-fns';
import * as XLSX from 'xlsx';

const statusColors = {
  completed: 'bg-green-100 text-green-800 border-green-200',
  in_progress: 'bg-blue-100 text-blue-800 border-blue-200',
  delayed: 'bg-red-100 text-red-800 border-red-200',
  not_started: 'bg-gray-100 text-gray-800 border-gray-200',
  cancelled: 'bg-gray-100 text-gray-800 border-gray-200'
};

const riskColors = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-red-100 text-red-800',
  critical: 'bg-purple-100 text-purple-800'
};

const DEFAULT_COLUMNS = [
  { key: 'name', label: 'Activity', default: true },
  { key: 'project', label: 'Project', default: true },
  { key: 'assigned', label: 'Assigned', default: true },
  { key: 'team', label: 'Team', default: true },
  { key: 'status', label: 'Status', default: true },
  { key: 'risk', label: 'Risk', default: true },
  { key: 'start', label: 'Start', default: true },
  { key: 'end', label: 'End', default: true },
  { key: 'progress', label: 'Progress %', default: true },
  { key: 'target', label: 'Target', default: true },
  { key: 'achieved', label: 'Achieved', default: true },
  { key: 'budget', label: 'Budget', default: true },
  { key: 'schedule_var', label: 'Sched Var (d)', default: true },
  { key: 'completion_var', label: 'Compl Var %', default: true },
  { key: 'updated', label: 'Updated', default: true }
];

const ActivitiesTable = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [visibleCols, setVisibleCols] = useState(() => {
    const saved = localStorage.getItem('activities_table_columns');
    if (saved) return JSON.parse(saved);
    const def = {};
    DEFAULT_COLUMNS.forEach(c => { def[c.key] = c.default; });
    return def;
  });
  const [selectedRows, setSelectedRows] = useState({});
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const [activities, setActivities] = useState([]);
  const [projects, setProjects] = useState([]);
  const [users, setUsers] = useState([]);

  // Filters
  const [search, setSearch] = useState('');
  const [projectId, setProjectId] = useState('all');
  const [status, setStatus] = useState('all');
  const [risk, setRisk] = useState('all');
  const [team, setTeam] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const [actsRes, projsRes, usersRes] = await Promise.all([
          projectsAPI.getActivities(),
          projectsAPI.getProjects(),
          usersAPI.getUsers()
        ]);
        setActivities(actsRes.data);
        setProjects(projsRes.data);
        setUsers(usersRes.data);
      } catch (e) {
        console.error('Failed to load activities table data', e);
        toast({ title: 'Error', description: 'Failed to load activities data', variant: 'destructive' });
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const userById = useMemo(() => {
    const map = {};
    (users || []).forEach(u => { map[u.id] = u; });
    return map;
  }, [users]);

  const projectById = useMemo(() => {
    const map = {};
    (projects || []).forEach(p => { map[p.id || p._id] = p; map[p._id] = p; });
    return map;
  }, [projects]);

  const teams = useMemo(() => {
    // derive from activities + presets
    const preset = ['M&E', 'Field', 'Data', 'Operations'];
    const found = new Set(preset);
    activities.forEach(a => { if (a.assigned_team) found.add(a.assigned_team); });
    return Array.from(found);
  }, [activities]);

  // Per-column filters
  const [descFilter, setDescFilter] = useState('');
  const [minBudget, setMinBudget] = useState('');
  const [maxBudget, setMaxBudget] = useState('');

  const filtered = useMemo(() => {
    const s = search.trim().toLowerCase();
    const from = dateFrom ? new Date(dateFrom) : null;
    const to = dateTo ? new Date(dateTo) : null;
    return (activities || []).filter(a => {
      if (projectId !== 'all' && a.project_id !== projectId) return false;
      if (status !== 'all' && a.status !== status) return false;
      if (risk !== 'all' && a.risk_level !== risk) return false;
      if (team !== 'all' && (a.assigned_team || '') !== team) return false;
      if (s && !(`${a.name || ''} ${a.description || ''}`.toLowerCase().includes(s))) return false;
      if (descFilter && !(a.description || '').toLowerCase().includes(descFilter.toLowerCase())) return false;
      const budget = Number(a.budget_allocated || 0);
      if (minBudget !== '' && budget < Number(minBudget)) return false;
      if (maxBudget !== '' && budget > Number(maxBudget)) return false;
      if (from) {
        const sd = a.start_date ? new Date(a.start_date) : null;
        if (sd && sd < from) return false;
      }
      if (to) {
        const ed = a.end_date ? new Date(a.end_date) : null;
        if (ed && ed > to) return false;
      }
      return true;
    });
  }, [activities, projectId, status, risk, team, search, dateFrom, dateTo]);

  const persistCols = (next) => {
    setVisibleCols(next);
    localStorage.setItem('activities_table_columns', JSON.stringify(next));
  };

  const exportToExcel = () => {
    try {
      const rows = filtered.map(a => ({
        'Activity Name': a.name,
        'Project': projectById[a.project_id]?.name || a.project_id,
        'Assigned Person': userById[a.assigned_to]?.name || a.assigned_to,
        'Assigned Team': a.assigned_team || '',
        'Status': (a.status || '').replace('_', ' '),
        'Risk Level': a.risk_level || '',
        'Start Date': a.start_date ? format(new Date(a.start_date), 'yyyy-MM-dd') : '',
        'End Date': a.end_date ? format(new Date(a.end_date), 'yyyy-MM-dd') : '',
        'Planned Start': a.planned_start_date ? format(new Date(a.planned_start_date), 'yyyy-MM-dd') : '',
        'Planned End': a.planned_end_date ? format(new Date(a.planned_end_date), 'yyyy-MM-dd') : '',
        'Progress %': a.progress_percentage ?? 0,
        'Target': a.target_quantity != null ? `${a.target_quantity}${a.measurement_unit ? ' ' + a.measurement_unit : ''}` : '',
        'Achieved': a.achieved_quantity != null ? `${a.achieved_quantity}${a.measurement_unit ? ' ' + a.measurement_unit : ''}` : '',
        'Planned Output': a.planned_output || '',
        'Actual Output': a.actual_output || '',
        'Budget Allocated': a.budget_allocated ?? 0,
        'Budget Utilized': a.budget_utilized ?? 0,
        'Schedule Variance (days)': a.schedule_variance_days ?? 0,
        'Completion Variance %': a.completion_variance ?? 0,
        'Last Updated': a.updated_at ? format(new Date(a.updated_at), 'yyyy-MM-dd HH:mm') : ''
      }));
      const ws = XLSX.utils.json_to_sheet(rows);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Activities');
      XLSX.writeFile(wb, 'activities.xlsx');
    } catch (e) {
      console.error('Export error', e);
      toast({ title: 'Export failed', description: 'Unable to export to Excel', variant: 'destructive' });
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center">
              <Filter className="h-5 w-5 mr-2 text-blue-600" />
              Activities
            </CardTitle>
            <CardDescription>Browse, filter and export your activities</CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" onClick={exportToExcel}>
              <Download className="h-4 w-4 mr-2" /> Export Excel
            </Button>
          </div>
        </div>
        {/* Filters */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-6 gap-3">
          <div className="col-span-2">
            <div className="flex items-center border rounded px-2 py-1 bg-white">
              <Search className="h-4 w-4 text-gray-400" />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by name or description"
                className="border-0 focus-visible:ring-0"
              />
            </div>
          </div>
          <div>
            <Select value={projectId} onValueChange={setProjectId}>
              <SelectTrigger>
                <SelectValue placeholder="Project" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Projects</SelectItem>
                {(projects || []).map(p => (
                  <SelectItem key={p.id || p._id} value={p.id || p._id}>{p.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="not_started">Not Started</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="delayed">Delayed</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Select value={risk} onValueChange={setRisk}>
              <SelectTrigger>
                <SelectValue placeholder="Risk" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Risk</SelectItem>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Select value={team} onValueChange={setTeam}>
              <SelectTrigger>
                <SelectValue placeholder="Team" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Teams</SelectItem>
                {teams.map(t => (
                  <SelectItem key={t} value={t}>{t}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-2 items-center">
            <div className="flex items-center space-x-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <Input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
            </div>
            <div className="flex items-center space-x-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <Input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} />
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-10 text-gray-500">Loading activities...</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-10 text-gray-500">No activities found</div>
        ) : (
          <div className="overflow-x-auto border rounded">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 text-gray-600">
                <tr>
                  <th className="text-left p-2">Activity</th>
                  <th className="text-left p-2">Project</th>
                  <th className="text-left p-2">Assigned</th>
                  <th className="text-left p-2">Team</th>
                  <th className="text-left p-2">Status</th>
                  <th className="text-left p-2">Risk</th>
                  <th className="text-left p-2">Start</th>
                  <th className="text-left p-2">End</th>
                  <th className="text-right p-2">Progress %</th>
                  <th className="text-right p-2">Target</th>
                  <th className="text-right p-2">Achieved</th>
                  <th className="text-right p-2">Budget</th>
                  <th className="text-right p-2">Sched Var (d)</th>
                  <th className="text-right p-2">Compl Var %</th>
                  <th className="text-left p-2">Updated</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(a => (
                  <tr key={a.id} className="border-t hover:bg-gray-50">
                    <td className="p-2">
                      <div className="font-medium text-gray-900">{a.name}</div>
                      {a.planned_output && (
                        <div className="text-xs text-gray-500">{a.planned_output}</div>
                      )}
                    </td>
                    <td className="p-2">{projectById[a.project_id]?.name || a.project_id}</td>
                    <td className="p-2">{userById[a.assigned_to]?.name || a.assigned_to}</td>
                    <td className="p-2">{a.assigned_team || '-'}</td>
                    <td className="p-2">
                      <Badge className={statusColors[a.status] || statusColors.not_started}>
                        {(a.status || '').replace('_', ' ')}
                      </Badge>
                    </td>
                    <td className="p-2">
                      <Badge className={riskColors[a.risk_level] || 'bg-gray-100 text-gray-800'}>
                        {a.risk_level || 'low'}
                      </Badge>
                    </td>
                    <td className="p-2">{a.start_date ? format(new Date(a.start_date), 'yyyy-MM-dd') : ''}</td>
                    <td className="p-2">{a.end_date ? format(new Date(a.end_date), 'yyyy-MM-dd') : ''}</td>
                    <td className="p-2 text-right">{Math.round(a.progress_percentage || 0)}</td>
                    <td className="p-2 text-right">{a.target_quantity != null ? `${a.target_quantity}${a.measurement_unit ? ' ' + a.measurement_unit : ''}` : '-'}</td>
                    <td className="p-2 text-right">{a.achieved_quantity != null ? `${a.achieved_quantity}${a.measurement_unit ? ' ' + a.measurement_unit : ''}` : '-'}</td>
                    <td className="p-2 text-right">{(a.budget_allocated ?? 0).toLocaleString()}</td>
                    <td className="p-2 text-right">{a.schedule_variance_days ?? 0}</td>
                    <td className="p-2 text-right">{Math.round(a.completion_variance ?? 0)}</td>
                    <td className="p-2">{a.updated_at ? format(new Date(a.updated_at), 'yyyy-MM-dd HH:mm') : ''}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ActivitiesTable;