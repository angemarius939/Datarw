from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, File, UploadFile
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our models and services
from models import *
from auth import *
from database import DatabaseService
from payment_service import IremboPayService
from ai_service import AIService
from project_service import ProjectService
from admin_service import AdminService
from irembopay_service import irembopay_service

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Set db in auth module to avoid circular import
import auth
auth.db = db

# Initialize services
db_service = DatabaseService(db)
payment_service = IremboPayService(db)
ai_service = AIService(db)
project_service = ProjectService(db)
admin_service = AdminService(db)

# Create the main app without a prefix
app = FastAPI(title="DataRW API", description="Survey and Data Management Platform")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Authentication endpoints
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user and organization"""
    # Check if user already exists
    existing_user = await db_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create organization first
    org_create = OrganizationCreate(name=f"{user_data.name}'s Organization")
    organization = await db_service.create_organization(org_create)
    
    # Hash password and create user
    password_hash = get_password_hash(user_data.password)
    user_data.organization_id = organization.id
    user_data.role = UserRole.ADMIN  # First user is admin
    
    user = await db_service.create_user(user_data, password_hash)
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.id,
            "org_id": user.organization_id,
            "role": user.role.value
        }
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(**user.dict()),
        organization=organization
    )

@api_router.post("/auth/login", response_model=Token)
async def login(form_data: UserLogin):
    """Login user"""
    user = await authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    # Update last login
    await db_service.update_user_last_login(user.id)
    
    # Get organization
    organization = await db_service.get_organization(user.organization_id)
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.id,
            "org_id": user.organization_id,
            "role": user.role.value
        }
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(**user.dict()),
        organization=organization
    )

# Organization endpoints
@api_router.get("/organizations/me", response_model=Organization)
async def get_my_organization(current_user: User = Depends(get_current_active_user)):
    """Get current user's organization"""
    organization = await db_service.get_organization(current_user.organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization

@api_router.put("/organizations/me", response_model=Organization)
async def update_my_organization(
    updates: OrganizationUpdate,
    current_user: User = Depends(require_admin())
):
    """Update current user's organization"""
    organization = await db_service.update_organization(current_user.organization_id, updates)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization

# User management endpoints
@api_router.get("/users", response_model=List[UserResponse])
async def get_organization_users(current_user: User = Depends(get_current_active_user)):
    """Get all users in the organization"""
    users = await db_service.get_organization_users(current_user.organization_id)
    return [UserResponse(**user.dict()) for user in users]

@api_router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin())
):
    """Create a new user in the organization"""
    # Check if user already exists
    existing_user = await db_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Set organization ID
    user_data.organization_id = current_user.organization_id
    
    # Hash password and create user
    password_hash = get_password_hash(user_data.password)
    user = await db_service.create_user(user_data, password_hash)
    
    return UserResponse(**user.dict())

@api_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    updates: UserUpdate,
    current_user: User = Depends(require_admin())
):
    """Update a user in the organization"""
    user = await db_service.get_user(user_id)
    if not user or user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await db_service.update_user(user_id, updates)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(**updated_user.dict())

@api_router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_admin())
):
    """Delete a user from the organization"""
    user = await db_service.get_user(user_id)
    if not user or user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    success = await db_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}

# Survey endpoints
@api_router.get("/surveys", response_model=List[Survey])
async def get_surveys(current_user: User = Depends(get_current_active_user)):
    """Get all surveys in the organization"""
    surveys = await db_service.get_organization_surveys(current_user.organization_id)
    return surveys

@api_router.post("/surveys", response_model=Survey)
async def create_survey(
    survey_data: SurveyCreate,
    current_user: User = Depends(require_editor())
):
    """Create a new survey"""
    # Check survey limit
    organization = await db_service.get_organization(current_user.organization_id)
    if (organization.survey_limit > 0 and 
        organization.survey_count >= organization.survey_limit):
        raise HTTPException(
            status_code=400, 
            detail=f"Survey limit reached. Upgrade your plan to create more surveys."
        )
    
    survey = await db_service.create_survey(
        survey_data, 
        current_user.organization_id, 
        current_user.id
    )
    return survey

