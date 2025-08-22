import os
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.responses import PlainTextResponse, JSONResponse

from models import (
    Project, ProjectCreate, ProjectUpdate, ProjectStatus,
    Activity, ActivityCreate, ActivityUpdate, ActivityStatus,
    BudgetItem, BudgetItemCreate, BudgetItemUpdate,
    KPIIndicator, KPIIndicatorCreate, KPIIndicatorUpdate,
    Beneficiary, BeneficiaryCreate, BeneficiaryUpdate,
    ProjectDocument, ProjectDashboardData,
    Expense, ExpenseCreate, ExpenseUpdate,
    User
)
from project_service import ProjectService
from finance_service import FinanceService

# Environment loader (fallback to .env file)
from pathlib import Path

# AI Finance insights
from ai_service import FinanceAI


def _load_env_if_needed():
    if os.environ.get('MONGO_URL'):
        return
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        try:
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k, v)
        except Exception:
            pass

_load_env_if_needed()

MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    raise RuntimeError('MONGO_URL not configured')

client = AsyncIOMotorClient(MONGO_URL)

# Auto-detect database containing prior data if configured DB is empty
def select_database(client: AsyncIOMotorClient) -> Any:
    configured = os.environ.get('DB_NAME') or os.environ.get('MONGO_DB_NAME') or 'datarw_database'
    try:
        db = client[configured]
        # Check if projects or activities exist
        if db.projects.estimated_document_count() > 0 or db.activities.estimated_document_count() > 0:
            return db
        # Fallback: scan databases
        for name in client.list_database_names():
            if name in ('admin', 'local', 'config'):
                continue
            cand = client[name]
            try:
                if cand.projects.estimated_document_count() > 0 or cand.activities.estimated_document_count() > 0:
                    return cand
            except Exception:
                continue
        return db
    except Exception:
        return client[configured]

_db = select_database(client)
db = _db

project_service = ProjectService(db)
finance_service = FinanceService(db)
finance_ai = FinanceAI()

app = FastAPI(title='DataRW API', version='1.0.0')

# CORS (allow frontend domain via env or default *)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

api = APIRouter(prefix='/api')

# --------------- Health ---------------
@api.get('/health')
async def health():
    return {'status': 'ok', 'time': datetime.utcnow().isoformat()}

# --------------- Users (minimal) ---------------
@api.get('/users')
async def list_users():
    users = []
    cursor = db.users.find({}).sort('name', 1)
    async for u in cursor:
        u['id'] = u.get('id') or str(u.get('_id'))
        users.append({'id': u['id'], 'name': u.get('name') or u.get('email'), 'email': u.get('email')})
    return users

# --------------- Projects ---------------
@api.get('/projects')
async def get_projects(status: Optional[ProjectStatus] = None, organization_id: Optional[str] = Query(None)):
    # For selection lists, allow returning all if org is not specified
    return await project_service.get_projects(organization_id or None, status)

@api.post('/projects', response_model=Project)
async def create_project(payload: ProjectCreate, organization_id: Optional[str] = Query(None)):
    org = organization_id or payload.organization_id or 'org'
    creator = 'system'
    return await project_service.create_project(payload, org, creator)

