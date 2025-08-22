import os
import uuid
from typing import Optional, Dict, Any, List
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
    User, Organization
)
from project_service import ProjectService
from finance_service import FinanceService

# Auth utilities
import auth as auth_util
from models import UserRole

# Environment loader (fallback to .env file)
from pathlib import Path

# AI Finance insights
from ai_service import FinanceAI

# For XLSX/PDF streaming and charts
from io import BytesIO
from fastapi.responses import StreamingResponse
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


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
        if db.projects.estimated_document_count() > 0 or db.activities.estimated_document_count() > 0:
            return db
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

auth_util.db = db

project_service = ProjectService(db)
finance_service = FinanceService(db)
finance_ai = FinanceAI()

app = FastAPI(title='DataRW API', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

api = APIRouter(prefix='/api')

@api.get('/health')
async def health():
    return {'status': 'ok', 'time': datetime.utcnow().isoformat()}

# ... existing endpoints omitted for brevity ...

# --------------- Helpers: Charts for PDFs ---------------
def _fig_to_image_reader(fig) -> ImageReader:
    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=140)
    plt.close(fig)
    buf.seek(0)
    return ImageReader(buf)

async def _chart_burn_rate(organization_id: str, project_id: Optional[str], date_from: Optional[str], date_to: Optional[str]) -> Optional[ImageReader]:
    try:
        data = await finance_service.burn_rate(organization_id, 'monthly', project_id, date_from, date_to)
        series = data.get('series', [])
        if not series:
            return None
        x = [s['period'] for s in series]
        y = [s['spent'] for s in series]
        fig, ax = plt.subplots(figsize=(6, 2.4))
        ax.plot(x, y, marker='o')
        ax.set_title('Burn Rate (Monthly)')
        ax.set_xlabel('Period')
        ax.set_ylabel('Spent')
        ax.tick_params(axis='x', rotation=45)
        return _fig_to_image_reader(fig)
    except Exception:
        return None

async def _chart_variance_project(organization_id: str, project_id: str, date_from: Optional[str], date_to: Optional[str]) -> Optional[ImageReader]:
    try:
        var = await finance_service.budget_vs_actual(organization_id, project_id, date_from, date_to)
        rows = var.get('by_project', [])
        if not rows:
            return None
        row = next((r for r in rows if r.get('project_id') == project_id), rows[0])
        labels = ['Planned','Actual']
        values = [row.get('planned',0), row.get('actual',0)]
        fig, ax = plt.subplots(figsize=(4, 2.4))
        ax.bar(labels, values, color=['#60a5fa','#34d399'])
        ax.set_title('Budget vs Actual')
        return _fig_to_image_reader(fig)
    except Exception:
        return None

async def _chart_funding_util(organization_id: str, project_id: Optional[str], date_from: Optional[str], date_to: Optional[str]) -> Optional[ImageReader]:
    try:
        util = await finance_service.funding_utilization(organization_id, donor=None, date_from=date_from, date_to=date_to, project_id=project_id)
        rows = util.get('by_funding_source', [])
        rows = [r for r in rows if r.get('funding_source')]
        if not rows:
            return None
        x = [r['funding_source'] for r in rows][:10]
        y = [r['spent'] for r in rows][:10]
        fig, ax = plt.subplots(figsize=(6, 2.4))
        ax.barh(x, y, color='#f59e0b')
        ax.set_title('Funding Utilization by Source')
        ax.set_xlabel('Spent')
        return _fig_to_image_reader(fig)
    except Exception:
        return None

# --------------- Finance Reports (PDF with charts) ---------------
@api.get('/finance/reports/project-pdf')
async def finance_report_project_pdf(project_id: str, organization_id: Optional[str] = Query(None), date_from: Optional[str] = Query(None), date_to: Optional[str] = Query(None)):
    org = organization_id or 'org'
    details = await finance_service.project_budget_details(org, project_id, date_from, date_to)
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    # Cover page
    c.setFont('Helvetica-Bold', 20)
    c.drawCentredString(width/2, height - 120, 'Project Finance Summary')
    c.setFont('Helvetica', 12)
    c.drawCentredString(width/2, height - 145, f'Project ID: {project_id}')
    if date_from or date_to:
        c.drawCentredString(width/2, height - 165, f"Period: {date_from or 'Start'} to {date_to or 'Now'}")
    c.showPage()

    # Summary + Charts page
    y = height - 60
    c.setFont('Helvetica-Bold', 14)
    c.drawString(50, y, 'Budget Overview')
    y -= 20
    c.setFont('Helvetica', 11)
    c.drawString(50, y, f"Total Budgeted: {details['total_budgeted']:.2f}")
    y -= 16
    c.drawString(50, y, f"Total Allocated: {details['total_allocated']:.2f}")
    y -= 16
    c.drawString(50, y, f"Total Spent: {details['total_spent']:.2f}")
    y -= 16
    c.drawString(50, y, f"Variance: {details['variance_amount']:.2f} ({details['variance_pct']:.1f}%)")

    # Charts
    br_img = await _chart_burn_rate(org, project_id, date_from, date_to)
    var_img = await _chart_variance_project(org, project_id, date_from, date_to)
    fu_img = await _chart_funding_util(org, project_id, date_from, date_to)

    y_chart = y - 30
    if br_img:
      c.drawImage(br_img, 50, y_chart-150, width=500, height=140, preserveAspectRatio=True, mask='auto')
      y_chart -= 160
    if var_img:
      c.drawImage(var_img, 50, y_chart-130, width=300, height=120, preserveAspectRatio=True, mask='auto')
    if fu_img:
      c.drawImage(fu_img, 360, y_chart-130, width=220, height=120, preserveAspectRatio=True, mask='auto')
    c.showPage()

    # Budget lines
    y = height - 60
    c.setFont('Helvetica-Bold', 12)
    c.drawString(50, y, 'Budget Lines (Category / Activity / Budgeted / Allocated / Utilized)')
    y -= 18
    c.setFont('Helvetica', 10)
    for bl in details['budget_lines'][:40]:
        line = f"{bl['category']} / {bl['activity_id']} / {bl['budgeted']:.2f} / {bl['allocated']:.2f} / {bl['utilized_pi']:.2f}"
        c.drawString(50, y, line[:110])
        y -= 12
        if y < 60:
            c.showPage()
            y = height - 60
            c.setFont('Helvetica', 10)

    # Activity spend
    if y < 120:
        c.showPage()
        y = height - 60
    c.setFont('Helvetica-Bold', 12)
    c.drawString(50, y, 'Expenses by Activity (Activity ID / Transactions / Spent)')
    y -= 18
    c.setFont('Helvetica', 10)
    items: List = list(details['spent_by_activity'].items())[:70]
    for aid, row in items:
        line = f"{aid or '(none)'} / {row['transactions']} / {row['spent']:.2f}"
        c.drawString(50, y, line[:110])
        y -= 12
        if y < 60:
            c.showPage()
            y = height - 60
            c.setFont('Helvetica', 10)

    c.showPage()
    c.save()
    pdf = buf.getvalue()
    buf.close()
    return StreamingResponse(BytesIO(pdf), media_type='application/pdf', headers={"Content-Disposition": f"attachment; filename=finance_project_{project_id}.pdf"})

# Other PDF endpoints (activities/all-projects) already implemented above

app.include_router(api)