@api_router.get("/surveys/{survey_id}", response_model=Survey)
async def get_survey(
    survey_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific survey"""
    survey = await db_service.get_survey(survey_id)
    if not survey or survey.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Survey not found")
    return survey

@api_router.put("/surveys/{survey_id}", response_model=Survey)
async def update_survey(
    survey_id: str,
    updates: SurveyUpdate,
    current_user: User = Depends(require_editor())
):
    """Update a survey"""
    survey = await db_service.get_survey(survey_id)
    if not survey or survey.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    updated_survey = await db_service.update_survey(survey_id, updates)
    if not updated_survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    return updated_survey

@api_router.delete("/surveys/{survey_id}")
async def delete_survey(
    survey_id: str,
    current_user: User = Depends(require_editor())
):
    """Delete a survey"""
    survey = await db_service.get_survey(survey_id)
    if not survey or survey.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    success = await db_service.delete_survey(survey_id)
    if not success:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    return {"message": "Survey deleted successfully"}

# Survey response endpoints
@api_router.post("/surveys/{survey_id}/responses", response_model=SurveyResponse)
async def submit_survey_response(
    survey_id: str,
    response_data: SurveyResponseCreate
):
    """Submit a response to a survey (public endpoint)"""
    # Verify survey exists and is active
    survey = await db_service.get_survey(survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    if survey.status != SurveyStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Survey is not active")
    
    response_data.survey_id = survey_id
    response = await db_service.create_survey_response(response_data)
    return response

@api_router.get("/surveys/{survey_id}/responses", response_model=List[SurveyResponse])
async def get_survey_responses(
    survey_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get all responses for a survey"""
    survey = await db_service.get_survey(survey_id)
    if not survey or survey.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    responses = await db_service.get_survey_responses(survey_id)
    return responses

# Analytics endpoints
@api_router.get("/analytics", response_model=AnalyticsData)
async def get_analytics(current_user: User = Depends(get_current_active_user)):
    """Get analytics data for the organization"""
    analytics = await db_service.get_organization_analytics(current_user.organization_id)
    return analytics

# Payment endpoints
@api_router.post("/payments/create-invoice", response_model=IremboPayInvoiceResponse)
async def create_payment_invoice(
    plan: SubscriptionPlan,
    current_user: User = Depends(get_current_active_user)
):
    """Create an IremboPay invoice for subscription"""
    try:
        invoice = await payment_service.create_invoice(
            organization_id=current_user.organization_id,
            plan=plan,
            user_id=current_user.id,
            customer_name=current_user.name,
            customer_email=current_user.email
        )
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/payments/status/{invoice_number}")
async def get_payment_status(
    invoice_number: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get payment status for an invoice"""
    try:
        status = await payment_service.get_invoice_status(invoice_number)
        return status
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/payments/webhook")
async def payment_webhook(request: Request):
    """Handle IremboPay payment webhooks"""
    try:
        body = await request.body()
        signature = request.headers.get("irembopay-signature", "")
        
        # Verify webhook signature
        if not await payment_service.verify_webhook_signature(body.decode(), signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Process webhook payload
        payload = json.loads(body)
        
        # Handle payment notification
        if payload.get("event") == "payment.successful":
            invoice_number = payload.get("data", {}).get("invoiceNumber")
            if invoice_number:
                await payment_service.get_invoice_status(invoice_number)
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/payments/widget-config")
async def get_payment_widget_config():
    """Get IremboPay widget configuration"""
    return payment_service.get_widget_config()

@api_router.get("/payments/history", response_model=List[PaymentTransaction])
async def get_payment_history(current_user: User = Depends(get_current_active_user)):
    """Get payment history for the organization"""
    history = await payment_service.get_payment_history(current_user.organization_id)
    return history

@api_router.get("/payments/plans")
async def get_payment_plans():
    """Get all available payment plans"""
    plans = payment_service.get_all_plans()
    return plans

# Enumerator Management endpoints
@api_router.get("/enumerators", response_model=List[Enumerator])
async def get_enumerators(current_user: User = Depends(get_current_active_user)):
    """Get all enumerators for the organization"""
    enumerators = await db_service.get_organization_enumerators(current_user.organization_id)
    return enumerators

@api_router.post("/enumerators", response_model=Enumerator)
async def create_enumerator(
    enumerator_data: EnumeratorCreate,
    current_user: User = Depends(require_admin())
):
    """Create a new enumerator"""
    enumerator = await db_service.create_enumerator(enumerator_data, current_user.organization_id)
    return enumerator

@api_router.post("/enumerators/assign")
async def assign_survey_to_enumerator(
    assignment: EnumeratorAssignment,
    current_user: User = Depends(require_admin())
):
    """Assign a survey to an enumerator"""
    success = await db_service.assign_survey_to_enumerator(
        assignment.enumerator_id, 
        assignment.survey_id,
        current_user.organization_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Enumerator or survey not found")
    return {"message": "Survey assigned successfully"}

@api_router.post("/enumerators/auth")
async def authenticate_enumerator(credentials: dict):
    """Authenticate enumerator for mobile app access"""
    enumerator_id = credentials.get("enumerator_id")
    access_password = credentials.get("access_password")
    
    if not enumerator_id or not access_password:
        raise HTTPException(status_code=400, detail="Missing credentials")
    
    enumerator = await db_service.authenticate_enumerator(enumerator_id, access_password)
    if not enumerator:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Get assigned surveys
    surveys = await db_service.get_enumerator_surveys(enumerator.id)
    
    return {
        "enumerator": enumerator,
        "assigned_surveys": surveys
    }

# Mobile app sync endpoints
@api_router.post("/mobile/sync/upload")
async def mobile_sync_upload(sync_data: dict):
    """Upload survey responses from mobile app"""
    try:
        enumerator_id = sync_data.get("enumerator_id")
        responses = sync_data.get("responses", [])
        
        if not enumerator_id:
            raise HTTPException(status_code=400, detail="Missing enumerator ID")
        
        # Verify enumerator exists
        enumerator = await db_service.get_enumerator(enumerator_id)
        if not enumerator:
            raise HTTPException(status_code=404, detail="Enumerator not found")
        
        # Process responses
        processed_count = 0
        for response_data in responses:
            try:
                # Create survey response
                response = SurveyResponseCreate(**response_data)
                await db_service.create_survey_response(response)
                processed_count += 1
            except Exception as e:
                logger.error(f"Error processing response: {str(e)}")
                continue
        
        # Update enumerator's last sync
        await db_service.update_enumerator_sync(enumerator_id)
        
        return {
            "status": "success",
            "processed_responses": processed_count,
            "sync_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Mobile sync upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Sync failed")

@api_router.get("/mobile/sync/download/{enumerator_id}")
async def mobile_sync_download(enumerator_id: str):
    """Download assigned surveys for mobile app"""
    try:
        enumerator = await db_service.get_enumerator(enumerator_id)
        if not enumerator:
            raise HTTPException(status_code=404, detail="Enumerator not found")
        
        surveys = await db_service.get_enumerator_surveys(enumerator_id)
        
        return {
            "enumerator": enumerator,
            "surveys": surveys,
            "sync_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Mobile sync download error: {str(e)}")
        raise HTTPException(status_code=500, detail="Sync failed")

# AI Survey Generation endpoints
@api_router.post("/surveys/generate-ai")
async def generate_survey_with_ai(
    request: AISurveyGenerationRequest,
    current_user: User = Depends(require_editor())
):
    """Generate a survey using AI based on user description and optional document context"""
    try:
        survey_data = await ai_service.generate_survey_with_ai(request, current_user.organization_id)
        return {"success": True, "survey_data": survey_data}
    except Exception as e:
        logger.error(f"AI survey generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate survey: {str(e)}")

@api_router.post("/surveys/upload-context")
async def upload_survey_context(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(require_editor())
):
    """Upload documents to provide context for AI survey generation"""
    try:
        documents = []
        for file in files:
            # Read file content
            content = await file.read()
            
            # For now, assume text files. In production, you'd want to handle PDFs, DOCX, etc.
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                # Skip binary files for now
                continue
                
            document = DocumentUpload(
                filename=file.filename,
                content_type=file.content_type,
                file_size=len(content),
                content=text_content
            )
            documents.append(document)
        
        context = await ai_service.save_document_context(current_user.organization_id, documents)
        return {"success": True, "context_id": context.id, "documents_processed": len(documents)}
        
    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload documents: {str(e)}")

@api_router.post("/surveys/{survey_id}/translate")
async def translate_survey(
    survey_id: str,
    target_language: str = "kinyarwanda",
    current_user: User = Depends(get_current_active_user)
):
    """Translate an existing survey to the specified language"""
    try:
        # Get the survey
        survey = await db_service.get_survey(survey_id)
        if not survey or survey.organization_id != current_user.organization_id:
            raise HTTPException(status_code=404, detail="Survey not found")
        
        # Prepare survey data for translation
        survey_data = {
            "title": survey.title,
            "description": survey.description,
            "questions": [q.model_dump() for q in survey.questions]
        }
        
        # Translate using AI
        translated_data = await ai_service.translate_survey(survey_data, target_language)
        
        return {"success": True, "translated_survey": translated_data}
        
    except Exception as e:
        logger.error(f"Survey translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to translate survey: {str(e)}")

@api_router.get("/surveys/context/{organization_id}")
async def get_survey_context(
    organization_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get uploaded document context for survey generation"""
    if organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        context = await ai_service._get_organization_context(organization_id)
        if context:
            return {"success": True, "context": context.model_dump()}
        else:
            return {"success": True, "context": None}
    except Exception as e:
        logger.error(f"Get context error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get context: {str(e)}")

# Project Management Endpoints
@api_router.get("/projects/dashboard")
async def get_project_dashboard(
    current_user: User = Depends(get_current_active_user)
):
    """Get project dashboard data"""
    try:
        dashboard_data = await project_service.get_dashboard_data(current_user.organization_id)
        return {"success": True, "data": dashboard_data.model_dump()}
    except Exception as e:
        logger.error(f"Project dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

@api_router.post("/projects", response_model=Project)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(require_editor())
):
    """Create a new project"""
    try:
        project = await project_service.create_project(
            project_data, 
            current_user.organization_id, 
            current_user.id
        )
        return project
    except Exception as e:
        logger.error(f"Project creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@api_router.get("/projects", response_model=List[Project])
async def get_projects(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get all projects for the organization"""
    try:
        project_status = ProjectStatus(status) if status else None
        projects = await project_service.get_projects(current_user.organization_id, project_status)
        return projects
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid status: {str(e)}")
    except Exception as e:
        logger.error(f"Get projects error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific project"""
    try:
        project = await project_service.get_project(project_id)
        if not project or project.organization_id != current_user.organization_id:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    updates: ProjectUpdate,
    current_user: User = Depends(require_editor())
):
    """Update a project"""
    try:
        # Verify project belongs to organization
        project = await project_service.get_project(project_id)
        if not project or project.organization_id != current_user.organization_id:
            raise HTTPException(status_code=404, detail="Project not found")
        
        updated_project = await project_service.update_project(project_id, updates)
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found")
        return updated_project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update project error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")

@api_router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(require_admin())
):
    """Delete a project"""
    try:
        # Verify project belongs to organization
        project = await project_service.get_project(project_id)
        if not project or project.organization_id != current_user.organization_id:
            raise HTTPException(status_code=404, detail="Project not found")
        
        success = await project_service.delete_project(project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"success": True, "message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete project error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")

# Activity Management Endpoints
@api_router.post("/activities", response_model=Activity)
async def create_activity(
    activity_data: ActivityCreate,
    current_user: User = Depends(require_editor())
):
    """Create a new activity"""
    try:
        activity = await project_service.create_activity(activity_data, current_user.organization_id)
        return activity
    except Exception as e:
        logger.error(f"Activity creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create activity: {str(e)}")

@api_router.get("/activities", response_model=List[Activity])
async def get_activities(
    project_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get activities for the organization or specific project"""
    try:
        activities = await project_service.get_activities(current_user.organization_id, project_id)
        return activities
    except Exception as e:
        logger.error(f"Get activities error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get activities: {str(e)}")

@api_router.put("/activities/{activity_id}", response_model=Activity)
async def update_activity(
    activity_id: str,
    updates: ActivityUpdate,
    current_user: User = Depends(require_editor())
):
    """Update an activity"""
    try:
        updated_activity = await project_service.update_activity(activity_id, updates)
        if not updated_activity:
            raise HTTPException(status_code=404, detail="Activity not found")
        return updated_activity
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update activity error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update activity: {str(e)}")

# Budget Management Endpoints
@api_router.post("/budget", response_model=BudgetItem)
async def create_budget_item(
    budget_data: BudgetItemCreate,
    current_user: User = Depends(require_editor())
):
    """Create a new budget item"""
    try:
        budget_item = await project_service.create_budget_item(budget_data, current_user.organization_id)
        return budget_item
    except Exception as e:
        logger.error(f"Budget item creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create budget item: {str(e)}")

@api_router.get("/budget", response_model=List[BudgetItem])
async def get_budget_items(
    project_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get budget items for the organization or specific project"""
    try:
        budget_items = await project_service.get_budget_items(current_user.organization_id, project_id)
        return budget_items
    except Exception as e:
        logger.error(f"Get budget items error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get budget items: {str(e)}")

@api_router.get("/budget/summary")
async def get_budget_summary(
    project_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get budget summary with utilization rates"""
    try:
        summary = await project_service.get_budget_summary(current_user.organization_id, project_id)
        return {"success": True, "data": summary}
    except Exception as e:
        logger.error(f"Budget summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get budget summary: {str(e)}")

# KPI Management Endpoints
@api_router.post("/kpis", response_model=KPIIndicator)
async def create_kpi_indicator(
    kpi_data: KPIIndicatorCreate,
    current_user: User = Depends(require_editor())
):
    """Create a new KPI indicator"""
    try:
        kpi = await project_service.create_kpi_indicator(kpi_data, current_user.organization_id)
        return kpi
    except Exception as e:
        logger.error(f"KPI creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create KPI: {str(e)}")

@api_router.get("/kpis", response_model=List[KPIIndicator])
async def get_kpi_indicators(
    project_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get KPI indicators for the organization or specific project"""
    try:
        kpis = await project_service.get_kpi_indicators(current_user.organization_id, project_id)
        return kpis
    except Exception as e:
        logger.error(f"Get KPIs error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get KPIs: {str(e)}")

@api_router.put("/kpis/{indicator_id}/value")
async def update_kpi_value(
    indicator_id: str,
    current_value: float,
    current_user: User = Depends(require_editor())
):
    """Update the current value of a KPI indicator"""
    try:
        kpi = await project_service.update_kpi_current_value(indicator_id, current_value)
        if not kpi:
            raise HTTPException(status_code=404, detail="KPI indicator not found")
        return kpi
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update KPI value error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update KPI value: {str(e)}")

# Beneficiary Management Endpoints
@api_router.post("/beneficiaries", response_model=Beneficiary)
async def create_beneficiary(
    beneficiary_data: BeneficiaryCreate,
    current_user: User = Depends(require_editor())
):
    """Create a new beneficiary"""
    try:
        beneficiary = await project_service.create_beneficiary(beneficiary_data, current_user.organization_id)
        return beneficiary
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Beneficiary creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create beneficiary: {str(e)}")

@api_router.get("/beneficiaries", response_model=List[Beneficiary])
async def get_beneficiaries(
    project_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get beneficiaries for the organization or specific project"""
    try:
        beneficiaries = await project_service.get_beneficiaries(current_user.organization_id, project_id)
        return beneficiaries
    except Exception as e:
        logger.error(f"Get beneficiaries error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get beneficiaries: {str(e)}")

@api_router.get("/beneficiaries/demographics")
async def get_beneficiary_demographics(
    project_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get demographic breakdown of beneficiaries"""
    try:
        demographics = await project_service.get_beneficiary_demographics(current_user.organization_id, project_id)
        return {"success": True, "data": demographics}
    except Exception as e:
        logger.error(f"Beneficiary demographics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get demographics: {str(e)}")

# User Management Endpoints  
@api_router.get("/users", response_model=List[User])
async def get_organization_users(
    current_user: User = Depends(get_current_active_user)
):
    """Get all users in the current organization"""
    try:
        # Get users from the same organization
        users = await db_service.get_organization_users(current_user.organization_id)
        return users
    except Exception as e:
        logger.error(f"Get organization users error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

# Advanced Admin Panel Endpoints
@api_router.post("/admin/users/create-advanced")
async def create_user_advanced(
    user_data: UserCreateAdvanced,
    current_user: User = Depends(require_admin())
):
    """Create user with advanced features (Admin/Director only)"""
    try:
        result = await admin_service.create_user_advanced(
            user_data, 
            current_user.organization_id, 
            current_user.id
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Advanced user creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@api_router.post("/admin/users/bulk-create")
async def bulk_create_users(
    users_data: List[UserCreateAdvanced],
    send_emails: bool = True,
    current_user: User = Depends(require_admin())
):
    """Create multiple users with batch processing"""
    try:
        result = await admin_service.bulk_create_users(
            users_data,
            current_user.organization_id,
            current_user.id,
            send_emails
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Bulk user creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create users: {str(e)}")

# Partner Organization Management
@api_router.post("/admin/partners", response_model=PartnerOrganization)
async def create_partner_organization(
    partner_data: PartnerOrganizationCreate,
    current_user: User = Depends(require_admin())
):
    """Create a new partner organization"""
    try:
        partner = await admin_service.create_partner_organization(
            partner_data, 
            current_user.organization_id
        )
        return partner
    except Exception as e:
        logger.error(f"Partner creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create partner: {str(e)}")

@api_router.get("/admin/partners", response_model=List[PartnerOrganization])
async def get_partner_organizations(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get all partner organizations"""
    try:
        partners = await admin_service.get_partner_organizations(
            current_user.organization_id, 
            status
        )
        return partners
    except Exception as e:
        logger.error(f"Get partners error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get partners: {str(e)}")

@api_router.put("/admin/partners/{partner_id}", response_model=PartnerOrganization)
async def update_partner_organization(
    partner_id: str,
    updates: PartnerOrganizationUpdate,
    current_user: User = Depends(require_admin())
):
    """Update a partner organization"""
    try:
        partner = await admin_service.update_partner_organization(partner_id, updates)
        if not partner:
            raise HTTPException(status_code=404, detail="Partner organization not found")
        return partner
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update partner error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update partner: {str(e)}")

# Partner Performance Tracking
@api_router.post("/admin/partners/performance", response_model=PartnerPerformance)
async def create_partner_performance(
    performance_data: PartnerPerformanceCreate,
    current_user: User = Depends(require_editor())
):
    """Create partner performance record"""
    try:
        performance = await admin_service.create_partner_performance(
            performance_data, 
            current_user.id
        )
        return performance
    except Exception as e:
        logger.error(f"Partner performance creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create performance record: {str(e)}")

@api_router.get("/admin/partners/performance/summary")
async def get_partner_performance_summary(
    partner_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get partner performance summary"""
    try:
        summary = await admin_service.get_partner_performance_summary(
            current_user.organization_id, 
            partner_id
        )
        return {"success": True, "data": summary}
    except Exception as e:
        logger.error(f"Partner performance summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance summary: {str(e)}")

# Organization Branding
@api_router.put("/admin/branding")
async def update_organization_branding(
    branding_data: OrganizationBrandingCreate,
    current_user: User = Depends(require_admin())
):
    """Update organization branding settings"""
    try:
        branding = await admin_service.update_organization_branding(
            current_user.organization_id, 
            branding_data
        )
        return {"success": True, "data": branding.model_dump()}
    except Exception as e:
        logger.error(f"Branding update error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update branding: {str(e)}")

@api_router.get("/admin/branding")
async def get_organization_branding(
    current_user: User = Depends(get_current_active_user)
):
    """Get organization branding settings"""
    try:
        branding = await admin_service.get_organization_branding(current_user.organization_id)
        if branding:
            return {"success": True, "data": branding.model_dump()}
        else:
            return {"success": True, "data": None}
    except Exception as e:
        logger.error(f"Get branding error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get branding: {str(e)}")

# Email Logs (Mock Email System)
@api_router.get("/admin/email-logs")
async def get_email_logs(
    limit: int = 50,
    current_user: User = Depends(require_admin())
):
    """Get email logs for organization"""
    try:
        logs = await admin_service.get_email_logs(current_user.organization_id, limit)
        return {"success": True, "data": logs}
    except Exception as e:
        logger.error(f"Get email logs error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get email logs: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Test endpoint
@api_router.get("/")
async def root():
    return {"message": "DataRW API is running!", "version": "1.0.0"}

# Also add a root endpoint for the main app
@app.get("/")
async def app_root():
    return {"message": "DataRW API Server", "version": "1.0.0", "docs": "/docs"}
