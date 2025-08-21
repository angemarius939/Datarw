import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from models import (
    Project, ProjectCreate, ProjectUpdate, ProjectStatus,
    Activity, ActivityCreate, ActivityUpdate, ActivityStatus,
    BudgetItem, BudgetItemCreate, BudgetItemUpdate,
    KPIIndicator, KPIIndicatorCreate, KPIIndicatorUpdate,
    Beneficiary, BeneficiaryCreate, BeneficiaryUpdate,
    ProjectDocument, ProjectDocumentCreate, ProjectDocumentUpdate,
    ProjectDashboardData, User
)

class ProjectService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    # Project Management
    async def create_project(self, project_data: ProjectCreate, organization_id: str, creator_id: str) -> Project:
        """Create a new project"""
        project_dict = project_data.model_dump()
        project_dict["organization_id"] = organization_id
        project_dict["created_at"] = datetime.utcnow()
        project_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.projects.insert_one(project_dict)
        project_dict["_id"] = str(result.inserted_id)
        
        return Project(**project_dict)

    async def get_projects(self, organization_id: str, status: Optional[ProjectStatus] = None) -> List[Project]:
        """Get all projects for an organization"""
        query = {"organization_id": organization_id}
        if status:
            query["status"] = status
            
        cursor = self.db.projects.find(query).sort("created_at", -1)
        projects = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            projects.append(Project(**doc))
        return projects

    async def get_project(self, project_id: str) -> Optional[Project]:
        """Get a specific project"""
        doc = await self.db.projects.find_one({"_id": ObjectId(project_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
            return Project(**doc)
        return None

    async def update_project(self, project_id: str, updates: ProjectUpdate) -> Optional[Project]:
        """Update a project"""
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.db.projects.update_one(
            {"_id": ObjectId(project_id)}, 
            {"$set": update_data}
        )
        
        if result.modified_count:
            return await self.get_project(project_id)
        return None

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project and all related data"""
        # Delete related activities, budgets, KPIs, documents
        await self.db.activities.delete_many({"project_id": project_id})
        await self.db.budget_items.delete_many({"project_id": project_id})
        await self.db.kpi_indicators.delete_many({"project_id": project_id})
        await self.db.project_documents.delete_many({"project_id": project_id})
        
        # Delete the project
        result = await self.db.projects.delete_one({"_id": ObjectId(project_id)})
        return result.deleted_count > 0

    # Activity Management
    async def create_activity(self, activity_data: ActivityCreate, organization_id: str) -> Activity:
        """Create a new activity"""
        activity_dict = activity_data.model_dump()
        activity_dict["organization_id"] = organization_id
        activity_dict["created_at"] = datetime.utcnow()
        activity_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.activities.insert_one(activity_dict)
        activity_dict["_id"] = str(result.inserted_id)
        
        return Activity(**activity_dict)

    async def get_activities(self, organization_id: str, project_id: Optional[str] = None) -> List[Activity]:
        """Get activities for an organization or project"""
        query = {"organization_id": organization_id}
        if project_id:
            query["project_id"] = project_id
            
        cursor = self.db.activities.find(query).sort("start_date", 1)
        activities = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            activities.append(Activity(**doc))
        return activities

    async def update_activity(self, activity_id: str, updates: ActivityUpdate) -> Optional[Activity]:
        """Update an activity"""
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.db.activities.update_one(
            {"_id": ObjectId(activity_id)}, 
            {"$set": update_data}
        )
        
        if result.modified_count:
            doc = await self.db.activities.find_one({"_id": ObjectId(activity_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                return Activity(**doc)
        return None

    # Budget Management
    async def create_budget_item(self, budget_data: BudgetItemCreate, organization_id: str) -> BudgetItem:
        """Create a new budget item"""
        budget_dict = budget_data.model_dump()
        budget_dict["organization_id"] = organization_id
        budget_dict["created_at"] = datetime.utcnow()
        budget_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.budget_items.insert_one(budget_dict)
        budget_dict["_id"] = str(result.inserted_id)
        
        return BudgetItem(**budget_dict)

    async def get_budget_items(self, organization_id: str, project_id: Optional[str] = None) -> List[BudgetItem]:
        """Get budget items for an organization or project"""
        query = {"organization_id": organization_id}
        if project_id:
            query["project_id"] = project_id
            
        cursor = self.db.budget_items.find(query).sort("created_at", -1)
        items = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            items.append(BudgetItem(**doc))
        return items

    async def get_budget_summary(self, organization_id: str, project_id: Optional[str] = None) -> Dict[str, float]:
        """Get budget summary with utilization rates"""
        query = {"organization_id": organization_id}
        if project_id:
            query["project_id"] = project_id
            
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "total_budget": {"$sum": "$budgeted_amount"},
                "total_spent": {"$sum": "$spent_amount"}
            }}
        ]
        
        result = await self.db.budget_items.aggregate(pipeline).to_list(1)
        if result:
            total_budget = result[0]["total_budget"]
            total_spent = result[0]["total_spent"]
            utilization_rate = (total_spent / total_budget * 100) if total_budget > 0 else 0
            
            return {
                "total_budget": total_budget,
                "total_spent": total_spent,
                "remaining_budget": total_budget - total_spent,
                "utilization_rate": utilization_rate
            }
        return {"total_budget": 0, "total_spent": 0, "remaining_budget": 0, "utilization_rate": 0}

    # KPI Management
    async def create_kpi_indicator(self, kpi_data: KPIIndicatorCreate, organization_id: str) -> KPIIndicator:
        """Create a new KPI indicator"""
        kpi_dict = kpi_data.model_dump()
        kpi_dict["organization_id"] = organization_id
        kpi_dict["created_at"] = datetime.utcnow()
        kpi_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.kpi_indicators.insert_one(kpi_dict)
        kpi_dict["_id"] = str(result.inserted_id)
        
        return KPIIndicator(**kpi_dict)

    async def get_kpi_indicators(self, organization_id: str, project_id: Optional[str] = None) -> List[KPIIndicator]:
        """Get KPI indicators for an organization or project"""
        query = {"organization_id": organization_id}
        if project_id:
            query["project_id"] = project_id
            
        cursor = self.db.kpi_indicators.find(query).sort("created_at", -1)
        indicators = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            indicators.append(KPIIndicator(**doc))
        return indicators

    async def update_kpi_current_value(self, indicator_id: str, current_value: float) -> Optional[KPIIndicator]:
        """Update the current value of a KPI indicator"""
        result = await self.db.kpi_indicators.update_one(
            {"_id": ObjectId(indicator_id)}, 
            {"$set": {"current_value": current_value, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count:
            doc = await self.db.kpi_indicators.find_one({"_id": ObjectId(indicator_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                return KPIIndicator(**doc)
        return None

    # Beneficiary Management
    async def create_beneficiary(self, beneficiary_data: BeneficiaryCreate, organization_id: str) -> Beneficiary:
        """Create a new beneficiary"""
        # Check if unique_id already exists for this organization
        existing = await self.db.beneficiaries.find_one({
            "organization_id": organization_id,
            "unique_id": beneficiary_data.unique_id
        })
        if existing:
            raise ValueError("Beneficiary with this unique ID already exists")
            
        beneficiary_dict = beneficiary_data.model_dump()
        beneficiary_dict["organization_id"] = organization_id
        beneficiary_dict["created_at"] = datetime.utcnow()
        beneficiary_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.beneficiaries.insert_one(beneficiary_dict)
        beneficiary_dict["_id"] = str(result.inserted_id)
        
        return Beneficiary(**beneficiary_dict)

    async def get_beneficiaries(self, organization_id: str, project_id: Optional[str] = None) -> List[Beneficiary]:
        """Get beneficiaries for an organization or project"""
        query = {"organization_id": organization_id}
        if project_id:
            query["project_ids"] = project_id
            
        cursor = self.db.beneficiaries.find(query).sort("last_name", 1)
        beneficiaries = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            beneficiaries.append(Beneficiary(**doc))
        return beneficiaries

    async def get_beneficiary_demographics(self, organization_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get demographic breakdown of beneficiaries"""
        query = {"organization_id": organization_id}
        if project_id:
            query["project_ids"] = project_id
            
        # Gender distribution
        gender_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$gender", "count": {"$sum": 1}}}
        ]
        
        # Age distribution
        age_pipeline = [
            {"$match": query},
            {"$addFields": {
                "age": {
                    "$divide": [
                        {"$subtract": [datetime.utcnow(), "$date_of_birth"]},
                        31536000000  # milliseconds in a year
                    ]
                }
            }},
            {"$bucket": {
                "groupBy": "$age",
                "boundaries": [0, 18, 35, 50, 65, 100],
                "default": "Unknown",
                "output": {"count": {"$sum": 1}}
            }}
        ]
        
        # Location distribution
        location_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$location", "count": {"$sum": 1}}}
        ]
        
        gender_data = await self.db.beneficiaries.aggregate(gender_pipeline).to_list(None)
        age_data = await self.db.beneficiaries.aggregate(age_pipeline).to_list(None)
        location_data = await self.db.beneficiaries.aggregate(location_pipeline).to_list(None)
        
        return {
            "gender_distribution": gender_data,
            "age_distribution": age_data,
            "location_distribution": location_data
        }

    # Document Management
    async def create_document(self, doc_data: ProjectDocumentCreate, organization_id: str, uploaded_by: str, file_url: str) -> ProjectDocument:
        """Create a new project document"""
        doc_dict = doc_data.model_dump()
        doc_dict["organization_id"] = organization_id
        doc_dict["uploaded_by"] = uploaded_by
        doc_dict["file_url"] = file_url
        doc_dict["created_at"] = datetime.utcnow()
        doc_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.project_documents.insert_one(doc_dict)
        doc_dict["_id"] = str(result.inserted_id)
        
        return ProjectDocument(**doc_dict)

    async def get_documents(self, organization_id: str, project_id: Optional[str] = None) -> List[ProjectDocument]:
        """Get documents for an organization or project"""
        query = {"organization_id": organization_id}
        if project_id:
            query["project_id"] = project_id
            
        cursor = self.db.project_documents.find(query).sort("created_at", -1)
        documents = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            documents.append(ProjectDocument(**doc))
        return documents

    # Dashboard Data
    async def get_dashboard_data(self, organization_id: str) -> ProjectDashboardData:
        """Get comprehensive dashboard data for projects"""
        # Project counts
        total_projects = await self.db.projects.count_documents({"organization_id": organization_id})
        active_projects = await self.db.projects.count_documents({
            "organization_id": organization_id,
            "status": ProjectStatus.ACTIVE
        })
        completed_projects = await self.db.projects.count_documents({
            "organization_id": organization_id,
            "status": ProjectStatus.COMPLETED
        })
        
        # Budget calculations
        total_budget = 0
        budget_utilized = 0
        projects_cursor = self.db.projects.find({"organization_id": organization_id})
        async for project in projects_cursor:
            total_budget += project.get("budget_total", 0)
            budget_utilized += project.get("budget_utilized", 0)
        
        utilization_rate = (budget_utilized / total_budget * 100) if total_budget > 0 else 0
        
        # Beneficiary calculations
        total_beneficiaries = 0
        beneficiaries_reached = 0
        beneficiaries_cursor = self.db.beneficiaries.find({"organization_id": organization_id})
        async for _ in beneficiaries_cursor:
            total_beneficiaries += 1
            beneficiaries_reached += 1  # Assume all registered beneficiaries are reached
        
        # KPI performance - average achievement rate
        kpi_pipeline = [
            {"$match": {"organization_id": organization_id}},
            {"$addFields": {
                "achievement_rate": {
                    "$cond": [
                        {"$and": [{"$ne": ["$target_value", None]}, {"$gt": ["$target_value", 0]}]},
                        {"$multiply": [{"$divide": ["$current_value", "$target_value"]}, 100]},
                        0
                    ]
                }
            }},
            {"$group": {
                "_id": None,
                "avg_achievement": {"$avg": "$achievement_rate"}
            }}
        ]
        
        kpi_result = await self.db.kpi_indicators.aggregate(kpi_pipeline).to_list(1)
        kpi_achievement_rate = kpi_result[0]["avg_achievement"] if kpi_result else 0
        
        # Budget by category
        budget_pipeline = [
            {"$match": {"organization_id": organization_id}},
            {"$group": {
                "_id": "$category",
                "total": {"$sum": "$budgeted_amount"}
            }}
        ]
        
        budget_category_result = await self.db.budget_entries.aggregate(budget_pipeline).to_list(100)
        budget_by_category = {item["_id"]: item["total"] for item in budget_category_result}
        
        # Projects by status
        status_pipeline = [
            {"$match": {"organization_id": organization_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        status_result = await self.db.projects.aggregate(status_pipeline).to_list(100)
        projects_by_status = {item["_id"]: item["count"] for item in status_result}
        
        # Recent activities
        recent_activities_cursor = self.db.activities.find(
            {"organization_id": organization_id}
        ).sort("updated_at", -1).limit(5)
        
        recent_activities = []
        async for activity in recent_activities_cursor:
            recent_activities.append({
                "id": str(activity.get("_id", activity.get("id", ""))),
                "name": activity.get("name", "Unknown Activity"),
                "status": activity.get("status", "unknown"),
                "progress": activity.get("progress_percentage", 0),
                "updated_at": activity.get("updated_at", datetime.utcnow()).isoformat()
            })
        
        return ProjectDashboardData(
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            total_budget=total_budget,
            budget_utilized=budget_utilized,
            utilization_rate=utilization_rate,
            total_beneficiaries=total_beneficiaries,
            beneficiaries_reached=beneficiaries_reached,
            kpi_achievement_rate=kpi_achievement_rate,
            recent_activities=recent_activities,
            budget_by_category=budget_by_category,
            projects_by_status=projects_by_status
        )