@api.get('/projects/dashboard', response_model=ProjectDashboardData)
async def get_dashboard(organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    return await project_service.get_dashboard_data(org)

@api.get('/projects/{project_id}', response_model=Optional[Project])
async def get_project(project_id: str):
    return await project_service.get_project(project_id)

@api.put('/projects/{project_id}', response_model=Optional[Project])
async def update_project(project_id: str, payload: ProjectUpdate):
    return await project_service.update_project(project_id, payload)

@api.delete('/projects/{project_id}')
async def delete_project(project_id: str):
    ok = await project_service.delete_project(project_id)
    return {'success': ok}

# --------------- Activities ---------------
@api.get('/activities')
async def get_activities(project_id: Optional[str] = None, organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    return await project_service.get_activities(org, project_id)

@api.post('/activities', response_model=Activity)
async def create_activity(payload: ActivityCreate, organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    creator = 'system'
    return await project_service.create_activity(payload, org, creator)

@api.put('/activities/{activity_id}', response_model=Optional[Activity])
async def update_activity(activity_id: str, payload: ActivityUpdate):
    return await project_service.update_activity(activity_id, payload)

# --------------- Budget ---------------
@api.get('/budget')
async def get_budget_items(project_id: Optional[str] = None, organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    return await project_service.get_budget_items(org, project_id)

@api.post('/budget', response_model=BudgetItem)
async def create_budget_item(payload: BudgetItemCreate, organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    return await project_service.create_budget_item(payload, org, created_by='system')

@api.get('/budget/summary')
async def budget_summary(project_id: Optional[str] = None, organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    return await project_service.get_budget_summary(org, project_id)

# --------------- Finance: Org Config ---------------
@api.get('/finance/config')
async def get_finance_config(organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    return await finance_service.get_org_config(org)

@api.put('/finance/config')
async def update_finance_config(payload: Dict[str, Any], organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    return await finance_service.update_org_config(org, payload)

# --------------- Finance: Expenses & Analytics ---------------
@api.post('/finance/expenses', response_model=Expense)
async def create_expense(payload: ExpenseCreate, organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    return await finance_service.create_expense(payload, org, user_id='system')

@api.get('/finance/expenses')
async def list_expenses(
    organization_id: Optional[str] = Query(None),
    project_id: Optional[str] = None,
    activity_id: Optional[str] = None,
    funding_source: Optional[str] = None,
    vendor: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    org = organization_id or 'org'
    filters: Dict[str, Any] = {k: v for k, v in {
        'project_id': project_id,
        'activity_id': activity_id,
        'funding_source': funding_source,
        'vendor': vendor,
        'date_from': date_from,
        'date_to': date_to,
    }.items() if v}
    return await finance_service.list_expenses(org, filters, page, page_size)

@api.put('/finance/expenses/{expense_id}', response_model=Optional[Expense])
async def update_expense(expense_id: str, payload: ExpenseUpdate, organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    return await finance_service.update_expense(org, expense_id, payload, user_id='system')

@api.delete('/finance/expenses/{expense_id}')
async def delete_expense(expense_id: str, organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    ok = await finance_service.delete_expense(org, expense_id)
    return {'success': ok}

@api.get('/finance/burn-rate')
async def burn_rate(period: str = 'monthly', organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    return await finance_service.burn_rate(org, period)

@api.get('/finance/variance')
async def variance(project_id: Optional[str] = None, organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    return await finance_service.budget_vs_actual(org, project_id)

@api.get('/finance/forecast')
async def forecast(organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    return await finance_service.forecast(org)

@api.get('/finance/funding-utilization')
async def funding_utilization(donor: Optional[str] = None, organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    return await finance_service.funding_utilization(org, donor)

# --------------- Finance CSV import/export (stubs/minimal) ---------------
@api.post('/finance/expenses/import-csv')
async def import_expenses_csv(file: UploadFile = File(...)):
    # Phase 1 stub: acknowledge receipt only
    return {"status": "received", "processed": 0, "message": "CSV import stub in Phase 1"}

@api.get('/finance/expenses/export-csv', response_class=PlainTextResponse)
async def export_expenses_csv(
    organization_id: Optional[str] = Query(None),
    project_id: Optional[str] = None,
    funding_source: Optional[str] = None,
    vendor: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    org = organization_id or 'org'
    filters: Dict[str, Any] = {k: v for k, v in {
        'project_id': project_id,
        'funding_source': funding_source,
        'vendor': vendor,
        'date_from': date_from,
        'date_to': date_to,
    }.items() if v}
    data = await finance_service.list_expenses(org, filters, page=1, page_size=1000)
    rows = data.get('items', [])
    headers = ['Expense ID','Project ID','Activity ID','Date','Vendor','Invoice','Amount','Currency','Funding Source','Cost Center','Notes']
    def sanitize(v: Any) -> str:
        s = str(v or '')
        if any(c in s for c in ['"', ',', '\n']):
            s = '"' + s.replace('"','""') + '"'
        return s
    lines = [','.join(headers)]
    for e in rows:
        line = [
            sanitize(e.get('id') or e.get('_id')),
            sanitize(e.get('project_id')),
            sanitize(e.get('activity_id')),
            sanitize((e.get('date').isoformat() if e.get('date') else '')[:10]),
            sanitize(e.get('vendor')),
            sanitize(e.get('invoice_no')),
            sanitize(e.get('amount')),
            sanitize(e.get('currency')),
            sanitize(e.get('funding_source')),
            sanitize(e.get('cost_center')),
            sanitize(e.get('notes')),
        ]
        lines.append(','.join(line))
    csv = '\n'.join(lines)
    return PlainTextResponse(content=csv, media_type='text/csv')

# --------------- QuickBooks Online stub endpoints ---------------
@api.post('/finance/integrations/qbo/connect')
async def qbo_connect():
    return {"status": "stub", "message": "QBO connect flow not implemented in Phase 1"}

@api.get('/finance/integrations/qbo/status')
async def qbo_status():
    return {"connected": False, "message": "QBO not connected (stub)"}

@api.post('/finance/integrations/qbo/push-expenses')
async def qbo_push_expenses():
    return {"status": "stub", "pushed": 0, "message": "No expenses pushed in Phase 1"}

# --------------- AI Insights ---------------
@api.post('/finance/ai/insights')
async def ai_insights(payload: Dict[str, Any], organization_id: Optional[str] = Query(None)):
    org = organization_id or 'org'
    try:
      # Summaries to provide richer context
      variance = await finance_service.budget_vs_actual(org)
      burn = await finance_service.burn_rate(org, 'monthly')
      forecast_data = await finance_service.forecast(org)
      anomalies = payload.get('anomalies', [])
      summary = { 'variance': variance, 'burn_rate': burn, 'forecast': forecast_data }
      insight = await finance_ai.analyze(summary, anomalies)
      return JSONResponse(content={
          'ai_used': True,
          'risk_level': insight.risk_level,
          'description': insight.description,
          'recommendations': insight.recommendations,
          'confidence': insight.confidence,
      })
    except Exception:
      anomalies = payload.get('anomalies', [])
      count = len(anomalies)
      risk = 'low' if count == 0 else 'medium' if count < 5 else 'high'
      return {
          'ai_used': False,
          'risk_level': risk,
          'anomaly_count': count,
          'recommendations': [
              'Review high-variance line items',
              'Adjust disbursement schedule to match burn rate',
              'Set alerts for vendor spikes > 2x baseline'
          ],
          'confidence': 0.6 if count == 0 else 0.7 if count < 5 else 0.8,
      }

app.include_router(api)