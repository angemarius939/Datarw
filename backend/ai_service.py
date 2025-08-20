import os
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from emergentintegrations.llm.chat import LlmChat, UserMessage
from models import (
    SurveyQuestion, QuestionType, AISurveyGenerationRequest, 
    SurveyGenerationContext, DocumentUpload
)

class AIService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.emergent_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.emergent_key:
            raise ValueError("EMERGENT_LLM_KEY environment variable is required")

    async def generate_survey_with_ai(
        self, 
        request: AISurveyGenerationRequest, 
        organization_id: str
    ) -> Dict[str, Any]:
        """Generate a survey using AI based on user description and optional document context"""
        
        # Get organization context if available
        context = await self._get_organization_context(organization_id)
        
        # Build the AI prompt
        prompt = await self._build_survey_generation_prompt(request, context)
        
        try:
            # Initialize LLM chat
            session_id = f"survey_gen_{organization_id}_{uuid.uuid4().hex[:8]}"
            chat = LlmChat(
                api_key=self.emergent_key,
                session_id=session_id,
                system_message="You are an expert survey designer with deep knowledge of research methodologies, questionnaire design, and data collection best practices. Your task is to create comprehensive, well-structured surveys that will generate high-quality data."
            ).with_model("openai", "gpt-4.1")
            
            # Create user message
            user_message = UserMessage(text=prompt)
            
            # Get AI response
            response = await chat.send_message(user_message)
            
            # Parse the AI response to extract survey structure
            survey_data = await self._parse_ai_response(response)
            
        except Exception as e:
            print(f"AI generation failed: {e}")
            # Fallback to a template-based survey generation
            survey_data = await self._generate_fallback_survey(request)
        
        return survey_data

    async def _get_organization_context(self, organization_id: str) -> Optional[SurveyGenerationContext]:
        """Get organization's document context for survey generation"""
        context_doc = await self.db.survey_generation_contexts.find_one(
            {"organization_id": organization_id}
        )
        if context_doc:
            # Convert ObjectId to string if present
            if "_id" in context_doc and hasattr(context_doc["_id"], "hex"):
                context_doc["_id"] = str(context_doc["_id"])
            return SurveyGenerationContext(**context_doc)
        return None

    async def _build_survey_generation_prompt(
        self, 
        request: AISurveyGenerationRequest, 
        context: Optional[SurveyGenerationContext]
    ) -> str:
        """Build a comprehensive prompt for survey generation"""
        
        prompt_parts = [
            "Create a comprehensive survey based on the following requirements:",
            f"Survey Description: {request.description}",
        ]
        
        if request.target_audience:
            prompt_parts.append(f"Target Audience: {request.target_audience}")
            
        if request.survey_purpose:
            prompt_parts.append(f"Survey Purpose: {request.survey_purpose}")
            
        prompt_parts.append(f"Number of Questions Requested: {request.question_count}")
        
        if request.include_demographics:
            prompt_parts.append("Include demographic questions (age, gender, location, etc.)")
            
        # Add document context if available
        if context:
            prompt_parts.append("\nDocument Context Available:")
            if context.business_profile:
                prompt_parts.append(f"Business Profile: {context.business_profile[:500]}...")
            if context.participant_profiles:
                prompt_parts.append(f"Participant Profiles: {context.participant_profiles[:500]}...")
            if context.policies:
                prompt_parts.append(f"Policies: {context.policies[:500]}...")
            if context.strategic_documents:
                prompt_parts.append(f"Strategic Documents: {context.strategic_documents[:500]}...")
        
        # Add question types information
        question_types_info = """
Available Question Types:
1. multiple_choice_single - Single selection from multiple options
2. multiple_choice_multiple - Multiple selections allowed (checkboxes)
3. short_text - Brief text responses (1-2 words or short phrases)
4. long_text - Detailed text responses (paragraphs)
5. rating_scale - Numeric rating (1-5, 1-10, etc.)
6. likert_scale - Agreement scale (Strongly Disagree to Strongly Agree)
7. ranking - Rank options in order of preference
8. dropdown - Select one option from dropdown list
9. matrix_grid - Grid of questions with same response options
10. file_upload - Allow file attachments
11. date_picker - Select a date
12. time_picker - Select a time
13. datetime_picker - Select date and time
14. slider - Visual slider for numeric input
15. numeric_scale - Enter numeric value within range
16. image_choice - Choose from images
17. yes_no - Simple yes/no question
18. signature - Digital signature capture
"""
        
        prompt_parts.append(question_types_info)
        
        # Response format instructions
        format_instructions = """
Return your response as a JSON object with the following structure:
{
    "title": "Survey Title",
    "description": "Survey Description",
    "questions": [
        {
            "type": "question_type",
            "question": "Question text",
            "required": true/false,
            "options": ["Option 1", "Option 2"] (for multiple choice, dropdown, etc.),
            "scale_min": 1 (for rating/slider),
            "scale_max": 5 (for rating/slider),
            "scale_labels": ["Very Poor", "Poor", "Fair", "Good", "Excellent"] (for likert),
            "matrix_rows": ["Row 1", "Row 2"] (for matrix),
            "matrix_columns": ["Col 1", "Col 2"] (for matrix),
            "file_types_allowed": ["pdf", "doc", "jpg"] (for file upload),
            "max_file_size_mb": 10 (for file upload),
            "multiple_selection": true/false (for multiple choice),
            "validation_rules": {"min_length": 10} (optional)
        }
    ]
}

Guidelines:
- Create engaging, clear, and unbiased questions
- Use appropriate question types for different data needs
- Ensure logical flow and question order
- Include validation rules where appropriate
- Make questions specific and actionable
- Avoid leading or loaded questions
- Consider cultural sensitivity and inclusivity
"""
        
        prompt_parts.append(format_instructions)
        
        return "\n\n".join(prompt_parts)

    async def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and convert to survey structure"""
        try:
            # Try to extract JSON from response
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:-3].strip()
            elif response_clean.startswith("```"):
                response_clean = response_clean[3:-3].strip()
            
            survey_data = json.loads(response_clean)
            
            # Validate and clean the survey data
            cleaned_questions = []
            for q in survey_data.get("questions", []):
                try:
                    question_type = QuestionType(q.get("type"))
                    
                    # Create question object with proper defaults
                    question = {
                        "type": question_type,
                        "question": q.get("question", ""),
                        "required": q.get("required", False),
                        "options": q.get("options", []),
                        "scale_min": q.get("scale_min"),
                        "scale_max": q.get("scale_max"),
                        "scale_labels": q.get("scale_labels", []),
                        "matrix_rows": q.get("matrix_rows", []),
                        "matrix_columns": q.get("matrix_columns", []),
                        "file_types_allowed": q.get("file_types_allowed", []),
                        "max_file_size_mb": q.get("max_file_size_mb"),
                        "multiple_selection": q.get("multiple_selection", False),
                        "validation_rules": q.get("validation_rules", {})
                    }
                    cleaned_questions.append(question)
                except ValueError:
                    # Skip invalid question types
                    continue
            
            return {
                "title": survey_data.get("title", "AI Generated Survey"),
                "description": survey_data.get("description", "Survey generated by AI"),
                "questions": cleaned_questions
            }
            
        except json.JSONDecodeError:
            # Fallback: create a basic survey structure
            return {
                "title": "AI Generated Survey",
                "description": "Survey generated by AI (parsing error occurred)",
                "questions": [
                    {
                        "type": QuestionType.LONG_TEXT,
                        "question": "Please provide your feedback on the topic discussed.",
                        "required": False,
                        "options": [],
                        "validation_rules": {}
                    }
                ]
            }

    async def save_document_context(
        self, 
        organization_id: str, 
        documents: List[DocumentUpload]
    ) -> SurveyGenerationContext:
        """Save uploaded documents as context for survey generation"""
        
        # Get existing context or create new
        existing_context = await self._get_organization_context(organization_id)
        
        if existing_context:
            # Update existing context
            context_data = existing_context.model_dump()
            context_data["uploaded_documents"].extend([doc.model_dump() for doc in documents])
            context_data["last_updated"] = datetime.utcnow()
        else:
            # Create new context
            context_data = {
                "organization_id": organization_id,
                "uploaded_documents": [doc.model_dump() for doc in documents],
                "last_updated": datetime.utcnow()
            }
        
        # Extract content for different categories
        await self._categorize_documents(context_data)
        
        # Save to database
        result = await self.db.survey_generation_contexts.replace_one(
            {"organization_id": organization_id},
            context_data,
            upsert=True
        )
        
        # Set the ID for the returned object
        if result.upserted_id:
            context_data["_id"] = str(result.upserted_id)
        else:
            # Get the existing document to get its ID
            existing_doc = await self.db.survey_generation_contexts.find_one(
                {"organization_id": organization_id}
            )
            if existing_doc and "_id" in existing_doc:
                context_data["_id"] = str(existing_doc["_id"])
        
        return SurveyGenerationContext(**context_data)

    async def _categorize_documents(self, context_data: Dict[str, Any]):
        """Use AI to categorize and extract relevant information from documents"""
        documents = context_data.get("uploaded_documents", [])
        if not documents:
            return
            
        # Combine all document content
        all_content = "\n\n".join([doc.get("content", "") for doc in documents])
        
        # Use AI to categorize and extract key information
        session_id = f"doc_analysis_{uuid.uuid4().hex[:8]}"
        chat = LlmChat(
            api_key=self.emergent_key,
            session_id=session_id,
            system_message="You are an expert document analyzer. Extract and categorize key information from business documents."
        ).with_model("openai", "gpt-4.1")
        
        prompt = f"""
