from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid

# Existing enums and models...

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    EMAIL = "email"
    PHONE = "phone"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    SCALE = "scale"
    MATRIX = "matrix"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    FILE_UPLOAD = "file_upload"
    SIGNATURE = "signature"
    LIKERT = "likert"
    RANKING = "ranking"
    SLIDER = "slider"
    IMAGE_CHOICE = "image_choice"
    STAR_RATING = "star_rating"

class UserRole(str, Enum):
    ADMIN = "Admin"
    EDITOR = "Editor" 
    VIEWER = "Viewer"
    PROJECT_MANAGER = "Project Manager"
    ME_OFFICER = "M&E Officer"
    DONOR_VIEWER = "Donor Viewer"
    DIRECTOR = "Director"
    OFFICER = "Officer"
    FIELD_STAFF = "Field Staff"
    PARTNER_STAFF = "Partner Staff"
    SYSTEM_ADMIN = "System Admin"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    role: Optional[UserRole] = None

# Payment-related models
class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class PaymentProvider(str, Enum):
    MTN = "MTN"
    AIRTEL = "AIRTEL"
    CARD = "CARD"
    BANK = "BANK"

class SubscriptionPlan(str, Enum):
    BASIC = "Basic"
    PROFESSIONAL = "Professional"
    ENTERPRISE = "Enterprise"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"

# Payment Models
class PaymentCustomer(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., pattern=r"^07[0-9]{8}$")

class PaymentItem(BaseModel):
    unit_amount: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None

class CreateInvoiceRequest(BaseModel):
    transaction_id: Optional[str] = None
    customer: PaymentCustomer
    payment_items: List[PaymentItem]
    description: str = Field(..., max_length=500)
    currency: str = Field(default="RWF")

class InvoiceResponse(BaseModel):
    invoice_number: str
    transaction_id: str
    status: PaymentStatus
    amount: int
    currency: str
    payment_url: str
    customer: PaymentCustomer
    description: str
    expiry_at: datetime
    created_at: datetime

class InitiatePaymentRequest(BaseModel):
    invoice_number: str
    phone_number: str = Field(..., pattern=r"^07[0-9]{8}$")
    provider: PaymentProvider

class PaymentResponse(BaseModel):
    payment_reference: str
    status: PaymentStatus
    message: str
    amount: int
    currency: str
    provider: PaymentProvider
    phone_number: str
    estimated_processing_time: str

class SubscriptionPaymentRequest(BaseModel):
    user_email: EmailStr
    user_name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., pattern=r"^07[0-9]{8}$")
    plan_name: SubscriptionPlan
    payment_method: PaymentProvider = PaymentProvider.MTN

class WebhookEvent(BaseModel):
    id: str
    type: str
    created_at: datetime
    data: Dict[str, Any]

# Database Models (for storage)
class PaymentRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    invoice_number: str
    transaction_id: str
    status: PaymentStatus
    amount: int
    currency: str
    provider: Optional[PaymentProvider] = None
    phone_number: Optional[str] = None
    payment_reference: Optional[str] = None
    plan_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None

class UserSubscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    plan_name: SubscriptionPlan
    status: SubscriptionStatus
    payment_record_id: Optional[str] = None
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    auto_renew: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Existing models continue...

class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: QuestionType
    title: str
    description: Optional[str] = None
    required: bool = False
    options: Optional[List[str]] = None
    validation: Optional[Dict[str, Any]] = None
    
