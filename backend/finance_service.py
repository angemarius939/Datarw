import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from models import (
    Expense, ExpenseCreate, ExpenseUpdate,
    BudgetItem, BudgetItemCreate, BudgetItemUpdate,
)

class FinanceService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    # -------------------- Organization Finance Config --------------------
    async def get_org_config(self, organization_id: str) -> Dict[str, Any]:
        doc = await self.db.org_finance_configs.find_one({"organization_id": organization_id})
        if not doc:
            return {
                "organization_id": organization_id,
                "funding_sources": ["World Bank", "Mastercard Foundation", "USAID", "UNDP"],
                "cost_centers": ["HR", "Operations", "Field Work", "M&E", "Project officers"],
                "updated_at": datetime.utcnow().isoformat()
            }
        doc.pop("_id", None)
        return doc

    async def update_org_config(self, organization_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        allowed = {k: v for k, v in updates.items() if k in ("funding_sources", "cost_centers") and isinstance(v, list)}
        allowed["updated_at"] = datetime.utcnow().isoformat()
        allowed["organization_id"] = organization_id
        await self.db.org_finance_configs.update_one(
            {"organization_id": organization_id},
            {"$set": allowed},
            upsert=True
        )
        return await self.get_org_config(organization_id)

    # -------------------- Expenses CRUD --------------------
    async def create_expense(self, data: ExpenseCreate, organization_id: str, user_id: str) -> Expense:
        payload = data.model_dump()
        now = datetime.utcnow()
        payload.update({
            "id": str(uuid.uuid4()),
            "organization_id": organization_id,
            "created_by": user_id,
            "created_at": now,
            "updated_at": now,
        })
        await self.db.expenses.insert_one(payload)
        payload["_id"] = str(payload.get("_id"))
        return Expense(**payload)

    async def list_expenses(self, organization_id: str, filters: Dict[str, Any], page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        query: Dict[str, Any] = {"organization_id": organization_id}
        if project_id := filters.get("project_id"):
            query["project_id"] = project_id
        if activity_id := filters.get("activity_id"):
            query["activity_id"] = activity_id
        if funding_source := filters.get("funding_source"):
            query["funding_source"] = funding_source
        if vendor := filters.get("vendor"):
            query["vendor"] = {"$regex": vendor, "$options": "i"}
        if date_from := filters.get("date_from"):
            query.setdefault("date", {})["$gte"] = datetime.fromisoformat(date_from)
        if date_to := filters.get("date_to"):
            query.setdefault("date", {})["$lte"] = datetime.fromisoformat(date_to)

        total = await self.db.expenses.count_documents(query)
        cursor = self.db.expenses.find(query).sort("date", -1).skip((page - 1) * page_size).limit(page_size)
        items: List[Dict[str, Any]] = []
        async for doc in cursor:
            doc["_id"] = str(doc.get("_id"))
            items.append(doc)
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    async def get_expense(self, organization_id: str, expense_id: str) -> Optional[Expense]:
        filters = []
        try:
            filters.append({"_id": ObjectId(expense_id)})
        except Exception:
            pass
        filters.append({"id": expense_id})
        query = {"$and": [{"organization_id": organization_id}, {"$or": filters}]}
        doc = await self.db.expenses.find_one(query)
        if doc:
            doc["_id"] = str(doc.get("_id"))
            return Expense(**doc)
        return None

    async def update_expense(self, organization_id: str, expense_id: str, updates: ExpenseUpdate, user_id: str) -> Optional[Expense]:
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        update_data["last_updated_by"] = user_id
        filters = []
        try:
            filters.append({"_id": ObjectId(expense_id)})
        except Exception:
            pass
        filters.append({"id": expense_id})
        query = {"$and": [{"organization_id": organization_id}, {"$or": filters}]}
        res = await self.db.expenses.update_one(query, {"$set": update_data})
        if res.matched_count:
            doc = await self.db.expenses.find_one(query)
            if doc:
                doc["_id"] = str(doc.get("_id"))
                return Expense(**doc)
        return None

    async def delete_expense(self, organization_id: str, expense_id: str) -> bool:
        filters = []
        try:
            filters.append({"_id": ObjectId(expense_id)})
        except Exception:
            pass
        filters.append({"id": expense_id})
        query = {"$and": [{"organization_id": organization_id}, {"$or": filters}]}
        res = await self.db.expenses.delete_one(query)
        return res.deleted_count > 0

    # -------------------- Summaries & Analytics --------------------
    async def budget_vs_actual(self, organization_id: str, project_id: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        match_budget = {"organization_id": organization_id}
        if project_id:
            match_budget["project_id"] = project_id
        # Aggregate BudgetItems (planned)
        pipeline_budget = [
            {"$match": match_budget},
            {"$group": {"_id": "$project_id", "planned": {"$sum": "$budgeted_amount"}, "allocated": {"$sum": "$allocated_amount"}, "utilized_pi": {"$sum": "$utilized_amount"}}}
        ]
        planned_by_project: Dict[str, Dict[str, float]] = {}
        async for b in self.db.budget_items.aggregate(pipeline_budget):
            planned_by_project[str(b["_id"]) or "unknown"] = {
                "planned": float(b.get("planned", 0)),
                "allocated": float(b.get("allocated", 0)),
                "utilized_pi": float(b.get("utilized_pi", 0)),
            }
        # Aggregate expenses (actual)
        match_exp = {"organization_id": organization_id}
        if project_id:
            match_exp["project_id"] = project_id
        if date_from:
            match_exp.setdefault("date", {})["$gte"] = datetime.fromisoformat(date_from)
        if date_to:
            match_exp.setdefault("date", {})["$lte"] = datetime.fromisoformat(date_to)
        pipeline_exp = [
            {"$match": match_exp},
            {"$group": {"_id": "$project_id", "actual": {"$sum": "$amount"}}}
        ]
        actual_by_project: Dict[str, float] = {}
        async for e in self.db.expenses.aggregate(pipeline_exp):
            actual_by_project[str(e["_id"]) or "unknown"] = float(e.get("actual", 0))
        # Merge
        result: List[Dict[str, Any]] = []
        keys = set(planned_by_project.keys()) | set(actual_by_project.keys())
        for k in keys:
            planned = planned_by_project.get(k, {}).get("planned", 0.0)
            allocated = planned_by_project.get(k, {}).get("allocated", 0.0)
            utilized_pi = planned_by_project.get(k, {}).get("utilized_pi", 0.0)
            actual = actual_by_project.get(k, 0.0)
            variance_amount = planned - actual
            variance_pct = (variance_amount / planned * 100.0) if planned else 0.0
            result.append({
                "project_id": k,
                "planned": planned,
                "allocated": allocated,
                "actual": actual,
                "variance_amount": variance_amount,
                "variance_pct": variance_pct,
            })
        return {"by_project": result}

    async def burn_rate(self, organization_id: str, period: str = "monthly", project_id: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        now = datetime.utcnow()
        start = now - timedelta(days=365)
        match = {"organization_id": organization_id, "date": {"$gte": start}}
        if project_id:
            match["project_id"] = project_id
        if date_from:
            match.setdefault("date", {})["$gte"] = datetime.fromisoformat(date_from)
        if date_to:
            match.setdefault("date", {})["$lte"] = datetime.fromisoformat(date_to)
        if period == "quarterly":
            group_id = {"year": {"$year": "$date"}, "quarter": {"$ceil": {"$divide": [{"$month": "$date"}, 3]}}}
            label_build = lambda g: f"{int(g['year'])}-Q{int(g['quarter'])}"
        elif period == "annual":
            group_id = {"year": {"$year": "$date"}}
            label_build = lambda g: f"{int(g['year'])}"
        else:
            group_id = {"year": {"$year": "$date"}, "month": {"$month": "$date"}}
            label_build = lambda g: f"{int(g['year'])}-{int(g['month']):02d}"
        pipeline = [
            {"$match": match},
            {"$group": {"_id": group_id, "spent": {"$sum": "$amount"}}},
            {"$sort": {"_id.year": 1, "_id.month": 1 if period == 'monthly' else 1, "_id.quarter": 1 if period == 'quarterly' else 1}},
        ]
        series: List[Dict[str, Any]] = []
        async for d in self.db.expenses.aggregate(pipeline):
            label = label_build(d["_id"])
            series.append({"period": label, "spent": float(d.get("spent", 0))})
        return {"period": period, "series": series}

    async def forecast(self, organization_id: str) -> Dict[str, Any]:
        now = datetime.utcnow()
        start_year = datetime(now.year, 1, 1)
        match = {"organization_id": organization_id, "date": {"$gte": start_year}}
        pipeline = [
            {"$match": match},
            {"$group": {"_id": {"year": {"$year": "$date"}, "month": {"$month": "$date"}}, "spent": {"$sum": "$amount"}}}
        ]
        monthly = []
        async for d in self.db.expenses.aggregate(pipeline):
            monthly.append(float(d.get("spent", 0)))
        avg = sum(monthly) / len(monthly) if monthly else 0.0
        remaining_months = 12 - now.month
        projection = avg * remaining_months
        return {"avg_monthly": avg, "projected_spend_rest_of_year": projection, "months_remaining": remaining_months}

    async def funding_utilization(self, organization_id: str, donor: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        match = {"organization_id": organization_id}
        if donor:
            match["funding_source"] = donor
        if date_from:
            match.setdefault("date", {})["$gte"] = datetime.fromisoformat(date_from)
        if date_to:
            match.setdefault("date", {})["$lte"] = datetime.fromisoformat(date_to)
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$funding_source", "spent": {"$sum": "$amount"}}}
        ]
        items: List[Dict[str, Any]] = []
        async for d in self.db.expenses.aggregate(pipeline):
            items.append({"funding_source": d.get("_id") or "Unknown", "spent": float(d.get("spent", 0))})
        return {"by_funding_source": items}

    # -------------------- Finance Reports Data Helpers --------------------
    async def project_budget_details(self, organization_id: str, project_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        # Budget lines
        match_budget = {"organization_id": organization_id, "project_id": project_id}
        budget_cursor = self.db.budget_items.find(match_budget)
        budget_lines: List[Dict[str, Any]] = []
        total_budgeted = 0.0
        total_allocated = 0.0
        async for b in budget_cursor:
            amt = float(b.get("budgeted_amount", 0))
            total_budgeted += amt
            total_allocated += float(b.get("allocated_amount", 0))
            budget_lines.append({
                "category": b.get("category") or "(uncategorized)",
                "activity_id": b.get("activity_id") or "",
                "budgeted": amt,
                "allocated": float(b.get("allocated_amount", 0)),
                "utilized_pi": float(b.get("utilized_amount", 0)),
            })
        # Expenses by activity within date range
        match_exp = {"organization_id": organization_id, "project_id": project_id}
        if date_from:
            match_exp.setdefault("date", {})["$gte"] = datetime.fromisoformat(date_from)
        if date_to:
            match_exp.setdefault("date", {})["$lte"] = datetime.fromisoformat(date_to)
        pipeline = [
            {"$match": match_exp},
            {"$group": {"_id": "$activity_id", "spent": {"$sum": "$amount"}, "count": {"$sum": 1}}}
        ]
        spent_by_activity: Dict[str, Dict[str, Any]] = {}
        async for e in self.db.expenses.aggregate(pipeline):
            spent_by_activity[str(e.get("_id") or "")] = {"spent": float(e.get("spent", 0)), "transactions": int(e.get("count", 0))}
        total_spent = sum([v["spent"] for v in spent_by_activity.values()])
        variance_amount = total_budgeted - total_spent
        variance_pct = (variance_amount / total_budgeted * 100) if total_budgeted else 0.0
        return {
            "total_budgeted": total_budgeted,
            "total_allocated": total_allocated,
            "total_spent": total_spent,
            "variance_amount": variance_amount,
            "variance_pct": variance_pct,
            "budget_lines": budget_lines,
            "spent_by_activity": spent_by_activity,
        }

    async def all_projects_variance(self, organization_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[Dict[str, Any]]:
        return (await self.budget_vs_actual(organization_id, None, date_from, date_to)).get("by_project", [])