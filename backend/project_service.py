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
    async def create_budget_item(self, budget_data: BudgetItemCreate, organization_id: str, created_by: str) -> BudgetItem:
        """Create a new budget item"""
        budget_dict = budget_data.model_dump()
        budget_dict["organization_id"] = organization_id
        budget_dict["created_by"] = created_by
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
        budget_by_category = {
            str(item["_id"]) if item["_id"] is not None else "uncategorized": item["total"] 
            for item in budget_category_result
        }
        
        # Projects by status
        status_pipeline = [
            {"$match": {"organization_id": organization_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        status_result = await self.db.projects.aggregate(status_pipeline).to_list(100)
        projects_by_status = {
            str(item["_id"]) if item["_id"] is not None else "unknown": item["count"] 
            for item in status_result
        }
        
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
        
        # Calculate overdue activities
        current_date = datetime.utcnow()
        overdue_activities = await self.db.activities.count_documents({
            "organization_id": organization_id,
            "end_date": {"$lt": current_date},
            "status": {"$ne": "completed"}
        })
        
        # Calculate advanced analytics
        activity_insights = await self._calculate_activity_insights(organization_id)
        performance_trends = await self._calculate_performance_trends(organization_id)
        risk_indicators = await self._calculate_risk_indicators(organization_id, current_date)
        completion_analytics = await self._calculate_completion_analytics(organization_id)
        
        return ProjectDashboardData(
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            total_budget=total_budget,
            budget_utilized=budget_utilized,
            utilization_rate=utilization_rate,
            budget_utilization=utilization_rate,  # Same as utilization_rate for frontend compatibility
            total_beneficiaries=total_beneficiaries,
            beneficiaries_reached=beneficiaries_reached,
            kpi_achievement_rate=kpi_achievement_rate,
            kpi_performance={"average_achievement": kpi_achievement_rate},  # Structured for frontend
            overdue_activities=overdue_activities,
            recent_activities=recent_activities,
            budget_by_category=budget_by_category,
            projects_by_status=projects_by_status,
            activity_insights=activity_insights,
            performance_trends=performance_trends,
            risk_indicators=risk_indicators,
            completion_analytics=completion_analytics
        )

    async def _calculate_activity_insights(self, organization_id: str) -> Dict[str, Any]:
        """Calculate insights from activity progress"""
        
        # Activity completion rates by status
        activity_pipeline = [
            {"$match": {"organization_id": organization_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "avg_progress": {"$avg": "$progress_percentage"},
                "total_budget": {"$sum": "$budget_allocated"}
            }}
        ]
        
        activity_stats = await self.db.activities.aggregate(activity_pipeline).to_list(100)
        
        # Weekly activity completion trend (last 8 weeks)
        eight_weeks_ago = datetime.utcnow() - timedelta(weeks=8)
        completion_trend_pipeline = [
            {"$match": {
                "organization_id": organization_id,
                "updated_at": {"$gte": eight_weeks_ago},
                "status": "completed"
            }},
            {"$group": {
                "_id": {
                    "year": {"$year": "$updated_at"},
                    "week": {"$week": "$updated_at"}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.year": 1, "_id.week": 1}}
        ]
        
        completion_trend = await self.db.activities.aggregate(completion_trend_pipeline).to_list(100)
        
        # Activity efficiency (avg days to complete)
        efficiency_pipeline = [
            {"$match": {
                "organization_id": organization_id,
                "status": "completed",
                "start_date": {"$exists": True},
                "end_date": {"$exists": True}
            }},
            {"$addFields": {
                "completion_days": {
                    "$divide": [
                        {"$subtract": ["$end_date", "$start_date"]},
                        86400000  # Convert milliseconds to days
                    ]
                }
            }},
            {"$group": {
                "_id": None,
                "avg_completion_days": {"$avg": "$completion_days"},
                "median_completion_days": {"$push": "$completion_days"}
            }}
        ]
        
        efficiency_result = await self.db.activities.aggregate(efficiency_pipeline).to_list(1)
        avg_completion_days = efficiency_result[0]["avg_completion_days"] if efficiency_result else 0
        
        return {
            "activity_status_breakdown": {
                item["_id"] if item["_id"] else "unknown": {
                    "count": item["count"],
                    "avg_progress": round(item["avg_progress"], 1) if item["avg_progress"] is not None else 0,
                    "budget_allocated": item["total_budget"] if item["total_budget"] is not None else 0
                }
                for item in activity_stats
            },
            "completion_trend_weekly": [
                {
                    "week": f"{item['_id']['year']}-W{item['_id']['week']}",
                    "completed": item["count"]
                }
                for item in completion_trend
            ],
            "avg_completion_days": round(avg_completion_days, 1) if avg_completion_days else 0,
            "total_activities": sum(item["count"] for item in activity_stats)
        }

    async def _calculate_performance_trends(self, organization_id: str) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        
        # Monthly budget utilization trend (last 6 months)
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        budget_trend_pipeline = [
            {"$match": {
                "organization_id": organization_id,
                "created_at": {"$gte": six_months_ago}
            }},
            {"$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"}
                },
                "total_spent": {"$sum": "$budgeted_amount"}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        
        budget_trend = await self.db.budget_items.aggregate(budget_trend_pipeline).to_list(100)
        
        # KPI achievement trend
        kpi_trend_pipeline = [
            {"$match": {
                "organization_id": organization_id,
                "updated_at": {"$gte": six_months_ago}
            }},
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
                "_id": {
                    "year": {"$year": "$updated_at"},
                    "month": {"$month": "$updated_at"}
                },
                "avg_achievement": {"$avg": "$achievement_rate"}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        
        kpi_trend = await self.db.kpi_indicators.aggregate(kpi_trend_pipeline).to_list(100)
        
        return {
            "budget_trend_monthly": [
                {
                    "month": f"{item['_id']['year']}-{item['_id']['month']:02d}",
                    "amount": item["total_spent"]
                }
                for item in budget_trend
            ],
            "kpi_trend_monthly": [
                {
                    "month": f"{item['_id']['year']}-{item['_id']['month']:02d}",
                    "achievement": round(item["avg_achievement"], 1) if item["avg_achievement"] is not None else 0
                }
                for item in kpi_trend
            ]
        }

    async def _calculate_risk_indicators(self, organization_id: str, current_date: datetime) -> Dict[str, Any]:
        """Calculate risk indicators for projects and activities"""
        
        # Budget risk (projects with high utilization)
        budget_risk_pipeline = [
            {"$match": {"organization_id": organization_id}},
            {"$addFields": {
                "utilization_rate": {
                    "$cond": [
                        {"$gt": ["$budget_total", 0]},
                        {"$multiply": [{"$divide": ["$budget_utilized", "$budget_total"]}, 100]},
                        0
                    ]
                }
            }},
            {"$match": {"utilization_rate": {"$gt": 80}}},
            {"$count": "high_utilization_projects"}
        ]
        
        high_utilization_result = await self.db.projects.aggregate(budget_risk_pipeline).to_list(1)
        high_utilization_projects = high_utilization_result[0]["high_utilization_projects"] if high_utilization_result else 0
        
        # Timeline risk (projects approaching deadline)
        thirty_days_ahead = current_date + timedelta(days=30)
        timeline_risk = await self.db.projects.count_documents({
            "organization_id": organization_id,
            "end_date": {"$lte": thirty_days_ahead, "$gte": current_date},
            "status": {"$ne": "completed"}
        })
        
        # Performance risk (activities with low progress)
        performance_risk = await self.db.activities.count_documents({
            "organization_id": organization_id,
            "progress_percentage": {"$lt": 50},
            "status": {"$in": ["in_progress", "delayed"]},
            "start_date": {"$lte": current_date - timedelta(days=30)}
        })
        
        return {
            "budget_risk": {
                "high_utilization_projects": high_utilization_projects,
                "threshold": 80,
                "description": "Projects with >80% budget utilization"
            },
            "timeline_risk": {
                "projects_due_soon": timeline_risk,
                "threshold_days": 30,
                "description": "Projects due within 30 days"
            },
            "performance_risk": {
                "low_progress_activities": performance_risk,
                "threshold": 50,
                "description": "Activities with <50% progress after 30+ days"
            }
        }

    async def _calculate_completion_analytics(self, organization_id: str) -> Dict[str, Any]:
        """Calculate completion analytics and success rates"""
        
        # Project success rate
        total_closed_projects = await self.db.projects.count_documents({
            "organization_id": organization_id,
            "status": {"$in": ["completed", "cancelled"]}
        })
        
        successful_projects = await self.db.projects.count_documents({
            "organization_id": organization_id,
            "status": "completed"
        })
        
        success_rate = (successful_projects / total_closed_projects * 100) if total_closed_projects > 0 else 0
        
        # Time-to-completion analysis
        completion_analysis_pipeline = [
            {"$match": {
                "organization_id": organization_id,
                "status": "completed",
                "start_date": {"$exists": True},
                "end_date": {"$exists": True}
            }},
            {"$addFields": {
                "planned_duration": {
                    "$divide": [
                        {"$subtract": ["$end_date", "$start_date"]},
                        86400000
                    ]
                },
                "actual_duration": {
                    "$divide": [
                        {"$subtract": ["$updated_at", "$created_at"]},
                        86400000
                    ]
                }
            }},
            {"$addFields": {
                "schedule_variance": {
                    "$subtract": ["$actual_duration", "$planned_duration"]
                }
            }},
            {"$group": {
                "_id": None,
                "avg_planned_duration": {"$avg": "$planned_duration"},
                "avg_actual_duration": {"$avg": "$actual_duration"},
                "avg_schedule_variance": {"$avg": "$schedule_variance"},
                "on_time_projects": {
                    "$sum": {
                        "$cond": [{"$lte": ["$schedule_variance", 0]}, 1, 0]
                    }
                },
                "total_projects": {"$sum": 1}
            }}
        ]
        
        completion_result = await self.db.projects.aggregate(completion_analysis_pipeline).to_list(1)
        
        if completion_result:
            data = completion_result[0]
            on_time_rate = (data["on_time_projects"] / data["total_projects"] * 100) if data["total_projects"] > 0 else 0
        else:
            data = {
                "avg_planned_duration": 0,
                "avg_actual_duration": 0,
                "avg_schedule_variance": 0,
                "on_time_projects": 0,
                "total_projects": 0
            }
            on_time_rate = 0
        
        return {
            "project_success_rate": round(success_rate, 1),
            "on_time_completion_rate": round(on_time_rate, 1),
            "avg_planned_duration_days": round(data["avg_planned_duration"], 1),
            "avg_actual_duration_days": round(data["avg_actual_duration"], 1),
            "avg_schedule_variance_days": round(data["avg_schedule_variance"], 1),
            "total_completed_projects": successful_projects,
            "total_closed_projects": total_closed_projects
        }