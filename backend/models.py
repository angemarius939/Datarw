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
    PROJECT_MANAGER = "Project Manager"
    ME_OFFICER = "M&E Officer"
    DONOR_VIEWER = "Donor Viewer"
    DIRECTOR = "Director"
    OFFICER = "Officer"
    FIELD_STAFF = "Field Staff"
    PARTNER_STAFF = "Partner Staff"
    SYSTEM_ADMIN = "System Admin"

class SubscriptionPlan(str, Enum):
    BASIC = "Basic"
    PROFESSIONAL = "Professional"
    ENTERPRISE = "Enterprise"

class SurveyStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE_SINGLE = "multiple_choice_single"
    MULTIPLE_CHOICE_MULTIPLE = "multiple_choice_multiple"
    SHORT_TEXT = "short_text"
    LONG_TEXT = "long_text"
    RATING_SCALE = "rating_scale"
    LIKERT_SCALE = "likert_scale"
    RANKING = "ranking"
    DROPDOWN = "dropdown"
    MATRIX_GRID = "matrix_grid"
    FILE_UPLOAD = "file_upload"
    DATE_PICKER = "date_picker"
    TIME_PICKER = "time_picker"
    DATETIME_PICKER = "datetime_picker"
    SLIDER = "slider"
    NUMERIC_SCALE = "numeric_scale"
    IMAGE_CHOICE = "image_choice"
    YES_NO = "yes_no"
    SIGNATURE = "signature"
    CALCULATION = "calculation"
    SKIP_LOGIC = "skip_logic"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    EXPIRED = "expired"

# Project Management Enums
class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ActivityStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"

class BudgetCategory(str, Enum):
    ADMINISTRATION = "administration"
    LOGISTICS = "logistics"
    TRAINING = "training"
    PERSONNEL = "personnel"
    EQUIPMENT = "equipment"
    TRAVEL = "travel"
    COMMUNICATIONS = "communications"
    MONITORING = "monitoring"
    OTHER = "other"

class IndicatorType(str, Enum):
    QUANTITATIVE = "quantitative"
    QUALITATIVE = "qualitative"

class IndicatorLevel(str, Enum):
    OUTPUT = "output"
    OUTCOME = "outcome"
    IMPACT = "impact"

class DocumentType(str, Enum):
    PROJECT_DOCUMENT = "project_document"
    DONOR_AGREEMENT = "donor_agreement"
    REPORT = "report"
    POLICY = "policy"
    TRAINING_MATERIAL = "training_material"
    FINANCIAL = "financial"
    LEGAL = "legal"
    OTHER = "other"

# Base Models
class BaseDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True  # Updated for Pydantic v2

# Organization Models
class Organization(BaseDocument):
    name: str
    plan: SubscriptionPlan
    survey_limit: int = Field(default=4)
    storage_limit: float = Field(default=1.0)  # in GB
    survey_count: int = Field(default=0)
    storage_used: float = Field(default=0.0)  # in GB
    status: str = Field(default="active")
    irembopay_account_id: Optional[str] = None

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
    options: List[str] = Field(default_factory=list)  # For multiple choice, dropdown, image choice
    scale_min: Optional[int] = None  # For rating/slider
    scale_max: Optional[int] = None  # For rating/slider
    scale_labels: Optional[List[str]] = Field(default_factory=list)  # For likert scale labels
    matrix_rows: Optional[List[str]] = Field(default_factory=list)  # For matrix questions
    matrix_columns: Optional[List[str]] = Field(default_factory=list)  # For matrix questions
    file_types_allowed: Optional[List[str]] = Field(default_factory=list)  # For file upload
    max_file_size_mb: Optional[int] = None  # For file upload
    date_format: Optional[str] = None  # For date/time pickers
    slider_step: Optional[float] = None  # For slider
    image_urls: Optional[List[str]] = Field(default_factory=list)  # For image choice
    multiple_selection: bool = False  # For multiple choice multiple
    skip_logic: Optional[Dict[str, Any]] = None
    calculation: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = Field(default_factory=dict)  # Custom validation

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
    irembopay_invoice_number: str
    transaction_id: str
    amount: float
    currency: str = "RWF"
    plan: SubscriptionPlan
    payment_status: PaymentStatus = PaymentStatus.PENDING
    irembopay_transaction_id: Optional[str] = None
    payment_reference: Optional[str] = None
    payment_method: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PaymentTransactionCreate(BaseModel):
    organization_id: str
    user_id: Optional[str] = None
    irembopay_invoice_number: str
    transaction_id: str
    amount: float
    currency: str = "RWF"
    plan: SubscriptionPlan
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Enumerator Models
class Enumerator(BaseDocument):
    name: str
    email: EmailStr
    phone: str
    organization_id: str
    assigned_surveys: List[str] = Field(default_factory=list)
    access_password: str  # Special password for survey access
    status: str = Field(default="active")
    last_sync: Optional[datetime] = None

class EnumeratorCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    access_password: str

class EnumeratorAssignment(BaseModel):
    enumerator_id: str
    survey_id: str

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

# AI Survey Generation Models
class AISurveyGenerationRequest(BaseModel):
    description: str
    target_audience: Optional[str] = None
    survey_purpose: Optional[str] = None
    question_count: Optional[int] = Field(default=10, ge=1, le=50)
    include_demographics: bool = False
    document_context: Optional[str] = None  # Context extracted from uploaded documents

class DocumentUpload(BaseModel):
    filename: str
    content_type: str
    file_size: int
    content: str  # Extracted text content

class SurveyGenerationContext(BaseDocument):
    organization_id: str
    uploaded_documents: List[DocumentUpload] = Field(default_factory=list)
    business_profile: Optional[str] = None
    participant_profiles: Optional[str] = None
    policies: Optional[str] = None
    strategic_documents: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
class IremboPayInvoiceRequest(BaseModel):
    transaction_id: str
    amount: float
    currency: str = "RWF"
    description: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_name: Optional[str] = None

class IremboPayInvoiceResponse(BaseModel):
    success: bool
    invoice_number: str
    payment_link_url: str
    amount: float
    currency: str
    status: str

# Project Management Models
class Project(BaseDocument):
    title: str
    description: str
    organization_id: str
    sector: str
    donor: str
    implementation_start: datetime
    implementation_end: datetime
    total_budget: float
    budget_currency: str = "RWF"
    status: ProjectStatus = ProjectStatus.PLANNING
    team_members: List[str] = Field(default_factory=list)  # User IDs
    project_manager_id: Optional[str] = None
    me_officer_id: Optional[str] = None
    location: Optional[str] = None
    target_beneficiaries: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProjectCreate(BaseModel):
    title: str
    description: str
    sector: str
    donor: str
    implementation_start: datetime
    implementation_end: datetime
    total_budget: float
    budget_currency: str = "RWF"
    team_members: List[str] = Field(default_factory=list)
    project_manager_id: Optional[str] = None
    me_officer_id: Optional[str] = None
    location: Optional[str] = None
    target_beneficiaries: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    sector: Optional[str] = None
    donor: Optional[str] = None
    implementation_start: Optional[datetime] = None
    implementation_end: Optional[datetime] = None
    total_budget: Optional[float] = None
    budget_currency: Optional[str] = None
    status: Optional[ProjectStatus] = None
    team_members: Optional[List[str]] = None
    project_manager_id: Optional[str] = None
    me_officer_id: Optional[str] = None
    location: Optional[str] = None
    target_beneficiaries: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class Activity(BaseDocument):
    project_id: str
    title: str
    description: str
    organization_id: str
    responsible_user_id: str
    start_date: datetime
    end_date: datetime
    status: ActivityStatus = ActivityStatus.NOT_STARTED
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    budget_allocated: Optional[float] = None
    budget_spent: Optional[float] = None
    deliverables: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)  # Activity IDs
    results_framework_link: Optional[str] = None
    notes: Optional[str] = None

class ActivityCreate(BaseModel):
    project_id: str
    title: str
    description: str
    responsible_user_id: str
    start_date: datetime
    end_date: datetime
    budget_allocated: Optional[float] = None
    deliverables: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    results_framework_link: Optional[str] = None
    notes: Optional[str] = None

class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    responsible_user_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[ActivityStatus] = None
    progress_percentage: Optional[float] = None
    budget_spent: Optional[float] = None
    deliverables: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    results_framework_link: Optional[str] = None
    notes: Optional[str] = None

class BudgetItem(BaseDocument):
    project_id: str
    organization_id: str
    category: BudgetCategory
    description: str
    budgeted_amount: float
    spent_amount: float = Field(default=0.0)
    currency: str = "RWF"
    period_start: datetime
    period_end: datetime
    responsible_user_id: Optional[str] = None
    notes: Optional[str] = None

class BudgetItemCreate(BaseModel):
    project_id: str
    category: BudgetCategory
    description: str
    budgeted_amount: float
    currency: str = "RWF"
    period_start: datetime
    period_end: datetime
    responsible_user_id: Optional[str] = None
    notes: Optional[str] = None

class BudgetItemUpdate(BaseModel):
    category: Optional[BudgetCategory] = None
    description: Optional[str] = None
    budgeted_amount: Optional[float] = None
    spent_amount: Optional[float] = None
    currency: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    responsible_user_id: Optional[str] = None
    notes: Optional[str] = None

