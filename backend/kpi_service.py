import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bson import ObjectId
import asyncio
class KPIService:
    def __init__(self, db):
        self.db = db

    # -------------------- Indicator Level KPIs --------------------
    async def get_indicator_kpis(self, organization_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """Get high-level organization indicators"""
        try:
            # Date filtering
            date_filter = {"organization_id": organization_id}
            if date_from and date_to:
                date_filter["created_at"] = {
                    "$gte": datetime.fromisoformat(date_from.replace('Z', '+00:00')),
                    "$lte": datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                }

            # Overall Performance Indicators
            total_projects = await self.db.projects.count_documents({"organization_id": organization_id})
            active_projects = await self.db.projects.count_documents({"organization_id": organization_id, "status": "active"})
            completed_projects = await self.db.projects.count_documents({"organization_id": organization_id, "status": "completed"})
            
            # Activity Performance
            total_activities = await self.db.activities.count_documents({"organization_id": organization_id})
            completed_activities = await self.db.activities.count_documents({"organization_id": organization_id, "status": "completed"})
            overdue_activities = await self.db.activities.count_documents({
                "organization_id": organization_id,
                "end_date": {"$lt": datetime.utcnow()},
                "status": {"$ne": "completed"}
            })

            # Beneficiary Impact
            total_beneficiaries = await self.db.beneficiaries.count_documents({"organization_id": organization_id})
            
            # Budget Performance
            total_budget = 0
            utilized_budget = 0
            async for project in self.db.projects.find({"organization_id": organization_id}):
                project_budget = project.get("budget", 0)
                if isinstance(project_budget, (int, float)):
                    total_budget += project_budget
            
            # Get expenses
            async for expense in self.db.expenses.find({"organization_id": organization_id, "approval_status": "approved"}):
                expense_amount = expense.get("amount", 0)
                if isinstance(expense_amount, (int, float)):
                    utilized_budget += expense_amount

            # Calculate key indicators
            project_completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
            activity_completion_rate = (completed_activities / total_activities * 100) if total_activities > 0 else 0
            budget_utilization_rate = (utilized_budget / total_budget * 100) if total_budget > 0 else 0
            overdue_rate = (overdue_activities / total_activities * 100) if total_activities > 0 else 0

            return {
                "overview": {
                    "total_projects": total_projects,
                    "active_projects": active_projects,
                    "completed_projects": completed_projects,
                    "total_activities": total_activities,
                    "total_beneficiaries": total_beneficiaries,
                    "total_budget": total_budget,
                    "utilized_budget": utilized_budget
                },
                "performance_indicators": {
                    "project_completion_rate": round(project_completion_rate, 2),
                    "activity_completion_rate": round(activity_completion_rate, 2),
                    "budget_utilization_rate": round(budget_utilization_rate, 2),
                    "overdue_rate": round(overdue_rate, 2),
                    "on_time_delivery_rate": round(100 - overdue_rate, 2)
                },
                "trends": await self._get_indicator_trends(organization_id, date_from, date_to)
            }
        except Exception as e:
            print(f"Error getting indicator KPIs: {e}")
            return {"overview": {}, "performance_indicators": {}, "trends": {}}

    async def _get_indicator_trends(self, organization_id: str, date_from: Optional[str], date_to: Optional[str]) -> Dict[str, Any]:
        """Get trend data for indicators over time"""
        try:
            # Get data for the last 6 months
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=180)
            
            monthly_trends = []
            for i in range(6):
                month_start = start_date + timedelta(days=30 * i)
                month_end = start_date + timedelta(days=30 * (i + 1))
                
                # Count projects and activities for this month
                projects_count = await self.db.projects.count_documents({
                    "organization_id": organization_id,
                    "created_at": {"$gte": month_start, "$lt": month_end}
                })
                
                activities_count = await self.db.activities.count_documents({
                    "organization_id": organization_id,
                    "created_at": {"$gte": month_start, "$lt": month_end}
                })
                
                monthly_trends.append({
                    "month": month_start.strftime("%b %Y"),
                    "projects": projects_count,
                    "activities": activities_count
                })
            
            return {"monthly_trends": monthly_trends}
        except Exception as e:
            print(f"Error getting indicator trends: {e}")
            return {"monthly_trends": []}

    # -------------------- Activity Level KPIs --------------------
    async def get_activity_kpis(self, organization_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get activity-level KPIs with drill-down capabilities"""
        try:
            query = {"organization_id": organization_id}
            if project_id:
                query["project_id"] = project_id

            activities = []
            async for activity in self.db.activities.find(query):
                activity["_id"] = str(activity.get("_id"))
                
                # Calculate activity-specific KPIs
                progress = activity.get("progress_percentage", 0)
                planned_end = activity.get("planned_end_date")
                actual_end = activity.get("actual_end_date")
                status = activity.get("status", "not_started")
                
                # Timeline performance
                is_overdue = False
                days_variance = 0
                if planned_end:
                    planned_date = planned_end if isinstance(planned_end, datetime) else datetime.fromisoformat(str(planned_end).replace('Z', '+00:00'))
                    current_date = actual_end if actual_end else datetime.utcnow()
                    if isinstance(current_date, str):
                        current_date = datetime.fromisoformat(current_date.replace('Z', '+00:00'))
                    
                    days_variance = (current_date - planned_date).days
                    is_overdue = days_variance > 0 and status != "completed"

                # Risk assessment
                risk_level = activity.get("risk_level", "low")
                risk_score = {"low": 1, "medium": 2, "high": 3}.get(risk_level, 1)
                
                activity_kpi = {
                    "activity_id": activity.get("id", str(activity.get("_id"))),
                    "name": activity.get("name", "Unnamed Activity"),
                    "project_id": activity.get("project_id"),
                    "status": status,
                    "progress_percentage": progress,
                    "risk_level": risk_level,
                    "risk_score": risk_score,
                    "is_overdue": is_overdue,
                    "days_variance": days_variance,
                    "target_quantity": activity.get("target_quantity", 0),
                    "achieved_quantity": activity.get("achieved_quantity", 0),
                    "completion_rate": (activity.get("achieved_quantity", 0) / activity.get("target_quantity", 1) * 100) if activity.get("target_quantity", 0) > 0 else 0,
                    "assigned_team": activity.get("assigned_team"),
                    "created_at": activity.get("created_at"),
                    "updated_at": activity.get("updated_at")
                }
                activities.append(activity_kpi)

            # Aggregate activity KPIs
            total_activities = len(activities)
            if total_activities == 0:
                return {"activities": [], "summary": {}, "analytics": {}}

            completed_activities = len([a for a in activities if a["status"] == "completed"])
            overdue_activities = len([a for a in activities if a["is_overdue"]])
            high_risk_activities = len([a for a in activities if a["risk_level"] == "high"])
            
            avg_progress = sum(a["progress_percentage"] for a in activities) / total_activities
            avg_completion_rate = sum(a["completion_rate"] for a in activities) / total_activities

            return {
                "activities": activities,
                "summary": {
                    "total_activities": total_activities,
                    "completed_activities": completed_activities,
                    "overdue_activities": overdue_activities,
                    "high_risk_activities": high_risk_activities,
                    "completion_rate": round(completed_activities / total_activities * 100, 2),
                    "overdue_rate": round(overdue_activities / total_activities * 100, 2),
                    "avg_progress": round(avg_progress, 2),
                    "avg_completion_rate": round(avg_completion_rate, 2)
                },
                "analytics": {
                    "status_breakdown": self._get_status_breakdown(activities),
                    "risk_distribution": self._get_risk_distribution(activities),
                    "performance_trends": self._get_activity_performance_trends(activities)
                }
            }
        except Exception as e:
            print(f"Error getting activity KPIs: {e}")
            return {"activities": [], "summary": {}, "analytics": {}}

    # -------------------- Project Level KPIs --------------------
    async def get_project_kpis(self, organization_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get project-level KPIs with drill-down capabilities"""
        try:
            query = {"organization_id": organization_id}
            if project_id:
                query["id"] = project_id

            projects = []
            async for project in self.db.projects.find(query):
                project["_id"] = str(project.get("_id"))
                project_id_str = project.get("id", str(project.get("_id")))
                
                # Get project activities
                project_activities = []
                async for activity in self.db.activities.find({"project_id": project_id_str}):
                    activity["_id"] = str(activity.get("_id"))
                    project_activities.append(activity)
                
                # Get project beneficiaries
                project_beneficiaries = await self.db.beneficiaries.count_documents({"project_ids": project_id_str})
                
                # Get project expenses
                project_expenses = 0
                async for expense in self.db.expenses.find({"project_id": project_id_str, "approval_status": "approved"}):
                    project_expenses += expense.get("amount", 0)

                # Calculate project KPIs
                total_activities = len(project_activities)
                completed_activities = len([a for a in project_activities if a.get("status") == "completed"])
                overdue_activities = len([a for a in project_activities if self._is_activity_overdue(a)])
                
                project_budget = project.get("budget", 0)
                budget_utilization = (project_expenses / project_budget * 100) if project_budget > 0 else 0
                
                avg_activity_progress = sum(a.get("progress_percentage", 0) for a in project_activities) / total_activities if total_activities > 0 else 0
                
                target_beneficiaries = project.get("target_beneficiaries", 0)
                beneficiary_achievement_rate = (project_beneficiaries / target_beneficiaries * 100) if target_beneficiaries > 0 else 0

                project_kpi = {
                    "project_id": project_id_str,
                    "name": project.get("name", "Unnamed Project"),
                    "status": project.get("status", "planning"),
                    "total_activities": total_activities,
                    "completed_activities": completed_activities,
                    "overdue_activities": overdue_activities,
                    "activity_completion_rate": round(completed_activities / total_activities * 100, 2) if total_activities > 0 else 0,
                    "avg_activity_progress": round(avg_activity_progress, 2),
                    "budget": project_budget,
                    "expenses": project_expenses,
                    "budget_utilization": round(budget_utilization, 2),
                    "target_beneficiaries": target_beneficiaries,
                    "actual_beneficiaries": project_beneficiaries,
                    "beneficiary_achievement_rate": round(beneficiary_achievement_rate, 2),
                    "start_date": project.get("start_date"),
                    "end_date": project.get("end_date"),
                    "created_at": project.get("created_at"),
                    "updated_at": project.get("updated_at")
                }
                projects.append(project_kpi)

            # Aggregate project KPIs
            total_projects = len(projects)
            if total_projects == 0:
                return {"projects": [], "summary": {}, "analytics": {}}

            completed_projects = len([p for p in projects if p["status"] == "completed"])
            total_budget = sum(p["budget"] for p in projects)
            total_expenses = sum(p["expenses"] for p in projects)
            avg_budget_utilization = sum(p["budget_utilization"] for p in projects) / total_projects

            return {
                "projects": projects,
                "summary": {
                    "total_projects": total_projects,
                    "completed_projects": completed_projects,
                    "project_completion_rate": round(completed_projects / total_projects * 100, 2),
                    "total_budget": total_budget,
                    "total_expenses": total_expenses,
                    "overall_budget_utilization": round(total_expenses / total_budget * 100, 2) if total_budget > 0 else 0,
                    "avg_budget_utilization": round(avg_budget_utilization, 2)
                },
                "analytics": {
                    "status_distribution": self._get_project_status_distribution(projects),
                    "budget_performance": self._get_budget_performance_analytics(projects),
                    "beneficiary_impact": self._get_beneficiary_impact_analytics(projects)
                }
            }
        except Exception as e:
            print(f"Error getting project KPIs: {e}")
            return {"projects": [], "summary": {}, "analytics": {}}

    # -------------------- Helper Methods --------------------
    def _is_activity_overdue(self, activity: Dict) -> bool:
        """Check if an activity is overdue"""
        planned_end = activity.get("planned_end_date") or activity.get("end_date")
        if not planned_end or activity.get("status") == "completed":
            return False
        
        if isinstance(planned_end, str):
            planned_end = datetime.fromisoformat(planned_end.replace('Z', '+00:00'))
        
        return planned_end < datetime.utcnow()

    def _get_status_breakdown(self, activities: List[Dict]) -> Dict[str, int]:
        """Get status breakdown for activities"""
        status_count = {}
        for activity in activities:
            status = activity.get("status", "not_started")
            status_count[status] = status_count.get(status, 0) + 1
        return status_count

    def _get_risk_distribution(self, activities: List[Dict]) -> Dict[str, int]:
        """Get risk level distribution for activities"""
        risk_count = {}
        for activity in activities:
            risk = activity.get("risk_level", "low")
            risk_count[risk] = risk_count.get(risk, 0) + 1
        return risk_count

    def _get_activity_performance_trends(self, activities: List[Dict]) -> Dict[str, Any]:
        """Get performance trends for activities"""
        # Sort by created date
        sorted_activities = sorted(activities, key=lambda x: x.get("created_at") or datetime.min)
        
        # Group by month
        monthly_performance = {}
        for activity in sorted_activities:
            created_at = activity.get("created_at")
            if created_at:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                month_key = created_at.strftime("%Y-%m")
                
                if month_key not in monthly_performance:
                    monthly_performance[month_key] = {"total": 0, "completed": 0}
                
                monthly_performance[month_key]["total"] += 1
                if activity.get("status") == "completed":
                    monthly_performance[month_key]["completed"] += 1

        return {"monthly_performance": monthly_performance}

    def _get_project_status_distribution(self, projects: List[Dict]) -> Dict[str, int]:
        """Get status distribution for projects"""
        status_count = {}
        for project in projects:
            status = project.get("status", "planning")
            status_count[status] = status_count.get(status, 0) + 1
        return status_count

    def _get_budget_performance_analytics(self, projects: List[Dict]) -> Dict[str, Any]:
        """Get budget performance analytics for projects"""
        budget_ranges = {"0-10k": 0, "10k-50k": 0, "50k-100k": 0, "100k+": 0}
        utilization_ranges = {"0-25%": 0, "25-50%": 0, "50-75%": 0, "75-100%": 0, "100%+": 0}
        
        for project in projects:
            # Budget ranges
            budget = project.get("budget", 0)
            if budget <= 10000:
                budget_ranges["0-10k"] += 1
            elif budget <= 50000:
                budget_ranges["10k-50k"] += 1
            elif budget <= 100000:
                budget_ranges["50k-100k"] += 1
            else:
                budget_ranges["100k+"] += 1
            
            # Utilization ranges
            utilization = project.get("budget_utilization", 0)
            if utilization <= 25:
                utilization_ranges["0-25%"] += 1
            elif utilization <= 50:
                utilization_ranges["25-50%"] += 1
            elif utilization <= 75:
                utilization_ranges["50-75%"] += 1
            elif utilization <= 100:
                utilization_ranges["75-100%"] += 1
            else:
                utilization_ranges["100%+"] += 1

        return {
            "budget_distribution": budget_ranges,
            "utilization_distribution": utilization_ranges
        }

    def _get_beneficiary_impact_analytics(self, projects: List[Dict]) -> Dict[str, Any]:
        """Get beneficiary impact analytics for projects"""
        total_target = sum(p.get("target_beneficiaries", 0) for p in projects)
        total_actual = sum(p.get("actual_beneficiaries", 0) for p in projects)
        
        achievement_ranges = {"0-25%": 0, "25-50%": 0, "50-75%": 0, "75-100%": 0, "100%+": 0}
        
        for project in projects:
            rate = project.get("beneficiary_achievement_rate", 0)
            if rate <= 25:
                achievement_ranges["0-25%"] += 1
            elif rate <= 50:
                achievement_ranges["25-50%"] += 1
            elif rate <= 75:
                achievement_ranges["50-75%"] += 1
            elif rate <= 100:
                achievement_ranges["75-100%"] += 1
            else:
                achievement_ranges["100%+"] += 1

        return {
            "total_target_beneficiaries": total_target,
            "total_actual_beneficiaries": total_actual,
            "overall_achievement_rate": round(total_actual / total_target * 100, 2) if total_target > 0 else 0,
            "achievement_distribution": achievement_ranges
        }

# Initialize the service
kpi_service = KPIService()