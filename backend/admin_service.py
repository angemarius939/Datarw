import os
import secrets
import string
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from models import (
    User, UserCreateAdvanced, UserRole,
    PartnerOrganization, PartnerOrganizationCreate, PartnerOrganizationUpdate,
    PartnerPerformance, PartnerPerformanceCreate,
    OrganizationBranding, OrganizationBrandingCreate,
    EmailTemplate, EmailLog
)
from auth import get_password_hash

class AdminService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    # Advanced User Management
    async def create_user_advanced(self, user_data: UserCreateAdvanced, organization_id: str, created_by: str) -> Dict[str, Any]:
        """Create user with advanced features and optional email sending"""
        
        # Generate password if not provided
        if not user_data.password:
            password = self._generate_secure_password()
            user_data.password = password
        else:
            password = user_data.password
        
        # Generate username from email
        username = user_data.email.split('@')[0]
        
        # Hash password
        password_hash = get_password_hash(user_data.password)
        
        # Create user document
        user_dict = {
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": password_hash,
            "role": user_data.role,
            "organization_id": organization_id,
            "partner_organization_id": user_data.partner_organization_id,
            "department": user_data.department,
            "position": user_data.position,
            "supervisor_id": user_data.supervisor_id,
            "access_level": user_data.access_level,
            "permissions": user_data.permissions or self._get_default_permissions(user_data.role),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": created_by,
            "last_login": None,
            "login_count": 0,
            "must_change_password": user_data.temporary_password
        }
        
        result = await self.db.users.insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        
        # Send credentials email if requested
        if user_data.send_credentials_email:
            await self._send_user_credentials_email(
                organization_id=organization_id,
                user_email=user_data.email,
                user_name=user_data.name,
                username=username,
                password=password,
                role=user_data.role,
                created_by=created_by
            )
        
        # Remove sensitive data from response
        response_user = User(**user_dict)
        
        return {
            "user": response_user,
            "username": username,
            "password": password if not user_data.send_credentials_email else None,
            "credentials_sent": user_data.send_credentials_email
        }

    async def bulk_create_users(self, users_data: List[UserCreateAdvanced], organization_id: str, created_by: str, send_emails: bool = True) -> Dict[str, Any]:
        """Create multiple users at once with batch email sending"""
        
        created_users = []
        failed_users = []
        email_queue = []
        
        for user_data in users_data:
            try:
                # Override email sending for individual users if batch processing
                user_data.send_credentials_email = False
                
                result = await self.create_user_advanced(user_data, organization_id, created_by)
                created_users.append(result)
                
                if send_emails:
                    email_queue.append({
                        "user": result["user"],
                        "username": result["username"],
                        "password": result["password"]
                    })
                    
            except Exception as e:
                failed_users.append({
                    "email": user_data.email,
                    "error": str(e)
                })
        
        # Send batch emails if requested
        if send_emails and email_queue:
            await self._send_batch_credentials_emails(organization_id, email_queue, created_by)
        
        return {
            "created_count": len(created_users),
            "failed_count": len(failed_users),
            "created_users": created_users,
            "failed_users": failed_users,
            "emails_sent": send_emails
        }

    def _generate_secure_password(self, length: int = 12) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # Ensure password has at least one uppercase, lowercase, digit, and special char
        if not any(c.isupper() for c in password):
            password = password[:-1] + secrets.choice(string.ascii_uppercase)
        if not any(c.islower() for c in password):
            password = password[:-1] + secrets.choice(string.ascii_lowercase)
        if not any(c.isdigit() for c in password):
            password = password[:-1] + secrets.choice(string.digits)
        if not any(c in "!@#$%&*" for c in password):
            password = password[:-1] + secrets.choice("!@#$%&*")
            
        return password

    def _get_default_permissions(self, role: UserRole) -> Dict[str, bool]:
        """Get default permissions based on user role"""
        base_permissions = {
            "view_dashboard": True,
            "view_projects": True,
            "view_activities": True,
            "view_kpis": True,
            "view_beneficiaries": True,
            "view_documents": True,
            "view_reports": True,
            "create_projects": False,
            "edit_projects": False,
            "delete_projects": False,
            "create_activities": False,
            "edit_activities": False,
            "delete_activities": False,
            "create_users": False,
            "edit_users": False,
            "delete_users": False,
            "manage_partners": False,
            "view_financial_data": False,
            "edit_financial_data": False,
            "generate_reports": False,
            "export_data": False,
            "system_admin": False
        }
        
        # Role-specific permissions
        if role == UserRole.DIRECTOR:
            base_permissions.update({
                "create_projects": True,
                "edit_projects": True,
                "delete_projects": True,
                "create_users": True,
                "edit_users": True,
                "delete_users": True,
                "manage_partners": True,
                "view_financial_data": True,
                "edit_financial_data": True,
                "generate_reports": True,
                "export_data": True
            })
        elif role == UserRole.OFFICER:
            base_permissions.update({
                "create_projects": True,
                "edit_projects": True,
                "create_activities": True,
                "edit_activities": True,
                "view_financial_data": True,
                "generate_reports": True,
                "export_data": True
            })
        elif role == UserRole.PROJECT_MANAGER:
            base_permissions.update({
                "create_activities": True,
                "edit_activities": True,
                "create_projects": True,
                "edit_projects": True,
                "view_financial_data": True
            })
        elif role == UserRole.ME_OFFICER:
            base_permissions.update({
                "create_activities": True,
                "edit_activities": True,
                "generate_reports": True,
                "export_data": True,
                "view_financial_data": True
            })
        elif role == UserRole.FIELD_STAFF:
            base_permissions.update({
                "create_activities": True,
                "edit_activities": True
            })
        elif role == UserRole.PARTNER_STAFF:
            # Limited permissions for partner staff
            base_permissions.update({
                "view_projects": True,
                "view_activities": True,
                "create_activities": True,
                "edit_activities": True
            })
        elif role == UserRole.SYSTEM_ADMIN:
            # All permissions for system admin
            for key in base_permissions:
                base_permissions[key] = True
        
        return base_permissions

    # Partner Organization Management
    async def create_partner_organization(self, partner_data: PartnerOrganizationCreate, parent_organization_id: str) -> PartnerOrganization:
        """Create a new partner organization"""
        partner_dict = partner_data.model_dump()
        partner_dict["parent_organization_id"] = parent_organization_id
        partner_dict["created_at"] = datetime.utcnow()
        partner_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.partner_organizations.insert_one(partner_dict)
        partner_dict["_id"] = str(result.inserted_id)
        
        return PartnerOrganization(**partner_dict)

    async def get_partner_organizations(self, parent_organization_id: str, status: Optional[str] = None) -> List[PartnerOrganization]:
        """Get all partner organizations for a parent organization"""
        query = {"parent_organization_id": parent_organization_id}
        if status:
            query["status"] = status
            
        cursor = self.db.partner_organizations.find(query).sort("name", 1)
        partners = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            partners.append(PartnerOrganization(**doc))
        return partners

    async def update_partner_organization(self, partner_id: str, updates: PartnerOrganizationUpdate) -> Optional[PartnerOrganization]:
        """Update a partner organization"""
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.db.partner_organizations.update_one(
            {"_id": ObjectId(partner_id)}, 
            {"$set": update_data}
        )
        
        if result.modified_count:
            doc = await self.db.partner_organizations.find_one({"_id": ObjectId(partner_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                return PartnerOrganization(**doc)
        return None

    # Partner Performance Tracking
    async def create_partner_performance(self, performance_data: PartnerPerformanceCreate, evaluated_by: str) -> PartnerPerformance:
        """Create partner performance record"""
        performance_dict = performance_data.model_dump()
        performance_dict["evaluated_by"] = evaluated_by
        performance_dict["created_at"] = datetime.utcnow()
        performance_dict["updated_at"] = datetime.utcnow()
        
        # Calculate performance score
        performance_dict["performance_score"] = self._calculate_performance_score(performance_data)
        
        result = await self.db.partner_performances.insert_one(performance_dict)
        performance_dict["_id"] = str(result.inserted_id)
        
        return PartnerPerformance(**performance_dict)

    def _calculate_performance_score(self, performance_data: PartnerPerformanceCreate) -> float:
        """Calculate overall performance score based on metrics"""
        scores = []
        
        # Budget utilization score (0-30 points)
        if performance_data.budget_allocated > 0:
            budget_ratio = performance_data.budget_utilized / performance_data.budget_allocated
            if budget_ratio <= 1.0:  # Under or on budget
                budget_score = 30 * budget_ratio
            else:  # Over budget
                budget_score = max(0, 30 - (budget_ratio - 1) * 20)
            scores.append(budget_score)
        
        # Activity completion score (0-30 points)
        if performance_data.activities_planned > 0:
            activity_ratio = performance_data.activities_completed / performance_data.activities_planned
            activity_score = min(30, 30 * activity_ratio)
            scores.append(activity_score)
        
        # KPI achievement score (0-40 points)
        if performance_data.kpi_achievements:
            kpi_avg = sum(performance_data.kpi_achievements.values()) / len(performance_data.kpi_achievements)
            kpi_score = min(40, 40 * (kpi_avg / 100))  # Assuming KPIs are in percentage
            scores.append(kpi_score)
        
        return sum(scores) if scores else 0.0

    async def get_partner_performance_summary(self, organization_id: str, partner_id: Optional[str] = None) -> Dict[str, Any]:
        """Get consolidated partner performance summary"""
        match_query = {"parent_organization_id": organization_id}
        if partner_id:
            match_query["partner_organization_id"] = partner_id
        
        pipeline = [
            {"$match": match_query},
            {"$lookup": {
                "from": "partner_performances",
                "localField": "_id",
                "foreignField": "partner_organization_id", 
                "as": "performances"
            }},
            {"$addFields": {
                "avg_performance": {"$avg": "$performances.performance_score"},
                "total_budget_allocated": {"$sum": "$performances.budget_allocated"},
                "total_budget_utilized": {"$sum": "$performances.budget_utilized"},
                "total_beneficiaries": {"$sum": "$performances.beneficiaries_reached"}
            }}
        ]
        
        results = []
        async for doc in self.db.partner_organizations.aggregate(pipeline):
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        
        return {
            "partners": results,
            "summary": {
                "total_partners": len(results),
                "avg_performance": sum(p.get("avg_performance", 0) or 0 for p in results) / len(results) if results else 0,
                "total_budget": sum(p.get("total_budget_allocated", 0) or 0 for p in results),
                "total_beneficiaries": sum(p.get("total_beneficiaries", 0) or 0 for p in results)
            }
        }

    # Organization Branding
    async def update_organization_branding(self, organization_id: str, branding_data: OrganizationBrandingCreate) -> OrganizationBranding:
        """Update organization branding settings"""
        branding_dict = branding_data.model_dump(exclude_none=True)
        branding_dict["organization_id"] = organization_id
        branding_dict["updated_at"] = datetime.utcnow()
        
        # Upsert branding document
        result = await self.db.organization_branding.update_one(
            {"organization_id": organization_id},
            {"$set": branding_dict, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True
        )
        
        # Get the updated document
        doc = await self.db.organization_branding.find_one({"organization_id": organization_id})
        doc["_id"] = str(doc["_id"])
        return OrganizationBranding(**doc)

    async def get_organization_branding(self, organization_id: str) -> Optional[OrganizationBranding]:
        """Get organization branding settings"""
        doc = await self.db.organization_branding.find_one({"organization_id": organization_id})
        if doc:
            doc["_id"] = str(doc["_id"])
            return OrganizationBranding(**doc)
        return None

    # Mock Email System
    async def _send_user_credentials_email(self, organization_id: str, user_email: str, user_name: str, 
                                         username: str, password: str, role: str, created_by: str):
        """Send user credentials via mock email system"""
        
        # Create email log entry
        email_log = {
            "organization_id": organization_id,
            "recipient_email": user_email,
            "recipient_name": user_name,
            "template_used": "user_credentials",
            "subject": "Your DataRW Account Credentials",
            "body": f"""
            Dear {user_name},
            
            Your DataRW account has been created with the following credentials:
            
            Email: {user_email}
            Username: {username}
            Temporary Password: {password}
            Role: {role}
            
            Please log in and change your password on first access.
            
            Best regards,
            DataRW Team
            """,
            "status": "sent",  # Mock as sent
            "sent_at": datetime.utcnow(),
            "triggered_by": created_by,
            "created_at": datetime.utcnow()
        }
        
        await self.db.email_logs.insert_one(email_log)

    async def _send_batch_credentials_emails(self, organization_id: str, email_queue: List[Dict], created_by: str):
        """Send batch credentials emails"""
        
        for email_data in email_queue:
            await self._send_user_credentials_email(
                organization_id=organization_id,
                user_email=email_data["user"].email,
                user_name=email_data["user"].name,
                username=email_data["username"],
                password=email_data["password"],
                role=email_data["user"].role,
                created_by=created_by
            )

    async def get_email_logs(self, organization_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get email logs for organization"""
        cursor = self.db.email_logs.find(
            {"organization_id": organization_id}
        ).sort("created_at", -1).limit(limit)
        
        logs = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            logs.append(doc)
        
        return logs