Analyze the following documents and extract key information for survey generation:

Documents Content:
{all_content[:5000]}  # Limit content to avoid token limits

Please categorize and extract the following:
1. Business Profile: Company overview, mission, values, services/products
2. Participant Profiles: Target audience, customer segments, stakeholder information
3. Policies: Rules, guidelines, compliance requirements
4. Strategic Information: Goals, objectives, KPIs, strategic initiatives

Return as JSON:
{{
    "business_profile": "extracted business information",
    "participant_profiles": "target audience and stakeholder info", 
    "policies": "relevant policies and guidelines",
    "strategic_documents": "strategic goals and objectives"
}}
"""
        
        try:
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Parse response
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:-3].strip()
            elif response_clean.startswith("```"):
                response_clean = response_clean[3:-3].strip()
                
            categorized_info = json.loads(response_clean)
            
            # Update context data
            context_data.update(categorized_info)
            
        except Exception as e:
            print(f"Error categorizing documents: {e}")
            # Set basic categorization
            context_data["business_profile"] = all_content[:1000]
            
    async def translate_survey(
        self, 
        survey_data: Dict[str, Any], 
        target_language: str = "kinyarwanda"
    ) -> Dict[str, Any]:
        """Translate survey content to specified language"""
        
        session_id = f"translation_{uuid.uuid4().hex[:8]}"
        chat = LlmChat(
            api_key=self.emergent_key,
            session_id=session_id,
            system_message=f"You are an expert translator with deep knowledge of {target_language}. Provide accurate, culturally appropriate translations while maintaining the original meaning and context."
        ).with_model("openai", "gpt-4.1")
        
        prompt = f"""
Translate the following survey content to {target_language}. Maintain the JSON structure and translate only the text content (title, description, questions, options, labels).

Original Survey:
{json.dumps(survey_data, indent=2)}

Guidelines:
- Keep technical field names unchanged
- Translate title, description, question text, options, and labels
- Maintain cultural sensitivity and appropriateness
- Use formal/respectful tone appropriate for surveys
- Keep the same JSON structure

Return the translated survey as JSON.
"""
        
        try:
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Parse response
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:-3].strip()
            elif response_clean.startswith("```"):
                response_clean = response_clean[3:-3].strip()
                
            translated_survey = json.loads(response_clean)
            return translated_survey
            
        except Exception as e:
            print(f"Translation error: {e}")
            # Return original survey if translation fails
            return survey_data