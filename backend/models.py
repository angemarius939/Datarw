from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# Enums
class UserRole(str, Enum):
    ADMIN = "Admin"
    EDITOR = "Editor"
    VIEWER = "Viewer"

class SubscriptionPlan(str, Enum):
    BASIC = "Basic"
    PROFESSIONAL = "Professional"
    ENTERPRISE = "Enterprise"

class SurveyStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT = "text"
    RATING = "rating"
    FILE_UPLOAD = "file_upload"
    CALCULATION = "calculation"
    SKIP_LOGIC = "skip_logic"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    EXPIRED = "expired"

# Base Models
class BaseDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True

# Organization Models
class Organization(BaseDocument):
    name: str
    plan: SubscriptionPlan
    survey_limit: int = Field(default=4)
    storage_limit: float = Field(default=1.0)  # in GB
    survey_count: int = Field(default=0)
    storage_used: float = Field(default=0.0)  # in GB
    status: str = Field(default="active")
    stripe_customer_id: Optional[str] = None
    subscription_id: Optional[str] = None

class OrganizationCreate(BaseModel):
    name: str
    plan: SubscriptionPlan = SubscriptionPlan.BASIC

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[SubscriptionPlan] = None
    survey_limit: Optional[int] = None
    storage_limit: Optional[float] = None

# User Models
class User(BaseDocument):
    email: EmailStr
    password_hash: str
    name: str
    organization_id: str
    role: UserRole = UserRole.VIEWER
    status: str = Field(default="active")
    last_login: Optional[datetime] = None
    surveys_created: int = Field(default=0)

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    organization_id: Optional[str] = None
    role: UserRole = UserRole.VIEWER

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    organization_id: str
    role: UserRole
    status: str
    last_login: Optional[datetime] = None
    surveys_created: int
    created_at: datetime

# Survey Models
class SurveyQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: QuestionType
    question: str
    required: bool = False
    options: List[str] = Field(default_factory=list)
    scale: Optional[int] = None
    skip_logic: Optional[Dict[str, Any]] = None
    calculation: Optional[Dict[str, Any]] = None

class Survey(BaseDocument):
    title: str
    description: str
    organization_id: str
    creator_id: str
    status: SurveyStatus = SurveyStatus.DRAFT
    questions: List[SurveyQuestion] = Field(default_factory=list)
    responses_count: int = Field(default=0)
    settings: Dict[str, Any] = Field(default_factory=dict)

class SurveyCreate(BaseModel):
    title: str
    description: str
    questions: List[SurveyQuestion] = Field(default_factory=list)

class SurveyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[SurveyStatus] = None
    questions: Optional[List[SurveyQuestion]] = None
    settings: Optional[Dict[str, Any]] = None

class SurveyResponse(BaseDocument):
    survey_id: str
    respondent_id: Optional[str] = None
    responses: Dict[str, Any]  # question_id -> answer
    completion_time: Optional[float] = None  # in minutes
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class SurveyResponseCreate(BaseModel):
    survey_id: str
    responses: Dict[str, Any]
    completion_time: Optional[float] = None

# Payment Models
class PaymentTransaction(BaseDocument):
    organization_id: str
    user_id: Optional[str] = None
    stripe_session_id: str
    amount: float
    currency: str = "FRW"
    plan: SubscriptionPlan
    payment_status: PaymentStatus = PaymentStatus.PENDING
    stripe_payment_intent_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PaymentTransactionCreate(BaseModel):
    organization_id: str
    user_id: Optional[str] = None
    stripe_session_id: str
    amount: float
    currency: str = "FRW"
    plan: SubscriptionPlan
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Analytics Models
class AnalyticsData(BaseModel):
    total_responses: int
    response_rate: float
    average_completion_time: float
    top_performing_survey: str
    monthly_growth: float
    storage_growth: float
    responses_by_month: List[Dict[str, Any]]
    survey_types: List[Dict[str, Any]]

# Auth Models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse
    organization: Organization

class TokenData(BaseModel):
    user_id: str
    organization_id: str
    role: UserRole