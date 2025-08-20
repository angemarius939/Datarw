from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
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
