from __future__ import annotations
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid

from pydantic import BaseModel, Field, ConfigDict, EmailStr

# Global model config: be permissive to avoid validation crashes while restoring
class SafeModel(BaseModel):
    model_config = ConfigDict(extra='allow', arbitrary_types_allowed=True)

# -------------------- Enums --------------------
class ProjectStatus(str, Enum):
    PLANNED = 'planned'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    ON_HOLD = 'on_hold'
    CANCELLED = 'cancelled'

class ActivityStatus(str, Enum):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    DELAYED = 'delayed'
    CANCELLED = 'cancelled'

class Gender(str, Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

class UserRole(str, Enum):
    ADMIN = 'Admin'
    DIRECTOR = 'Director'
    EDITOR = 'Editor'
    VIEWER = 'Viewer'
    SYSTEM_ADMIN = 'System Admin'

class ServiceType(str, Enum):
    TRAINING = 'training'
    DISTRIBUTION = 'distribution'
    GRANT = 'grant'
    MENTORSHIP = 'mentorship'
    CONSULTATION = 'consultation'
    FOLLOW_UP = 'follow_up'
    ASSESSMENT = 'assessment'

class BeneficiaryStatus(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    GRADUATED = 'graduated'
    DROPPED_OUT = 'dropped_out'

class RiskLevel(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

# -------------------- Core / Auth --------------------
class Organization(SafeModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    plan: Optional[str] = 'Basic'
    survey_limit: Optional[int] = 0
    storage_limit: Optional[int] = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrganizationCreate(SafeModel):
    name: str
    plan: Optional[str] = 'Basic'

class OrganizationUpdate(SafeModel):
    name: Optional[str] = None
    plan: Optional[str] = None

class User(SafeModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    organization_id: str
    role: UserRole = UserRole.EDITOR
    status: Optional[str] = 'active'
    password_hash: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(SafeModel):
    email: EmailStr
    name: str
    organization_id: str
    role: UserRole = UserRole.EDITOR
    password: Optional[str] = None

class UserUpdate(SafeModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[UserRole] = None

class TokenData(SafeModel):
    user_id: str
    organization_id: Optional[str] = None
    role: Optional[UserRole] = None

# -------------------- Projects --------------------
class Project(SafeModel):
    id: str | None = None
    _id: Optional[str] = None
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNED
    organization_id: str
    budget_total: float = 0.0
    budget_utilized: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectCreate(SafeModel):
    name: str
    description: Optional[str] = None
    status: Optional[ProjectStatus] = ProjectStatus.PLANNED
    organization_id: Optional[str] = None
    budget_total: float = 0.0

class ProjectUpdate(SafeModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    budget_total: Optional[float] = None
    budget_utilized: Optional[float] = None

# -------------------- Activities --------------------
class Activity(SafeModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    description: Optional[str] = None
    status: ActivityStatus = ActivityStatus.NOT_STARTED
    assigned_to: Optional[str] = None
    assigned_team: Optional[str] = None
    start_date: datetime
    end_date: datetime
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None

    budget_allocated: float = 0.0
    budget_utilized: float = 0.0

    planned_output: Optional[str] = None
    target_quantity: Optional[float] = None
    actual_output: Optional[str] = None
    achieved_quantity: Optional[float] = None
    measurement_unit: Optional[str] = None

    progress_percentage: float = 0.0
    completion_variance: float = 0.0
    schedule_variance_days: int = 0

    milestones: List[Dict[str, Any]] = []
    completed_milestones: List[str] = []

    status_notes: Optional[str] = None
    comments: List[Dict[str, Any]] = []
    risk_level: str = 'low'

    deliverables: List[str] = []
    dependencies: List[str] = []

    last_updated_by: Optional[str] = None
    organization_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ActivityCreate(SafeModel):
    project_id: str
    name: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    assigned_team: Optional[str] = None
    start_date: datetime
    end_date: datetime
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    budget_allocated: float = 0.0
    planned_output: Optional[str] = None
    target_quantity: Optional[float] = None
    measurement_unit: Optional[str] = None
    milestones: List[Dict[str, Any]] = []
    deliverables: List[str] = []
    dependencies: List[str] = []
    status_notes: Optional[str] = None
    risk_level: str = 'low'

class ActivityUpdate(SafeModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ActivityStatus] = None
    assigned_to: Optional[str] = None
    assigned_team: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    budget_allocated: Optional[float] = None
    budget_utilized: Optional[float] = None
    planned_output: Optional[str] = None
    target_quantity: Optional[float] = None
    actual_output: Optional[str] = None
    achieved_quantity: Optional[float] = None
    progress_percentage: Optional[float] = None
    measurement_unit: Optional[str] = None
    milestones: Optional[List[Dict[str, Any]]] = None
    completed_milestones: Optional[List[str]] = None
    status_notes: Optional[str] = None
    risk_level: Optional[str] = None
    deliverables: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None

# -------------------- Budget Items --------------------
class BudgetItem(SafeModel):
    id: Optional[str] = None
    _id: Optional[str] = None
    project_id: str
    activity_id: Optional[str] = None
    category: Optional[str] = None
    budgeted_amount: float = 0.0
    allocated_amount: float = 0.0
    utilized_amount: float = 0.0
    spent_amount: float = 0.0
    organization_id: str
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BudgetItemCreate(SafeModel):
    project_id: str
    activity_id: Optional[str] = None
    category: Optional[str] = None
    budgeted_amount: float = 0.0
    allocated_amount: float = 0.0
    utilized_amount: float = 0.0
    spent_amount: float = 0.0

class BudgetItemUpdate(SafeModel):
    category: Optional[str] = None
    budgeted_amount: Optional[float] = None
    allocated_amount: Optional[float] = None
    utilized_amount: Optional[float] = None
    spent_amount: Optional[float] = None

# -------------------- KPI --------------------
class KPIIndicator(SafeModel):
    id: Optional[str] = None
    _id: Optional[str] = None
    project_id: Optional[str] = None
    organization_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class KPIIndicatorCreate(SafeModel):
    project_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    unit: Optional[str] = None
    target_value: Optional[float] = None

class KPIIndicatorUpdate(SafeModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None

# -------------------- Beneficiaries --------------------
class Beneficiary(SafeModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # Basic Information
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: str
    age: Optional[int] = None
    date_of_birth: Optional[datetime] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    
    # Identification
    national_id: Optional[str] = None
    system_id: Optional[str] = None
    alternative_id: Optional[str] = None
    
    # Location Information
    address: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    gps_accuracy: Optional[float] = None
    service_location: Optional[str] = None
    household_gps_lat: Optional[float] = None
    household_gps_lng: Optional[float] = None
    
    # Project Linkages
    project_ids: List[str] = []
    activity_ids: List[str] = []
    primary_project_id: Optional[str] = None
    
    # Status and Tracking
    status: BeneficiaryStatus = BeneficiaryStatus.ACTIVE
    enrollment_date: datetime = Field(default_factory=datetime.utcnow)
    graduation_date: Optional[datetime] = None
    last_service_date: Optional[datetime] = None
    
    # Risk and Progress
    risk_level: RiskLevel = RiskLevel.LOW
    risk_score: Optional[float] = None
    progress_score: Optional[float] = None
    
    # Documents and Media
    profile_photo_url: Optional[str] = None
    document_urls: List[str] = []
    verification_status: str = "pending"
    
    # Custom Attributes
    custom_fields: Dict[str, Any] = {}
    tags: List[str] = []
    
    # Metadata
    organization_id: str
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BeneficiaryCreate(SafeModel):
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: str
    age: Optional[int] = None
    date_of_birth: Optional[datetime] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    national_id: Optional[str] = None
    address: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    project_ids: List[str] = []
    activity_ids: List[str] = []
    custom_fields: Dict[str, Any] = {}
    tags: List[str] = []

class BeneficiaryUpdate(SafeModel):
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    date_of_birth: Optional[datetime] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    national_id: Optional[str] = None
    address: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    project_ids: Optional[List[str]] = None
    activity_ids: Optional[List[str]] = None
    status: Optional[BeneficiaryStatus] = None
    risk_level: Optional[RiskLevel] = None
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

# -------------------- Project Documents --------------------
class ProjectDocument(SafeModel):
    id: Optional[str] = None
    _id: Optional[str] = None
    project_id: str
    file_url: str
    uploaded_by: str
    organization_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectDocumentCreate(SafeModel):
    project_id: str
    title: Optional[str] = None
    description: Optional[str] = None

class ProjectDocumentUpdate(SafeModel):
    title: Optional[str] = None
    description: Optional[str] = None

# -------------------- Dashboard DTO --------------------
class ProjectDashboardData(SafeModel):
    total_projects: int = 0
    active_projects: int = 0
    completed_projects: int = 0
    total_budget: float = 0.0
    budget_utilized: float = 0.0
    utilization_rate: float = 0.0
    total_beneficiaries: int = 0
    beneficiaries_reached: int = 0
    kpi_achievement_rate: float = 0.0
    budget_by_category: Dict[str, float] = {}
    projects_by_status: Dict[str, int] = {}
    recent_activities: List[Dict[str, Any]] = []
    overdue_activities: int = 0
    activity_insights: Dict[str, Any] = {}
    performance_trends: Dict[str, Any] = {}
    risk_indicators: Dict[str, Any] = {}
    completion_analytics: Dict[str, Any] = {}

# -------------------- Surveys (minimal for compatibility) --------------------
class Survey(SafeModel):
    id: Optional[str] = None
    _id: Optional[str] = None
    title: str
    description: Optional[str] = None
    organization_id: str
    creator_id: Optional[str] = None
    responses_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SurveyCreate(SafeModel):
    title: str
    description: Optional[str] = None
    questions: Optional[List[Dict[str, Any]]] = []

class SurveyUpdate(SafeModel):
    title: Optional[str] = None
    description: Optional[str] = None

class SurveyResponse(SafeModel):
    id: Optional[str] = None
    _id: Optional[str] = None
    survey_id: str
    responses: Dict[str, Any] = {}
    completion_time: Optional[float] = None

class SurveyResponseCreate(SafeModel):
    survey_id: str
    responses: Dict[str, Any] = {}

# -------------------- Enumerator (minimal) --------------------
class Enumerator(SafeModel):
    id: Optional[str] = None
    _id: Optional[str] = None
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    organization_id: str
    access_password: Optional[str] = None
    assigned_surveys: List[str] = []

# -------------------- Finance --------------------
class ApprovalStatus(str, Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    DRAFT = 'draft'

class Expense(SafeModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    activity_id: Optional[str] = None
    date: datetime
    vendor: Optional[str] = None
    invoice_no: Optional[str] = None
    amount: float
    currency: Optional[str] = 'USD'
    funding_source: Optional[str] = None
    cost_center: Optional[str] = None
    notes: Optional[str] = None
    organization_id: str
    created_by: Optional[str] = None
    last_updated_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # Approval workflow fields
    approval_status: ApprovalStatus = Field(default=ApprovalStatus.DRAFT)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    requires_director_approval: bool = Field(default=False)  # For amounts above threshold

class ExpenseCreate(SafeModel):
    project_id: str
    activity_id: Optional[str] = None
    date: datetime
    vendor: Optional[str] = None
    invoice_no: Optional[str] = None
    amount: float
    currency: Optional[str] = 'USD'
    funding_source: Optional[str] = None
    cost_center: Optional[str] = None
    notes: Optional[str] = None

class ExpenseUpdate(SafeModel):
    project_id: Optional[str] = None
    activity_id: Optional[str] = None
    date: Optional[datetime] = None
    vendor: Optional[str] = None
    invoice_no: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    funding_source: Optional[str] = None
    cost_center: Optional[str] = None
    notes: Optional[str] = None
    approval_status: Optional[ApprovalStatus] = None
    rejection_reason: Optional[str] = None

class ExpenseApprovalRequest(SafeModel):
    action: str  # 'approve' or 'reject'
    rejection_reason: Optional[str] = None

class ExpenseSubmitRequest(SafeModel):
    """Request to submit expense for approval"""
    pass

# -------------------- AI Service Models --------------------
class QuestionType(str, Enum):
    SHORT_TEXT = 'short_text'
    LONG_TEXT = 'long_text'
    MULTIPLE_CHOICE_SINGLE = 'multiple_choice_single'
    MULTIPLE_CHOICE_MULTIPLE = 'multiple_choice_multiple'
    RATING_SCALE = 'rating_scale'
    LIKERT_SCALE = 'likert_scale'
    YES_NO = 'yes_no'
    DATE_PICKER = 'date_picker'
    TIME_PICKER = 'time_picker'
    SLIDER = 'slider'
    MATRIX_GRID = 'matrix_grid'
    FILE_UPLOAD = 'file_upload'
    IMAGE_CHOICE = 'image_choice'
    SIGNATURE = 'signature'

class SurveyQuestion(SafeModel):
    type: QuestionType
    question: str
    required: bool = False
    options: Optional[List[str]] = None
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None
    scale_labels: Optional[List[str]] = None
    matrix_rows: Optional[List[str]] = None
    matrix_columns: Optional[List[str]] = None
    slider_step: Optional[int] = None
    date_format: Optional[str] = None
    file_types: Optional[List[str]] = None
    max_file_size: Optional[int] = None

class AISurveyGenerationRequest(SafeModel):
    description: str
    target_audience: Optional[str] = None
    survey_purpose: Optional[str] = None
    question_count: Optional[int] = 8
    include_demographics: Optional[bool] = False
    document_context: Optional[str] = None

class SurveyGenerationContext(SafeModel):
    organization_id: str
    documents: List[Dict[str, Any]] = []
    context_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentUpload(SafeModel):
    filename: str
    content: str
    content_type: str
    size: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)