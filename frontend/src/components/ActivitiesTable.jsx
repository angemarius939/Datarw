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
//

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
  const selectedCount = useMemo(() => Object.values(selectedRows).filter(Boolean).length, [selectedRows]);
  const toggleRow = (id, checked) => {
    setSelectedRows(prev => ({ ...prev, [id]: checked }));
  };
  const isRowSelected = (id) => !!selectedRows[id];
  const togglePage = (checked) => {
    const pageRows = filtered.slice((page-1)*pageSize, page*pageSize);
    const next = { ...selectedRows };
    pageRows.forEach(a => { next[a.id] = !!checked; });
    setSelectedRows(next);
  };
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const pageCount = Math.max(1, Math.ceil((activities || []).length / pageSize));
  const pageNumbers = Array.from({ length: Math.min(5, pageCount) }, (_, i) => i + 1);

  // Export options
  const [exportFormat, setExportFormat] = useState('nested'); // 'nested' | 'wide'


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

  const exportToCSV = (selectedOnly = false) => {
    try {
      const headers = [
        'Activity Name','Project','Assigned Person','Assigned Team','Status','Risk Level','Start Date','End Date','Planned Start','Planned End','Progress %','Target','Achieved','Planned Output','Actual Output','Budget Allocated','Budget Utilized','Schedule Variance (days)','Completion Variance %','Last Updated','Milestones','Deliverables'
      ];
      const dataToExport = selectedOnly ? filtered.filter(a => selectedRows[a.id]) : filtered;
      const lines = dataToExport.map(a => {
        const milestones = (a.milestones || []).map(m => `${m.name || ''} (${m.target_date ? format(new Date(m.target_date), 'yyyy-MM-dd') : ''})`).join('; ');
        const deliverables = (a.deliverables || []).join('; ');
        const row = [
          a.name,
          projectById[a.project_id]?.name || a.project_id,
          userById[a.assigned_to]?.name || a.assigned_to,
          a.assigned_team || '',
          (a.status || '').replace('_', ' '),
          a.risk_level || '',
          a.start_date ? format(new Date(a.start_date), 'yyyy-MM-dd') : '',
          a.end_date ? format(new Date(a.end_date), 'yyyy-MM-dd') : '',
          a.planned_start_date ? format(new Date(a.planned_start_date), 'yyyy-MM-dd') : '',
          a.planned_end_date ? format(new Date(a.planned_end_date), 'yyyy-MM-dd') : '',
          a.progress_percentage ?? 0,
          a.target_quantity != null ? `${a.target_quantity}${a.measurement_unit ? ' ' + a.measurement_unit : ''}` : '',
          a.achieved_quantity != null ? `${a.achieved_quantity}${a.measurement_unit ? ' ' + a.measurement_unit : ''}` : '',
          a.planned_output || '',
          a.actual_output || '',
          a.budget_allocated ?? 0,
          a.budget_utilized ?? 0,
          a.schedule_variance_days ?? 0,
          a.completion_variance ?? 0,
          a.updated_at ? format(new Date(a.updated_at), 'yyyy-MM-dd HH:mm') : '',
          milestones,
          deliverables
        ];
        return row.map(v => (v === null || v === undefined) ? '' : String(v).replace(/\n/g, ' ')).join(',');
      });
      const csv = [headers.join(','), ...lines].join('\n');
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', selectedOnly ? 'selected_activities.csv' : 'activities.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('CSV export error', e);
      toast({ title: 'Export failed', description: 'Unable to export to CSV', variant: 'destructive' });
    }
  };

  const exportToExcel = (selectedOnly = false) => {
    try {
      const dataToExport = selectedOnly ? filtered.filter(a => selectedRows[a.id]) : filtered;
      const rows = dataToExport.map(a => ({
        'Activity Name': a.name,
        'Project': projectById[a.project_id]?.name || a.project_id,
        'Assigned Person': userById[a.assigned_to]?.name || a.assigned_to,
        'Assigned Team': a.assigned_team || '', 'Milestones': (a.milestones || []).map(m => `${m.name || ''} (${m.target_date ? format(new Date(m.target_date), 'yyyy-MM-dd') : ''})`).join('; '), 'Deliverables': (a.deliverables || []).join('; '),
        'Milestones': (a.milestones || []).map(m => `${m.name || ''} (${m.target_date ? format(new Date(m.target_date), 'yyyy-MM-dd') : ''})`).join('; '),
        'Deliverables': (a.deliverables || []).join('; '),
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
      XLSX.writeFile(wb, selectedOnly ? 'selected_activities.xlsx' : 'activities.xlsx');
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
            {selectedCount > 0 && (
              <Button variant="default" onClick={() => exportToCSV(true)}>
                <Download className="h-4 w-4 mr-2" /> Selected to CSV ({selectedCount})
              </Button>
            )}
            {selectedCount > 0 && (
              <Button variant="default" onClick={() => exportToExcel(true)}>
                <Download className="h-4 w-4 mr-2" /> Selected to Excel ({selectedCount})
              </Button>
            )}
            <Button variant="outline" onClick={exportToCSV}>
              <Download className="h-4 w-4 mr-2" /> Export CSV
            </Button>
            <Button variant="outline" onClick={exportToExcel}>
              <Download className="h-4 w-4 mr-2" /> Export Excel
            </Button>
          </div>
        </div>
        {/* Filters */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-6 gap-3">
          {/* Quick filter chips */}
          <div className="md:col-span-6 flex flex-wrap gap-2">
            {['not_started','in_progress','completed','delayed'].map(s => (
              <Button key={s} size="sm" variant={status === s ? 'default' : 'outline'} onClick={() => setStatus(s)}>
                {s.replace('_',' ')}
              </Button>
            ))}
            <Button size="sm" variant={status === 'all' ? 'default' : 'outline'} onClick={() => setStatus('all')}>All status</Button>
          </div>
          <div className="col-span-2">
            {/* Per-column filters row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
              <div>
                <Input placeholder="Filter by description" value={descFilter} onChange={e => setDescFilter(e.target.value)} />
              </div>
              <div className="flex items-center space-x-2">
                <Input placeholder="Min budget" type="number" value={minBudget} onChange={e => setMinBudget(e.target.value)} />
                <Input placeholder="Max budget" type="number" value={maxBudget} onChange={e => setMaxBudget(e.target.value)} />
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="outline" onClick={() => { setDescFilter(''); setMinBudget(''); setMaxBudget(''); }}>Clear</Button>
              </div>
            </div>
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

          {/* Column chooser */}
          <div className="md:col-span-6">
            <div className="flex items-center flex-wrap gap-3 p-2 border rounded bg-white">
              <span className="text-sm text-gray-600 mr-2">Columns:</span>
              {DEFAULT_COLUMNS.map(col => (
                <label key={col.key} className="flex items-center space-x-2 text-sm">
                  <Checkbox
                    checked={!!visibleCols[col.key]}
                    onCheckedChange={(checked) => {
                      const next = { ...visibleCols, [col.key]: !!checked };
                      persistCols(next);
                    }}
                  />
                  <span>{col.label}</span>
                </label>
              ))}
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
            <table className="min-w-full text-sm relative">
              <thead className="bg-gray-50 text-gray-600 sticky top-0 z-10">
                <tr>
                  <th className="text-left p-2 w-12">
                    <Checkbox
                      checked={filtered.slice((page-1)*pageSize, page*pageSize).every(a => isRowSelected(a.id))}
                      onCheckedChange={togglePage}
                    />
                  </th>
                  {visibleCols.name && <th className="text-left p-2">Activity</th>}
                  {visibleCols.project && <th className="text-left p-2">Project</th>}
                  {visibleCols.assigned && <th className="text-left p-2">Assigned</th>}
                  {visibleCols.team && <th className="text-left p-2">Team</th>}
                  {visibleCols.status && <th className="text-left p-2">Status</th>}
                  {visibleCols.risk && <th className="text-left p-2">Risk</th>}
                  {visibleCols.start && <th className="text-left p-2">Start</th>}
                  {visibleCols.end && <th className="text-left p-2">End</th>}
                  {visibleCols.progress && <th className="text-right p-2">Progress %</th>}
                  {visibleCols.target && <th className="text-right p-2">Target</th>}
                  {visibleCols.achieved && <th className="text-right p-2">Achieved</th>}
                  {visibleCols.budget && <th className="text-right p-2">Budget</th>}
                  {visibleCols.schedule_var && <th className="text-right p-2">Sched Var (d)</th>}
                  {visibleCols.completion_var && <th className="text-right p-2">Compl Var %</th>}
                  {visibleCols.updated && <th className="text-left p-2">Updated</th>}
                </tr>
              </thead>
              <tbody>
                {filtered.slice((page-1)*pageSize, page*pageSize).map(a => (
                  <tr key={a.id} className="border-t hover:bg-gray-50">
                    <td className="p-2">
                      <Checkbox
                        checked={isRowSelected(a.id)}
                        onCheckedChange={(checked) => toggleRow(a.id, checked)}
                      />
                    </td>
                    {visibleCols.name && (
                      <td className="p-2">
                        <div className="font-medium text-gray-900">{a.name}</div>
                        {a.planned_output && (
                          <div className="text-xs text-gray-500">{a.planned_output}</div>
                        )}
                      </td>
                    )}
                    {visibleCols.project && (
                      <td className="p-2">{projectById[a.project_id]?.name || a.project_id}</td>
                    )}
                    {visibleCols.assigned && (
                      <td className="p-2">{userById[a.assigned_to]?.name || a.assigned_to}</td>
                    )}
                    {visibleCols.team && (
                      <td className="p-2">{a.assigned_team || '-'}</td>
                    )}
                    {visibleCols.status && (
                      <td className="p-2">
                        <Badge className={statusColors[a.status] || statusColors.not_started}>
                          {(a.status || '').replace('_', ' ')}
                        </Badge>
                      </td>
                    )}
                    {visibleCols.risk && (
                      <td className="p-2">
                        <Badge className={riskColors[a.risk_level] || 'bg-gray-100 text-gray-800'}>
                          {a.risk_level || 'low'}
                        </Badge>
                      </td>
                    )}
                    {visibleCols.start && (
                      <td className="p-2">{a.start_date ? format(new Date(a.start_date), 'yyyy-MM-dd') : ''}</td>
                    )}
                    {visibleCols.end && (
                      <td className="p-2">{a.end_date ? format(new Date(a.end_date), 'yyyy-MM-dd') : ''}</td>
                    )}
                    {visibleCols.progress && (
                      <td className="p-2 text-right">{Math.round(a.progress_percentage || 0)}</td>
                    )}
                    {visibleCols.target && (
                      <td className="p-2 text-right">{a.target_quantity != null ? `${a.target_quantity}${a.measurement_unit ? ' ' + a.measurement_unit : ''}` : '-'}</td>
                    )}
                    {visibleCols.achieved && (
                      <td className="p-2 text-right">{a.achieved_quantity != null ? `${a.achieved_quantity}${a.measurement_unit ? ' ' + a.measurement_unit : ''}` : '-'}</td>
                    )}
                    {visibleCols.budget && (
                      <td className="p-2 text-right">{(a.budget_allocated ?? 0).toLocaleString()}</td>
                    )}
                    {visibleCols.schedule_var && (
                      <td className="p-2 text-right">{a.schedule_variance_days ?? 0}</td>
                    )}
                    {visibleCols.completion_var && (
                      <td className="p-2 text-right">{Math.round(a.completion_variance ?? 0)}</td>
                    )}
                    {visibleCols.updated && (
                      <td className="p-2">{a.updated_at ? format(new Date(a.updated_at), 'yyyy-MM-dd HH:mm') : ''}</td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-3">
            <div className="text-sm text-gray-600">
              Showing {(page-1)*pageSize + 1} - {Math.min(page*pageSize, filtered.length)} of {filtered.length}
            </div>
            <div className="flex items-center space-x-3">
              <Select value={String(pageSize)} onValueChange={(v) => setPageSize(Number(v))}>
                <SelectTrigger className="w-24">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {[10,20,50,100].map(s => (
                    <SelectItem key={s} value={String(s)}>{s} / page</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Pagination>
                <PaginationContent>
                  <PaginationPrevious href="#" onClick={(e) => { e.preventDefault(); setPage(p => Math.max(1, p-1)); }} />
                  {Array.from({ length: Math.min(5, Math.ceil(filtered.length / pageSize)) }).map((_, idx) => {
                    const pnum = idx + 1;
                    return (
                      <PaginationItem key={pnum}>
                        <PaginationLink href="#" isActive={pnum === page} onClick={(e) => { e.preventDefault(); setPage(pnum); }}>
                          {pnum}
                        </PaginationLink>
                      </PaginationItem>
                    );
                  })}
                  <PaginationNext href="#" onClick={(e) => { e.preventDefault(); setPage(p => Math.min(Math.ceil(filtered.length / pageSize) || 1, p+1)); }} />
                </PaginationContent>
              </Pagination>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ActivitiesTable;