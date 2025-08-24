import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bson import ObjectId
import asyncio
import math
from models import (
    Beneficiary, BeneficiaryCreate, BeneficiaryUpdate,
    ServiceRecord, ServiceRecordCreate, BatchServiceRecord,
    BeneficiaryKPI, BeneficiaryKPICreate, BeneficiaryKPIUpdate,
    BeneficiaryStatus, RiskLevel, ServiceType
)

class BeneficiaryService:
    def __init__(self, db):
        self.db = db

    # -------------------- Beneficiary CRUD Operations --------------------
    async def create_beneficiary(self, beneficiary_data: BeneficiaryCreate, organization_id: str, created_by: str) -> Beneficiary:
        """Create a new beneficiary"""
        try:
            # Generate system ID if not provided
            system_id = f"BEN-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            beneficiary = Beneficiary(
                **beneficiary_data.dict(),
                system_id=system_id,
                organization_id=organization_id,
                created_by=created_by,
                enrollment_date=datetime.utcnow()
            )
            
            # Insert into database
            result = await self.db.beneficiaries.insert_one(beneficiary.dict())
            beneficiary.id = str(result.inserted_id) if result.inserted_id else beneficiary.id
            
            return beneficiary
        except Exception as e:
            raise Exception(f"Failed to create beneficiary: {str(e)}")

    async def get_beneficiaries(
        self, 
        organization_id: str, 
        project_id: Optional[str] = None,
        activity_id: Optional[str] = None,
        status: Optional[BeneficiaryStatus] = None,
        risk_level: Optional[RiskLevel] = None,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get beneficiaries with filtering and pagination"""
        try:
            query = {"organization_id": organization_id}
            
            # Apply filters
            if project_id:
                query["project_ids"] = project_id
            if activity_id:
                query["activity_ids"] = activity_id
            if status:
                query["status"] = status
            if risk_level:
                query["risk_level"] = risk_level
            
            # Search functionality
            if search:
                query["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"first_name": {"$regex": search, "$options": "i"}},
                    {"last_name": {"$regex": search, "$options": "i"}},
                    {"national_id": {"$regex": search, "$options": "i"}},
                    {"system_id": {"$regex": search, "$options": "i"}}
                ]
            
            # Count total for pagination
            total = await self.db.beneficiaries.count_documents(query)
            
            # Apply pagination
            cursor = self.db.beneficiaries.find(query).sort("created_at", -1).skip((page - 1) * page_size).limit(page_size)
            
            beneficiaries = []
            async for doc in cursor:
                doc["_id"] = str(doc.get("_id"))
                beneficiaries.append(Beneficiary(**doc))
            
            return {
                "items": beneficiaries,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": math.ceil(total / page_size)
            }
        except Exception as e:
            raise Exception(f"Failed to get beneficiaries: {str(e)}")

    async def get_beneficiary_by_id(self, beneficiary_id: str, organization_id: str) -> Optional[Beneficiary]:
        """Get a specific beneficiary by ID"""
        try:
            query = {"organization_id": organization_id}
            
            # Try both _id and id fields
            try:
                query["_id"] = ObjectId(beneficiary_id)
            except Exception:
                query = {"organization_id": organization_id, "id": beneficiary_id}
            
            doc = await self.db.beneficiaries.find_one(query)
            if doc:
                doc["_id"] = str(doc.get("_id"))
                return Beneficiary(**doc)
            return None
        except Exception as e:
            raise Exception(f"Failed to get beneficiary: {str(e)}")

    async def update_beneficiary(
        self, 
        beneficiary_id: str, 
        beneficiary_data: BeneficiaryUpdate, 
        organization_id: str,
        updated_by: str
    ) -> Optional[Beneficiary]:
        """Update a beneficiary"""
        try:
            query = {"organization_id": organization_id}
            
            # Try both _id and id fields
            try:
                query["_id"] = ObjectId(beneficiary_id)
            except Exception:
                query = {"organization_id": organization_id, "id": beneficiary_id}
            
            update_data = {k: v for k, v in beneficiary_data.dict().items() if v is not None}
            update_data["updated_by"] = updated_by
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.db.beneficiaries.update_one(query, {"$set": update_data})
            
            if result.modified_count > 0:
                updated_doc = await self.db.beneficiaries.find_one(query)
                if updated_doc:
                    updated_doc["_id"] = str(updated_doc.get("_id"))
                    return Beneficiary(**updated_doc)
            return None
        except Exception as e:
            raise Exception(f"Failed to update beneficiary: {str(e)}")

    async def delete_beneficiary(self, beneficiary_id: str, organization_id: str) -> bool:
        """Delete a beneficiary (soft delete by setting status to inactive)"""
        try:
            query = {"organization_id": organization_id}
            
            # Try both _id and id fields
            try:
                query["_id"] = ObjectId(beneficiary_id)
            except Exception:
                query = {"organization_id": organization_id, "id": beneficiary_id}
            
            result = await self.db.beneficiaries.update_one(
                query, 
                {"$set": {"status": BeneficiaryStatus.INACTIVE, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Failed to delete beneficiary: {str(e)}")

    # -------------------- Service Records Management --------------------
    async def create_service_record(
        self, 
        service_data: ServiceRecordCreate, 
        organization_id: str,
        created_by: str
    ) -> ServiceRecord:
        """Create a service record"""
        try:
            service_record = ServiceRecord(
                **service_data.dict(),
                organization_id=organization_id,
                created_by=created_by
            )
            
            result = await self.db.service_records.insert_one(service_record.dict())
            service_record.id = str(result.inserted_id) if result.inserted_id else service_record.id
            
            # Update beneficiary's last service date
            await self.db.beneficiaries.update_one(
                {"id": service_data.beneficiary_id, "organization_id": organization_id},
                {"$set": {"last_service_date": service_data.service_date, "updated_at": datetime.utcnow()}}
            )
            
            return service_record
        except Exception as e:
            raise Exception(f"Failed to create service record: {str(e)}")

    async def create_batch_service_records(
        self, 
        batch_data: BatchServiceRecord, 
        organization_id: str,
        created_by: str
    ) -> List[ServiceRecord]:
        """Create service records for multiple beneficiaries"""
        try:
            service_records = []
            
            for beneficiary_id in batch_data.beneficiary_ids:
                service_data = ServiceRecordCreate(
                    beneficiary_id=beneficiary_id,
                    project_id=batch_data.project_id,
                    activity_id=batch_data.activity_id,
                    service_type=batch_data.service_type,
                    service_name=batch_data.service_name,
                    service_description=batch_data.service_description,
                    service_date=batch_data.service_date,
                    service_location=batch_data.service_location,
                    gps_latitude=batch_data.gps_latitude,
                    gps_longitude=batch_data.gps_longitude,
                    staff_responsible=batch_data.staff_responsible,
                    staff_name=batch_data.staff_name,
                    resources_used=batch_data.resources_used,
                    cost=batch_data.cost_per_beneficiary,
                    notes=batch_data.notes
                )
                
                service_record = await self.create_service_record(service_data, organization_id, created_by)
                service_records.append(service_record)
            
            return service_records
        except Exception as e:
            raise Exception(f"Failed to create batch service records: {str(e)}")

    async def get_service_records(
        self, 
        organization_id: str,
        beneficiary_id: Optional[str] = None,
        project_id: Optional[str] = None,
        activity_id: Optional[str] = None,
        service_type: Optional[ServiceType] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get service records with filtering and pagination"""
        try:
            query = {"organization_id": organization_id}
            
            if beneficiary_id:
                query["beneficiary_id"] = beneficiary_id
            if project_id:
                query["project_id"] = project_id
            if activity_id:
                query["activity_id"] = activity_id
            if service_type:
                query["service_type"] = service_type
            
            if date_from or date_to:
                date_filter = {}
                if date_from:
                    date_filter["$gte"] = date_from
                if date_to:
                    date_filter["$lte"] = date_to
                query["service_date"] = date_filter
            
            # Count total for pagination
            total = await self.db.service_records.count_documents(query)
            
            # Apply pagination
            cursor = self.db.service_records.find(query).sort("service_date", -1).skip((page - 1) * page_size).limit(page_size)
            
            records = []
            async for doc in cursor:
                doc["_id"] = str(doc.get("_id"))
                records.append(ServiceRecord(**doc))
            
            return {
                "items": records,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": math.ceil(total / page_size)
            }
        except Exception as e:
            raise Exception(f"Failed to get service records: {str(e)}")

    # -------------------- KPI Management --------------------
    async def create_beneficiary_kpi(
        self, 
        kpi_data: BeneficiaryKPICreate, 
        organization_id: str,
        created_by: str
    ) -> BeneficiaryKPI:
        """Create a KPI for a beneficiary"""
        try:
            # Calculate initial progress if baseline and current values exist
            progress_percentage = None
            if kpi_data.baseline_value is not None and kpi_data.current_value is not None and kpi_data.target_value is not None:
                if kpi_data.target_value != kpi_data.baseline_value:
                    progress_percentage = ((kpi_data.current_value - kpi_data.baseline_value) / 
                                         (kpi_data.target_value - kpi_data.baseline_value)) * 100
            
            kpi = BeneficiaryKPI(
                **kpi_data.dict(),
                progress_percentage=progress_percentage,
                organization_id=organization_id,
                created_by=created_by
            )
            
            result = await self.db.beneficiary_kpis.insert_one(kpi.dict())
            kpi.id = str(result.inserted_id) if result.inserted_id else kpi.id
            
            return kpi
        except Exception as e:
            raise Exception(f"Failed to create beneficiary KPI: {str(e)}")

    async def update_beneficiary_kpi(
        self, 
        kpi_id: str, 
        kpi_data: BeneficiaryKPIUpdate, 
        organization_id: str,
        updated_by: str
    ) -> Optional[BeneficiaryKPI]:
        """Update a beneficiary KPI"""
        try:
            # Get current KPI
            current_kpi = await self.db.beneficiary_kpis.find_one({
                "id": kpi_id, 
                "organization_id": organization_id
            })
            
            if not current_kpi:
                return None
            
            update_data = {k: v for k, v in kpi_data.dict().items() if v is not None}
            update_data["updated_by"] = updated_by
            update_data["updated_at"] = datetime.utcnow()
            
            # Recalculate progress if values are updated
            if "current_value" in update_data or "target_value" in update_data:
                current_value = update_data.get("current_value", current_kpi.get("current_value"))
                target_value = update_data.get("target_value", current_kpi.get("target_value"))
                baseline_value = current_kpi.get("baseline_value")
                
                if all(v is not None for v in [baseline_value, current_value, target_value]) and target_value != baseline_value:
                    progress_percentage = ((current_value - baseline_value) / (target_value - baseline_value)) * 100
                    update_data["progress_percentage"] = progress_percentage
                    update_data["is_on_track"] = progress_percentage >= 80  # 80% threshold for on-track
            
            result = await self.db.beneficiary_kpis.update_one(
                {"id": kpi_id, "organization_id": organization_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                updated_doc = await self.db.beneficiary_kpis.find_one({"id": kpi_id, "organization_id": organization_id})
                if updated_doc:
                    updated_doc["_id"] = str(updated_doc.get("_id"))
                    return BeneficiaryKPI(**updated_doc)
            return None
        except Exception as e:
            raise Exception(f"Failed to update beneficiary KPI: {str(e)}")

    async def get_beneficiary_kpis(
        self, 
        organization_id: str,
        beneficiary_id: Optional[str] = None,
        project_id: Optional[str] = None,
        activity_id: Optional[str] = None
    ) -> List[BeneficiaryKPI]:
        """Get KPIs for beneficiaries"""
        try:
            query = {"organization_id": organization_id}
            
            if beneficiary_id:
                query["beneficiary_id"] = beneficiary_id
            if project_id:
                query["project_id"] = project_id
            if activity_id:
                query["activity_id"] = activity_id
            
            cursor = self.db.beneficiary_kpis.find(query).sort("measurement_date", -1)
            
            kpis = []
            async for doc in cursor:
                doc["_id"] = str(doc.get("_id"))
                kpis.append(BeneficiaryKPI(**doc))
            
            return kpis
        except Exception as e:
            raise Exception(f"Failed to get beneficiary KPIs: {str(e)}")

    # -------------------- Analytics and Insights --------------------
    async def get_beneficiary_analytics(
        self, 
        organization_id: str,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive beneficiary analytics"""
        try:
            query = {"organization_id": organization_id}
            if project_id:
                query["project_ids"] = project_id
            
            # Basic statistics
            total_beneficiaries = await self.db.beneficiaries.count_documents(query)
            active_beneficiaries = await self.db.beneficiaries.count_documents({**query, "status": "active"})
            graduated_beneficiaries = await self.db.beneficiaries.count_documents({**query, "status": "graduated"})
            
            # Demographics
            demographics = {
                "gender_distribution": {},
                "age_distribution": {"0-18": 0, "19-35": 0, "36-50": 0, "50+": 0},
                "risk_distribution": {"low": 0, "medium": 0, "high": 0, "critical": 0}
            }
            
            # Get all beneficiaries for analysis
            cursor = self.db.beneficiaries.find(query)
            async for doc in cursor:
                # Gender distribution
                gender = doc.get("gender", "unknown")
                demographics["gender_distribution"][gender] = demographics["gender_distribution"].get(gender, 0) + 1
                
                # Age distribution
                age = doc.get("age")
                if age:
                    if age <= 18:
                        demographics["age_distribution"]["0-18"] += 1
                    elif age <= 35:
                        demographics["age_distribution"]["19-35"] += 1
                    elif age <= 50:
                        demographics["age_distribution"]["36-50"] += 1
                    else:
                        demographics["age_distribution"]["50+"] += 1
                
                # Risk distribution
                risk_level = doc.get("risk_level", "low")
                demographics["risk_distribution"][risk_level] = demographics["risk_distribution"].get(risk_level, 0) + 1
            
            # Service statistics
            service_query = {"organization_id": organization_id}
            if project_id:
                service_query["project_id"] = project_id
            
            total_services = await self.db.service_records.count_documents(service_query)
            
            # Recent services (last 30 days)
            recent_date = datetime.utcnow() - timedelta(days=30)
            recent_services = await self.db.service_records.count_documents({
                **service_query,
                "service_date": {"$gte": recent_date}
            })
            
            # Service type distribution
            service_types = {}
            service_cursor = self.db.service_records.find(service_query)
            async for doc in service_cursor:
                service_type = doc.get("service_type", "unknown")
                service_types[service_type] = service_types.get(service_type, 0) + 1
            
            return {
                "summary": {
                    "total_beneficiaries": total_beneficiaries,
                    "active_beneficiaries": active_beneficiaries,
                    "graduated_beneficiaries": graduated_beneficiaries,
                    "dropout_rate": round((total_beneficiaries - active_beneficiaries - graduated_beneficiaries) / max(total_beneficiaries, 1) * 100, 2),
                    "graduation_rate": round(graduated_beneficiaries / max(total_beneficiaries, 1) * 100, 2)
                },
                "demographics": demographics,
                "services": {
                    "total_services": total_services,
                    "recent_services": recent_services,
                    "service_type_distribution": service_types,
                    "avg_services_per_beneficiary": round(total_services / max(total_beneficiaries, 1), 2)
                }
            }
        except Exception as e:
            raise Exception(f"Failed to get beneficiary analytics: {str(e)}")

    async def get_beneficiary_map_data(
        self, 
        organization_id: str,
        project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get beneficiary location data for mapping"""
        try:
            query = {"organization_id": organization_id}
            if project_id:
                query["project_ids"] = project_id
            
            # Only get beneficiaries with GPS coordinates
            query["gps_latitude"] = {"$ne": None}
            query["gps_longitude"] = {"$ne": None}
            
            cursor = self.db.beneficiaries.find(query)
            
            map_data = []
            async for doc in cursor:
                map_point = {
                    "id": doc.get("id", str(doc.get("_id"))),
                    "name": doc.get("name", "Unknown"),
                    "latitude": doc.get("gps_latitude"),
                    "longitude": doc.get("gps_longitude"),
                    "status": doc.get("status", "active"),
                    "risk_level": doc.get("risk_level", "low"),
                    "progress_score": doc.get("progress_score"),
                    "last_service_date": doc.get("last_service_date"),
                    "project_ids": doc.get("project_ids", [])
                }
                map_data.append(map_point)
            
            return map_data
        except Exception as e:
            raise Exception(f"Failed to get map data: {str(e)}")

    async def calculate_risk_scores(self, organization_id: str) -> Dict[str, int]:
        """Calculate and update risk scores for all beneficiaries"""
        try:
            updated_count = 0
            
            cursor = self.db.beneficiaries.find({"organization_id": organization_id, "status": "active"})
            
            async for beneficiary in cursor:
                beneficiary_id = beneficiary.get("id", str(beneficiary.get("_id")))
                
                # Calculate risk score based on multiple factors
                risk_score = await self._calculate_individual_risk_score(beneficiary_id, organization_id)
                
                # Determine risk level
                if risk_score >= 80:
                    risk_level = RiskLevel.CRITICAL
                elif risk_score >= 60:
                    risk_level = RiskLevel.HIGH
                elif risk_score >= 40:
                    risk_level = RiskLevel.MEDIUM
                else:
                    risk_level = RiskLevel.LOW
                
                # Update beneficiary
                await self.db.beneficiaries.update_one(
                    {"id": beneficiary_id, "organization_id": organization_id},
                    {"$set": {"risk_score": risk_score, "risk_level": risk_level, "updated_at": datetime.utcnow()}}
                )
                
                updated_count += 1
            
            return {"updated_count": updated_count}
        except Exception as e:
            raise Exception(f"Failed to calculate risk scores: {str(e)}")

    async def _calculate_individual_risk_score(self, beneficiary_id: str, organization_id: str) -> float:
        """Calculate risk score for individual beneficiary"""
        try:
            risk_score = 0.0
            
            # Factor 1: Service attendance (40% weight)
            # Get recent services (last 90 days)
            recent_date = datetime.utcnow() - timedelta(days=90)
            recent_services = await self.db.service_records.count_documents({
                "beneficiary_id": beneficiary_id,
                "organization_id": organization_id,
                "service_date": {"$gte": recent_date}
            })
            
            # Expected services (assume 1 per week = 12 in 90 days)
            expected_services = 12
            attendance_rate = min(recent_services / expected_services, 1.0)
            risk_score += (1 - attendance_rate) * 40
            
            # Factor 2: KPI performance (30% weight)
            kpis = await self.get_beneficiary_kpis(organization_id, beneficiary_id=beneficiary_id)
            if kpis:
                avg_progress = sum(kpi.progress_percentage or 0 for kpi in kpis) / len(kpis)
                expected_progress = 75  # 75% expected progress
                kpi_risk = max(0, (expected_progress - avg_progress) / expected_progress)
                risk_score += kpi_risk * 30
            else:
                risk_score += 15  # Penalty for no KPI tracking
            
            # Factor 3: Time since last service (20% weight)
            beneficiary = await self.get_beneficiary_by_id(beneficiary_id, organization_id)
            if beneficiary and beneficiary.last_service_date:
                days_since_service = (datetime.utcnow() - beneficiary.last_service_date).days
                if days_since_service > 30:  # More than 30 days
                    time_risk = min(days_since_service / 90, 1.0)  # Cap at 90 days
                    risk_score += time_risk * 20
            else:
                risk_score += 20  # No service record
            
            # Factor 4: Satisfaction scores (10% weight)
            avg_satisfaction = await self.db.service_records.aggregate([
                {"$match": {"beneficiary_id": beneficiary_id, "organization_id": organization_id, "satisfaction_score": {"$ne": None}}},
                {"$group": {"_id": None, "avg_satisfaction": {"$avg": "$satisfaction_score"}}}
            ]).to_list(1)
            
            if avg_satisfaction:
                satisfaction = avg_satisfaction[0]["avg_satisfaction"]
                satisfaction_risk = max(0, (3 - satisfaction) / 2)  # 3 is middle score on 1-5 scale
                risk_score += satisfaction_risk * 10
            
            return min(risk_score, 100.0)  # Cap at 100
        except Exception as e:
            print(f"Error calculating risk score for beneficiary {beneficiary_id}: {e}")
            return 50.0  # Default medium risk

# Service will be initialized in server.py with database connection