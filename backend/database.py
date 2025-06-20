from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any
from models import *
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db

    # Organization CRUD
    async def create_organization(self, organization: OrganizationCreate) -> Organization:
        """Create a new organization"""
        org_doc = Organization(**organization.dict())
        
        # Set plan limits
        if org_doc.plan == SubscriptionPlan.BASIC:
            org_doc.survey_limit = 4
            org_doc.storage_limit = 1.0
        elif org_doc.plan == SubscriptionPlan.PROFESSIONAL:
            org_doc.survey_limit = 10
            org_doc.storage_limit = 3.0
        elif org_doc.plan == SubscriptionPlan.ENTERPRISE:
            org_doc.survey_limit = -1  # Unlimited
            org_doc.storage_limit = -1.0  # Unlimited
        
        result = await self.db.organizations.insert_one(org_doc.dict(by_alias=True))
        org_doc.id = result.inserted_id
        return org_doc

    async def get_organization(self, organization_id: str) -> Optional[Organization]:
        """Get organization by ID"""
        org_doc = await self.db.organizations.find_one({"_id": organization_id})
        if org_doc:
            return Organization(**org_doc)
        return None

    async def update_organization(self, organization_id: str, updates: OrganizationUpdate) -> Optional[Organization]:
        """Update organization"""
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.db.organizations.update_one(
            {"_id": organization_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get_organization(organization_id)
        return None

    # User CRUD
    async def create_user(self, user: UserCreate, password_hash: str) -> User:
        """Create a new user"""
        user_doc = User(
            email=user.email,
            password_hash=password_hash,
            name=user.name,
            organization_id=user.organization_id,
            role=user.role
        )
        
        result = await self.db.users.insert_one(user_doc.dict(by_alias=True))
        user_doc.id = result.inserted_id
        return user_doc

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_doc = await self.db.users.find_one({"_id": user_id})
        if user_doc:
            return User(**user_doc)
        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_doc = await self.db.users.find_one({"email": email})
        if user_doc:
            return User(**user_doc)
        return None

    async def get_organization_users(self, organization_id: str) -> List[User]:
        """Get all users for an organization"""
        users = await self.db.users.find({"organization_id": organization_id}).to_list(1000)
        return [User(**user) for user in users]

    async def update_user(self, user_id: str, updates: UserUpdate) -> Optional[User]:
        """Update user"""
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.db.users.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get_user(user_id)
        return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        result = await self.db.users.delete_one({"_id": user_id})
        return result.deleted_count > 0

    async def update_user_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        await self.db.users.update_one(
            {"_id": user_id},
            {"$set": {"last_login": datetime.utcnow()}}
        )

    # Survey CRUD
    async def create_survey(self, survey: SurveyCreate, organization_id: str, creator_id: str) -> Survey:
        """Create a new survey"""
        survey_doc = Survey(
            title=survey.title,
            description=survey.description,
            organization_id=organization_id,
            creator_id=creator_id,
            questions=survey.questions
        )
        
        result = await self.db.surveys.insert_one(survey_doc.dict(by_alias=True))
        survey_doc.id = result.inserted_id
        
        # Update user's survey count
        await self.db.users.update_one(
            {"_id": creator_id},
            {"$inc": {"surveys_created": 1}}
        )
        
        # Update organization's survey count
        await self.db.organizations.update_one(
            {"_id": organization_id},
            {"$inc": {"survey_count": 1}}
        )
        
        return survey_doc

    async def get_survey(self, survey_id: str) -> Optional[Survey]:
        """Get survey by ID"""
        survey_doc = await self.db.surveys.find_one({"_id": survey_id})
        if survey_doc:
            return Survey(**survey_doc)
        return None

    async def get_organization_surveys(self, organization_id: str) -> List[Survey]:
        """Get all surveys for an organization"""
        surveys = await self.db.surveys.find({"organization_id": organization_id}).to_list(1000)
        return [Survey(**survey) for survey in surveys]

    async def update_survey(self, survey_id: str, updates: SurveyUpdate) -> Optional[Survey]:
        """Update survey"""
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.db.surveys.update_one(
            {"_id": survey_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get_survey(survey_id)
        return None

    async def delete_survey(self, survey_id: str) -> bool:
        """Delete survey"""
        survey = await self.get_survey(survey_id)
        if not survey:
            return False
        
        # Delete all responses
        await self.db.survey_responses.delete_many({"survey_id": survey_id})
        
        # Delete survey
        result = await self.db.surveys.delete_one({"_id": survey_id})
        
        if result.deleted_count > 0:
            # Update organization survey count
            await self.db.organizations.update_one(
                {"_id": survey.organization_id},
                {"$inc": {"survey_count": -1}}
            )
            
            # Update user survey count
            await self.db.users.update_one(
                {"_id": survey.creator_id},
                {"$inc": {"surveys_created": -1}}
            )
            
            return True
        return False

    # Survey Response CRUD
    async def create_survey_response(self, response: SurveyResponseCreate) -> SurveyResponse:
        """Create a new survey response"""
        response_doc = SurveyResponse(**response.dict())
        
        result = await self.db.survey_responses.insert_one(response_doc.dict(by_alias=True))
        response_doc.id = result.inserted_id
        
        # Update survey response count
        await self.db.surveys.update_one(
            {"_id": response.survey_id},
            {"$inc": {"responses_count": 1}}
        )
        
        return response_doc

    async def get_survey_responses(self, survey_id: str) -> List[SurveyResponse]:
        """Get all responses for a survey"""
        responses = await self.db.survey_responses.find({"survey_id": survey_id}).to_list(10000)
        return [SurveyResponse(**response) for response in responses]

    async def get_organization_analytics(self, organization_id: str) -> AnalyticsData:
        """Get analytics data for an organization"""
        # Get organization surveys
        org_surveys = await self.get_organization_surveys(organization_id)
        survey_ids = [survey.id for survey in org_surveys]
        
        # Get total responses
        total_responses = 0
        for survey in org_surveys:
            total_responses += survey.responses_count
        
        # Calculate response rate (assuming 100 invitations per survey for demo)
        response_rate = (total_responses / (len(org_surveys) * 100)) * 100 if org_surveys else 0
        
        # Get completion times
        completion_times = []
        for survey_id in survey_ids:
            responses = await self.db.survey_responses.find(
                {"survey_id": survey_id, "completion_time": {"$exists": True}}
            ).to_list(1000)
            completion_times.extend([r["completion_time"] for r in responses if r.get("completion_time")])
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 4.2
        
        # Get top performing survey
        top_survey = max(org_surveys, key=lambda s: s.responses_count) if org_surveys else None
        top_performing_survey = top_survey.title if top_survey else "No surveys yet"
        
        # Mock monthly data for now
        responses_by_month = [
            {"month": "Jan", "responses": 180},
            {"month": "Feb", "responses": 220},
            {"month": "Mar", "responses": 285},
            {"month": "Apr", "responses": 310},
            {"month": "May", "responses": 255}
        ]
        
        survey_types = [
            {"type": "Customer Feedback", "count": 45, "percentage": 35},
            {"type": "Employee Surveys", "count": 32, "percentage": 25},
            {"type": "Market Research", "count": 28, "percentage": 22},
            {"type": "Product Feedback", "count": 23, "percentage": 18}
        ]
        
        return AnalyticsData(
            total_responses=total_responses,
            response_rate=min(response_rate, 100),
            average_completion_time=avg_completion_time,
            top_performing_survey=top_performing_survey,
            monthly_growth=15.3,
            storage_growth=12.8,
            responses_by_month=responses_by_month,
            survey_types=survey_types
        )