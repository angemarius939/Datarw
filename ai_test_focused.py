#!/usr/bin/env python3
"""
Focused AI Survey Generation Testing for DataRW
Tests only the AI-related endpoints to avoid survey limit issues.
"""

import requests
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://datarw-platform.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class AITestFocused:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.test_results = []
        
        # Test data
        self.test_email = f"ai.test.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "AI Test User"
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def setup_authentication(self):
        """Setup authentication for AI tests"""
        try:
            # Register user
            registration_data = {
                "email": self.test_email,
                "password": self.test_password,
                "name": self.test_name
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=registration_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.user_data = data["user"]
                self.organization_data = data["organization"]
                
                # Set authorization header
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                self.log_result("Authentication Setup", True, "User registered and authenticated")
                return True
            else:
                self.log_result("Authentication Setup", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Authentication Setup", False, f"Request error: {str(e)}")
            return False

    def test_ai_survey_generation(self):
        """Test AI survey generation endpoint"""
        try:
            ai_request_data = {
                "description": "Create a customer satisfaction survey for a restaurant business",
                "target_audience": "Restaurant customers aged 25-55",
                "survey_purpose": "Measure customer satisfaction and identify improvement areas",
                "question_count": 8,
                "include_demographics": True
            }
            
            response = self.session.post(
                f"{self.base_url}/surveys/generate-ai",
                json=ai_request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and 
                    "survey_data" in data and 
                    "title" in data["survey_data"] and 
                    "questions" in data["survey_data"]):
                    
                    survey_data = data["survey_data"]
                    questions = survey_data.get("questions", [])
                    
                    if len(questions) > 0:
                        self.ai_generated_survey = survey_data
                        self.log_result("AI Survey Generation", True, 
                                      f"AI generated survey with {len(questions)} questions successfully")
                        return True
                    else:
                        self.log_result("AI Survey Generation", False, "No questions generated", data)
                        return False
                else:
                    self.log_result("AI Survey Generation", False, "Missing required fields in response", data)
                    return False
            else:
                self.log_result("AI Survey Generation", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("AI Survey Generation", False, f"Request error: {str(e)}")
            return False

    def test_document_upload_context(self):
        """Test document upload for AI context"""
        try:
            # Create a sample document content
            sample_document = """
            Restaurant Business Plan
            
            Our restaurant "Taste of Rwanda" specializes in traditional Rwandan cuisine with a modern twist.
            We serve customers from all walks of life, focusing on authentic flavors and excellent service.
            
            Target Market:
            - Local professionals aged 25-45
            - Tourists interested in authentic cuisine
            - Families looking for quality dining experiences
            
            Our Mission: To provide exceptional dining experiences while preserving Rwandan culinary traditions.
            """
            
            # Create multipart form data manually
            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
            
            # Build multipart body
            body_parts = []
            body_parts.append(f'--{boundary}')
            body_parts.append('Content-Disposition: form-data; name="files"; filename="business_plan.txt"')
            body_parts.append('Content-Type: text/plain')
            body_parts.append('')
            body_parts.append(sample_document)
            body_parts.append(f'--{boundary}--')
            
            body = '\r\n'.join(body_parts)
            
            headers = {
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            }
            
            response = self.session.post(
                f"{self.base_url}/surveys/upload-context",
                data=body.encode('utf-8'),
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and 
                    "context_id" in data and 
                    "documents_processed" in data):
                    
                    self.context_id = data["context_id"]
                    self.log_result("Document Upload Context", True, 
                                  f"Uploaded {data['documents_processed']} documents successfully")
                    return True
                else:
                    self.log_result("Document Upload Context", False, "Missing required fields in response", data)
                    return False
            else:
                self.log_result("Document Upload Context", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Document Upload Context", False, f"Request error: {str(e)}")
            return False

    def test_get_survey_context(self):
        """Test getting survey context for organization"""
        try:
            if not self.organization_data:
                self.log_result("Get Survey Context", False, "No organization data available")
                return False
            
            # Handle both 'id' and '_id' fields
            org_id = self.organization_data.get("id") or self.organization_data.get("_id")
            if not org_id:
                self.log_result("Get Survey Context", False, "No organization ID found in organization data")
                return False
                
            response = self.session.get(f"{self.base_url}/surveys/context/{org_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Context can be None if no documents uploaded
                    context = data.get("context")
                    if context is not None:
                        self.log_result("Get Survey Context", True, "Survey context retrieved successfully")
                    else:
                        self.log_result("Get Survey Context", True, "No context found (expected for new organization)")
                    return True
                else:
                    self.log_result("Get Survey Context", False, "Success flag not set", data)
                    return False
            else:
                self.log_result("Get Survey Context", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Survey Context", False, f"Request error: {str(e)}")
            return False

    def test_ai_with_context_generation(self):
        """Test AI survey generation with document context"""
        try:
            ai_request_data = {
                "description": "Create a comprehensive employee satisfaction survey based on our company policies and culture",
                "target_audience": "All company employees",
                "survey_purpose": "Annual employee satisfaction assessment",
                "question_count": 12,
                "include_demographics": True,
                "document_context": "Use uploaded business documents for context"
            }
            
            response = self.session.post(
                f"{self.base_url}/surveys/generate-ai",
                json=ai_request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and 
                    "survey_data" in data and 
                    "title" in data["survey_data"] and 
                    "questions" in data["survey_data"]):
                    
                    survey_data = data["survey_data"]
                    questions = survey_data.get("questions", [])
                    
                    if len(questions) > 0:
                        self.log_result("AI with Context Generation", True, 
                                      f"AI generated contextual survey with {len(questions)} questions")
                        return True
                    else:
                        self.log_result("AI with Context Generation", False, "No questions generated", data)
                        return False
                else:
                    self.log_result("AI with Context Generation", False, "Missing required fields in response", data)
                    return False
            else:
                self.log_result("AI with Context Generation", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("AI with Context Generation", False, f"Request error: {str(e)}")
            return False

    def test_survey_translation(self):
        """Test survey translation endpoint"""
        # Create a simple survey for translation first
        try:
            survey_data = {
                "title": "Customer Feedback Survey",
                "description": "Please provide your feedback about our service",
                "questions": [
                    {
                        "type": "short_text",
                        "question": "What is your name?",
                        "required": True
                    },
                    {
                        "type": "rating_scale",
                        "question": "How satisfied are you with our service?",
                        "required": True,
                        "scale_min": 1,
                        "scale_max": 5
                    }
                ]
            }
            
            create_response = self.session.post(
                f"{self.base_url}/surveys",
                json=survey_data
            )
            
            if create_response.status_code == 200:
                survey_response_data = create_response.json()
                # Handle both 'id' and '_id' fields
                survey_id = survey_response_data.get("id") or survey_response_data.get("_id")
                if not survey_id:
                    self.log_result("Survey Translation", False, "No survey ID in response", survey_response_data)
                    return False
            else:
                self.log_result("Survey Translation", False, "Failed to create survey for translation test")
                return False
            
            # Now test translation
            response = self.session.post(
                f"{self.base_url}/surveys/{survey_id}/translate",
                params={"target_language": "kinyarwanda"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and 
                    "translated_survey" in data):
                    
                    translated_survey = data["translated_survey"]
                    if ("title" in translated_survey and 
                        "questions" in translated_survey):
                        self.log_result("Survey Translation", True, "Survey translated successfully to Kinyarwanda")
                        return True
                    else:
                        self.log_result("Survey Translation", False, "Incomplete translated survey structure", data)
                        return False
                else:
                    self.log_result("Survey Translation", False, "Missing required fields in response", data)
                    return False
            else:
                self.log_result("Survey Translation", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Survey Translation", False, f"Request error: {str(e)}")
            return False

    def run_ai_tests(self):
        """Run all AI-focused tests"""
        print(f"🤖 Starting DataRW AI Survey Generation Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Setup authentication first
        if not self.setup_authentication():
            print("❌ Authentication failed - cannot proceed with AI tests")
            return 0, 1
        
        # AI-focused test sequence
        ai_tests = [
            self.test_ai_survey_generation,
            self.test_document_upload_context,
            self.test_get_survey_context,
            self.test_ai_with_context_generation,
            self.test_survey_translation
        ]
        
        for test in ai_tests:
            test()
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 60)
        print("📊 AI TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        failed = len(self.test_results) - passed
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = AITestFocused()
    passed, failed = tester.run_ai_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()