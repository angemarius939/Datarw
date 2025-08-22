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

# For XLSX/PDF streaming
from io import BytesIO
from fastapi.responses import StreamingResponse
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


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

# Auth endpoints omitted for brevity (already defined above)...

# Existing finance routes ...

# Finance Reports (CSV) already defined ...

# --------------- Finance Reports (XLSX) ---------------
@api.get('/finance/reports/project-xlsx')
async def finance_report_project_xlsx(project_id: str, organization_id: Optional[str] = Query(None), date_from: Optional[str] = Query(None), date_to: Optional[str] = Query(None)):
    org = organization_id or 'org'
    csv_text = await finance_service.project_report_csv(org, project_id, date_from, date_to)
    dfs = []
    parts = csv_text.split('\n\n') if '\n\n' in csv_text else [csv_text]
    for idx, part in enumerate(parts):
        lines = [l for l in part.split('\n') if l.strip()]
        if not lines:
            continue
        header = lines[0].split(',')
        rows = [r.split(',') for r in lines[1:]]
        dfs.append(pd.DataFrame(rows, columns=header))
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for i, df in enumerate(dfs):
            sheet_name = 'Sheet' + str(i+1)
            df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    filename = f"finance_project_{project_id}.xlsx"
    return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={"Content-Disposition": f"attachment; filename={filename}"})

@api.get('/finance/reports/activities-xlsx')
async def finance_report_activities_xlsx(project_id: str, organization_id: Optional[str] = Query(None), date_from: Optional[str] = Query(None), date_to: Optional[str] = Query(None)):
    org = organization_id or 'org'
    csv_text = await finance_service.activities_report_csv(org, project_id, date_from, date_to)
    lines = [l for l in csv_text.split('\n') if l.strip()]
    header = lines[0].split(',') if lines else []
    rows = [r.split(',') for r in lines[1:]]
    df = pd.DataFrame(rows, columns=header)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Activities')
    output.seek(0)
    filename = f"finance_activities_{project_id}.xlsx"
    return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={"Content-Disposition": f"attachment; filename={filename}"})

@api.get('/finance/reports/all-projects-xlsx')
async def finance_report_all_projects_xlsx(organization_id: Optional[str] = Query(None), date_from: Optional[str] = Query(None), date_to: Optional[str] = Query(None)):
    org = organization_id or 'org'
    csv_text = await finance_service.all_projects_report_csv(org, date_from, date_to)
    lines = [l for l in csv_text.split('\n') if l.strip()]
    header = lines[0].split(',') if lines else []
    rows = [r.split(',') for r in lines[1:]]
    df = pd.DataFrame(rows, columns=header)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='All Projects')
    output.seek(0)
    filename = "finance_all_projects.xlsx"
    return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={"Content-Disposition": f"attachment; filename={filename}"})

# --------------- Finance Reports (PDF) ---------------

def _draw_header_footer(c: canvas.Canvas, title: str, page_num: int):
    width, height = A4
    c.setFont('Helvetica-Bold', 14)
    c.drawString(50, height - 50, title)
    c.setFont('Helvetica', 9)
    c.drawRightString(width - 40, 30, f"Page {page_num}")

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

    # Summary page
    _draw_header_footer(c, 'Budget Overview', 2)
    y = height - 80
    c.setFont('Helvetica', 11)
    c.drawString(50, y, f"Total Budgeted: {details['total_budgeted']:.2f}")
    y -= 18
    c.drawString(50, y, f"Total Allocated: {details['total_allocated']:.2f}")
    y -= 18
    c.drawString(50, y, f"Total Spent: {details['total_spent']:.2f}")
    y -= 18
    c.drawString(50, y, f"Variance: {details['variance_amount']:.2f} ({details['variance_pct']:.1f}%)")
    y -= 30

    # Budget lines table header
    c.setFont('Helvetica-Bold', 11)
    c.drawString(50, y, 'Budget Lines (Category / Activity / Budgeted / Allocated / Utilized)')
    y -= 16
    c.setFont('Helvetica', 10)
    for bl in details['budget_lines'][:30]:  # limit rows for now
        line = f"{bl['category']} / {bl['activity_id']} / {bl['budgeted']:.2f} / {bl['allocated']:.2f} / {bl['utilized_pi']:.2f}"
        c.drawString(50, y, line[:110])
        y -= 14
        if y < 60:
            c.showPage()
            y = height - 60

    # Activity spend table
    if y < 120:
        c.showPage()
        y = height - 60
    c.setFont('Helvetica-Bold', 11)
    c.drawString(50, y, 'Expenses by Activity (Activity ID / Transactions / Spent)')
    y -= 16
    c.setFont('Helvetica', 10)
    for aid, row in list(details['spent_by_activity'].items())[:40]:
        line = f"{aid or '(none)'} / {row['transactions']} / {row['spent']:.2f}"
        c.drawString(50, y, line[:110])
        y -= 14
        if y < 60:
            c.showPage()
            y = height - 60

    c.showPage()
    c.save()
    pdf = buf.getvalue()
    buf.close()
    return StreamingResponse(BytesIO(pdf), media_type='application/pdf', headers={"Content-Disposition": f"attachment; filename=finance_project_{project_id}.pdf"})

