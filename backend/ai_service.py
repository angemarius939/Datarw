import os
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from pydantic import BaseModel

from emergentintegrations.llm.chat import LlmChat, UserMessage
from models import (
    SurveyQuestion, QuestionType, AISurveyGenerationRequest, 
    SurveyGenerationContext, DocumentUpload
)

def convert_objectids_to_strings(obj):
    if isinstance(obj, dict):
        return {key: convert_objectids_to_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectids_to_strings(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj

class AIService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.emergent_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.emergent_key:
            raise ValueError("EMERGENT_LLM_KEY environment variable is required")

    # ... existing methods (unchanged) ...

# Finance AI functionality
try:
    from emergentintegrations import LLMClient
except Exception:
    LLMClient = None

class FinanceAIInsight(BaseModel):
    risk_level: str
    description: str
    recommendations: List[str]
    confidence: float
    reallocation_suggestions: Optional[List[str]] = None
    forecast_summary: Optional[Dict[str, Any]] = None
    disbursement_timing: Optional[List[str]] = None
    budget_finish_estimate: Optional[str] = None
    variance_hotspots: Optional[List[str]] = None
    risk_predictions: Optional[List[str]] = None

class FinanceAI:
    def __init__(self):
        self.key = os.environ.get('EMERGENT_LLM_KEY')
        self.client = None
        if self.key and LLMClient:
            try:
                self.client = LLMClient(api_key=self.key, provider='openai', model='gpt-4o')
            except Exception:
                self.client = None

    async def analyze(self, summary: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> FinanceAIInsight:
        if not self.client:
            count = len(anomalies)
            risk = 'low' if count == 0 else 'medium' if count < 5 else 'high'
            # Simple heuristic add-ons
            reallocation = ['Consider reallocating unused funds from low-variance items to critical path activities']
            forecast = {'method': 'avg_monthly', 'notes': 'Using simple average monthly spend for projection'}
            return FinanceAIInsight(
                risk_level=risk,
                description='Fallback analysis based on available summaries',
                recommendations=['Review high-variance items', 'Adjust disbursements', 'Set alerts for vendor spikes'],
                confidence=0.6,
                reallocation_suggestions=reallocation,
                forecast_summary=forecast,
                budget_finish_estimate='unknown',
            )
        # Rich prompt with requested capabilities
        prompt = (
            "You are a project finance co-pilot. Analyze provided summaries and anomalies and return STRICT JSON with keys: "
            "risk_level, description, recommendations (array of 3-7), confidence (0-1), "
            "reallocation_suggestions (array), forecast_summary (object with remaining_costs_estimate, cash_flow_alerts if any), "
            "disbursement_timing (array with activity-based timing guidance), budget_finish_estimate (under/over/about on budget with %), "
            "variance_hotspots (array identifying activities/lines requiring action), risk_predictions (array predicting likely over/under spend activities).\n"
            f"Summary: {json.dumps(summary)[:8000]}\n"
            f"Anomalies: {json.dumps(anomalies)[:2000]}\n"
            "Ensure JSON only, no prose."
        )
        try:
            resp = await self.client.chat(messages=[
                {"role": "system", "content": "Be concise, return JSON only."},
                {"role": "user", "content": prompt}
            ])
            text = resp.get('content') or resp.get('text') or str(resp)
            # Parse JSON
            data = json.loads(text)
            return FinanceAIInsight(**data)
        except Exception:
            # Fallback
            return FinanceAIInsight(
                risk_level='medium',
                description='AI service error; using fallback guidance',
                recommendations=['Review cost centers', 'Cut non-critical spend'],
                confidence=0.6,
            )