class Survey(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    questions: List[Question] = []
    organization_id: str
    created_by: str
    status: str = "draft"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    password_hash: str
    organization_id: str
    role: UserRole = UserRole.VIEWER
    status: str = "active"
    phone_number: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    last_login: Optional[datetime] = None
    surveys_created: int = 0
    current_plan: Optional[str] = None
    subscription_status: SubscriptionStatus = SubscriptionStatus.INACTIVE
    plan_expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Organization(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    plan: str = "Basic"
    survey_limit: int = 10
    storage_limit: int = 1  # GB
    survey_count: int = 0
    storage_used: float = 0.0
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Project Management Models
class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ActivityStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"

class FinancialCategory(str, Enum):
    PERSONNEL = "personnel"
    EQUIPMENT = "equipment"
    SUPPLIES = "supplies"
    TRAVEL = "travel"
    OVERHEAD = "overhead"
    OTHER = "other"

class KPIType(str, Enum):
    QUANTITATIVE = "quantitative"
    QUALITATIVE = "qualitative"

class DocumentType(str, Enum):
    PROPOSAL = "proposal"
    REPORT = "report"
    CONTRACT = "contract"
    BUDGET = "budget"
    EVALUATION = "evaluation"
    TRAINING_MATERIAL = "training_material"
    FINANCIAL = "financial"
    LEGAL = "legal"
    OTHER = "other"

class ReportFormat(str, Enum):
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"

class StakeholderType(str, Enum):
    DONOR = "donor"
    IMPLEMENTING_PARTNER = "implementing_partner"
    GOVERNMENT = "government"
    COMMUNITY = "community"
    BENEFICIARY = "beneficiary"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class BeneficiaryType(str, Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"

class ProjectIntegrationType(str, Enum):
    API = "api"
    WEBHOOK = "webhook"
    FILE_IMPORT = "file_import"
    MANUAL = "manual"

class ProjectAccessLevel(str, Enum):
    PUBLIC = "public"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"

# Project Management Models
class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    organization_id: str
    project_manager_id: str
    status: ProjectStatus = ProjectStatus.DRAFT
    start_date: datetime
    end_date: datetime
    budget_total: float
    budget_allocated: float = 0.0
    budget_utilized: float = 0.0
    beneficiaries_target: int = 0
    beneficiaries_reached: int = 0
    location: Optional[str] = None
    donor_organization: Optional[str] = None
    implementing_partners: List[str] = []
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Activity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    description: Optional[str] = None
    status: ActivityStatus = ActivityStatus.NOT_STARTED
    assigned_to: str  # User ID
    assigned_team: Optional[str] = None  # Team/Department name
    start_date: datetime
    end_date: datetime
    planned_start_date: datetime  # Original planned start
    planned_end_date: datetime    # Original planned end
    
    # Budget and resource allocation
    budget_allocated: float = 0.0
    budget_utilized: float = 0.0
    
    # Output and target tracking
    planned_output: Optional[str] = None  # Planned deliverable/target
    target_quantity: Optional[float] = None  # Quantitative target
    actual_output: Optional[str] = None   # Actual deliverable achieved
    achieved_quantity: Optional[float] = None  # Quantitative achievement
    
    # Progress and completion
    progress_percentage: float = 0.0  # Auto-calculated from outputs
    completion_variance: float = 0.0  # Planned vs Actual (%)
    schedule_variance_days: int = 0   # Days ahead/behind schedule
    
    # Milestones and tracking
    milestones: List[Dict[str, Any]] = []  # Planned milestones with dates
    completed_milestones: List[str] = []   # IDs of completed milestones
    
    # Status and notes
    status_notes: Optional[str] = None
    comments: List[Dict[str, Any]] = []  # Status updates and comments
    risk_level: str = "low"  # low, medium, high, critical
    
    # Legacy fields (maintained for compatibility)
    deliverables: List[str] = []
    dependencies: List[str] = []
    
    # Tracking fields
    last_updated_by: str
    organization_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BudgetEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    category: FinancialCategory
    item_name: str
    description: Optional[str] = None
    budgeted_amount: float
    allocated_amount: float = 0.0
    utilized_amount: float = 0.0
    remaining_amount: float = 0.0
    budget_period: str  # e.g., "2024-Q1", "2024-01", "Year-1"
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class KPIIndicator(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    description: Optional[str] = None
    type: KPIType
    measurement_unit: Optional[str] = None
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    achievement_percentage: float = 0.0
    data_source: Optional[str] = None
    frequency: str = "monthly"  # daily, weekly, monthly, quarterly, annual
    responsible_person: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Beneficiary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    unique_id: str  # National ID, passport, or project-specific ID
    name: str
    gender: Gender
    age: Optional[int] = None
    location: Optional[str] = None
    contact_info: Optional[str] = None
    beneficiary_type: BeneficiaryType
    services_received: List[str] = []
    enrollment_date: datetime
    status: str = "active"  # active, inactive, graduated, dropped_out
    household_size: Optional[int] = None
    income_level: Optional[str] = None
    education_level: Optional[str] = None
    additional_demographics: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    description: Optional[str] = None
    document_type: DocumentType
    file_name: str
    file_size: int
    mime_type: str
    file_url: str
    version: str = "1.0"
    uploaded_by: str
    access_level: ProjectAccessLevel = ProjectAccessLevel.RESTRICTED
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ReportTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    organization_id: str
    template_type: str  # donor_report, internal_report, financial_report, etc.
    format: ReportFormat
    sections: List[Dict[str, Any]] = []
    variables: List[str] = []  # Placeholder variables in template
    frequency: str = "monthly"  # daily, weekly, monthly, quarterly, annual
    auto_generate: bool = False
    recipients: List[str] = []
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PartnerOrganization(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    parent_organization_id: str  # Reference to main organization
    contact_person: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    organization_type: str = "NGO"  # NGO, Government, Private, International
    partnership_start_date: datetime
    partnership_end_date: Optional[datetime] = None
    status: str = "active"  # active, inactive, suspended
    capabilities: List[str] = []
    projects_involved: List[str] = []
    performance_rating: Optional[float] = None
    website: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectDashboardData(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    total_budget: float
    budget_utilized: float
    utilization_rate: float
    budget_utilization: float  # Added for frontend compatibility
    total_beneficiaries: int
    beneficiaries_reached: int
    kpi_achievement_rate: float
    kpi_performance: Dict[str, Any]  # Added for frontend compatibility
    overdue_activities: int  # Added for frontend compatibility
    recent_activities: List[Dict[str, Any]]
    budget_by_category: Dict[str, float]
    projects_by_status: Dict[str, int]
    # Enhanced analytics data
    activity_insights: Dict[str, Any]
    performance_trends: Dict[str, Any]
    risk_indicators: Dict[str, Any]
    completion_analytics: Dict[str, Any]

# AI Survey Generation Models
class AISurveyGenerationRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=1000)
    survey_type: Optional[str] = "general"
    target_audience: Optional[str] = None
    question_count: Optional[int] = Field(default=10, ge=5, le=50)
    language: Optional[str] = "en"
    include_demographics: bool = True

class DocumentUploadRequest(BaseModel):
    file_name: str
    file_type: str
    organization_id: str

class TranslatedSurveyResponse(BaseModel):
    original_language: str
    target_language: str
    translated_survey: Survey
    translation_notes: Optional[List[str]] = None

# User creation for admin panel
class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: Optional[str] = None  # Auto-generated if not provided
    role: UserRole = UserRole.VIEWER
    phone_number: Optional[str] = Field(None, pattern=r"^07[0-9]{8}$")
    department: Optional[str] = None
    position: Optional[str] = None
    partner_organization_id: Optional[str] = None
    supervisor_id: Optional[str] = None
    access_level: str = "standard"  # standard, elevated, restricted
    permissions: Dict[str, bool] = {}
    send_credentials_email: bool = True
    temporary_password: bool = True

# Advanced user creation (alias for admin panel)
class UserCreateAdvanced(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: Optional[str] = None  # Auto-generated if not provided
    role: UserRole = UserRole.VIEWER
    phone_number: Optional[str] = Field(None, pattern=r"^07[0-9]{8}$")
    department: Optional[str] = None
    position: Optional[str] = None
    partner_organization_id: Optional[str] = None
    supervisor_id: Optional[str] = None
    access_level: str = "standard"  # standard, elevated, restricted
    permissions: Dict[str, bool] = {}
    send_credentials_email: bool = True
    temporary_password: bool = True

class BulkCreateUsersRequest(BaseModel):
    users: List[CreateUserRequest]
    send_emails: bool = True

class CreatePartnerRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    contact_person: str = Field(..., min_length=2, max_length=100)
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    organization_type: str = "NGO"
    partnership_start_date: datetime
    partnership_end_date: Optional[datetime] = None
    website: Optional[str] = None
    capabilities: List[str] = []

# Partner organization creation (alias for admin panel)
class PartnerOrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    contact_person: str = Field(..., min_length=2, max_length=100)
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    organization_type: str = "NGO"
    partnership_start_date: datetime
    partnership_end_date: Optional[datetime] = None
    website: Optional[str] = None
    capabilities: List[str] = []

class PartnerOrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    organization_type: Optional[str] = None
    partnership_end_date: Optional[datetime] = None
    status: Optional[str] = None
    website: Optional[str] = None
    capabilities: Optional[List[str]] = None
    performance_rating: Optional[float] = None

class PartnerPerformance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    partner_id: str
    evaluation_period: str
    delivery_score: float = Field(..., ge=0, le=100)
    quality_score: float = Field(..., ge=0, le=100)
    timeliness_score: float = Field(..., ge=0, le=100)
    communication_score: float = Field(..., ge=0, le=100)
    overall_score: float = Field(..., ge=0, le=100)
    comments: Optional[str] = None
    evaluator_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PartnerPerformanceCreate(BaseModel):
    partner_id: str
    evaluation_period: str
    delivery_score: float = Field(..., ge=0, le=100)
    quality_score: float = Field(..., ge=0, le=100)
    timeliness_score: float = Field(..., ge=0, le=100)
    communication_score: float = Field(..., ge=0, le=100)
    comments: Optional[str] = None

class OrganizationBranding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    primary_color: str = "#3B82F6"
    secondary_color: str = "#64748B"
    accent_color: str = "#10B981"
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    custom_css: Optional[str] = None
    white_label: bool = False
    custom_domain: Optional[str] = None
    footer_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrganizationBrandingCreate(BaseModel):
    primary_color: str = "#3B82F6"
    secondary_color: str = "#64748B" 
    accent_color: str = "#10B981"
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    custom_css: Optional[str] = None
    white_label: bool = False
    custom_domain: Optional[str] = None
    footer_text: Optional[str] = None

class EmailTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    subject: str
    body_html: str
    body_text: Optional[str] = None
    organization_id: str
    template_type: str  # welcome, password_reset, credentials, etc.
    variables: List[str] = []  # Available template variables
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class EmailLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    recipient_email: str
    recipient_name: Optional[str] = None
    subject: str
    template_id: Optional[str] = None
    template_type: Optional[str] = None
    status: str = "sent"  # sent, failed, pending
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}

# Response models
class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    status: str
    phone_number: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    current_plan: Optional[str] = None
    subscription_status: SubscriptionStatus
    last_login: Optional[datetime] = None
    created_at: datetime

# Additional Create/Update models
class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    plan: str = "Basic"

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[str] = None
    survey_limit: Optional[int] = None
    storage_limit: Optional[int] = None

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.VIEWER
    organization_id: Optional[str] = None
    phone_number: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    phone_number: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse
    organization: Organization

class SurveyCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    questions: List[Question] = []
    status: str = "draft"

class SurveyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    questions: Optional[List[Question]] = None
    status: Optional[str] = None

class SurveyResponseCreate(BaseModel):
    survey_id: Optional[str] = None
    responses: Dict[str, Any] = {}
    respondent_info: Optional[Dict[str, Any]] = None

class SurveyResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    survey_id: str
    responses: Dict[str, Any] = {}
    respondent_info: Optional[Dict[str, Any]] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

class AnalyticsData(BaseModel):
    total_responses: int = 0
    response_rate: float = 0.0
    average_completion_time: float = 0.0
    top_performing_survey: Optional[str] = None
    monthly_growth: float = 0.0
    storage_growth: float = 0.0

class Enumerator(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    phone_number: str
    organization_id: str
    access_password: str
    assigned_surveys: List[str] = []
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_sync: Optional[datetime] = None

class EnumeratorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone_number: str
    access_password: str = Field(..., min_length=6)

class EnumeratorAssignment(BaseModel):
    enumerator_id: str
    survey_id: str

# Payment service models
class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    user_id: Optional[str] = None
    irembopay_invoice_number: str
    transaction_id: str
    amount: float
    currency: str = "RWF"
    plan: SubscriptionPlan
    payment_status: PaymentStatus = PaymentStatus.PENDING
    payment_reference: Optional[str] = None
    payment_method: Optional[str] = None
    irembopay_transaction_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PaymentTransactionCreate(BaseModel):
    organization_id: str
    user_id: Optional[str] = None
    irembopay_invoice_number: str
    transaction_id: str
    amount: float
    currency: str = "RWF"
    plan: SubscriptionPlan
    metadata: Optional[Dict[str, Any]] = None

class IremboPayInvoiceRequest(BaseModel):
    organization_id: str
    plan: SubscriptionPlan
    user_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None

class IremboPayInvoiceResponse(BaseModel):
    success: bool
    invoice_number: str
    payment_link_url: str
    amount: float
    currency: str
    status: str

# AI Service models
class SurveyQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: QuestionType
    question: str
    required: bool = False
    options: Optional[List[str]] = None
    validation: Optional[Dict[str, Any]] = None

class SurveyGenerationContext(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    documents: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentUpload(BaseModel):
    filename: str
    content_type: str
    file_size: int
    content: str

# Project service models
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    project_manager_id: str
    start_date: datetime
    end_date: datetime
    budget_total: float = Field(..., gt=0)
    beneficiaries_target: int = Field(..., ge=0)
    location: Optional[str] = None
    donor_organization: Optional[str] = None
    implementing_partners: List[str] = []
    tags: List[str] = []

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_manager_id: Optional[str] = None
    status: Optional[ProjectStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget_total: Optional[float] = None
    beneficiaries_target: Optional[int] = None
    location: Optional[str] = None
    donor_organization: Optional[str] = None
    implementing_partners: Optional[List[str]] = None
    tags: Optional[List[str]] = None

class ActivityCreate(BaseModel):
    project_id: str
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    assigned_to: str
    start_date: datetime
    end_date: datetime
    budget_allocated: float = Field(..., ge=0)
    deliverables: List[str] = []
    dependencies: List[str] = []

class ActivityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ActivityStatus] = None
    assigned_to: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget_allocated: Optional[float] = None
    budget_utilized: Optional[float] = None
    progress_percentage: Optional[float] = None
    deliverables: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None

class BudgetItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    category: FinancialCategory
    item_name: str
    description: Optional[str] = None
    budgeted_amount: float
    allocated_amount: float = 0.0
    utilized_amount: float = 0.0
    remaining_amount: float = 0.0
    budget_period: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BudgetItemCreate(BaseModel):
    project_id: str
    category: FinancialCategory
    item_name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    budgeted_amount: float = Field(..., gt=0)
    budget_period: str = Field(..., min_length=1)

class BudgetItemUpdate(BaseModel):
    category: Optional[FinancialCategory] = None
    item_name: Optional[str] = None
    description: Optional[str] = None
    budgeted_amount: Optional[float] = None
    allocated_amount: Optional[float] = None
    utilized_amount: Optional[float] = None
    budget_period: Optional[str] = None

class KPIIndicatorCreate(BaseModel):
    project_id: str
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    type: KPIType
    measurement_unit: Optional[str] = None
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    data_source: Optional[str] = None
    frequency: str = "monthly"
    responsible_person: str

class KPIIndicatorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[KPIType] = None
    measurement_unit: Optional[str] = None
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    data_source: Optional[str] = None
    frequency: Optional[str] = None
    responsible_person: Optional[str] = None

class BeneficiaryCreate(BaseModel):
    project_id: str
    unique_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)  # Single name field to match main model
    gender: Gender  # Use Gender enum to match main model
    age: Optional[int] = None
    location: Optional[str] = None
    contact_info: Optional[str] = None  # Match main model field name
    beneficiary_type: BeneficiaryType  # Required field from main model
    enrollment_date: datetime = Field(default_factory=datetime.utcnow)  # Required field from main model
    household_size: Optional[int] = None
    education_level: Optional[str] = None

class BeneficiaryUpdate(BaseModel):
    unique_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    contact_phone: Optional[str] = None
    household_size: Optional[int] = None
    education_level: Optional[str] = None
    employment_status: Optional[str] = None
    status: Optional[str] = None

class ProjectDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    description: Optional[str] = None
    document_type: DocumentType
    file_name: str
    file_size: int
    mime_type: str
    file_url: str
    version: str = "1.0"
    uploaded_by: str
    access_level: ProjectAccessLevel = ProjectAccessLevel.RESTRICTED
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectDocumentCreate(BaseModel):
    project_id: str
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    document_type: DocumentType
    file_name: str
    file_size: int
    mime_type: str
    file_url: str
    access_level: ProjectAccessLevel = ProjectAccessLevel.RESTRICTED
    tags: List[str] = []

class ProjectDocumentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    document_type: Optional[DocumentType] = None
    access_level: Optional[ProjectAccessLevel] = None
    tags: Optional[List[str]] = None

class PartnerResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    contact_person: str
    contact_email: str
    contact_phone: Optional[str] = None
    organization_type: str
    status: str
    partnership_start_date: datetime
    performance_rating: Optional[float] = None
    created_at: datetime