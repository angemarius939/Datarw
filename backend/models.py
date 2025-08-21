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
    phone_number: str = Field(..., regex=r"^07[0-9]{8}$")

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
    phone_number: str = Field(..., regex=r"^07[0-9]{8}$")
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
    phone_number: str = Field(..., regex=r"^07[0-9]{8}$")
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
    assigned_to: str
    start_date: datetime
    end_date: datetime
    budget_allocated: float = 0.0
    budget_utilized: float = 0.0
    progress_percentage: float = 0.0
    deliverables: List[str] = []
    dependencies: List[str] = []
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
    total_beneficiaries: int
    beneficiaries_reached: int
    kpi_achievement_rate: float
    recent_activities: List[Dict[str, Any]]
    budget_by_category: Dict[str, float]
    projects_by_status: Dict[str, int]

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
    phone_number: Optional[str] = Field(None, regex=r"^07[0-9]{8}$")
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