class KPIIndicator(BaseDocument):
    project_id: str
    organization_id: str
    name: str
    description: str
    indicator_type: IndicatorType
    level: IndicatorLevel
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit_of_measurement: Optional[str] = None
    frequency: str  # Monthly, Quarterly, Annually
    responsible_user_id: Optional[str] = None
    data_source: Optional[str] = None
    collection_method: Optional[str] = None
    disaggregation: Dict[str, Any] = Field(default_factory=dict)  # Gender, Age, Location, etc.

class KPIIndicatorCreate(BaseModel):
    project_id: str
    name: str
    description: str
    indicator_type: IndicatorType
    level: IndicatorLevel
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    unit_of_measurement: Optional[str] = None
    frequency: str
    responsible_user_id: Optional[str] = None
    data_source: Optional[str] = None
    collection_method: Optional[str] = None
    disaggregation: Dict[str, Any] = Field(default_factory=dict)

class KPIIndicatorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    indicator_type: Optional[IndicatorType] = None
    level: Optional[IndicatorLevel] = None
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit_of_measurement: Optional[str] = None
    frequency: Optional[str] = None
    responsible_user_id: Optional[str] = None
    data_source: Optional[str] = None
    collection_method: Optional[str] = None
    disaggregation: Optional[Dict[str, Any]] = None

class Beneficiary(BaseDocument):
    organization_id: str
    project_ids: List[str] = Field(default_factory=list)
    unique_id: str  # Organization-specific beneficiary ID
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    household_size: Optional[int] = None
    income_level: Optional[str] = None
    education_level: Optional[str] = None
    employment_status: Optional[str] = None
    disability_status: Optional[str] = None
    program_participation_history: List[Dict[str, Any]] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    consent_forms: List[str] = Field(default_factory=list)  # File URLs
    photos: List[str] = Field(default_factory=list)  # File URLs
    documents: List[str] = Field(default_factory=list)  # File URLs
    geographical_coordinates: Optional[Dict[str, float]] = None  # lat, lng

class BeneficiaryCreate(BaseModel):
    unique_id: str
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    household_size: Optional[int] = None
    income_level: Optional[str] = None
    education_level: Optional[str] = None
    employment_status: Optional[str] = None
    disability_status: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    geographical_coordinates: Optional[Dict[str, float]] = None

class BeneficiaryUpdate(BaseModel):
    unique_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    household_size: Optional[int] = None
    income_level: Optional[str] = None
    education_level: Optional[str] = None
    employment_status: Optional[str] = None
    disability_status: Optional[str] = None
    program_participation_history: Optional[List[Dict[str, Any]]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    consent_forms: Optional[List[str]] = None
    photos: Optional[List[str]] = None
    documents: Optional[List[str]] = None
    geographical_coordinates: Optional[Dict[str, float]] = None

class ProjectDocument(BaseDocument):
    project_id: str
    organization_id: str
    title: str
    description: Optional[str] = None
    document_type: DocumentType
    file_url: str
    file_name: str
    file_size: int
    mime_type: str
    version: str = "1.0"
    uploaded_by: str  # User ID
    tags: List[str] = Field(default_factory=list)
    access_level: str = Field(default="project")  # project, organization, public
    is_latest_version: bool = True

class ProjectDocumentCreate(BaseModel):
    project_id: str
    title: str
    description: Optional[str] = None
    document_type: DocumentType
    file_name: str
    file_size: int
    mime_type: str
    tags: List[str] = Field(default_factory=list)
    access_level: str = "project"

class ProjectDocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    document_type: Optional[DocumentType] = None
    tags: Optional[List[str]] = None
    access_level: Optional[str] = None

# Dashboard and Reporting Models
class ProjectDashboardData(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    overdue_activities: int
    budget_utilization: float
    kpi_performance: Dict[str, float]
    recent_activities: List[Dict[str, Any]]
    project_performance_summary: List[Dict[str, Any]]

class ReportTemplate(BaseDocument):
    organization_id: str
    name: str
    description: str
    report_type: str  # monthly, quarterly, annual, custom
    template_structure: Dict[str, Any]
    default_filters: Dict[str, Any] = Field(default_factory=dict)
    output_formats: List[str] = Field(default=["pdf", "excel"])
    created_by: str

class GeneratedReport(BaseDocument):
    organization_id: str
    project_id: Optional[str] = None
    template_id: str
    report_title: str
    report_period_start: datetime
    report_period_end: datetime
    generated_by: str
    file_url: str
    file_format: str
    generation_date: datetime = Field(default_factory=datetime.utcnow)
    parameters_used: Dict[str, Any] = Field(default_factory=dict)