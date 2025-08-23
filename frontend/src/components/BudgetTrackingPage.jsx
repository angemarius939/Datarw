import React, { useEffect, useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Download, Upload, Plus, RefreshCw } from 'lucide-react';
import { financeAPI, projectsAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

const dateToInput = (d) => {
  try { return new Date(d).toISOString().slice(0,10); } catch { return ''; }
};

const BudgetTrackingPage = () => {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('expenses');

  // Config state
  const [config, setConfig] = useState({ funding_sources: [], cost_centers: [] });
  const [newFunding, setNewFunding] = useState('');
  const [newCenter, setNewCenter] = useState('');
  const [savingConfig, setSavingConfig] = useState(false);

  // Expenses state
  const [projects, setProjects] = useState([]);
  const [filters, setFilters] = useState({ project_id: '', activity_id: '', funding_source: '', vendor: '', date_from: '', date_to: '' });
  const [expenses, setExpenses] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [loadingExpenses, setLoadingExpenses] = useState(false);

  // Create/Edit Expense
  const [openModal, setOpenModal] = useState(false);
  const emptyExpense = { project_id: '', activity_id: '', date: new Date().toISOString().slice(0,10), vendor: '', invoice_no: '', amount: '', currency: 'USD', funding_source: '', cost_center: '', notes: '' };
  const [expenseData, setExpenseData] = useState(emptyExpense);
  const [editingId, setEditingId] = useState(null);

  // Reports
  const [burnRate, setBurnRate] = useState(null);
  const [variance, setVariance] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [utilization, setUtilization] = useState(null);
  const [loadingReports, setLoadingReports] = useState(false);

  // AI
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);

  useEffect(() => {
    // Load projects and finance config
    (async () => {
      try {
        const [projRes, cfgRes] = await Promise.all([
          projectsAPI.getProjects(),
          financeAPI.getFinanceConfig()
        ]);
        setProjects(projRes.data || []);
        setConfig(cfgRes.data || { funding_sources: [], cost_centers: [] });
      } catch (e) {
        console.error('Init load failed', e);
      }
    })();
  }, []);

  const loadExpenses = async (resetPage = false) => {
    try {
      setLoadingExpenses(true);
      const params = { ...filters, page, page_size: pageSize };
      if (!params.project_id) delete params.project_id;
      if (!params.activity_id) delete params.activity_id;
      if (!params.funding_source) delete params.funding_source;
      if (!params.vendor) delete params.vendor;
      if (!params.date_from) delete params.date_from;
      if (!params.date_to) delete params.date_to;
      const res = await financeAPI.listExpenses(params);
      setExpenses(res.data.items || []);
      setTotal(res.data.total || 0);
      if (resetPage) setPage(1);
    } catch (e) {
      console.error('Failed to load expenses', e);
      toast({ title: 'Error', description: 'Failed to load expenses', variant: 'destructive' });
    } finally {
      setLoadingExpenses(false);
    }
  };

  useEffect(() => {
    loadExpenses();

  }, [page, pageSize]);

  const saveConfig = async () => {
    try {
      setSavingConfig(true);
      const res = await financeAPI.updateFinanceConfig(config);
      setConfig(res.data);
      toast({ title: 'Saved', description: 'Finance configuration updated' });
    } catch (e) {
      console.error('Save config failed', e);
      toast({ title: 'Save failed', description: 'Could not save finance config', variant: 'destructive' });
    } finally {
      setSavingConfig(false);
    }
  };

  const openCreate = () => {
    setEditingId(null);
    setExpenseData({ ...emptyExpense });
    setOpenModal(true);
  };

  const openEdit = (exp) => {
    setEditingId(exp.id || exp._id);
    setExpenseData({
      project_id: exp.project_id || '',
      activity_id: exp.activity_id || '',
      date: dateToInput(exp.date),
      vendor: exp.vendor || '',
      invoice_no: exp.invoice_no || '',
      amount: exp.amount || '',
      currency: exp.currency || 'USD',
      funding_source: exp.funding_source || '',
      cost_center: exp.cost_center || '',
      notes: exp.notes || ''
    });
    setOpenModal(true);
  };

  const saveExpense = async () => {
    try {
      const payload = {
        ...expenseData,
        amount: Number(expenseData.amount || 0),
        date: new Date(expenseData.date).toISOString(),
      };
      if (!payload.project_id) {
        toast({ title: 'Missing project', description: 'Please select a project', variant: 'destructive' });
        return;
      }
      if (editingId) {
        await financeAPI.updateExpense(editingId, payload);
      } else {
        await financeAPI.createExpense(payload);
      }
      toast({ title: 'Saved', description: 'Expense saved successfully' });
      setOpenModal(false);
      await loadExpenses();
    } catch (e) {
      console.error('Save expense failed', e);
      toast({ title: 'Save failed', description: 'Could not save expense', variant: 'destructive' });
    }
  };

  const deleteExpense = async (id) => {
    if (!window.confirm('Delete this expense?')) return;
    try {
      await financeAPI.deleteExpense(id);
      toast({ title: 'Deleted', description: 'Expense deleted' });
      await loadExpenses();
    } catch (e) {
      console.error('Delete failed', e);
      toast({ title: 'Delete failed', description: 'Could not delete expense', variant: 'destructive' });
    }
  };

  const exportCSV = async () => {
    try {
      const params = { ...filters };
      Object.keys(params).forEach(k => { if (!params[k]) delete params[k]; });
      const res = await financeAPI.exportExpensesCSV(params);
      const blob = new Blob([res.data], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'expenses.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Export failed', e);
      toast({ title: 'Export failed', description: 'Could not export CSV', variant: 'destructive' });
    }
  };

  const runReports = async () => {
    try {
      setLoadingReports(true);
      const [br, vr, fc, fu] = await Promise.all([
        financeAPI.getBurnRate('monthly'),
        financeAPI.getVariance(filters.project_id || null),
        financeAPI.getForecast(),
        financeAPI.getFundingUtilization(null)
      ]);
      setBurnRate(br.data);
      setVariance(vr.data);
      setForecast(fc.data);
      setUtilization(fu.data);
    } catch (e) {
      console.error('Reports failed', e);
      toast({ title: 'Report error', description: 'Failed to compute reports', variant: 'destructive' });
    } finally {
      setLoadingReports(false);
    }
  };

  const runAIInsights = async () => {
    try {
      setAiLoading(true);
      // Build a simple anomalies list from current page
      const anomalies = (expenses || []).filter(e => (e.amount || 0) > 1000000).map(e => ({ id: e.id, vendor: e.vendor, amount: e.amount }));
      const summary = { page, total, filters };
      const res = await financeAPI.getAIInsights({ anomalies, summary });
      setAiResult(res.data);
    } catch (e) {
      console.error('AI insights failed', e);
      toast({ title: 'AI error', description: 'Failed to run AI insights', variant: 'destructive' });
    } finally {
      setAiLoading(false);
    }
  };

  const getProjectName = (id) => {
    const p = (projects || []).find(x => (x.id || x._id) === id);
    return p ? p.name : id;
  };

  // Quick date presets
  const applyThisMonth = () => {
    const now = new Date();
    const start = new Date(now.getFullYear(), now.getMonth(), 1);
    setFilters(prev => ({ ...prev, date_from: dateToInput(start), date_to: dateToInput(now) }));
  };
  const applyLast90Days = () => {
    const now = new Date();
    const start = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
    setFilters(prev => ({ ...prev, date_from: dateToInput(start), date_to: dateToInput(now) }));
  };

  const totalPages = useMemo(() => Math.max(1, Math.ceil((total || 0) / pageSize)), [total, pageSize]);

  const downloadBlob = (data, filename, type = 'text/csv') => {
    const blob = new Blob([data], { type: `${type};charset=utf-8;` });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const downloadProjectReport = async () => {
    if (!filters.project_id) {
      toast({ title: 'Select project', description: 'Choose a project in the Expenses filter first', variant: 'destructive' });
      return;
    }
    const res = await financeAPI.downloadProjectReportCSV(filters.project_id, buildDateParams());
    downloadBlob(res.data, `finance_project_${filters.project_id}.csv`);
  };

  const downloadActivitiesReport = async () => {
    if (!filters.project_id) {
      toast({ title: 'Select project', description: 'Choose a project in the Expenses filter first', variant: 'destructive' });
      return;
    }
    const res = await financeAPI.downloadActivitiesReportCSV(filters.project_id, buildDateParams());
    downloadBlob(res.data, `finance_activities_${filters.project_id}.csv`);
  };

  const downloadAllProjectsReport = async () => {
    const res = await financeAPI.downloadAllProjectsReportCSV(buildDateParams());
    downloadBlob(res.data, 'finance_all_projects.csv');
  };

  const buildDateParams = () => {
    const params = {};
    if (filters.date_from) params.date_from = filters.date_from;
    if (filters.date_to) params.date_to = filters.date_to;
    return params;
  };

  const downloadProjectReportXLSX = async () => {
    if (!filters.project_id) {
      toast({ title: 'Select project', description: 'Choose a project in the Expenses filter first', variant: 'destructive' });
      return;
    }
    const res = await financeAPI.downloadProjectReportXLSX(filters.project_id, buildDateParams());
    downloadBlob(res.data, `finance_project_${filters.project_id}.xlsx`, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
  };

  const downloadActivitiesReportXLSX = async () => {
    if (!filters.project_id) {
      toast({ title: 'Select project', description: 'Choose a project in the Expenses filter first', variant: 'destructive' });
      return;
    }
    const res = await financeAPI.downloadActivitiesReportXLSX(filters.project_id, buildDateParams());
    downloadBlob(res.data, `finance_activities_${filters.project_id}.xlsx`, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
  };

  const downloadAllProjectsReportXLSX = async () => {
    const res = await financeAPI.downloadAllProjectsReportXLSX(buildDateParams());
    downloadBlob(res.data, 'finance_all_projects.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
  };

  const downloadProjectReportPDF = async () => {
    if (!filters.project_id) {
      toast({ title: 'Select project', description: 'Choose a project in the Expenses filter first', variant: 'destructive' });
      return;
    }
    const res = await financeAPI.downloadProjectReportPDF(filters.project_id, buildDateParams());
    downloadBlob(res.data, `finance_project_${filters.project_id}.pdf`, 'application/pdf');
  };

  const downloadActivitiesReportPDF = async () => {
    if (!filters.project_id) {
      toast({ title: 'Select project', description: 'Choose a project in the Expenses filter first', variant: 'destructive' });
      return;
    }
    const res = await financeAPI.downloadActivitiesReportPDF(filters.project_id, buildDateParams());
    downloadBlob(res.data, `finance_activities_${filters.project_id}.pdf`, 'application/pdf');
  };

  const downloadAllProjectsReportPDF = async () => {
    const res = await financeAPI.downloadAllProjectsReportPDF(buildDateParams());
    downloadBlob(res.data, 'finance_all_projects.pdf', 'application/pdf');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Budget Tracking</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={exportCSV}><Download className="h-4 w-4 mr-2"/>Export CSV</Button>
          <Button variant="outline" onClick={() => document.getElementById('expenses-import').click()}><Upload className="h-4 w-4 mr-2"/>Import CSV (stub)</Button>
          <input id="expenses-import" type="file" className="hidden" accept=".csv,text/csv" onChange={async (e) => {
            const file = e.target.files?.[0];
            if (!file) return;
            try {
              await financeAPI.importExpensesCSV(file); // stub
              toast({ title: 'Import received', description: 'CSV import received (stub). No rows processed.' });
            } catch (err) {
              toast({ title: 'Import failed', description: 'CSV import failed', variant: 'destructive' });
            } finally {
              e.target.value = '';
            }
          }} />
          <Button onClick={openCreate}><Plus className="h-4 w-4 mr-2"/>New Expense</Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="config">Config</TabsTrigger>
          <TabsTrigger value="expenses">Expenses</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
          <TabsTrigger value="ai">AI Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="config">
          <Card>
            <CardHeader>
              <CardTitle>Finance Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium">Funding Sources</h3>
                    <div className="flex gap-2">
                      <Input placeholder="Add funding source" value={newFunding} onChange={e => setNewFunding(e.target.value)} />
                      <Button variant="outline" onClick={() => {
                        if (!newFunding.trim()) return;
                        setConfig(prev => ({ ...prev, funding_sources: Array.from(new Set([...(prev.funding_sources||[]), newFunding.trim()])) }));
                        setNewFunding('');
                      }}>Add</Button>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(config.funding_sources || []).map(fs => (
                      <Badge key={fs} className="bg-gray-100 text-gray-800">
                        {fs}
                        <button className="ml-2 text-red-600" onClick={() => setConfig(prev => ({ ...prev, funding_sources: (prev.funding_sources||[]).filter(x => x !== fs) }))}>×</button>
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium">Cost Centers</h3>
                    <div className="flex gap-2">
                      <Input placeholder="Add cost center" value={newCenter} onChange={e => setNewCenter(e.target.value)} />
                      <Button variant="outline" onClick={() => {
                        if (!newCenter.trim()) return;
                        setConfig(prev => ({ ...prev, cost_centers: Array.from(new Set([...(prev.cost_centers||[]), newCenter.trim()])) }));
                        setNewCenter('');
                      }}>Add</Button>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(config.cost_centers || []).map(cc => (
                      <Badge key={cc} className="bg-gray-100 text-gray-800">
                        {cc}
                        <button className="ml-2 text-red-600" onClick={() => setConfig(prev => ({ ...prev, cost_centers: (prev.cost_centers||[]).filter(x => x !== cc) }))}>×</button>
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
              <div className="mt-4">
                <Button onClick={saveConfig} disabled={savingConfig}>{savingConfig ? 'Saving…' : 'Save Config'}</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="expenses">
          <Card>
            <CardHeader>
              <CardTitle>Expenses</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-7 gap-3 items-end">
                <div className="md:col-span-2">
                  <label className="text-sm text-gray-600">Project</label>
                  <Select value={filters.project_id || ''} onValueChange={(v) => setFilters(prev => ({ ...prev, project_id: v === 'all' ? '' : v }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Projects" />
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
                  <label className="text-sm text-gray-600">Funding Source</label>
                  <Select value={filters.funding_source || ''} onValueChange={(v) => setFilters(prev => ({ ...prev, funding_source: v === 'all' ? '' : v }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Funding" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All</SelectItem>
                      {(config.funding_sources || []).map(fs => (
                        <SelectItem key={fs} value={fs}>{fs}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm text-gray-600">Vendor</label>
                  <Input value={filters.vendor || ''} onChange={e => setFilters(prev => ({ ...prev, vendor: e.target.value }))} placeholder="Vendor name" />
                </div>
                <div>
                  <label className="text-sm text-gray-600">From</label>
                  <Input type="date" value={filters.date_from || ''} onChange={e => setFilters(prev => ({ ...prev, date_from: e.target.value }))} />
                </div>
                <div>
                  <label className="text-sm text-gray-600">To</label>
                  <Input type="date" value={filters.date_to || ''} onChange={e => setFilters(prev => ({ ...prev, date_to: e.target.value }))} />
                </div>
                <div className="flex gap-2 flex-wrap items-center">
                  <Button onClick={() => { setPage(1); loadExpenses(true); }}><RefreshCw className="h-4 w-4 mr-2"/>Apply</Button>
                  <Button variant="outline" onClick={() => { setFilters({ project_id: '', activity_id: '', funding_source: '', vendor: '', date_from: '', date_to: '' }); setPage(1); loadExpenses(true); }}>Clear</Button>
                  <div className="flex gap-1">
                    <Button type="button" variant="outline" onClick={applyThisMonth}>This Month</Button>
                    <Button type="button" variant="outline" onClick={applyLast90Days}>Last 90 Days</Button>
                  </div>
                </div>
              </div>

              <div className="mt-4 overflow-x-auto border rounded">
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50 text-gray-600">
                    <tr>
                      <th className="text-left p-2">Date</th>
                      <th className="text-left p-2">Project</th>
                      <th className="text-left p-2">Vendor</th>
                      <th className="text-right p-2">Amount</th>
                      <th className="text-left p-2">Funding</th>
                      <th className="text-left p-2">Cost Center</th>
                      <th className="text-left p-2">Invoice</th>
                      <th className="text-left p-2">Notes</th>
                      <th className="text-right p-2">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {loadingExpenses ? (
                      <tr><td colSpan={9} className="text-center p-6 text-gray-500">Loading expenses…</td></tr>
                    ) : expenses.length === 0 ? (
                      <tr><td colSpan={9} className="text-center p-6 text-gray-500">No expenses found</td></tr>
                    ) : (
                      expenses.map(exp => (
                        <tr key={exp.id || exp._id} className="border-t hover:bg-gray-50">
                          <td className="p-2">{dateToInput(exp.date)}</td>
                          <td className="p-2">{getProjectName(exp.project_id)}</td>
                          <td className="p-2">{exp.vendor || '-'}</td>
                          <td className="p-2 text-right">{(exp.amount ?? 0).toLocaleString()} {exp.currency || ''}</td>
                          <td className="p-2">{exp.funding_source || '-'}</td>
                          <td className="p-2">{exp.cost_center || '-'}</td>
                          <td className="p-2">{exp.invoice_no || '-'}</td>
                          <td className="p-2">{exp.notes || ''}</td>
                          <td className="p-2 text-right">
                            <Button size="sm" variant="outline" onClick={() => openEdit(exp)}>Edit</Button>
                            <Button size="sm" variant="ghost" className="text-red-600 ml-2" onClick={() => deleteExpense(exp.id || exp._id)}>Delete</Button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              <div className="mt-3 flex items-center justify-between">
                <div className="text-sm text-gray-600">Showing {(page-1)*pageSize + 1} - {Math.min(page*pageSize, total)} of {total}</div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p-1))}>Prev</Button>
                  <span className="text-sm">Page {page} / {totalPages}</span>
                  <Button variant="outline" disabled={page >= totalPages} onClick={() => setPage(p => Math.min(totalPages, p+1))}>Next</Button>
                  <Select value={String(pageSize)} onValueChange={(v) => { setPageSize(Number(v)); setPage(1); }}>
                    <SelectTrigger className="w-28"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {[10,20,50,100].map(s => (<SelectItem key={s} value={String(s)}>{s} / page</SelectItem>))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Finance Reports</CardTitle>
                <div className="flex gap-2 flex-wrap">
                  <Button variant="outline" onClick={downloadProjectReport}><Download className="h-4 w-4 mr-2"/>Project CSV</Button>
                  <Button variant="outline" onClick={downloadActivitiesReport}><Download className="h-4 w-4 mr-2"/>Activities CSV</Button>
                  <Button variant="outline" onClick={downloadAllProjectsReport}><Download className="h-4 w-4 mr-2"/>All Projects CSV</Button>
                  <Button variant="outline" onClick={() => downloadProjectReportXLSX()}><Download className="h-4 w-4 mr-2"/>Project XLSX</Button>
                  <Button variant="outline" onClick={() => downloadActivitiesReportXLSX()}><Download className="h-4 w-4 mr-2"/>Activities XLSX</Button>
                  <Button variant="outline" onClick={() => downloadAllProjectsReportXLSX()}><Download className="h-4 w-4 mr-2"/>All Projects XLSX</Button>
                  <Button onClick={runReports} disabled={loadingReports}>{loadingReports ? 'Running…' : 'Run Summaries'}</Button>
                  <Button variant="outline" onClick={() => downloadProjectReportPDF()}><Download className="h-4 w-4 mr-2"/>Project PDF</Button>
                  <Button variant="outline" onClick={() => downloadActivitiesReportPDF()}><Download className="h-4 w-4 mr-2"/>Activities PDF</Button>
                  <Button variant="outline" onClick={() => downloadAllProjectsReportPDF()}><Download className="h-4 w-4 mr-2"/>All Projects PDF</Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {!burnRate && !variance && !forecast && !utilization ? (
                <div className="text-center py-10 text-gray-500">Run summaries to see burn rate, variance and projections</div>
              ) : (
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-medium mb-2">Burn Rate ({burnRate?.period})</h3>
                    <div className="border rounded p-2 bg-white max-h-64 overflow-auto">
                      {(burnRate?.series || []).map((s) => (
                        <div key={s.period} className="flex items-center justify-between py-1 text-sm">
                          <span>{s.period}</span>
                          <span>{s.spent.toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium mb-2">Budget vs Actual (by project)</h3>
                    <div className="border rounded p-2 bg-white max-h-64 overflow-auto">
                      {(variance?.by_project || []).map((row) => (
                        <div key={row.project_id} className="grid grid-cols-5 gap-2 text-sm py-1">
                          <span className="truncate" title={getProjectName(row.project_id)}>{getProjectName(row.project_id)}</span>
                          <span className="text-right">Planned: {row.planned.toLocaleString()}</span>
                          <span className="text-right">Allocated: {row.allocated.toLocaleString()}</span>
                          <span className="text-right">Actual: {row.actual.toLocaleString()}</span>
                          <span className={`text-right ${row.variance_amount < 0 ? 'text-red-600' : 'text-green-700'}`}>Var: {row.variance_amount.toLocaleString()} ({Number(row.variance_pct||0).toFixed(1)}%)</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium mb-2">Forecast (Year)</h3>
                    <div className="border rounded p-3 bg-white text-sm space-y-1">
                      <div>Avg Monthly: {Number(forecast?.avg_monthly || 0).toLocaleString()}</div>
                      <div>Months Remaining: {forecast?.months_remaining}</div>
                      <div>Projected Spend (rest of year): {Number(forecast?.projected_spend_rest_of_year || 0).toLocaleString()}</div>
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium mb-2">Funding Utilization</h3>
                    <div className="border rounded p-2 bg-white max-h-64 overflow-auto">
                      {(utilization?.by_funding_source || []).map(u => (
                        <div key={u.funding_source} className="flex items-center justify-between py-1 text-sm">
                          <span>{u.funding_source}</span>
                          <span>{u.spent.toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ai">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>AI Financial Insights</CardTitle>
                <Button onClick={runAIInsights} disabled={aiLoading}>{aiLoading ? 'Analyzing…' : 'Run Insights'}</Button>
              </div>
            </CardHeader>
            <CardContent>
              {!aiResult ? (
                <div className="text-center py-10 text-gray-500">Run AI insights to detect anomalies and get recommendations</div>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">Risk Level:</span>
                    <Badge className={aiResult.risk_level === 'high' ? 'bg-red-100 text-red-800' : aiResult.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}>
                      {aiResult.risk_level}
                    </Badge>
                    <span className="text-sm text-gray-500">Confidence: {Math.round((aiResult.confidence || 0)*100)}%</span>
                    {aiResult.ai_used ? <Badge className="bg-blue-100 text-blue-800">AI</Badge> : <Badge className="bg-gray-100 text-gray-700">Fallback</Badge>}
                  </div>
                  {aiResult.description && (
                    <p className="text-sm text-gray-800 whitespace-pre-wrap">{aiResult.description}</p>
                  )}
                  <div>
                    <h4 className="font-medium mb-1">Recommendations</h4>
                    <ul className="list-disc pl-6 text-sm">
                      {(aiResult.recommendations || []).map((r, idx) => (
                        <li key={idx}>{r}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create/Edit Expense Modal */}
      <Dialog open={openModal} onOpenChange={setOpenModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingId ? 'Edit Expense' : 'New Expense'}</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium">Project</label>
              <Select value={expenseData.project_id} onValueChange={(v) =&gt; setExpenseData(prev =&gt; ({ ...prev, project_id: v }))}>
                <SelectTrigger><SelectValue placeholder="Select project"/></SelectTrigger>
                <SelectContent>
                  {(projects || []).map(p =&gt; (
                    <SelectItem key={p.id || p._id} value={p.id || p._id}>{p.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium">Date</label>
              <Input type="date" value={expenseData.date} onChange={e =&gt; setExpenseData(prev =&gt; ({ ...prev, date: e.target.value }))} />
            </div>
            <div>
              <label className="text-sm font-medium">Vendor</label>
              <Input value={expenseData.vendor} onChange={e =&gt; setExpenseData(prev =&gt; ({ ...prev, vendor: e.target.value }))} />
            </div>
            <div>
              <label className="text-sm font-medium">Invoice No</label>
              <Input value={expenseData.invoice_no} onChange={e =&gt; setExpenseData(prev =&gt; ({ ...prev, invoice_no: e.target.value }))} />
            </div>
            <div>
              <label className="text-sm font-medium">Amount</label>
              <Input type="number" value={expenseData.amount} onChange={e =&gt; setExpenseData(prev =&gt; ({ ...prev, amount: e.target.value }))} />
            </div>
            <div>
              <label className="text-sm font-medium">Currency</label>
              <Select value={expenseData.currency} onValueChange={(v) =&gt; setExpenseData(prev =&gt; ({ ...prev, currency: v }))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {['USD','RWF','EUR','KES','UGX'].map(c =&gt; (<SelectItem key={c} value={c}>{c}</SelectItem>))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium">Funding Source</label>
              <Select value={expenseData.funding_source} onValueChange={(v) =&gt; setExpenseData(prev =&gt; ({ ...prev, funding_source: v }))}>
                <SelectTrigger><SelectValue placeholder="Select"/></SelectTrigger>
                <SelectContent>
                  {(config.funding_sources || []).map(fs =&gt; (<SelectItem key={fs} value={fs}>{fs}</SelectItem>))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium">Cost Center</label>
              <Select value={expenseData.cost_center} onValueChange={(v) =&gt; setExpenseData(prev =&gt; ({ ...prev, cost_center: v }))}>
                <SelectTrigger><SelectValue placeholder="Select"/></SelectTrigger>
                <SelectContent>
                  {(config.cost_centers || []).map(cc =&gt; (<SelectItem key={cc} value={cc}>{cc}</SelectItem>))}
                </SelectContent>
              </Select>
            </div>
            <div className="col-span-2">
              <label className="text-sm font-medium">Notes</label>
              <Input value={expenseData.notes} onChange={e =&gt; setExpenseData(prev =&gt; ({ ...prev, notes: e.target.value }))} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() =&gt; setOpenModal(false)}>Cancel</Button>
            <Button onClick={saveExpense}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default BudgetTrackingPage;