@api.get('/finance/reports/activities-pdf')
async def finance_report_activities_pdf(project_id: str, organization_id: Optional[str] = Query(None), date_from: Optional[str] = Query(None), date_to: Optional[str] = Query(None)):
    org = organization_id or 'org'
    details = await finance_service.project_budget_details(org, project_id, date_from, date_to)
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    _draw_header_footer(c, 'Activities Finance Summary', 1)
    y = height - 80
    c.setFont('Helvetica-Bold', 12)
    c.drawString(50, y, f"Project ID: {project_id}")
    y -= 24
    c.setFont('Helvetica-Bold', 11)
    c.drawString(50, y, 'Expenses by Activity (Activity ID / Transactions / Spent)')
    y -= 16
    c.setFont('Helvetica', 10)
    for aid, row in list(details['spent_by_activity'].items())[:70]:
        line = f"{aid or '(none)'} / {row['transactions']} / {row['spent']:.2f}"
        c.drawString(50, y, line[:110])
        y -= 14
        if y < 60:
            c.showPage()
            y = height - 60
            _draw_header_footer(c, 'Activities Finance Summary (cont.)', 1)
    c.showPage()
    c.save()
    pdf = buf.getvalue()
    buf.close()
    return StreamingResponse(BytesIO(pdf), media_type='application/pdf', headers={"Content-Disposition": f"attachment; filename=finance_activities_{project_id}.pdf"})

@api.get('/finance/reports/all-projects-pdf')
async def finance_report_all_projects_pdf(organization_id: Optional[str] = Query(None), date_from: Optional[str] = Query(None), date_to: Optional[str] = Query(None)):
    org = organization_id or 'org'
    rows = await finance_service.all_projects_variance(org, date_from, date_to)
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    _draw_header_footer(c, 'All Projects Finance Summary', 1)
    y = height - 80
    c.setFont('Helvetica-Bold', 11)
    c.drawString(50, y, 'Project ID / Planned / Allocated / Actual / Variance / Var%')
    y -= 16
    c.setFont('Helvetica', 10)
    for r in rows[:70]:
        line = f"{r['project_id']} / {r['planned']:.2f} / {r['allocated']:.2f} / {r['actual']:.2f} / {r['variance_amount']:.2f} / {r['variance_pct']:.1f}%"
        c.drawString(50, y, line[:110])
        y -= 14
        if y < 60:
            c.showPage()
            y = height - 60
            _draw_header_footer(c, 'All Projects Finance Summary (cont.)', 1)
    c.showPage()
    c.save()
    pdf = buf.getvalue()
    buf.close()
    return StreamingResponse(BytesIO(pdf), media_type='application/pdf', headers={"Content-Disposition": f"attachment; filename=finance_all_projects.pdf"})

@api.get('/finance/burn-rate')
async def burn_rate(period: str = 'monthly', organization_id: Optional[str] = Query(None), project_id: Optional[str] = Query(None), date_from: Optional[str] = Query(None), date_to: Optional[str] = Query(None)):
    org = organization_id or 'org'
    return await finance_service.burn_rate(org, period, project_id, date_from, date_to)

app.include_router(api)