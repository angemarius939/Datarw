#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for DataRW
Tests all backend endpoints including authentication, organization management,
survey management, user management, and analytics.
"""

import requests
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment - use localhost for testing
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
# For testing, always use localhost since we're testing from within the container
API_BASE_URL = "http://localhost:8001/api"

class DataRWAPITester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.test_results = []
        
        # Test data
        self.test_email = f"test.user.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Test User"
        
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
    
    def test_api_health(self):
        """Test API health endpoint"""
        try:
            # Test a simple API endpoint to verify API is working
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json={"test": "data"}  # Invalid data to trigger validation
            )
            
            # If we get a validation error, the API is working
            if response.status_code == 422:
                data = response.json()
                if "detail" in data and isinstance(data["detail"], list):
                    self.log_result("API Health Check", True, "API is responding with proper validation")
                    return True
            
            self.log_result("API Health Check", False, f"Unexpected response: {response.status_code}", response.text)
            return False
            
        except Exception as e:
            self.log_result("API Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration with valid data"""
        try:
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
                if "access_token" in data and "user" in data and "organization" in data:
                    self.auth_token = data["access_token"]
                    self.user_data = data["user"]
                    self.organization_data = data["organization"]
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    
                    self.log_result("User Registration", True, "User registered successfully")
                    return True
                else:
                    self.log_result("User Registration", False, "Missing required fields in response", data)
                    return False
            else:
                self.log_result("User Registration", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("User Registration", False, f"Request error: {str(e)}")
            return False
    
    def test_duplicate_registration(self):
        """Test user registration with duplicate email"""
        try:
            registration_data = {
                "email": self.test_email,  # Same email as before
                "password": "AnotherPassword123!",
                "name": "Another User"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=registration_data
            )
            
            if response.status_code == 400:
                data = response.json()
                if "Email already registered" in data.get("detail", ""):
                    self.log_result("Duplicate Registration", True, "Properly rejected duplicate email")
                    return True
                else:
                    self.log_result("Duplicate Registration", False, "Wrong error message", data)
                    return False
            else:
                self.log_result("Duplicate Registration", False, f"Expected 400, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Duplicate Registration", False, f"Request error: {str(e)}")
            return False
    
    def test_user_login_valid(self):
        """Test user login with valid credentials"""
        try:
            login_data = {
                "email": self.test_email,
                "password": self.test_password
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    # Update token in case it changed
                    self.auth_token = data["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    self.log_result("Valid Login", True, "Login successful")
                    return True
                else:
                    self.log_result("Valid Login", False, "Missing required fields in response", data)
                    return False
            else:
                self.log_result("Valid Login", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Valid Login", False, f"Request error: {str(e)}")
            return False
    
    def test_user_login_invalid(self):
        """Test user login with invalid credentials"""
        try:
            login_data = {
                "email": self.test_email,
                "password": "WrongPassword123!"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data
            )
            
            if response.status_code == 401:
                data = response.json()
                if "Incorrect email or password" in data.get("detail", ""):
                    self.log_result("Invalid Login", True, "Properly rejected invalid credentials")
                    return True
                else:
                    self.log_result("Invalid Login", False, "Wrong error message", data)
                    return False
            else:
                self.log_result("Invalid Login", False, f"Expected 401, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Invalid Login", False, f"Request error: {str(e)}")
            return False
    
    def test_get_organization(self):
        """Test getting organization details"""
        try:
            response = self.session.get(f"{self.base_url}/organizations/me")
            
            if response.status_code == 200:
                data = response.json()
                # Check for either 'id' or '_id' field
                org_id = data.get("id") or data.get("_id")
                if org_id and "name" in data and "plan" in data:
                    self.log_result("Get Organization", True, "Organization details retrieved successfully")
                    return True
                else:
                    self.log_result("Get Organization", False, "Missing required fields", data)
                    return False
            else:
                self.log_result("Get Organization", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Organization", False, f"Request error: {str(e)}")
            return False
    
    def test_update_organization(self):
        """Test updating organization information"""
        try:
            update_data = {
                "name": f"Updated Organization {uuid.uuid4().hex[:8]}"
            }
            
            response = self.session.put(
                f"{self.base_url}/organizations/me",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("name") == update_data["name"]:
                    self.log_result("Update Organization", True, "Organization updated successfully")
                    return True
                else:
                    self.log_result("Update Organization", False, "Organization name not updated", data)
                    return False
            else:
                self.log_result("Update Organization", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update Organization", False, f"Request error: {str(e)}")
            return False
    
    def test_create_survey(self):
        """Test creating a survey"""
        try:
            survey_data = {
                "title": f"Test Survey {uuid.uuid4().hex[:8]}",
                "description": "This is a test survey for API testing",
                "questions": [
                    {
                        "type": "short_text",
                        "question": "What is your name?",
                        "required": True
                    },
                    {
                        "type": "multiple_choice_single",
                        "question": "What is your favorite color?",
                        "required": False,
                        "options": ["Red", "Blue", "Green", "Yellow"]
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/surveys",
                json=survey_data
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle both 'id' and '_id' fields
                survey_id = data.get("id") or data.get("_id")
                if survey_id and data.get("title") == survey_data["title"]:
                    self.survey_id = survey_id
                    self.log_result("Create Survey", True, "Survey created successfully")
                    return True
                else:
                    self.log_result("Create Survey", False, "Survey data mismatch", data)
                    return False
            else:
                self.log_result("Create Survey", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Survey", False, f"Request error: {str(e)}")
            return False
    
    def test_get_surveys(self):
        """Test getting all surveys"""
        try:
            response = self.session.get(f"{self.base_url}/surveys")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Surveys", True, f"Retrieved {len(data)} surveys")
                    return True
                else:
                    self.log_result("Get Surveys", False, "Response is not a list", data)
                    return False
            else:
                self.log_result("Get Surveys", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Surveys", False, f"Request error: {str(e)}")
            return False
    
    def test_get_specific_survey(self):
        """Test getting a specific survey"""
        if not hasattr(self, 'survey_id'):
            self.log_result("Get Specific Survey", False, "No survey ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/surveys/{self.survey_id}")
            
            if response.status_code == 200:
                data = response.json()
                # Handle both 'id' and '_id' fields
                survey_id = data.get("id") or data.get("_id")
                if survey_id == self.survey_id:
                    self.log_result("Get Specific Survey", True, "Survey retrieved successfully")
                    return True
                else:
                    self.log_result("Get Specific Survey", False, "Survey ID mismatch", data)
                    return False
            else:
                self.log_result("Get Specific Survey", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Specific Survey", False, f"Request error: {str(e)}")
            return False
    
    def test_update_survey(self):
        """Test updating a survey"""
        if not hasattr(self, 'survey_id'):
            self.log_result("Update Survey", False, "No survey ID available from previous test")
            return False
        
        try:
            update_data = {
                "title": f"Updated Survey {uuid.uuid4().hex[:8]}",
                "status": "active"
            }
            
            response = self.session.put(
                f"{self.base_url}/surveys/{self.survey_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("title") == update_data["title"]:
                    self.log_result("Update Survey", True, "Survey updated successfully")
                    return True
                else:
                    self.log_result("Update Survey", False, "Survey title not updated", data)
                    return False
            else:
                self.log_result("Update Survey", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update Survey", False, f"Request error: {str(e)}")
            return False
    
    def test_get_organization_users(self):
        """Test getting organization users"""
        try:
            response = self.session.get(f"{self.base_url}/users")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_result("Get Organization Users", True, f"Retrieved {len(data)} users")
                    return True
                else:
                    self.log_result("Get Organization Users", False, "No users found or invalid response", data)
                    return False
            else:
                self.log_result("Get Organization Users", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Organization Users", False, f"Request error: {str(e)}")
            return False
    
    def test_create_user(self):
        """Test creating a new user in organization"""
        try:
            user_data = {
                "email": f"new.user.{uuid.uuid4().hex[:8]}@datarw.com",
                "password": "NewUserPassword123!",
                "name": "New Test User",
                "role": "Viewer"
            }
            
            response = self.session.post(
                f"{self.base_url}/users",
                json=user_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("email") == user_data["email"]:
                    # Handle both 'id' and '_id' fields
                    user_id = data.get("id") or data.get("_id")
                    self.new_user_id = user_id
                    self.log_result("Create User", True, "User created successfully")
                    return True
                else:
                    self.log_result("Create User", False, "User data mismatch", data)
                    return False
            else:
                self.log_result("Create User", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create User", False, f"Request error: {str(e)}")
            return False
    
    def test_update_user_role(self):
        """Test updating user role"""
        if not hasattr(self, 'new_user_id'):
            self.log_result("Update User Role", False, "No user ID available from previous test")
            return False
        
        try:
            update_data = {
                "role": "Editor"
            }
            
            response = self.session.put(
                f"{self.base_url}/users/{self.new_user_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("role") == update_data["role"]:
                    self.log_result("Update User Role", True, "User role updated successfully")
                    return True
                else:
                    self.log_result("Update User Role", False, "User role not updated", data)
                    return False
            else:
                self.log_result("Update User Role", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update User Role", False, f"Request error: {str(e)}")
            return False
    
    def test_get_analytics(self):
        """Test getting analytics data"""
        try:
            response = self.session.get(f"{self.base_url}/analytics")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_responses", "response_rate", "average_completion_time", 
                                 "top_performing_survey", "monthly_growth", "storage_growth"]
                
                if all(field in data for field in required_fields):
                    self.log_result("Get Analytics", True, "Analytics data retrieved successfully")
                    return True
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("Get Analytics", False, f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("Get Analytics", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Analytics", False, f"Request error: {str(e)}")
            return False
    
    def test_survey_limit_enforcement(self):
        """Test survey limit enforcement for Basic plan"""
        try:
            # Create surveys up to the limit (Basic plan has 4 survey limit)
            surveys_created = 0
            for i in range(5):  # Try to create 5 surveys (should fail on 5th)
                survey_data = {
                    "title": f"Limit Test Survey {i+1}",
                    "description": f"Survey {i+1} for testing limits"
                }
                
                response = self.session.post(
                    f"{self.base_url}/surveys",
                    json=survey_data
                )
                
                if response.status_code == 200:
                    surveys_created += 1
                elif response.status_code == 400:
                    data = response.json()
                    if "Survey limit reached" in data.get("detail", ""):
                        self.log_result("Survey Limit Enforcement", True, 
                                      f"Survey limit properly enforced after {surveys_created} surveys")
                        return True
                    else:
                        self.log_result("Survey Limit Enforcement", False, 
                                      "Wrong error message for limit", data)
                        return False
                else:
                    self.log_result("Survey Limit Enforcement", False, 
                                  f"Unexpected response: {response.status_code}", response.text)
                    return False
            
            # If we get here, limit wasn't enforced
            self.log_result("Survey Limit Enforcement", False, 
                          f"Created {surveys_created} surveys without limit enforcement")
            return False
            
        except Exception as e:
            self.log_result("Survey Limit Enforcement", False, f"Request error: {str(e)}")
            return False
    
    def test_delete_user(self):
        """Test deleting a user"""
        if not hasattr(self, 'new_user_id'):
            self.log_result("Delete User", False, "No user ID available from previous test")
            return False
        
        try:
            response = self.session.delete(f"{self.base_url}/users/{self.new_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "deleted successfully" in data.get("message", ""):
                    self.log_result("Delete User", True, "User deleted successfully")
                    return True
                else:
                    self.log_result("Delete User", False, "Unexpected response message", data)
                    return False
            else:
                self.log_result("Delete User", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Delete User", False, f"Request error: {str(e)}")
            return False
    
    def test_delete_survey(self):
        """Test deleting a survey"""
        if not hasattr(self, 'survey_id'):
            self.log_result("Delete Survey", False, "No survey ID available from previous test")
            return False
        
        try:
            response = self.session.delete(f"{self.base_url}/surveys/{self.survey_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "deleted successfully" in data.get("message", ""):
                    self.log_result("Delete Survey", True, "Survey deleted successfully")
                    return True
                else:
                    self.log_result("Delete Survey", False, "Unexpected response message", data)
                    return False
            else:
                self.log_result("Delete Survey", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Delete Survey", False, f"Request error: {str(e)}")
            return False

    # AI Survey Generation Tests
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
            import io
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

    def test_survey_translation(self):
        """Test survey translation endpoint"""
        # First create a survey to translate
        if not hasattr(self, 'survey_id'):
            # Create a simple survey for translation
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
                self.survey_id = create_response.json()["id"]
            else:
                self.log_result("Survey Translation", False, "Failed to create survey for translation test")
                return False
        
        try:
            response = self.session.post(
                f"{self.base_url}/surveys/{self.survey_id}/translate",
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

    def test_enhanced_question_types(self):
        """Test creating survey with enhanced question types"""
        try:
            survey_data = {
                "title": "Enhanced Question Types Test Survey",
                "description": "Testing all enhanced question types supported by the system",
                "questions": [
                    {
                        "type": "multiple_choice_single",
                        "question": "What is your preferred communication method?",
                        "required": True,
                        "options": ["Email", "Phone", "Text", "In-person"]
                    },
                    {
                        "type": "likert_scale",
                        "question": "I am satisfied with the current service quality",
                        "required": True,
                        "scale_labels": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
                    },
                    {
                        "type": "matrix_grid",
                        "question": "Rate the following aspects of our service",
                        "required": True,
                        "matrix_rows": ["Quality", "Speed", "Friendliness", "Value"],
                        "matrix_columns": ["Poor", "Fair", "Good", "Excellent"]
                    },
                    {
                        "type": "slider",
                        "question": "On a scale of 0-100, how likely are you to recommend us?",
                        "required": False,
                        "scale_min": 0,
                        "scale_max": 100,
                        "slider_step": 5
                    },
                    {
                        "type": "date_picker",
                        "question": "When did you first use our service?",
                        "required": False,
                        "date_format": "YYYY-MM-DD"
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/surveys",
                json=survey_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("title") == survey_data["title"]:
                    questions = data.get("questions", [])
                    if len(questions) == 5:  # All question types created
                        self.enhanced_survey_id = data["id"]
                        self.log_result("Enhanced Question Types", True, 
                                      "Survey with enhanced question types created successfully")
                        return True
                    else:
                        self.log_result("Enhanced Question Types", False, 
                                      f"Expected 5 questions, got {len(questions)}", data)
                        return False
                else:
                    self.log_result("Enhanced Question Types", False, "Survey data mismatch", data)
                    return False
            else:
                self.log_result("Enhanced Question Types", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Enhanced Question Types", False, f"Request error: {str(e)}")
            return False

    # Project Management Tests
    def test_project_dashboard(self):
        """Test project dashboard endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/projects/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    dashboard_data = data["data"]
                    required_fields = ["total_projects", "active_projects", "completed_projects", 
                                     "overdue_activities", "budget_utilization", "kpi_performance", "recent_activities"]
                    
                    if all(field in dashboard_data for field in required_fields):
                        self.log_result("Project Dashboard", True, "Dashboard data retrieved successfully")
                        return True
                    else:
                        missing_fields = [field for field in required_fields if field not in dashboard_data]
                        self.log_result("Project Dashboard", False, f"Missing fields: {missing_fields}", data)
                        return False
                else:
                    self.log_result("Project Dashboard", False, "Missing required fields in response", data)
                    return False
            else:
                self.log_result("Project Dashboard", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Project Dashboard", False, f"Request error: {str(e)}")
            return False

    def test_dashboard_pydantic_validation_fix(self):
        """Test dashboard endpoint for Pydantic validation error fix - specifically projects_by_status and budget_by_category string keys"""
        try:
            response = self.session.get(f"{self.base_url}/projects/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    dashboard_data = data["data"]
                    
                    # Check for projects_by_status field
                    if "projects_by_status" in dashboard_data:
                        projects_by_status = dashboard_data["projects_by_status"]
                        if isinstance(projects_by_status, dict):
                            # Verify all keys are strings (not None)
                            for key in projects_by_status.keys():
                                if not isinstance(key, str):
                                    self.log_result("Dashboard Pydantic Fix", False, 
                                                  f"projects_by_status contains non-string key: {key} (type: {type(key)})", data)
                                    return False
                            
                            # Check if None values were converted to 'unknown' strings
                            if None in projects_by_status:
                                self.log_result("Dashboard Pydantic Fix", False, 
                                              "projects_by_status still contains None key", data)
                                return False
                        else:
                            self.log_result("Dashboard Pydantic Fix", False, 
                                          f"projects_by_status is not a dict: {type(projects_by_status)}", data)
                            return False
                    else:
                        self.log_result("Dashboard Pydantic Fix", False, "projects_by_status field missing", data)
                        return False
                    
                    # Check for budget_by_category field
                    if "budget_by_category" in dashboard_data:
                        budget_by_category = dashboard_data["budget_by_category"]
                        if isinstance(budget_by_category, dict):
                            # Verify all keys are strings (not None)
                            for key in budget_by_category.keys():
                                if not isinstance(key, str):
                                    self.log_result("Dashboard Pydantic Fix", False, 
                                                  f"budget_by_category contains non-string key: {key} (type: {type(key)})", data)
                                    return False
                            
                            # Check if None values were converted to 'unknown' strings
                            if None in budget_by_category:
                                self.log_result("Dashboard Pydantic Fix", False, 
                                              "budget_by_category still contains None key", data)
                                return False
                        else:
                            self.log_result("Dashboard Pydantic Fix", False, 
                                          f"budget_by_category is not a dict: {type(budget_by_category)}", data)
                            return False
                    else:
                        self.log_result("Dashboard Pydantic Fix", False, "budget_by_category field missing", data)
                        return False
                    
                    # Verify response matches ProjectDashboardData model structure
                    required_dashboard_fields = ["total_projects", "active_projects", "completed_projects", 
                                               "overdue_activities", "budget_utilization", "kpi_performance", 
                                               "recent_activities", "projects_by_status", "budget_by_category"]
                    
                    missing_fields = [field for field in required_dashboard_fields if field not in dashboard_data]
                    if missing_fields:
                        self.log_result("Dashboard Pydantic Fix", False, 
                                      f"Missing ProjectDashboardData fields: {missing_fields}", data)
                        return False
                    
                    self.log_result("Dashboard Pydantic Fix", True, 
                                  "Dashboard endpoint returns valid ProjectDashboardData with string keys - Pydantic validation fix verified")
                    return True
                else:
                    self.log_result("Dashboard Pydantic Fix", False, "Missing success/data fields in response", data)
                    return False
            else:
                # Check if this is the specific Pydantic validation error we're testing for
                if response.status_code == 500:
                    error_text = response.text
                    if "projects_by_status.None.[key] Input should be a valid string" in error_text:
                        self.log_result("Dashboard Pydantic Fix", False, 
                                      "CRITICAL: Original Pydantic validation error still present - fix not working", error_text)
                        return False
                    elif "budget_by_category.None.[key] Input should be a valid string" in error_text:
                        self.log_result("Dashboard Pydantic Fix", False, 
                                      "CRITICAL: Budget category Pydantic validation error present", error_text)
                        return False
                
                self.log_result("Dashboard Pydantic Fix", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Dashboard Pydantic Fix", False, f"Request error: {str(e)}")
            return False

    def test_create_project(self):
        """Test creating a new project with CORRECTED field mapping"""
        try:
            from datetime import datetime, timedelta
            
            # CORRECTED field mapping based on ProjectCreate model
            project_data = {
                "name": f"Digital Literacy Training Program {uuid.uuid4().hex[:8]}",  # CORRECTED: name not title
                "description": "Comprehensive digital literacy training program for rural communities in Rwanda, focusing on basic computer skills, internet usage, and digital communication tools",
                "project_manager_id": self.user_data["id"],  # REQUIRED field
                "start_date": (datetime.now() + timedelta(days=30)).isoformat(),  # CORRECTED: start_date not implementation_start
                "end_date": (datetime.now() + timedelta(days=365)).isoformat(),  # CORRECTED: end_date not implementation_end
                "budget_total": 2500000.0,  # CORRECTED: budget_total not total_budget (realistic RWF amount)
                "beneficiaries_target": 5000,  # CORRECTED: beneficiaries_target not target_beneficiaries
                "location": "Nyagatare District, Eastern Province, Rwanda",
                "donor_organization": "World Bank",  # CORRECTED: donor_organization not donor
                "implementing_partners": ["Rwanda Development Board", "Local NGO Partners"],
                "tags": ["education", "digital-literacy", "rural-development"]
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle both 'id' and '_id' fields
                project_id = data.get("id") or data.get("_id")
                if project_id and data.get("name") == project_data["name"]:  # Check 'name' field
                    self.project_id = project_id
                    self.log_result("Create Project", True, "Project created successfully with corrected field mapping")
                    return True
                else:
                    self.log_result("Create Project", False, "Project data mismatch", data)
                    return False
            else:
                self.log_result("Create Project", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Project", False, f"Request error: {str(e)}")
            return False

    def test_get_projects(self):
        """Test getting all projects"""
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Projects", True, f"Retrieved {len(data)} projects")
                    return True
                else:
                    self.log_result("Get Projects", False, "Response is not a list", data)
                    return False
            else:
                self.log_result("Get Projects", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Projects", False, f"Request error: {str(e)}")
            return False

    def test_get_specific_project(self):
        """Test getting a specific project"""
        if not hasattr(self, 'project_id'):
            self.log_result("Get Specific Project", False, "No project ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{self.project_id}")
            
            if response.status_code == 200:
                data = response.json()
                # Handle both 'id' and '_id' fields
                project_id = data.get("id") or data.get("_id")
                if project_id == self.project_id:
                    self.log_result("Get Specific Project", True, "Project retrieved successfully")
                    return True
                else:
                    self.log_result("Get Specific Project", False, "Project ID mismatch", data)
                    return False
            else:
                self.log_result("Get Specific Project", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Specific Project", False, f"Request error: {str(e)}")
            return False

    def test_update_project(self):
        """Test updating a project"""
        if not hasattr(self, 'project_id'):
            self.log_result("Update Project", False, "No project ID available from previous test")
            return False
        
        try:
            update_data = {
                "title": f"Updated Project {uuid.uuid4().hex[:8]}",
                "status": "active"
            }
            
            response = self.session.put(
                f"{self.base_url}/projects/{self.project_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("title") == update_data["title"]:
                    self.log_result("Update Project", True, "Project updated successfully")
                    return True
                else:
                    self.log_result("Update Project", False, "Project title not updated", data)
                    return False
            else:
                self.log_result("Update Project", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update Project", False, f"Request error: {str(e)}")
            return False

    def test_create_activity_corrected_fields(self):
        """Test creating a project activity with CORRECTED field mapping (name not title, assigned_to not responsible_user_id)"""
        if not hasattr(self, 'project_id'):
            self.log_result("Create Activity - Corrected Fields", False, "No project ID available from previous test")
            return False
        
        try:
            from datetime import datetime, timedelta
            
            # CORRECTED field mapping based on ActivityCreate model
            activity_data = {
                "project_id": self.project_id,
                "name": f"Community Mobilization and Awareness Campaign {uuid.uuid4().hex[:8]}",  # CORRECTED: name not title
                "description": "Comprehensive community outreach program to raise awareness about digital literacy opportunities and mobilize participation from target beneficiaries in rural communities",
                "assigned_to": self.user_data["id"],  # CORRECTED: assigned_to not responsible_user_id
                "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "budget_allocated": 150000.0,  # Realistic budget in RWF
                "deliverables": [
                    "Community awareness sessions conducted in 5 villages",
                    "Registration of 200+ participants completed",
                    "Training materials distributed to all participants",
                    "Community feedback collected and analyzed"
                ],
                "dependencies": [
                    "Project approval and funding confirmation",
                    "Training materials preparation completed"
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/activities",
                json=activity_data
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle both 'id' and '_id' fields
                activity_id = data.get("id") or data.get("_id")
                if activity_id and data.get("name") == activity_data["name"]:  # Check 'name' field
                    self.activity_id = activity_id
                    self.log_result("Create Activity - Corrected Fields", True, 
                                  "Activity created successfully with corrected field mapping (name, assigned_to)")
                    return True
                else:
                    self.log_result("Create Activity - Corrected Fields", False, "Activity data mismatch", data)
                    return False
            else:
                self.log_result("Create Activity - Corrected Fields", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Activity - Corrected Fields", False, f"Request error: {str(e)}")
            return False

    def test_create_activity_validation_errors(self):
        """Test activity creation with invalid data to verify proper JSON error responses"""
        if not hasattr(self, 'project_id'):
            self.log_result("Create Activity - Validation Errors", False, "No project ID available from previous test")
            return False
        
        try:
            from datetime import datetime, timedelta
            
            # Test 1: Missing required fields
            invalid_data_1 = {
                "project_id": self.project_id,
                # Missing required 'name' field
                "description": "Test activity without name",
                "assigned_to": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "budget_allocated": 5000.0
            }
            
            response = self.session.post(
                f"{self.base_url}/activities",
                json=invalid_data_1
            )
            
            if response.status_code == 422:  # Validation error
                data = response.json()
                # Verify it returns proper JSON (not objects that cause React errors)
                if isinstance(data, dict) and "detail" in data:
                    self.log_result("Create Activity - Validation Errors", True, 
                                  "Missing required field properly rejected with JSON response")
                else:
                    self.log_result("Create Activity - Validation Errors", False, 
                                  "Validation error response is not proper JSON", data)
                    return False
            else:
                self.log_result("Create Activity - Validation Errors", False, 
                              f"Expected 422 for missing field, got {response.status_code}", response.text)
                return False
            
            # Test 2: Invalid field types
            invalid_data_2 = {
                "project_id": self.project_id,
                "name": "Test Activity",
                "assigned_to": self.user_data["id"],
                "start_date": "invalid-date-format",  # Invalid date
                "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "budget_allocated": -1000.0  # Negative budget (should be >= 0)
            }
            
            response = self.session.post(
                f"{self.base_url}/activities",
                json=invalid_data_2
            )
            
            if response.status_code == 422:  # Validation error
                data = response.json()
                # Verify it returns proper JSON (not objects that cause React errors)
                if isinstance(data, dict) and "detail" in data:
                    self.log_result("Create Activity - Validation Errors", True, 
                                  "Invalid data types properly rejected with JSON response")
                    return True
                else:
                    self.log_result("Create Activity - Validation Errors", False, 
                                  "Validation error response is not proper JSON", data)
                    return False
            else:
                self.log_result("Create Activity - Validation Errors", False, 
                              f"Expected 422 for invalid data, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Create Activity - Validation Errors", False, f"Request error: {str(e)}")
            return False

    def test_create_activity_old_field_names(self):
        """Test activity creation with OLD field names to verify they are properly rejected"""
        if not hasattr(self, 'project_id'):
            self.log_result("Create Activity - Old Field Names", False, "No project ID available from previous test")
            return False
        
        try:
            from datetime import datetime, timedelta
            
            # Use OLD field names that should be rejected
            old_field_data = {
                "project_id": self.project_id,
                "title": "Test Activity with Old Field Names",  # OLD: should be 'name'
                "description": "Testing with old field mapping",
                "responsible_user_id": self.user_data["id"],  # OLD: should be 'assigned_to'
                "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "budget_allocated": 5000.0,
                "deliverables": ["Test deliverable"]
            }
            
            response = self.session.post(
                f"{self.base_url}/activities",
                json=old_field_data
            )
            
            if response.status_code == 422:  # Should be validation error
                data = response.json()
                # Verify it returns proper JSON validation errors
                if isinstance(data, dict) and "detail" in data:
                    # Check if the error mentions the missing required fields
                    error_details = str(data.get("detail", ""))
                    if "name" in error_details.lower() or "assigned_to" in error_details.lower():
                        self.log_result("Create Activity - Old Field Names", True, 
                                      "Old field names properly rejected with validation errors for missing required fields")
                        return True
                    else:
                        self.log_result("Create Activity - Old Field Names", False, 
                                      "Validation error doesn't mention missing required fields", data)
                        return False
                else:
                    self.log_result("Create Activity - Old Field Names", False, 
                                  "Validation error response is not proper JSON", data)
                    return False
            elif response.status_code == 200:
                # If it succeeds, that means the backend is still accepting old field names (problem)
                self.log_result("Create Activity - Old Field Names", False, 
                              "CRITICAL: Backend still accepts old field names - field mapping fix not working")
                return False
            else:
                self.log_result("Create Activity - Old Field Names", False, 
                              f"Unexpected response code {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Create Activity - Old Field Names", False, f"Request error: {str(e)}")
            return False

    def test_get_activities(self):
        """Test getting activities"""
        try:
            response = self.session.get(f"{self.base_url}/activities")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Activities", True, f"Retrieved {len(data)} activities")
                    return True
                else:
                    self.log_result("Get Activities", False, "Response is not a list", data)
                    return False
            else:
                self.log_result("Get Activities", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Activities", False, f"Request error: {str(e)}")
            return False

    def test_update_activity(self):
        """Test updating an activity"""
        if not hasattr(self, 'activity_id'):
            self.log_result("Update Activity", False, "No activity ID available from previous test")
            return False
        
        try:
            update_data = {
                "status": "in_progress",
                "progress_percentage": 25.0
            }
            
            response = self.session.put(
                f"{self.base_url}/activities/{self.activity_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == update_data["status"]:
                    self.log_result("Update Activity", True, "Activity updated successfully")
                    return True
                else:
                    self.log_result("Update Activity", False, "Activity status not updated", data)
                    return False
            else:
                self.log_result("Update Activity", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update Activity", False, f"Request error: {str(e)}")
            return False

    def test_create_budget_item(self):
        """Test creating a budget item"""
        if not hasattr(self, 'project_id'):
            self.log_result("Create Budget Item", False, "No project ID available from previous test")
            return False
        
        try:
            budget_data = {
                "project_id": self.project_id,
                "category": "supplies",  # Use valid FinancialCategory enum value
                "item_name": "Training Materials and Workshop Supplies",  # Required field
                "description": "Educational materials, handouts, and workshop supplies for digital literacy training",
                "budgeted_amount": 800000.0,  # Realistic amount in RWF
                "budget_period": "Q1 2024"  # Required field
            }
            
            response = self.session.post(
                f"{self.base_url}/budget",
                json=budget_data
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle both 'id' and '_id' fields
                budget_id = data.get("id") or data.get("_id")
                if budget_id and data.get("category") == budget_data["category"]:
                    self.budget_item_id = budget_id
                    self.log_result("Create Budget Item", True, "Budget item created successfully")
                    return True
                else:
                    self.log_result("Create Budget Item", False, "Budget item data mismatch", data)
                    return False
            else:
                self.log_result("Create Budget Item", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Budget Item", False, f"Request error: {str(e)}")
            return False

    def test_get_budget_items(self):
        """Test getting budget items"""
        try:
            response = self.session.get(f"{self.base_url}/budget")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Budget Items", True, f"Retrieved {len(data)} budget items")
                    return True
                else:
                    self.log_result("Get Budget Items", False, "Response is not a list", data)
                    return False
            else:
                self.log_result("Get Budget Items", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Budget Items", False, f"Request error: {str(e)}")
            return False

    def test_get_budget_summary(self):
        """Test getting budget summary"""
        try:
            response = self.session.get(f"{self.base_url}/budget/summary")
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    summary_data = data["data"]
                    required_fields = ["total_budget", "total_spent", "remaining_budget", "utilization_rate"]
                    
                    if all(field in summary_data for field in required_fields):
                        self.log_result("Get Budget Summary", True, "Budget summary retrieved successfully")
                        return True
                    else:
                        missing_fields = [field for field in required_fields if field not in summary_data]
                        self.log_result("Get Budget Summary", False, f"Missing fields: {missing_fields}", data)
                        return False
                else:
                    self.log_result("Get Budget Summary", False, "Missing required fields in response", data)
                    return False
            else:
                self.log_result("Get Budget Summary", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Budget Summary", False, f"Request error: {str(e)}")
            return False

    def test_create_kpi_indicator(self):
        """Test creating a KPI indicator"""
        if not hasattr(self, 'project_id'):
            self.log_result("Create KPI Indicator", False, "No project ID available from previous test")
            return False
        
        try:
            kpi_data = {
                "project_id": self.project_id,
                "name": f"Test KPI {uuid.uuid4().hex[:8]}",
                "description": "Number of people trained in digital literacy",
                "indicator_type": "quantitative",
                "level": "output",
                "baseline_value": 0.0,
                "target_value": 500.0,
                "unit_of_measurement": "people",
                "frequency": "Monthly",
                "responsible_user_id": self.user_data["id"],
                "data_source": "Training records",
                "collection_method": "Manual count"
            }
            
            response = self.session.post(
                f"{self.base_url}/kpis",
                json=kpi_data
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle both 'id' and '_id' fields
                kpi_id = data.get("id") or data.get("_id")
                if kpi_id and data.get("name") == kpi_data["name"]:
                    self.kpi_id = kpi_id
                    self.log_result("Create KPI Indicator", True, "KPI indicator created successfully")
                    return True
                else:
                    self.log_result("Create KPI Indicator", False, "KPI data mismatch", data)
                    return False
            else:
                self.log_result("Create KPI Indicator", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create KPI Indicator", False, f"Request error: {str(e)}")
            return False

    def test_get_kpi_indicators(self):
        """Test getting KPI indicators"""
        try:
            response = self.session.get(f"{self.base_url}/kpis")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get KPI Indicators", True, f"Retrieved {len(data)} KPI indicators")
                    return True
                else:
                    self.log_result("Get KPI Indicators", False, "Response is not a list", data)
                    return False
            else:
                self.log_result("Get KPI Indicators", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get KPI Indicators", False, f"Request error: {str(e)}")
            return False

    def test_update_kpi_value(self):
        """Test updating KPI current value"""
        if not hasattr(self, 'kpi_id'):
            self.log_result("Update KPI Value", False, "No KPI ID available from previous test")
            return False
        
        try:
            current_value = 125.0
            
            response = self.session.put(
                f"{self.base_url}/kpis/{self.kpi_id}/value",
                params={"current_value": current_value}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("current_value") == current_value:
                    self.log_result("Update KPI Value", True, "KPI value updated successfully")
                    return True
                else:
                    self.log_result("Update KPI Value", False, "KPI value not updated", data)
                    return False
            else:
                self.log_result("Update KPI Value", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update KPI Value", False, f"Request error: {str(e)}")
            return False

    def test_create_beneficiary(self):
        """Test creating a beneficiary"""
        try:
            from datetime import datetime, timedelta
            
            beneficiary_data = {
                "unique_id": f"BEN-{uuid.uuid4().hex[:8].upper()}",
                "first_name": "Jean",
                "last_name": "Uwimana",
                "date_of_birth": (datetime.now() - timedelta(days=365*25)).isoformat(),
                "gender": "Male",
                "location": "Kigali",
                "contact_phone": "+250788123456",
                "household_size": 4,
                "education_level": "Secondary",
                "employment_status": "Employed"
            }
            
            response = self.session.post(
                f"{self.base_url}/beneficiaries",
                json=beneficiary_data
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle both 'id' and '_id' fields
                beneficiary_id = data.get("id") or data.get("_id")
                if beneficiary_id and data.get("unique_id") == beneficiary_data["unique_id"]:
                    self.beneficiary_id = beneficiary_id
                    self.log_result("Create Beneficiary", True, "Beneficiary created successfully")
                    return True
                else:
                    self.log_result("Create Beneficiary", False, "Beneficiary data mismatch", data)
                    return False
            else:
                self.log_result("Create Beneficiary", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Beneficiary", False, f"Request error: {str(e)}")
            return False

    def test_get_beneficiaries(self):
        """Test getting beneficiaries"""
        try:
            response = self.session.get(f"{self.base_url}/beneficiaries")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Beneficiaries", True, f"Retrieved {len(data)} beneficiaries")
                    return True
                else:
                    self.log_result("Get Beneficiaries", False, "Response is not a list", data)
                    return False
            else:
                self.log_result("Get Beneficiaries", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Beneficiaries", False, f"Request error: {str(e)}")
            return False

    def test_get_beneficiary_demographics(self):
        """Test getting beneficiary demographics"""
        try:
            response = self.session.get(f"{self.base_url}/beneficiaries/demographics")
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    demographics_data = data["data"]
                    required_fields = ["gender_distribution", "age_distribution", "location_distribution"]
                    
                    if all(field in demographics_data for field in required_fields):
                        self.log_result("Get Beneficiary Demographics", True, "Demographics data retrieved successfully")
                        return True
                    else:
                        missing_fields = [field for field in required_fields if field not in demographics_data]
                        self.log_result("Get Beneficiary Demographics", False, f"Missing fields: {missing_fields}", data)
                        return False
                else:
                    self.log_result("Get Beneficiary Demographics", False, "Missing required fields in response", data)
                    return False
            else:
                self.log_result("Get Beneficiary Demographics", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Beneficiary Demographics", False, f"Request error: {str(e)}")
            return False

    def test_delete_project(self):
        """Test deleting a project (admin only)"""
        if not hasattr(self, 'project_id'):
            self.log_result("Delete Project", False, "No project ID available from previous test")
            return False
        
        try:
            response = self.session.delete(f"{self.base_url}/projects/{self.project_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "deleted successfully" in data.get("message", ""):
                    self.log_result("Delete Project", True, "Project deleted successfully")
                    return True
                else:
                    self.log_result("Delete Project", False, "Unexpected response message", data)
                    return False
            else:
                self.log_result("Delete Project", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Delete Project", False, f"Request error: {str(e)}")
            return False

    # Admin Panel Tests
    def test_admin_create_user_advanced(self):
        """Test advanced user creation with different roles and permissions"""
        try:
            # Test creating a Director user
            user_data = {
                "name": "Dr. Marie Uwimana",
                "email": f"marie.uwimana.{uuid.uuid4().hex[:8]}@datarw.com",
                "role": "Director",
                "department": "Operations",
                "position": "Regional Director",
                "access_level": "elevated",
                "permissions": {
                    "view_dashboard": True,
                    "create_projects": True,
                    "manage_partners": True,
                    "view_financial_data": True
                },
                "send_credentials_email": False,
                "temporary_password": True
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/users/create-advanced",
                json=user_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    user_result = data["data"]
                    if ("user" in user_result and 
                        "username" in user_result and 
                        "password" in user_result):
                        
                        created_user = user_result["user"]
                        if (created_user.get("name") == user_data["name"] and
                            created_user.get("role") == user_data["role"]):
                            self.admin_user_id = created_user.get("id") or created_user.get("_id")
                            self.log_result("Admin Create User Advanced", True, 
                                          f"Director user created successfully with username: {user_result['username']}")
                            return True
                        else:
                            self.log_result("Admin Create User Advanced", False, "User data mismatch", data)
                            return False
                    else:
                        self.log_result("Admin Create User Advanced", False, "Missing required fields in response", data)
                        return False
                else:
                    self.log_result("Admin Create User Advanced", False, "Missing success or data fields", data)
                    return False
            else:
                self.log_result("Admin Create User Advanced", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Create User Advanced", False, f"Request error: {str(e)}")
            return False

    def test_admin_bulk_create_users(self):
        """Test bulk user creation with different roles"""
        try:
            users_data = [
                {
                    "name": "Jean Baptiste Nzeyimana",
                    "email": f"jean.nzeyimana.{uuid.uuid4().hex[:8]}@datarw.com",
                    "role": "Officer",
                    "department": "Field Operations",
                    "position": "Field Officer",
                    "access_level": "standard",
                    "send_credentials_email": False,
                    "temporary_password": True
                },
                {
                    "name": "Grace Mukamana",
                    "email": f"grace.mukamana.{uuid.uuid4().hex[:8]}@datarw.com",
                    "role": "Field Staff",
                    "department": "Community Outreach",
                    "position": "Community Mobilizer",
                    "access_level": "standard",
                    "send_credentials_email": False,
                    "temporary_password": True
                },
                {
                    "name": "Emmanuel Habimana",
                    "email": f"emmanuel.habimana.{uuid.uuid4().hex[:8]}@datarw.com",
                    "role": "Partner Staff",
                    "department": "External Relations",
                    "position": "Partner Coordinator",
                    "access_level": "restricted",
                    "send_credentials_email": False,
                    "temporary_password": True
                }
            ]
            
            response = self.session.post(
                f"{self.base_url}/admin/users/bulk-create",
                json=users_data,
                params={"send_emails": False}
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    result = data["data"]
                    if (result.get("created_count") == 3 and 
                        result.get("failed_count") == 0 and
                        len(result.get("created_users", [])) == 3):
                        
                        self.log_result("Admin Bulk Create Users", True, 
                                      f"Successfully created {result['created_count']} users in bulk")
                        return True
                    else:
                        self.log_result("Admin Bulk Create Users", False, 
                                      f"Expected 3 users created, got {result.get('created_count', 0)}", data)
                        return False
                else:
                    self.log_result("Admin Bulk Create Users", False, "Missing success or data fields", data)
                    return False
            else:
                self.log_result("Admin Bulk Create Users", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Bulk Create Users", False, f"Request error: {str(e)}")
            return False

    def test_admin_create_partner_organization(self):
        """Test creating a partner organization"""
        try:
            from datetime import datetime, timedelta
            
            partner_data = {
                "name": "Rwanda Youth Development Foundation",
                "description": "A local NGO focused on youth empowerment and skills development programs",
                "contact_person": "Alice Uwimana",
                "contact_email": f"alice.uwimana.{uuid.uuid4().hex[:8]}@rydf.org.rw",
                "contact_phone": "+250788456789",
                "address": "KG 15 Ave, Kigali, Rwanda",
                "organization_type": "NGO",
                "partnership_start_date": datetime.now().isoformat(),
                "partnership_end_date": (datetime.now() + timedelta(days=1095)).isoformat(),  # 3 years
                "website": "https://www.rydf.org.rw",
                "capabilities": [
                    "Youth Training Programs",
                    "Community Mobilization",
                    "Digital Literacy Training",
                    "Entrepreneurship Support"
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/partners",
                json=partner_data
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle both 'id' and '_id' fields
                partner_id = data.get("id") or data.get("_id")
                if (partner_id and 
                    data.get("name") == partner_data["name"] and
                    data.get("organization_type") == partner_data["organization_type"]):
                    
                    self.partner_id = partner_id
                    self.log_result("Admin Create Partner Organization", True, 
                                  f"Partner organization '{partner_data['name']}' created successfully")
                    return True
                else:
                    self.log_result("Admin Create Partner Organization", False, "Partner data mismatch", data)
                    return False
            else:
                self.log_result("Admin Create Partner Organization", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Create Partner Organization", False, f"Request error: {str(e)}")
            return False

    def test_admin_get_partner_organizations(self):
        """Test getting all partner organizations"""
        try:
            response = self.session.get(f"{self.base_url}/admin/partners")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Admin Get Partner Organizations", True, 
                                  f"Retrieved {len(data)} partner organizations")
                    return True
                else:
                    self.log_result("Admin Get Partner Organizations", False, "Response is not a list", data)
                    return False
            else:
                self.log_result("Admin Get Partner Organizations", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Get Partner Organizations", False, f"Request error: {str(e)}")
            return False

    def test_admin_update_partner_organization(self):
        """Test updating a partner organization"""
        if not hasattr(self, 'partner_id'):
            self.log_result("Admin Update Partner Organization", False, "No partner ID available from previous test")
            return False
        
        try:
            update_data = {
                "status": "active",
                "performance_rating": 4.5,
                "capabilities": [
                    "Youth Training Programs",
                    "Community Mobilization", 
                    "Digital Literacy Training",
                    "Entrepreneurship Support",
                    "Women Empowerment Programs"  # Added new capability
                ]
            }
            
            response = self.session.put(
                f"{self.base_url}/admin/partners/{self.partner_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("status") == update_data["status"] and
                    data.get("performance_rating") == update_data["performance_rating"]):
                    
                    self.log_result("Admin Update Partner Organization", True, 
                                  f"Partner organization updated with rating {update_data['performance_rating']}")
                    return True
                else:
                    self.log_result("Admin Update Partner Organization", False, "Partner data not updated", data)
                    return False
            else:
                self.log_result("Admin Update Partner Organization", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Update Partner Organization", False, f"Request error: {str(e)}")
            return False

    def test_admin_create_partner_performance(self):
        """Test creating partner performance record"""
        if not hasattr(self, 'partner_id'):
            self.log_result("Admin Create Partner Performance", False, "No partner ID available from previous test")
            return False
        
        if not hasattr(self, 'project_id'):
            # Create a project for performance tracking
            try:
                from datetime import datetime, timedelta
                
                project_data = {
                    "title": f"Youth Skills Development Project {uuid.uuid4().hex[:8]}",
                    "description": "Digital literacy and entrepreneurship training for youth",
                    "sector": "Education",
                    "donor": "USAID",
                    "implementation_start": (datetime.now() + timedelta(days=30)).isoformat(),
                    "implementation_end": (datetime.now() + timedelta(days=365)).isoformat(),
                    "total_budget": 150000.0,
                    "budget_currency": "RWF",
                    "location": "Kigali, Rwanda",
                    "target_beneficiaries": 500,
                    "team_members": []
                }
                
                project_response = self.session.post(
                    f"{self.base_url}/projects",
                    json=project_data
                )
                
                if project_response.status_code == 200:
                    project_result = project_response.json()
                    self.project_id = project_result.get("id") or project_result.get("_id")
                else:
                    self.log_result("Admin Create Partner Performance", False, "Failed to create project for performance test")
                    return False
            except Exception as e:
                self.log_result("Admin Create Partner Performance", False, f"Error creating project: {str(e)}")
                return False
        
        try:
            from datetime import datetime, timedelta
            
            performance_data = {
                "partner_organization_id": self.partner_id,
                "project_id": self.project_id,
                "period_start": (datetime.now() - timedelta(days=90)).isoformat(),
                "period_end": datetime.now().isoformat(),
                "budget_allocated": 50000.0,
                "budget_utilized": 45000.0,
                "activities_completed": 8,
                "activities_planned": 10,
                "beneficiaries_reached": 450,
                "kpi_achievements": {
                    "youth_trained": 85.0,
                    "completion_rate": 90.0,
                    "employment_rate": 75.0
                },
                "challenges": "Limited internet connectivity in rural areas affected some digital training sessions",
                "recommendations": "Invest in mobile internet solutions and offline training materials"
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/partners/performance",
                json=performance_data
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle both 'id' and '_id' fields
                performance_id = data.get("id") or data.get("_id")
                if (performance_id and 
                    data.get("partner_organization_id") == self.partner_id and
                    data.get("beneficiaries_reached") == performance_data["beneficiaries_reached"]):
                    
                    self.performance_id = performance_id
                    performance_score = data.get("performance_score", 0)
                    self.log_result("Admin Create Partner Performance", True, 
                                  f"Partner performance record created with score: {performance_score:.1f}")
                    return True
                else:
                    self.log_result("Admin Create Partner Performance", False, "Performance data mismatch", data)
                    return False
            else:
                self.log_result("Admin Create Partner Performance", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Create Partner Performance", False, f"Request error: {str(e)}")
            return False

    def test_admin_get_partner_performance_summary(self):
        """Test getting partner performance summary"""
        try:
            response = self.session.get(f"{self.base_url}/admin/partners/performance/summary")
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    summary_data = data["data"]
                    if ("partners" in summary_data and 
                        "summary" in summary_data):
                        
                        summary = summary_data["summary"]
                        required_fields = ["total_partners", "avg_performance", "total_budget", "total_beneficiaries"]
                        
                        if all(field in summary for field in required_fields):
                            self.log_result("Admin Get Partner Performance Summary", True, 
                                          f"Performance summary retrieved: {summary['total_partners']} partners, "
                                          f"avg performance: {summary['avg_performance']:.1f}")
                            return True
                        else:
                            missing_fields = [field for field in required_fields if field not in summary]
                            self.log_result("Admin Get Partner Performance Summary", False, 
                                          f"Missing fields: {missing_fields}", data)
                            return False
                    else:
                        self.log_result("Admin Get Partner Performance Summary", False, 
                                      "Missing partners or summary in response", data)
                        return False
                else:
                    self.log_result("Admin Get Partner Performance Summary", False, "Missing success or data fields", data)
                    return False
            else:
                self.log_result("Admin Get Partner Performance Summary", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Get Partner Performance Summary", False, f"Request error: {str(e)}")
            return False

    def test_admin_update_organization_branding(self):
        """Test updating organization branding settings"""
        try:
            branding_data = {
                "primary_color": "#1E40AF",  # Blue
                "secondary_color": "#059669",  # Green
                "accent_color": "#7C3AED",  # Purple
                "background_color": "#F9FAFB",  # Light gray
                "text_color": "#111827",  # Dark gray
                "white_label_enabled": True
            }
            
            response = self.session.put(
                f"{self.base_url}/admin/branding",
                json=branding_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    branding_result = data["data"]
                    if (branding_result.get("primary_color") == branding_data["primary_color"] and
                        branding_result.get("white_label_enabled") == branding_data["white_label_enabled"]):
                        
                        self.log_result("Admin Update Organization Branding", True, 
                                      f"Organization branding updated with primary color: {branding_data['primary_color']}")
                        return True
                    else:
                        self.log_result("Admin Update Organization Branding", False, "Branding data mismatch", data)
                        return False
                else:
                    self.log_result("Admin Update Organization Branding", False, "Missing success or data fields", data)
                    return False
            else:
                self.log_result("Admin Update Organization Branding", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Update Organization Branding", False, f"Request error: {str(e)}")
            return False

    def test_admin_get_organization_branding(self):
        """Test getting organization branding settings"""
        try:
            response = self.session.get(f"{self.base_url}/admin/branding")
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    branding_data = data["data"]
                    if branding_data:  # Branding exists
                        required_fields = ["primary_color", "secondary_color", "accent_color", 
                                         "background_color", "text_color", "white_label_enabled"]
                        
                        if all(field in branding_data for field in required_fields):
                            self.log_result("Admin Get Organization Branding", True, 
                                          f"Branding settings retrieved with primary color: {branding_data['primary_color']}")
                            return True
                        else:
                            missing_fields = [field for field in required_fields if field not in branding_data]
                            self.log_result("Admin Get Organization Branding", False, 
                                          f"Missing fields: {missing_fields}", data)
                            return False
                    else:
                        self.log_result("Admin Get Organization Branding", True, "No branding settings found (expected for new organization)")
                        return True
                else:
                    self.log_result("Admin Get Organization Branding", False, "Missing success or data fields", data)
                    return False
            else:
                self.log_result("Admin Get Organization Branding", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Get Organization Branding", False, f"Request error: {str(e)}")
            return False

    def test_admin_get_email_logs(self):
        """Test getting email logs from mock email system"""
        try:
            response = self.session.get(
                f"{self.base_url}/admin/email-logs",
                params={"limit": 20}
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    email_logs = data["data"]
                    if isinstance(email_logs, list):
                        # Check if we have any logs (might be empty for new organization)
                        if len(email_logs) > 0:
                            # Verify log structure
                            first_log = email_logs[0]
                            required_fields = ["recipient_email", "template_used", "subject", 
                                             "status", "sent_at", "triggered_by"]
                            
                            if all(field in first_log for field in required_fields):
                                self.log_result("Admin Get Email Logs", True, 
                                              f"Retrieved {len(email_logs)} email logs successfully")
                                return True
                            else:
                                missing_fields = [field for field in required_fields if field not in first_log]
                                self.log_result("Admin Get Email Logs", False, 
                                              f"Missing fields in log entry: {missing_fields}", data)
                                return False
                        else:
                            self.log_result("Admin Get Email Logs", True, "No email logs found (expected for new organization)")
                            return True
                    else:
                        self.log_result("Admin Get Email Logs", False, "Email logs data is not a list", data)
                        return False
                else:
                    self.log_result("Admin Get Email Logs", False, "Missing success or data fields", data)
                    return False
            else:
                self.log_result("Admin Get Email Logs", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Get Email Logs", False, f"Request error: {str(e)}")
            return False

    # IremboPay Payment Integration Tests
    def test_payment_plans_endpoint(self):
        """Test GET /api/payments/plans endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/payments/plans")
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"] and "plans" in data:
                    plans = data["plans"]
                    if "Basic" in plans and "Professional" in plans and "Enterprise" in plans:
                        basic_plan = plans["Basic"]
                        professional_plan = plans["Professional"]
                        enterprise_plan = plans["Enterprise"]
                        
                        # Verify Basic plan details
                        if (basic_plan.get("price") == 100000 and 
                            basic_plan.get("currency") == "RWF" and
                            "features" in basic_plan):
                            
                            # Verify Professional plan details
                            if (professional_plan.get("price") == 300000 and
                                professional_plan.get("currency") == "RWF"):
                                
                                # Verify Enterprise plan shows custom pricing
                                if enterprise_plan.get("price") == "Custom":
                                    self.log_result("Payment Plans Endpoint", True, 
                                                  "All payment plans retrieved with correct pricing")
                                    return True
                                else:
                                    self.log_result("Payment Plans Endpoint", False, 
                                                  "Enterprise plan pricing incorrect", data)
                                    return False
                            else:
                                self.log_result("Payment Plans Endpoint", False, 
                                              "Professional plan details incorrect", data)
                                return False
                        else:
                            self.log_result("Payment Plans Endpoint", False, 
                                          "Basic plan details incorrect", data)
                            return False
                    else:
                        self.log_result("Payment Plans Endpoint", False, 
                                      "Missing required plans", data)
                        return False
                else:
                    self.log_result("Payment Plans Endpoint", False, 
                                  "Invalid response structure", data)
                    return False
            else:
                self.log_result("Payment Plans Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Payment Plans Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_create_invoice_endpoint(self):
        """Test POST /api/payments/create-invoice endpoint"""
        try:
            invoice_data = {
                "customer": {
                    "email": "jean.uwimana@example.com",
                    "name": "Jean Uwimana",
                    "phone_number": "0788123456"
                },
                "payment_items": [
                    {
                        "unit_amount": 100000,
                        "quantity": 1,
                        "code": "BASIC-PLAN",
                        "description": "DataRW Basic Plan - Monthly Subscription"
                    }
                ],
                "description": "DataRW Basic Plan Subscription Payment",
                "currency": "RWF"
            }
            
            response = self.session.post(
                f"{self.base_url}/payments/create-invoice",
                json=invoice_data
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["invoice_number", "transaction_id", "status", 
                                 "amount", "currency", "payment_url", "expiry_at"]
                
                if all(field in data for field in required_fields):
                    if (data["amount"] == 100000 and 
                        data["currency"] == "RWF" and
                        data["status"] == "pending"):
                        
                        self.test_invoice_number = data["invoice_number"]
                        self.log_result("Create Invoice Endpoint", True, 
                                      f"Invoice created successfully: {data['invoice_number']}")
                        return True
                    else:
                        self.log_result("Create Invoice Endpoint", False, 
                                      "Invoice data incorrect", data)
                        return False
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("Create Invoice Endpoint", False, 
                                  f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("Create Invoice Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Invoice Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_initiate_mtn_payment(self):
        """Test POST /api/payments/initiate with MTN mobile money"""
        if not hasattr(self, 'test_invoice_number'):
            self.log_result("Initiate MTN Payment", False, "No invoice number from previous test")
            return False
        
        try:
            payment_data = {
                "invoice_number": self.test_invoice_number,
                "phone_number": "0788123456",
                "provider": "MTN"
            }
            
            response = self.session.post(
                f"{self.base_url}/payments/initiate",
                json=payment_data
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["payment_reference", "status", "message", 
                                 "amount", "currency", "provider", "phone_number"]
                
                if all(field in data for field in required_fields):
                    if (data["provider"] == "MTN" and 
                        data["status"] == "processing" and
                        data["amount"] == 100000):
                        
                        self.test_payment_reference = data["payment_reference"]
                        self.log_result("Initiate MTN Payment", True, 
                                      f"MTN payment initiated: {data['payment_reference']}")
                        return True
                    else:
                        self.log_result("Initiate MTN Payment", False, 
                                      "Payment data incorrect", data)
                        return False
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("Initiate MTN Payment", False, 
                                  f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("Initiate MTN Payment", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Initiate MTN Payment", False, f"Request error: {str(e)}")
            return False

    def test_initiate_airtel_payment(self):
        """Test POST /api/payments/initiate with Airtel mobile money"""
        # Create a new invoice for Airtel test
        try:
            invoice_data = {
                "customer": {
                    "email": "marie.mukamana@example.com",
                    "name": "Marie Mukamana",
                    "phone_number": "0738456789"
                },
                "payment_items": [
                    {
                        "unit_amount": 300000,
                        "quantity": 1,
                        "code": "PROFESSIONAL-PLAN",
                        "description": "DataRW Professional Plan - Monthly Subscription"
                    }
                ],
                "description": "DataRW Professional Plan Subscription Payment",
                "currency": "RWF"
            }
            
            invoice_response = self.session.post(
                f"{self.base_url}/payments/create-invoice",
                json=invoice_data
            )
            
            if invoice_response.status_code != 200:
                self.log_result("Initiate Airtel Payment", False, "Failed to create invoice for Airtel test")
                return False
            
            invoice_data = invoice_response.json()
            airtel_invoice_number = invoice_data["invoice_number"]
            
            # Now initiate Airtel payment
            payment_data = {
                "invoice_number": airtel_invoice_number,
                "phone_number": "0738456789",
                "provider": "AIRTEL"
            }
            
            response = self.session.post(
                f"{self.base_url}/payments/initiate",
                json=payment_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("provider") == "AIRTEL" and 
                    data.get("status") == "processing" and
                    data.get("amount") == 300000):
                    
                    self.log_result("Initiate Airtel Payment", True, 
                                  f"Airtel payment initiated: {data['payment_reference']}")
                    return True
                else:
                    self.log_result("Initiate Airtel Payment", False, 
                                  "Airtel payment data incorrect", data)
                    return False
            else:
                self.log_result("Initiate Airtel Payment", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Initiate Airtel Payment", False, f"Request error: {str(e)}")
            return False

    def test_subscription_payment_basic_plan(self):
        """Test POST /api/payments/subscription for Basic plan"""
        try:
            subscription_data = {
                "user_email": "alice.uwimana@example.com",
                "user_name": "Alice Uwimana",
                "phone_number": "0788987654",
                "plan_name": "Basic",
                "payment_method": "MTN"
            }
            
            response = self.session.post(
                f"{self.base_url}/payments/subscription",
                json=subscription_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and 
                    "data" in data and
                    data["data"].get("plan") == "Basic" and
                    data["data"].get("amount") == 100000):
                    
                    # Store invoice number for status checking
                    if "invoice" in data["data"]:
                        self.basic_subscription_invoice = data["data"]["invoice"]["invoiceNumber"]
                    
                    self.log_result("Subscription Payment Basic Plan", True, 
                                  "Basic plan subscription payment created successfully")
                    return True
                else:
                    self.log_result("Subscription Payment Basic Plan", False, 
                                  "Subscription data incorrect", data)
                    return False
            else:
                self.log_result("Subscription Payment Basic Plan", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Subscription Payment Basic Plan", False, f"Request error: {str(e)}")
            return False

    def test_subscription_payment_professional_plan(self):
        """Test POST /api/payments/subscription for Professional plan"""
        try:
            subscription_data = {
                "user_email": "bob.nzeyimana@example.com",
                "user_name": "Bob Nzeyimana",
                "phone_number": "0738123456",
                "plan_name": "Professional",
                "payment_method": "AIRTEL"
            }
            
            response = self.session.post(
                f"{self.base_url}/payments/subscription",
                json=subscription_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and 
                    "data" in data and
                    data["data"].get("plan") == "Professional" and
                    data["data"].get("amount") == 300000):
                    
                    # Store invoice number for status checking
                    if "invoice" in data["data"]:
                        self.professional_subscription_invoice = data["data"]["invoice"]["invoiceNumber"]
                    
                    self.log_result("Subscription Payment Professional Plan", True, 
                                  "Professional plan subscription payment created successfully")
                    return True
                else:
                    self.log_result("Subscription Payment Professional Plan", False, 
                                  "Subscription data incorrect", data)
                    return False
            else:
                self.log_result("Subscription Payment Professional Plan", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Subscription Payment Professional Plan", False, f"Request error: {str(e)}")
            return False

    def test_subscription_payment_enterprise_plan(self):
        """Test POST /api/payments/subscription for Enterprise plan (should show custom pricing)"""
        try:
            subscription_data = {
                "user_email": "ceo@bigcompany.com",
                "user_name": "CEO BigCompany",
                "phone_number": "0788555666",
                "plan_name": "Enterprise",
                "payment_method": "MTN"
            }
            
            response = self.session.post(
                f"{self.base_url}/payments/subscription",
                json=subscription_data
            )
            
            # Enterprise should return an error about custom pricing
            if response.status_code == 500:
                data = response.json()
                if "custom pricing" in data.get("detail", "").lower():
                    self.log_result("Subscription Payment Enterprise Plan", True, 
                                  "Enterprise plan correctly shows custom pricing message")
                    return True
                else:
                    self.log_result("Subscription Payment Enterprise Plan", False, 
                                  "Wrong error message for Enterprise plan", data)
                    return False
            else:
                self.log_result("Subscription Payment Enterprise Plan", False, 
                              f"Expected 500 error, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Subscription Payment Enterprise Plan", False, f"Request error: {str(e)}")
            return False

    def test_payment_status_endpoint(self):
        """Test GET /api/payments/status/{invoice_number}"""
        if not hasattr(self, 'test_invoice_number'):
            self.log_result("Payment Status Endpoint", False, "No invoice number from previous test")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/payments/status/{self.test_invoice_number}")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["invoice_number", "status", "amount", "currency", "created_at"]
                
                if all(field in data for field in required_fields):
                    if (data["invoice_number"] == self.test_invoice_number and
                        data["amount"] == 100000 and
                        data["currency"] == "RWF"):
                        
                        self.log_result("Payment Status Endpoint", True, 
                                      f"Payment status retrieved: {data['status']}")
                        return True
                    else:
                        self.log_result("Payment Status Endpoint", False, 
                                      "Payment status data incorrect", data)
                        return False
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("Payment Status Endpoint", False, 
                                  f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("Payment Status Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Payment Status Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_payment_history_endpoint(self):
        """Test GET /api/payments/history"""
        try:
            response = self.session.get(f"{self.base_url}/payments/history")
            
            if response.status_code == 200:
                data = response.json()
                if ("payments" in data and 
                    "total" in data and
                    isinstance(data["payments"], list)):
                    
                    # Check if we have payments from our tests
                    payments = data["payments"]
                    if len(payments) > 0:
                        # Verify payment structure
                        first_payment = payments[0]
                        required_fields = ["id", "invoice_number", "status", "amount", "currency", "created_at"]
                        
                        if all(field in first_payment for field in required_fields):
                            self.log_result("Payment History Endpoint", True, 
                                          f"Payment history retrieved with {len(payments)} payments")
                            return True
                        else:
                            missing_fields = [field for field in required_fields if field not in first_payment]
                            self.log_result("Payment History Endpoint", False, 
                                          f"Payment missing fields: {missing_fields}", first_payment)
                            return False
                    else:
                        self.log_result("Payment History Endpoint", True, 
                                      "Payment history endpoint working (no payments yet)")
                        return True
                else:
                    self.log_result("Payment History Endpoint", False, 
                                  "Invalid response structure", data)
                    return False
            else:
                self.log_result("Payment History Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Payment History Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_webhook_endpoint(self):
        """Test POST /api/webhooks/irembopay webhook processing"""
        try:
            import hmac
            import hashlib
            import json
            
            # Create mock webhook payload
            webhook_payload = {
                "id": str(uuid.uuid4()),
                "type": "payment.completed",
                "createdAt": datetime.now().isoformat(),
                "data": {
                    "invoiceNumber": getattr(self, 'test_invoice_number', '880123456789'),
                    "transactionId": "TXN-TEST-123456",
                    "paymentReference": "MTN-123456",
                    "amount": 100000,
                    "currency": "RWF",
                    "provider": "MTN",
                    "completedAt": datetime.now().isoformat()
                }
            }
            
            payload_str = json.dumps(webhook_payload)
            
            # Generate mock signature
            webhook_secret = "mock_webhook_secret_key_for_development"
            signature = hmac.new(
                webhook_secret.encode('utf-8'),
                payload_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            headers = {
                "X-IremboPay-Signature": f"sha256={signature}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                f"{self.base_url}/webhooks/irembopay",
                data=payload_str,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_result("Webhook Endpoint", True, 
                                  "Webhook processed successfully")
                    return True
                else:
                    self.log_result("Webhook Endpoint", False, 
                                  "Webhook response incorrect", data)
                    return False
            else:
                self.log_result("Webhook Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Webhook Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_webhook_signature_validation(self):
        """Test webhook signature validation (should reject invalid signatures)"""
        try:
            import json
            
            # Create mock webhook payload
            webhook_payload = {
                "id": str(uuid.uuid4()),
                "type": "payment.failed",
                "createdAt": datetime.now().isoformat(),
                "data": {
                    "invoiceNumber": "880987654321",
                    "transactionId": "TXN-FAIL-123456",
                    "failureReason": "Insufficient funds"
                }
            }
            
            payload_str = json.dumps(webhook_payload)
            
            # Use invalid signature
            headers = {
                "X-IremboPay-Signature": "sha256=invalid_signature_here",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                f"{self.base_url}/webhooks/irembopay",
                data=payload_str,
                headers=headers
            )
            
            # Should return 401 for invalid signature
            if response.status_code == 401:
                data = response.json()
                if "signature" in data.get("detail", "").lower():
                    self.log_result("Webhook Signature Validation", True, 
                                  "Invalid webhook signature correctly rejected")
                    return True
                else:
                    self.log_result("Webhook Signature Validation", False, 
                                  "Wrong error message for invalid signature", data)
                    return False
            else:
                self.log_result("Webhook Signature Validation", False, 
                              f"Expected 401, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Webhook Signature Validation", False, f"Request error: {str(e)}")
            return False

    def test_invalid_phone_number_error(self):
        """Test error handling for invalid phone numbers"""
        try:
            invoice_data = {
                "customer": {
                    "email": "test@example.com",
                    "name": "Test User",
                    "phone_number": "123456789"  # Invalid format
                },
                "payment_items": [
                    {
                        "unit_amount": 100000,
                        "quantity": 1,
                        "code": "TEST-PLAN",
                        "description": "Test Plan"
                    }
                ],
                "description": "Test payment with invalid phone",
                "currency": "RWF"
            }
            
            response = self.session.post(
                f"{self.base_url}/payments/create-invoice",
                json=invoice_data
            )
            
            # Should return validation error
            if response.status_code == 422:
                data = response.json()
                if "phone_number" in str(data).lower():
                    self.log_result("Invalid Phone Number Error", True, 
                                  "Invalid phone number correctly rejected")
                    return True
                else:
                    self.log_result("Invalid Phone Number Error", False, 
                                  "Wrong validation error message", data)
                    return False
            else:
                self.log_result("Invalid Phone Number Error", False, 
                              f"Expected 422, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Invalid Phone Number Error", False, f"Request error: {str(e)}")
            return False

    def test_nonexistent_invoice_error(self):
        """Test error handling for non-existent invoices"""
        try:
            fake_invoice_number = "880999999999"
            
            response = self.session.get(f"{self.base_url}/payments/status/{fake_invoice_number}")
            
            # Should return 404 or 500 with appropriate error
            if response.status_code in [404, 500]:
                data = response.json()
                if "not found" in data.get("detail", "").lower():
                    self.log_result("Nonexistent Invoice Error", True, 
                                  "Non-existent invoice correctly handled")
                    return True
                else:
                    self.log_result("Nonexistent Invoice Error", False, 
                                  "Wrong error message for non-existent invoice", data)
                    return False
            else:
                self.log_result("Nonexistent Invoice Error", False, 
                              f"Expected 404/500, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Nonexistent Invoice Error", False, f"Request error: {str(e)}")
            return False

    def test_project_creation_with_correct_fields(self):
        """Test project creation endpoint with correct field mapping"""
        try:
            # Get a user ID for project_manager_id (required field)
            users_response = self.session.get(f"{self.base_url}/users")
            if users_response.status_code != 200:
                self.log_result("Project Creation - Get Users", False, "Failed to get users for project manager ID")
                return False
            
            users = users_response.json()
            if not users:
                self.log_result("Project Creation - Get Users", False, "No users available for project manager ID")
                return False
            
            # Use the first user as project manager
            project_manager_id = users[0].get("id") or users[0].get("_id")
            if not project_manager_id:
                self.log_result("Project Creation - Get Users", False, "No valid user ID found")
                return False
            
            # Test with correct field mapping as per ProjectCreate model
            project_data = {
                "name": "Digital Literacy Training Program",  # NOT title
                "description": "A comprehensive program to improve digital literacy skills among rural communities in Rwanda",
                "project_manager_id": project_manager_id,  # Required field
                "start_date": "2024-02-01T00:00:00Z",  # NOT implementation_start
                "end_date": "2025-12-31T23:59:59Z",  # NOT implementation_end
                "budget_total": 2500000.0,  # NOT total_budget
                "beneficiaries_target": 5000,  # NOT target_beneficiaries
                "location": "Nyagatare District, Eastern Province",
                "donor_organization": "World Bank Group",  # NOT donor
                "implementing_partners": ["Rwanda ICT Chamber", "Digital Opportunity Trust"],
                "tags": ["education", "technology", "rural development"]
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data
            )
            
            if response.status_code == 200:
                data = response.json()
                project_id = data.get("id") or data.get("_id")
                
                # Verify all fields are correctly saved
                if (project_id and 
                    data.get("name") == project_data["name"] and
                    data.get("project_manager_id") == project_data["project_manager_id"] and
                    data.get("budget_total") == project_data["budget_total"] and
                    data.get("beneficiaries_target") == project_data["beneficiaries_target"] and
                    data.get("donor_organization") == project_data["donor_organization"]):
                    
                    self.project_id = project_id
                    self.log_result("Project Creation - Correct Fields", True, 
                                  f"Project created successfully with correct field mapping. ID: {project_id}")
                    return True
                else:
                    self.log_result("Project Creation - Correct Fields", False, 
                                  "Project data mismatch or missing fields", data)
                    return False
            else:
                self.log_result("Project Creation - Correct Fields", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Project Creation - Correct Fields", False, f"Request error: {str(e)}")
            return False

    def test_project_creation_validation_errors(self):
        """Test project creation with missing required fields"""
        try:
            # Test 1: Missing project_manager_id (required field)
            project_data_missing_manager = {
                "name": "Test Project Without Manager",
                "start_date": "2024-02-01T00:00:00Z",
                "end_date": "2025-12-31T23:59:59Z",
                "budget_total": 1000000.0,
                "beneficiaries_target": 1000
                # Missing project_manager_id
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data_missing_manager
            )
            
            if response.status_code == 422:  # Validation error
                data = response.json()
                # Check if it's a proper JSON response (not an object that causes React errors)
                if isinstance(data, dict) and "detail" in data:
                    self.log_result("Project Creation - Missing Manager Validation", True, 
                                  "Properly returns validation error for missing project_manager_id")
                else:
                    self.log_result("Project Creation - Missing Manager Validation", False, 
                                  "Invalid response format for validation error", data)
                    return False
            else:
                self.log_result("Project Creation - Missing Manager Validation", False, 
                              f"Expected 422, got {response.status_code}", response.text)
                return False
            
            # Test 2: Missing name (required field)
            project_data_missing_name = {
                "project_manager_id": "test-manager-id",
                "start_date": "2024-02-01T00:00:00Z",
                "end_date": "2025-12-31T23:59:59Z",
                "budget_total": 1000000.0,
                "beneficiaries_target": 1000
                # Missing name
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data_missing_name
            )
            
            if response.status_code == 422:  # Validation error
                data = response.json()
                if isinstance(data, dict) and "detail" in data:
                    self.log_result("Project Creation - Missing Name Validation", True, 
                                  "Properly returns validation error for missing name")
                else:
                    self.log_result("Project Creation - Missing Name Validation", False, 
                                  "Invalid response format for validation error", data)
                    return False
            else:
                self.log_result("Project Creation - Missing Name Validation", False, 
                              f"Expected 422, got {response.status_code}", response.text)
                return False
            
            # Test 3: Invalid budget_total (must be > 0)
            project_data_invalid_budget = {
                "name": "Test Project Invalid Budget",
                "project_manager_id": "test-manager-id",
                "start_date": "2024-02-01T00:00:00Z",
                "end_date": "2025-12-31T23:59:59Z",
                "budget_total": -1000.0,  # Invalid negative budget
                "beneficiaries_target": 1000
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data_invalid_budget
            )
            
            if response.status_code == 422:  # Validation error
                data = response.json()
                if isinstance(data, dict) and "detail" in data:
                    self.log_result("Project Creation - Invalid Budget Validation", True, 
                                  "Properly returns validation error for invalid budget")
                    return True
                else:
                    self.log_result("Project Creation - Invalid Budget Validation", False, 
                                  "Invalid response format for validation error", data)
                    return False
            else:
                self.log_result("Project Creation - Invalid Budget Validation", False, 
                              f"Expected 422, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Project Creation - Validation Errors", False, f"Request error: {str(e)}")
            return False

    def test_project_creation_with_old_field_names(self):
        """Test project creation with old field names (should fail)"""
        try:
            # Get a user ID for project_manager_id
            users_response = self.session.get(f"{self.base_url}/users")
            if users_response.status_code != 200:
                self.log_result("Project Creation - Old Fields", False, "Failed to get users")
                return False
            
            users = users_response.json()
            if not users:
                self.log_result("Project Creation - Old Fields", False, "No users available")
                return False
            
            project_manager_id = users[0].get("id") or users[0].get("_id")
            
            # Test with OLD field names (should cause validation errors)
            project_data_old_fields = {
                "title": "Project with Old Field Names",  # Should be 'name'
                "total_budget": 1000000.0,  # Should be 'budget_total'
                "target_beneficiaries": 1000,  # Should be 'beneficiaries_target'
                "implementation_start": "2024-02-01T00:00:00Z",  # Should be 'start_date'
                "implementation_end": "2025-12-31T23:59:59Z",  # Should be 'end_date'
                "donor": "World Bank",  # Should be 'donor_organization'
                "project_manager_id": project_manager_id  # This one is correct
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data_old_fields
            )
            
            # Should return validation error due to missing required fields
            if response.status_code == 422:
                data = response.json()
                if isinstance(data, dict) and "detail" in data:
                    self.log_result("Project Creation - Old Field Names", True, 
                                  "Correctly rejects old field names with validation error")
                    return True
                else:
                    self.log_result("Project Creation - Old Field Names", False, 
                                  "Invalid response format for validation error", data)
                    return False
            else:
                self.log_result("Project Creation - Old Field Names", False, 
                              f"Expected 422 validation error, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Project Creation - Old Field Names", False, f"Request error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🚀 Starting DataRW Backend API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test sequence - order matters for dependencies
        tests = [
            self.test_api_health,
            self.test_user_registration,
            self.test_duplicate_registration,
            self.test_user_login_valid,
            self.test_user_login_invalid,
            self.test_get_organization,
            self.test_update_organization,
            self.test_create_survey,
            self.test_get_surveys,
            self.test_get_specific_survey,
            self.test_update_survey,
            self.test_get_organization_users,
            self.test_create_user,
            self.test_update_user_role,
            self.test_get_analytics,
            self.test_survey_limit_enforcement,
            # IremboPay Payment Integration Tests
            self.test_payment_plans_endpoint,
            self.test_create_invoice_endpoint,
            self.test_initiate_mtn_payment,
            self.test_initiate_airtel_payment,
            self.test_subscription_payment_basic_plan,
            self.test_subscription_payment_professional_plan,
            self.test_subscription_payment_enterprise_plan,
            self.test_payment_status_endpoint,
            self.test_payment_history_endpoint,
            self.test_webhook_endpoint,
            self.test_webhook_signature_validation,
            self.test_invalid_phone_number_error,
            self.test_nonexistent_invoice_error,
            # AI Survey Generation Tests
            self.test_ai_survey_generation,
            self.test_document_upload_context,
            self.test_survey_translation,
            self.test_get_survey_context,
            self.test_ai_with_context_generation,
            self.test_enhanced_question_types,
            # Project Management System Tests
            self.test_project_dashboard,
            self.test_dashboard_pydantic_validation_fix,  # NEW: Test Pydantic validation fix
            self.test_project_creation_with_correct_fields,  # NEW: Test correct field mapping
            self.test_project_creation_validation_errors,    # NEW: Test validation errors  
            self.test_project_creation_with_old_field_names, # NEW: Test old field names rejection
            self.test_create_project,
            self.test_get_projects,
            self.test_get_specific_project,
            self.test_update_project,
            self.test_create_activity_corrected_fields,  # NEW: Test corrected field mapping
            self.test_create_activity_validation_errors,  # NEW: Test validation errors
            self.test_create_activity_old_field_names,    # NEW: Test old field names rejection
            self.test_get_activities,
            self.test_update_activity,
            self.test_create_budget_item,
            self.test_get_budget_items,
            self.test_get_budget_summary,
            self.test_create_kpi_indicator,
            self.test_get_kpi_indicators,
            self.test_update_kpi_value,
            self.test_create_beneficiary,
            self.test_get_beneficiaries,
            self.test_get_beneficiary_demographics,
            # Admin Panel Tests
            self.test_admin_create_user_advanced,
            self.test_admin_bulk_create_users,
            self.test_admin_create_partner_organization,
            self.test_admin_get_partner_organizations,
            self.test_admin_update_partner_organization,
            self.test_admin_create_partner_performance,
            self.test_admin_get_partner_performance_summary,
            self.test_admin_update_organization_branding,
            self.test_admin_get_organization_branding,
            self.test_admin_get_email_logs,
            self.test_delete_project,
            # Cleanup tests
            self.test_delete_user,
            self.test_delete_survey
        ]
        
        for test in tests:
            test()
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
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

    def run_activity_creation_tests(self):
        """Run focused tests for activity creation endpoint with corrected field mapping"""
        print(f"🎯 Starting Activity Creation Tests - Field Mapping Fix Verification")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Required setup tests
        setup_tests = [
            self.test_api_health,
            self.test_user_registration,
            self.test_user_login_valid,
            self.test_create_project,  # Need project for activity creation
        ]
        
        # Activity creation tests
        activity_tests = [
            self.test_create_activity_corrected_fields,
            self.test_create_activity_validation_errors,
            self.test_create_activity_old_field_names,
        ]
        
        print("🔧 Running setup tests...")
        for test in setup_tests:
            test()
            if not self.test_results[-1]['success']:
                print(f"❌ Setup failed at {test.__name__}, stopping tests")
                return 0, len(setup_tests)
        
        print("\n🎯 Running activity creation tests...")
        for test in activity_tests:
            test()
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 80)
        print("📊 ACTIVITY CREATION TEST SUMMARY")
        print("=" * 80)
        
        # Count only activity creation tests for summary
        activity_results = self.test_results[-len(activity_tests):]
        passed = sum(1 for result in activity_results if result['success'])
        failed = len(activity_results) - passed
        
        print(f"✅ Passed: {passed}/{len(activity_tests)}")
        print(f"❌ Failed: {failed}/{len(activity_tests)}")
        print(f"📈 Success Rate: {(passed/len(activity_tests)*100):.1f}%")
        
        if failed > 0:
            print("\n🔍 FAILED ACTIVITY TESTS:")
            for result in activity_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
        else:
            print("\n🎉 ALL ACTIVITY CREATION TESTS PASSED!")
            print("✅ Corrected field mapping (name, assigned_to) working correctly")
            print("✅ Proper JSON validation error responses confirmed")
            print("✅ Old field names (title, responsible_user_id) properly rejected")
        
        return passed, failed

    def run_project_management_comprehensive_tests(self):
        """Run comprehensive tests for all project management system endpoints as requested by user"""
        print(f"🎯 COMPREHENSIVE PROJECT MANAGEMENT SYSTEM TESTING")
        print(f"📍 Testing against: {self.base_url}")
        print("🔍 Focus: Dashboard Data, Beneficiaries, Budget Tracking, Activities, Projects")
        print("=" * 80)
        
        # Required setup tests
        setup_tests = [
            self.test_api_health,
            self.test_user_registration,
            self.test_user_login_valid,
        ]
        
        # Core project management tests as requested
        project_mgmt_tests = [
            # 1. Dashboard Data Testing
            self.test_project_dashboard,
            self.test_dashboard_pydantic_validation_fix,
            
            # 2. Project System Testing
            self.test_project_creation_with_correct_fields,
            self.test_get_projects,
            
            # 3. Activity System Testing  
            self.test_create_activity_corrected_fields,
            self.test_get_activities,
            
            # 4. Budget Tracking Testing
            self.test_create_budget_item,
            self.test_get_budget_items,
            self.test_get_budget_summary,
            
            # 5. Beneficiary System Testing
            self.test_create_beneficiary,
            self.test_get_beneficiaries,
            self.test_get_beneficiary_demographics,
            
            # 6. KPI System Testing
            self.test_create_kpi_indicator,
            self.test_get_kpi_indicators,
            self.test_update_kpi_value,
        ]
        
        print("🔧 Running setup tests...")
        for test in setup_tests:
            test()
            if not self.test_results[-1]['success']:
                print(f"❌ Setup failed at {test.__name__}, stopping tests")
                return 0, len(setup_tests)
        
        print("\n🎯 Running comprehensive project management tests...")
        for test in project_mgmt_tests:
            test()
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 80)
        print("📊 PROJECT MANAGEMENT SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        # Count only project management tests for summary
        pm_results = self.test_results[-len(project_mgmt_tests):]
        passed = sum(1 for result in pm_results if result['success'])
        failed = len(pm_results) - passed
        
        print(f"✅ Passed: {passed}/{len(project_mgmt_tests)}")
        print(f"❌ Failed: {failed}/{len(project_mgmt_tests)}")
        print(f"📈 Success Rate: {(passed/len(project_mgmt_tests)*100):.1f}%")
        
        # Detailed breakdown by category
        print("\n📋 DETAILED RESULTS BY CATEGORY:")
        
        # Dashboard tests
        dashboard_tests = [r for r in pm_results if 'dashboard' in r['test'].lower()]
        dashboard_passed = sum(1 for r in dashboard_tests if r['success'])
        print(f"   📊 Dashboard Data: {dashboard_passed}/{len(dashboard_tests)} passed")
        
        # Project tests
        project_tests = [r for r in pm_results if 'project' in r['test'].lower() and 'dashboard' not in r['test'].lower()]
        project_passed = sum(1 for r in project_tests if r['success'])
        print(f"   📁 Project System: {project_passed}/{len(project_tests)} passed")
        
        # Activity tests
        activity_tests = [r for r in pm_results if 'activity' in r['test'].lower()]
        activity_passed = sum(1 for r in activity_tests if r['success'])
        print(f"   ⚡ Activity System: {activity_passed}/{len(activity_tests)} passed")
        
        # Budget tests
        budget_tests = [r for r in pm_results if 'budget' in r['test'].lower()]
        budget_passed = sum(1 for r in budget_tests if r['success'])
        print(f"   💰 Budget Tracking: {budget_passed}/{len(budget_tests)} passed")
        
        # Beneficiary tests
        beneficiary_tests = [r for r in pm_results if 'beneficiary' in r['test'].lower() or 'beneficiaries' in r['test'].lower()]
        beneficiary_passed = sum(1 for r in beneficiary_tests if r['success'])
        print(f"   👥 Beneficiary System: {beneficiary_passed}/{len(beneficiary_tests)} passed")
        
        # KPI tests
        kpi_tests = [r for r in pm_results if 'kpi' in r['test'].lower()]
        kpi_passed = sum(1 for r in kpi_tests if r['success'])
        print(f"   📈 KPI Management: {kpi_passed}/{len(kpi_tests)} passed")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in pm_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
        else:
            print("\n🎉 ALL PROJECT MANAGEMENT TESTS PASSED!")
            print("✅ Dashboard data loading working correctly")
            print("✅ Project creation and listing working")
            print("✅ Activity creation and management working")
            print("✅ Budget tracking and summary working")
            print("✅ Beneficiary system working correctly")
            print("✅ KPI management system working")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = DataRWAPITester()
    
    # Run comprehensive project management tests as requested
    print("🎯 RUNNING COMPREHENSIVE PROJECT MANAGEMENT SYSTEM TESTS")
    print("Testing all project management endpoints to identify reported issues")
    print()
    
    passed, failed = tester.run_project_management_comprehensive_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()