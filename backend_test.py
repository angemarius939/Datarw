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

# Get backend URL from environment - use external URL for testing
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
# Use the external URL for testing as specified in the environment
API_BASE_URL = f"{BACKEND_URL}/api"

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
    
    def test_protected_endpoint_no_token(self):
        """Test protected endpoint without authorization token"""
        try:
            # Remove authorization header temporarily
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            response = self.session.get(f"{self.base_url}/organizations/me")
            
            # Restore headers
            self.session.headers.update(original_headers)
            
            if response.status_code in [401, 403]:
                self.log_result("Protected Endpoint - No Token", True, 
                              f"Properly rejected unauthorized access with HTTP {response.status_code}")
                return True
            else:
                self.log_result("Protected Endpoint - No Token", False, 
                              f"Expected 401/403, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Protected Endpoint - No Token", False, f"Request error: {str(e)}")
            return False
    
    def test_protected_endpoint_with_token(self):
        """Test protected endpoint with valid authorization token"""
        try:
            response = self.session.get(f"{self.base_url}/organizations/me")
            
            if response.status_code == 200:
                data = response.json()
                # Check for either 'id' or '_id' field
                org_id = data.get("id") or data.get("_id")
                if org_id and "name" in data:
                    # Verify the org_id matches what we expect from registration
                    if self.organization_data:
                        expected_org_id = self.organization_data.get("id") or self.organization_data.get("_id")
                        if org_id == expected_org_id:
                            self.log_result("Protected Endpoint - With Token", True, 
                                          "Organization data retrieved successfully with matching _id")
                            return True
                        else:
                            self.log_result("Protected Endpoint - With Token", False, 
                                          f"Organization ID mismatch: expected {expected_org_id}, got {org_id}")
                            return False
                    else:
                        self.log_result("Protected Endpoint - With Token", True, 
                                      "Organization data retrieved successfully")
                        return True
                else:
                    self.log_result("Protected Endpoint - With Token", False, 
                                  "Missing required fields in organization response", data)
                    return False
            else:
                self.log_result("Protected Endpoint - With Token", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Protected Endpoint - With Token", False, f"Request error: {str(e)}")
            return False

    def test_auth_endpoints_comprehensive(self):
        """Comprehensive test of auth endpoints as requested in review"""
        print("\n" + "="*60)
        print("COMPREHENSIVE AUTH ENDPOINTS TESTING")
        print("="*60)
        
        # Test 1: Registration with valid data
        success_count = 0
        total_tests = 6
        
        if self.test_user_registration():
            success_count += 1
        
        # Test 2: Duplicate registration
        if self.test_duplicate_registration():
            success_count += 1
        
        # Test 3: Valid login
        if self.test_user_login_valid():
            success_count += 1
        
        # Test 4: Invalid login
        if self.test_user_login_invalid():
            success_count += 1
        
        # Test 5: Protected endpoint without token
        if self.test_protected_endpoint_no_token():
            success_count += 1
        
        # Test 6: Protected endpoint with valid token
        if self.test_protected_endpoint_with_token():
            success_count += 1
        
        print(f"\nAUTH ENDPOINTS TESTING COMPLETE: {success_count}/{total_tests} tests passed")
        return success_count == total_tests
    
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
    def test_project_dashboard_datetime_bug_fix(self):
        """Test project dashboard endpoint specifically for datetime variable scoping bug fix"""
        try:
            response = self.session.get(f"{self.base_url}/projects/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    dashboard_data = data["data"]
                    
                    # Verify all required dashboard fields are present
                    required_fields = [
                        "total_projects", "active_projects", "completed_projects", 
                        "overdue_activities", "budget_utilization", "kpi_performance", 
                        "recent_activities", "projects_by_status", "budget_by_category"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in dashboard_data]
                    if missing_fields:
                        self.log_result("Project Dashboard DateTime Fix", False, 
                                      f"Missing required fields: {missing_fields}", data)
                        return False
                    
                    # Verify recent_activities structure (this uses datetime operations)
                    recent_activities = dashboard_data.get("recent_activities", [])
                    if isinstance(recent_activities, list):
                        for activity in recent_activities:
                            if not isinstance(activity, dict):
                                self.log_result("Project Dashboard DateTime Fix", False, 
                                              "recent_activities contains non-dict items", data)
                                return False
                            # Check for datetime-related fields
                            if "updated_at" in activity:
                                try:
                                    # Verify the datetime string is valid ISO format
                                    datetime.fromisoformat(activity["updated_at"].replace('Z', '+00:00'))
                                except ValueError:
                                    self.log_result("Project Dashboard DateTime Fix", False, 
                                                  f"Invalid datetime format in recent_activities: {activity['updated_at']}", data)
                                    return False
                    
                    # Verify overdue_activities calculation (uses datetime comparison)
                    overdue_activities = dashboard_data.get("overdue_activities", 0)
                    if not isinstance(overdue_activities, (int, float)):
                        self.log_result("Project Dashboard DateTime Fix", False, 
                                      f"overdue_activities should be numeric, got {type(overdue_activities)}", data)
                        return False
                    
                    # Verify projects_by_status has string keys (not None)
                    projects_by_status = dashboard_data.get("projects_by_status", {})
                    if isinstance(projects_by_status, dict):
                        for key in projects_by_status.keys():
                            if not isinstance(key, str):
                                self.log_result("Project Dashboard DateTime Fix", False, 
                                              f"projects_by_status contains non-string key: {key}", data)
                                return False
                    
                    # Verify budget_by_category has string keys (not None)
                    budget_by_category = dashboard_data.get("budget_by_category", {})
                    if isinstance(budget_by_category, dict):
                        for key in budget_by_category.keys():
                            if not isinstance(key, str):
                                self.log_result("Project Dashboard DateTime Fix", False, 
                                              f"budget_by_category contains non-string key: {key}", data)
                                return False
                    
                    self.log_result("Project Dashboard DateTime Fix", True, 
                                  "Dashboard endpoint working correctly - datetime scoping issue resolved, all datetime operations successful")
                    return True
                else:
                    self.log_result("Project Dashboard DateTime Fix", False, 
                                  "Missing success/data fields in response", data)
                    return False
            else:
                # Check specifically for the datetime scoping error
                if response.status_code == 500:
                    error_text = response.text
                    if "cannot access local variable 'datetime' where it is not associated with a value" in error_text:
                        self.log_result("Project Dashboard DateTime Fix", False, 
                                      "CRITICAL: Original datetime scoping error still present - fix not working", error_text)
                        return False
                    elif "Failed to get dashboard data" in error_text and "datetime" in error_text:
                        self.log_result("Project Dashboard DateTime Fix", False, 
                                      "CRITICAL: Datetime-related error in dashboard data retrieval", error_text)
                        return False
                
                self.log_result("Project Dashboard DateTime Fix", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Project Dashboard DateTime Fix", False, f"Request error: {str(e)}")
            return False

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
                if budget_id and data.get("item_name") == budget_data["item_name"]:
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
                "name": f"Number of People Trained in Digital Literacy {uuid.uuid4().hex[:8]}",
                "description": "Quantitative measure of people who completed digital literacy training program",
                "type": "quantitative",  # Use correct field name 'type' not 'indicator_type'
                "measurement_unit": "people",  # Use correct field name 'measurement_unit' not 'unit_of_measurement'
                "baseline_value": 0.0,
                "target_value": 5000.0,
                "frequency": "monthly",
                "responsible_person": self.user_data["id"],  # Use correct field name 'responsible_person' not 'responsible_user_id'
                "data_source": "Training completion records and certificates",
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
        if not hasattr(self, 'project_id'):
            self.log_result("Create Beneficiary", False, "No project ID available from previous test")
            return False
        
        try:
            from datetime import datetime, timedelta
            
            beneficiary_data = {
                "project_id": self.project_id,  # Required field that was missing
                "unique_id": f"BEN-{uuid.uuid4().hex[:8].upper()}",
                "first_name": "Jean Baptiste",
                "last_name": "Nzeyimana",
                "date_of_birth": (datetime.now() - timedelta(days=365*28)).isoformat(),  # 28 years old
                "gender": "Male",
                "location": "Nyagatare District, Eastern Province",
                "contact_phone": "+250788456789",
                "household_size": 6,
                "education_level": "Secondary School",
                "employment_status": "Farmer"
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
    
    def test_budget_system_fixed(self):
        """Test FIXED Budget Tracking System - POST /api/budget with corrected created_by field implementation"""
        if not hasattr(self, 'project_id'):
            self.log_result("Budget System - Fixed Implementation", False, "No project ID available from previous test")
            return False
        
        try:
            # Test BudgetItemCreate model with correct fields: project_id, category, item_name, description, budgeted_amount, budget_period
            budget_data = {
                "project_id": self.project_id,
                "category": "supplies",  # CORRECTED: use valid enum value
                "item_name": "Digital Literacy Training Manuals and Resources",
                "description": "Comprehensive training materials including printed manuals, digital resources, and interactive learning tools for digital literacy program participants",
                "budgeted_amount": 800000.0,  # Realistic amount in RWF
                "budget_period": "6 months"
            }
            
            response = self.session.post(
                f"{self.base_url}/budget",
                json=budget_data
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle both 'id' and '_id' fields
                budget_id = data.get("id") or data.get("_id")
                if (budget_id and 
                    data.get("item_name") == budget_data["item_name"] and
                    data.get("category") == budget_data["category"] and
                    data.get("budgeted_amount") == budget_data["budgeted_amount"]):
                    
                    self.budget_item_id = budget_id
                    # Verify created_by field is populated (this was the bug)
                    if "created_by" in data and data["created_by"]:
                        self.log_result("Budget System - Fixed Implementation", True, 
                                      "Budget item created successfully with corrected created_by field implementation")
                        return True
                    else:
                        self.log_result("Budget System - Fixed Implementation", False, 
                                      "Budget item created but created_by field still missing or empty", data)
                        return False
                else:
                    self.log_result("Budget System - Fixed Implementation", False, "Budget item data mismatch", data)
                    return False
            else:
                # Check if this is the original error we were fixing
                if response.status_code == 500:
                    error_text = response.text
                    if "created_by" in error_text.lower():
                        self.log_result("Budget System - Fixed Implementation", False, 
                                      "CRITICAL: Original created_by field bug still present - fix not working", error_text)
                        return False
                
                self.log_result("Budget System - Fixed Implementation", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Budget System - Fixed Implementation", False, f"Request error: {str(e)}")
            return False

    def test_budget_listing_fixed(self):
        """Test FIXED Budget Listing - GET /api/budget for budget item listing"""
        try:
            response = self.session.get(f"{self.base_url}/budget")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Budget Listing - Fixed Implementation", True, 
                                  f"Budget items retrieved successfully - {len(data)} items found")
                    return True
                else:
                    self.log_result("Budget Listing - Fixed Implementation", False, "Response is not a list", data)
                    return False
            else:
                # Check if this is the original error we were fixing
                if response.status_code == 500:
                    error_text = response.text
                    if "created_by" in error_text.lower():
                        self.log_result("Budget Listing - Fixed Implementation", False, 
                                      "CRITICAL: Original created_by field bug still affecting budget listing - fix not working", error_text)
                        return False
                
                self.log_result("Budget Listing - Fixed Implementation", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Budget Listing - Fixed Implementation", False, f"Request error: {str(e)}")
            return False

    def test_budget_summary_fixed(self):
        """Test FIXED Budget Summary - GET /api/budget/summary for budget tracking functionality"""
        try:
            response = self.session.get(f"{self.base_url}/budget/summary")
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    summary_data = data["data"]
                    # Check for expected budget summary fields
                    expected_fields = ["total_budgeted", "total_spent", "utilization_rate"]
                    
                    if any(field in summary_data for field in expected_fields):
                        self.log_result("Budget Summary - Fixed Implementation", True, 
                                      "Budget summary retrieved successfully with utilization rates")
                        return True
                    else:
                        self.log_result("Budget Summary - Fixed Implementation", False, 
                                      f"Budget summary missing expected fields: {expected_fields}", data)
                        return False
                else:
                    self.log_result("Budget Summary - Fixed Implementation", False, "Missing success/data fields in response", data)
                    return False
            else:
                self.log_result("Budget Summary - Fixed Implementation", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Budget Summary - Fixed Implementation", False, f"Request error: {str(e)}")
            return False

    def test_beneficiary_system_fixed(self):
        """Test FIXED Beneficiary System - POST /api/beneficiaries with updated BeneficiaryCreate model fields"""
        if not hasattr(self, 'project_id'):
            self.log_result("Beneficiary System - Fixed Implementation", False, "No project ID available from previous test")
            return False
        
        try:
            # Test BeneficiaryCreate model with corrected fields: project_id, unique_id, name (single field), gender (enum), beneficiary_type, enrollment_date
            beneficiary_data = {
                "project_id": self.project_id,
                "unique_id": f"BEN-{uuid.uuid4().hex[:12].upper()}",
                "name": "Jean Baptiste Nzeyimana",  # CORRECTED: single name field (not first_name/last_name)
                "age": 28,
                "gender": "male",  # CORRECTED: proper enum usage
                "location": "Nyagatare District, Eastern Province",
                "occupation": "Farmer",
                "beneficiary_type": "direct",  # CORRECTED: required field added
                "enrollment_date": "2024-01-15"  # CORRECTED: required field added
            }
            
            response = self.session.post(
                f"{self.base_url}/beneficiaries",
                json=beneficiary_data
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle both 'id' and '_id' fields
                beneficiary_id = data.get("id") or data.get("_id")
                if (beneficiary_id and 
                    data.get("name") == beneficiary_data["name"] and  # Check single name field
                    data.get("unique_id") == beneficiary_data["unique_id"] and
                    data.get("gender") == beneficiary_data["gender"] and
                    data.get("beneficiary_type") == beneficiary_data["beneficiary_type"]):
                    
                    self.beneficiary_id = beneficiary_id
                    self.log_result("Beneficiary System - Fixed Implementation", True, 
                                  "Beneficiary created successfully with corrected model fields (single name, proper enum, required fields)")
                    return True
                else:
                    self.log_result("Beneficiary System - Fixed Implementation", False, "Beneficiary data mismatch", data)
                    return False
            else:
                # Check if this is the original model mismatch error we were fixing
                if response.status_code == 400:
                    error_text = response.text
                    if ("first_name" in error_text.lower() or "last_name" in error_text.lower() or 
                        "beneficiary_type" in error_text.lower() or "enrollment_date" in error_text.lower()):
                        self.log_result("Beneficiary System - Fixed Implementation", False, 
                                      "CRITICAL: Original model mismatch bug still present - fix not working", error_text)
                        return False
                elif response.status_code == 500:
                    error_text = response.text
                    if "model" in error_text.lower():
                        self.log_result("Beneficiary System - Fixed Implementation", False, 
                                      "CRITICAL: Model mismatch causing server error - fix not working", error_text)
                        return False
                
                self.log_result("Beneficiary System - Fixed Implementation", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Beneficiary System - Fixed Implementation", False, f"Request error: {str(e)}")
            return False

    def test_beneficiary_listing_fixed(self):
        """Test FIXED Beneficiary Listing - GET /api/beneficiaries for beneficiary listing"""
        try:
            response = self.session.get(f"{self.base_url}/beneficiaries")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Beneficiary Listing - Fixed Implementation", True, 
                                  f"Beneficiaries retrieved successfully - {len(data)} beneficiaries found")
                    return True
                else:
                    self.log_result("Beneficiary Listing - Fixed Implementation", False, "Response is not a list", data)
                    return False
            else:
                # Check if this is the original model error we were fixing
                if response.status_code == 500:
                    error_text = response.text
                    if "model" in error_text.lower():
                        self.log_result("Beneficiary Listing - Fixed Implementation", False, 
                                      "CRITICAL: Original model mismatch bug still affecting beneficiary listing - fix not working", error_text)
                        return False
                
                self.log_result("Beneficiary Listing - Fixed Implementation", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Beneficiary Listing - Fixed Implementation", False, f"Request error: {str(e)}")
            return False

    def test_integration_dashboard_data(self):
        """Test Integration - Verify budget items and beneficiaries appear in project dashboard data"""
        try:
            response = self.session.get(f"{self.base_url}/projects/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    dashboard_data = data["data"]
                    
                    # Check if budget utilization is working (indicates budget items are being processed)
                    budget_utilization = dashboard_data.get("budget_utilization", 0)
                    if isinstance(budget_utilization, (int, float)):
                        budget_integration_ok = True
                    else:
                        budget_integration_ok = False
                    
                    # Check if there are recent activities that might include beneficiary data
                    recent_activities = dashboard_data.get("recent_activities", [])
                    activities_integration_ok = isinstance(recent_activities, list)
                    
                    # Check for budget_by_category data
                    budget_by_category = dashboard_data.get("budget_by_category", {})
                    budget_category_ok = isinstance(budget_by_category, dict)
                    
                    if budget_integration_ok and activities_integration_ok and budget_category_ok:
                        self.log_result("Integration - Dashboard Data", True, 
                                      "Budget and beneficiary data successfully integrated into project dashboard")
                        return True
                    else:
                        issues = []
                        if not budget_integration_ok:
                            issues.append("budget_utilization")
                        if not activities_integration_ok:
                            issues.append("recent_activities")
                        if not budget_category_ok:
                            issues.append("budget_by_category")
                        
                        self.log_result("Integration - Dashboard Data", False, 
                                      f"Dashboard integration issues with: {', '.join(issues)}", data)
                        return False
                else:
                    self.log_result("Integration - Dashboard Data", False, "Missing success/data fields in response", data)
                    return False
            else:
                self.log_result("Integration - Dashboard Data", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Integration - Dashboard Data", False, f"Request error: {str(e)}")
            return False

    def run_budget_beneficiary_fix_tests(self):
        """Run focused tests for FIXED budget and beneficiary endpoints"""
        print(f"🔧 Starting FIXED Budget and Beneficiary System Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Required setup tests
        setup_tests = [
            self.test_api_health,
            self.test_user_registration,
            self.test_user_login_valid,
            self.test_create_project,  # Need project for budget/beneficiary creation
        ]
        
        # Fixed system tests
        fix_tests = [
            self.test_budget_system_fixed,
            self.test_budget_listing_fixed,
            self.test_budget_summary_fixed,
            self.test_beneficiary_system_fixed,
            self.test_beneficiary_listing_fixed,
            self.test_integration_dashboard_data,
        ]
        
        print("🔧 Running setup tests...")
        for test in setup_tests:
            result = test()
            if not result and test == self.test_api_health:
                print("❌ API Health Check failed - stopping tests")
                return 0, 1
            elif not result and test == self.test_user_registration:
                print("❌ User Registration failed - stopping tests")
                return 0, 1
            print()
        
        print("\n🎯 Running FIXED budget and beneficiary tests...")
        print("=" * 60)
        for test in fix_tests:
            test()
            print()
        
        # Summary
        print("=" * 60)
        print("📊 BUDGET & BENEFICIARY FIX TEST SUMMARY")
        print("=" * 60)
        
        # Filter results for just the fix tests
        fix_test_names = [
            "Budget System - Fixed Implementation",
            "Budget Listing - Fixed Implementation", 
            "Budget Summary - Fixed Implementation",
            "Beneficiary System - Fixed Implementation",
            "Beneficiary Listing - Fixed Implementation",
            "Integration - Dashboard Data"
        ]
        
        fix_results = [r for r in self.test_results if r['test'] in fix_test_names]
        
        passed = sum(1 for result in fix_results if result['success'])
        failed = len(fix_results) - passed
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/len(fix_results)*100):.1f}%")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in fix_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
        
        return passed, failed

    def test_enhanced_project_dashboard_analytics(self):
        """Test enhanced project dashboard analytics endpoint with new analytics fields"""
        try:
            response = self.session.get(f"{self.base_url}/projects/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    dashboard_data = data["data"]
                    
                    # Verify all original required dashboard fields are present
                    original_fields = [
                        "total_projects", "active_projects", "completed_projects", 
                        "overdue_activities", "budget_utilization", "kpi_performance", 
                        "recent_activities", "projects_by_status", "budget_by_category"
                    ]
                    
                    # Verify all NEW enhanced analytics fields are present
                    new_analytics_fields = [
                        "activity_insights", "performance_trends", 
                        "risk_indicators", "completion_analytics"
                    ]
                    
                    all_required_fields = original_fields + new_analytics_fields
                    missing_fields = [field for field in all_required_fields if field not in dashboard_data]
                    
                    if missing_fields:
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      f"Missing required fields: {missing_fields}", data)
                        return False
                    
                    # Verify structure and data types of each NEW analytics section
                    
                    # 1. Activity Insights validation
                    activity_insights = dashboard_data.get("activity_insights", {})
                    if not isinstance(activity_insights, dict):
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      f"activity_insights should be dict, got {type(activity_insights)}", data)
                        return False
                    
                    expected_activity_fields = ["activity_status_breakdown", "completion_trend_weekly", 
                                              "avg_completion_days", "total_activities"]
                    for field in expected_activity_fields:
                        if field not in activity_insights:
                            self.log_result("Enhanced Project Dashboard Analytics", False, 
                                          f"activity_insights missing field: {field}", data)
                            return False
                    
                    # 2. Performance Trends validation
                    performance_trends = dashboard_data.get("performance_trends", {})
                    if not isinstance(performance_trends, dict):
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      f"performance_trends should be dict, got {type(performance_trends)}", data)
                        return False
                    
                    expected_performance_fields = ["budget_trend_monthly", "kpi_trend_monthly"]
                    for field in expected_performance_fields:
                        if field not in performance_trends:
                            self.log_result("Enhanced Project Dashboard Analytics", False, 
                                          f"performance_trends missing field: {field}", data)
                            return False
                    
                    # Verify budget_trend_monthly is a list
                    if not isinstance(performance_trends["budget_trend_monthly"], list):
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      "budget_trend_monthly should be a list", data)
                        return False
                    
                    # 3. Risk Indicators validation
                    risk_indicators = dashboard_data.get("risk_indicators", {})
                    if not isinstance(risk_indicators, dict):
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      f"risk_indicators should be dict, got {type(risk_indicators)}", data)
                        return False
                    
                    expected_risk_fields = ["budget_risk", "timeline_risk", "performance_risk"]
                    for field in expected_risk_fields:
                        if field not in risk_indicators:
                            self.log_result("Enhanced Project Dashboard Analytics", False, 
                                          f"risk_indicators missing field: {field}", data)
                            return False
                    
                    # Verify each risk indicator has proper structure
                    for risk_type in expected_risk_fields:
                        risk_data = risk_indicators[risk_type]
                        if not isinstance(risk_data, dict):
                            self.log_result("Enhanced Project Dashboard Analytics", False, 
                                          f"{risk_type} should be dict", data)
                            return False
                        
                        # Each risk indicator should have threshold and description
                        if "threshold" not in risk_data or "description" not in risk_data:
                            self.log_result("Enhanced Project Dashboard Analytics", False, 
                                          f"{risk_type} missing threshold or description", data)
                            return False
                    
                    # 4. Completion Analytics validation
                    completion_analytics = dashboard_data.get("completion_analytics", {})
                    if not isinstance(completion_analytics, dict):
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      f"completion_analytics should be dict, got {type(completion_analytics)}", data)
                        return False
                    
                    expected_completion_fields = ["project_success_rate", "on_time_completion_rate", 
                                                "avg_planned_duration_days", "avg_actual_duration_days",
                                                "avg_schedule_variance_days", "total_completed_projects", 
                                                "total_closed_projects"]
                    for field in expected_completion_fields:
                        if field not in completion_analytics:
                            self.log_result("Enhanced Project Dashboard Analytics", False, 
                                          f"completion_analytics missing field: {field}", data)
                            return False
                    
                    # Verify numeric fields are actually numeric
                    numeric_fields = ["project_success_rate", "on_time_completion_rate", 
                                    "avg_planned_duration_days", "avg_actual_duration_days", 
                                    "avg_schedule_variance_days"]
                    for field in numeric_fields:
                        value = completion_analytics[field]
                        if not isinstance(value, (int, float)):
                            self.log_result("Enhanced Project Dashboard Analytics", False, 
                                          f"completion_analytics.{field} should be numeric, got {type(value)}", data)
                            return False
                    
                    # Verify datetime operations work correctly (check recent_activities timestamps)
                    recent_activities = dashboard_data.get("recent_activities", [])
                    if isinstance(recent_activities, list):
                        for activity in recent_activities:
                            if "updated_at" in activity:
                                try:
                                    # Verify the datetime string is valid ISO format
                                    datetime.fromisoformat(activity["updated_at"].replace('Z', '+00:00'))
                                except ValueError:
                                    self.log_result("Enhanced Project Dashboard Analytics", False, 
                                                  f"Invalid datetime format in recent_activities: {activity['updated_at']}", data)
                                    return False
                    
                    # Verify all analytics calculations completed without errors
                    self.log_result("Enhanced Project Dashboard Analytics", True, 
                                  "Enhanced dashboard analytics working correctly - all 4 new analytics sections present with proper structure and data types")
                    return True
                else:
                    self.log_result("Enhanced Project Dashboard Analytics", False, 
                                  "Missing success/data fields in response", data)
                    return False
            else:
                # Check specifically for analytics calculation errors
                if response.status_code == 500:
                    error_text = response.text
                    if "activity_insights" in error_text or "performance_trends" in error_text or \
                       "risk_indicators" in error_text or "completion_analytics" in error_text:
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      "CRITICAL: Error in new analytics calculation methods", error_text)
                        return False
                
                self.log_result("Enhanced Project Dashboard Analytics", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Enhanced Project Dashboard Analytics", False, f"Request error: {str(e)}")
            return False

    def test_enhanced_activity_creation_endpoints(self):
        """Test enhanced activity creation endpoints as per CreateActivityModal refactor"""
        print("\n" + "="*60)
        print("TESTING ENHANCED ACTIVITY CREATION ENDPOINTS")
        print("="*60)
        
        # Test 1: GET /api/users - ensure it returns user list with id,name,email for assigned person dropdown
        self.test_get_users_for_dropdown()
        
        # Test 2: POST /api/projects - create a minimal project to link activities
        self.test_create_minimal_project_for_activities()
        
        # Test 3: POST /api/activities - create activity with enhanced fields
        self.test_create_enhanced_activity()
        
        # Test 4: GET /api/activities - ensure activity appears and fields serialize correctly
        self.test_get_activities_enhanced()
        
        # Test 5: PUT /api/activities/{activity_id}/progress - update progress
        self.test_update_activity_progress()
        
        # Test 6: GET /api/activities/{activity_id}/variance - returns variance analysis
        self.test_get_activity_variance_analysis()

    def test_get_users_for_dropdown(self):
        """Test GET /api/users for assigned person dropdown"""
        try:
            response = self.session.get(f"{self.base_url}/users")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Verify required fields for dropdown
                    user = data[0]
                    required_fields = ["id", "name", "email"]
                    missing_fields = [field for field in required_fields if field not in user]
                    
                    if not missing_fields:
                        self.log_result("GET /api/users for dropdown", True, 
                                      f"Retrieved {len(data)} users with required fields (id, name, email)")
                        return True
                    else:
                        self.log_result("GET /api/users for dropdown", False, 
                                      f"Missing required fields: {missing_fields}", data)
                        return False
                else:
                    self.log_result("GET /api/users for dropdown", False, 
                                  "No users found or invalid response", data)
                    return False
            else:
                self.log_result("GET /api/users for dropdown", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("GET /api/users for dropdown", False, f"Request error: {str(e)}")
            return False

    def test_create_minimal_project_for_activities(self):
        """Test creating a minimal project to link activities"""
        try:
            from datetime import datetime, timedelta
            
            project_data = {
                "name": f"Enhanced Activity Test Project {uuid.uuid4().hex[:8]}",
                "description": "Minimal project for testing enhanced activity creation",
                "project_manager_id": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
                "budget_total": 1000000.0,  # 1M RWF
                "beneficiaries_target": 100
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data
            )
            
            if response.status_code == 200:
                data = response.json()
                project_id = data.get("id") or data.get("_id")
                if project_id and data.get("name") == project_data["name"]:
                    self.enhanced_project_id = project_id
                    self.log_result("Create minimal project for activities", True, 
                                  "Minimal project created successfully for activity testing")
                    return True
                else:
                    self.log_result("Create minimal project for activities", False, 
                                  "Project data mismatch", data)
                    return False
            else:
                self.log_result("Create minimal project for activities", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create minimal project for activities", False, f"Request error: {str(e)}")
            return False

    def test_create_enhanced_activity(self):
        """Test creating activity with enhanced fields including milestones, planned/actual outputs"""
        if not hasattr(self, 'enhanced_project_id'):
            self.log_result("Create enhanced activity", False, "No project ID available from previous test")
            return False
        
        try:
            from datetime import datetime, timedelta
            
            # Enhanced activity data with all new fields
            activity_data = {
                "project_id": self.enhanced_project_id,
                "name": f"Enhanced Digital Training Workshop {uuid.uuid4().hex[:8]}",
                "description": "Comprehensive digital literacy training workshop with milestone tracking and output measurement",
                "assigned_to": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=21)).isoformat(),
                "budget_allocated": 250000.0,  # 250K RWF
                
                # Enhanced output tracking
                "planned_output": "50 participants trained in basic digital skills with certification",
                "target_quantity": 50.0,
                
                # Milestones array with name and planned_date
                "milestones": [
                    {
                        "name": "Training materials preparation completed",
                        "planned_date": (datetime.now() + timedelta(days=5)).isoformat(),
                        "description": "All training materials, handouts, and digital resources prepared"
                    },
                    {
                        "name": "Participant registration completed",
                        "planned_date": (datetime.now() + timedelta(days=10)).isoformat(),
                        "description": "50 participants registered and confirmed for training"
                    },
                    {
                        "name": "Training sessions completed",
                        "planned_date": (datetime.now() + timedelta(days=18)).isoformat(),
                        "description": "All 5 training sessions conducted successfully"
                    },
                    {
                        "name": "Certification and evaluation completed",
                        "planned_date": (datetime.now() + timedelta(days=21)).isoformat(),
                        "description": "Participants assessed and certificates issued"
                    }
                ],
                
                # Initial actual output and achieved quantity (can be set at creation)
                "actual_output": "Training preparation phase initiated with 80% materials ready",
                "achieved_quantity": 0.0,  # No participants trained yet
                
                # Status and risk tracking
                "status_notes": "Activity created with comprehensive milestone tracking and output measurement",
                "risk_level": "low",
                
                # Legacy fields for compatibility
                "deliverables": [
                    "Training curriculum and materials",
                    "Participant certificates",
                    "Training completion report",
                    "Skills assessment results"
                ],
                "dependencies": [
                    "Venue booking confirmation",
                    "Equipment setup completion"
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/activities",
                json=activity_data
            )
            
            if response.status_code == 200:
                data = response.json()
                activity_id = data.get("id") or data.get("_id")
                
                # Verify enhanced fields are present and correctly set
                validation_checks = [
                    (data.get("name") == activity_data["name"], "Activity name matches"),
                    (data.get("organization_id") is not None, "Organization ID is set"),
                    (data.get("planned_start_date") is not None, "Planned start date fallback set"),
                    (data.get("planned_end_date") is not None, "Planned end date fallback set"),
                    (data.get("progress_percentage") == 0.0, "Progress percentage default set to 0"),
                    (data.get("last_updated_by") == self.user_data["id"], "Last updated by auto-stamped"),
                    (data.get("completion_variance") == 0.0, "Completion variance default set"),
                    (data.get("schedule_variance_days") == 0, "Schedule variance default set"),
                    (isinstance(data.get("milestones", []), list), "Milestones array present"),
                    (len(data.get("milestones", [])) == 4, "All 4 milestones saved"),
                    (data.get("planned_output") == activity_data["planned_output"], "Planned output saved"),
                    (data.get("target_quantity") == activity_data["target_quantity"], "Target quantity saved"),
                    (data.get("actual_output") == activity_data["actual_output"], "Actual output saved"),
                    (data.get("achieved_quantity") == activity_data["achieved_quantity"], "Achieved quantity saved")
                ]
                
                failed_checks = [check[1] for check in validation_checks if not check[0]]
                
                if activity_id and not failed_checks:
                    self.enhanced_activity_id = activity_id
                    self.log_result("Create enhanced activity", True, 
                                  "Enhanced activity created successfully with all required fields: milestones, planned/actual outputs, auto-stamped creator, planned dates fallback, progress defaults")
                    return True
                else:
                    self.log_result("Create enhanced activity", False, 
                                  f"Validation failed: {failed_checks}", data)
                    return False
            else:
                self.log_result("Create enhanced activity", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create enhanced activity", False, f"Request error: {str(e)}")
            return False

    def test_get_activities_enhanced(self):
        """Test GET /api/activities to ensure enhanced activity appears with correct field serialization"""
        try:
            response = self.session.get(f"{self.base_url}/activities")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Find our enhanced activity
                    enhanced_activity = None
                    if hasattr(self, 'enhanced_activity_id'):
                        enhanced_activity = next((act for act in data if act.get("id") == self.enhanced_activity_id or act.get("_id") == self.enhanced_activity_id), None)
                    
                    if enhanced_activity:
                        # Verify field serialization (strings for IDs/dates as ISO)
                        serialization_checks = [
                            (isinstance(enhanced_activity.get("id") or enhanced_activity.get("_id"), str), "Activity ID serialized as string"),
                            (isinstance(enhanced_activity.get("organization_id"), str), "Organization ID serialized as string"),
                            (isinstance(enhanced_activity.get("project_id"), str), "Project ID serialized as string"),
                            (isinstance(enhanced_activity.get("assigned_to"), str), "Assigned to ID serialized as string"),
                            (isinstance(enhanced_activity.get("last_updated_by"), str), "Last updated by ID serialized as string"),
                            ("T" in str(enhanced_activity.get("start_date", "")), "Start date in ISO format"),
                            ("T" in str(enhanced_activity.get("end_date", "")), "End date in ISO format"),
                            ("T" in str(enhanced_activity.get("planned_start_date", "")), "Planned start date in ISO format"),
                            ("T" in str(enhanced_activity.get("planned_end_date", "")), "Planned end date in ISO format"),
                            ("T" in str(enhanced_activity.get("created_at", "")), "Created at in ISO format"),
                            ("T" in str(enhanced_activity.get("updated_at", "")), "Updated at in ISO format"),
                            (isinstance(enhanced_activity.get("milestones", []), list), "Milestones serialized as array"),
                            (isinstance(enhanced_activity.get("progress_percentage"), (int, float)), "Progress percentage as number"),
                            (isinstance(enhanced_activity.get("target_quantity"), (int, float)), "Target quantity as number"),
                            (isinstance(enhanced_activity.get("achieved_quantity"), (int, float)), "Achieved quantity as number")
                        ]
                        
                        failed_serialization = [check[1] for check in serialization_checks if not check[0]]
                        
                        if not failed_serialization:
                            self.log_result("GET /api/activities enhanced serialization", True, 
                                          f"Enhanced activity appears correctly with proper field serialization (strings for IDs, ISO dates, proper data types)")
                            return True
                        else:
                            self.log_result("GET /api/activities enhanced serialization", False, 
                                          f"Serialization issues: {failed_serialization}", enhanced_activity)
                            return False
                    else:
                        self.log_result("GET /api/activities enhanced serialization", False, 
                                      "Enhanced activity not found in activities list", data)
                        return False
                else:
                    self.log_result("GET /api/activities enhanced serialization", False, 
                                  "No activities found or invalid response", data)
                    return False
            else:
                self.log_result("GET /api/activities enhanced serialization", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("GET /api/activities enhanced serialization", False, f"Request error: {str(e)}")
            return False

    def test_update_activity_progress(self):
        """Test PUT /api/activities/{activity_id}/progress with achieved_quantity and status_notes"""
        if not hasattr(self, 'enhanced_activity_id'):
            self.log_result("Update activity progress", False, "No enhanced activity ID available from previous test")
            return False
        
        try:
            # Progress update data
            progress_data = {
                "achieved_quantity": 25.0,  # 25 out of 50 participants trained (50% progress)
                "status_notes": "Training sessions 1-3 completed successfully. 25 participants have completed basic digital skills modules. On track for full completion.",
                "actual_output": "25 participants completed basic digital skills training with hands-on practice sessions",
                "milestone_completed": "Training materials preparation completed",  # Mark first milestone as completed
                "comments": "Excellent participant engagement. All participants showing good progress in basic computer operations."
            }
            
            response = self.session.put(
                f"{self.base_url}/activities/{self.enhanced_activity_id}/progress",
                json=progress_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    result_data = data.get("data", {})
                    
                    # Verify progress update results
                    progress_checks = [
                        (result_data.get("progress_percentage") == 50.0, "Progress percentage auto-calculated from achieved_quantity (25/50 = 50%)"),
                        (isinstance(result_data.get("completion_variance"), (int, float)), "Completion variance calculated"),
                        (isinstance(result_data.get("schedule_variance_days"), int), "Schedule variance days calculated"),
                        (result_data.get("risk_level") in ["low", "medium", "high"], "Risk level assessed"),
                        (result_data.get("status") in ["not_started", "in_progress", "completed", "delayed"], "Status updated based on progress")
                    ]
                    
                    failed_progress_checks = [check[1] for check in progress_checks if not check[0]]
                    
                    if not failed_progress_checks:
                        self.log_result("Update activity progress", True, 
                                      f"Activity progress updated successfully: {result_data.get('progress_percentage')}% complete, variance analysis calculated, status updated to '{result_data.get('status')}'")
                        return True
                    else:
                        self.log_result("Update activity progress", False, 
                                      f"Progress update validation failed: {failed_progress_checks}", data)
                        return False
                else:
                    self.log_result("Update activity progress", False, 
                                  "Success flag not set in response", data)
                    return False
            else:
                self.log_result("Update activity progress", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update activity progress", False, f"Request error: {str(e)}")
            return False

    def test_get_activity_variance_analysis(self):
        """Test GET /api/activities/{activity_id}/variance for variance analysis structure"""
        if not hasattr(self, 'enhanced_activity_id'):
            self.log_result("Get activity variance analysis", False, "No enhanced activity ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/activities/{self.enhanced_activity_id}/variance")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    variance_data = data.get("data", {})
                    
                    # Verify variance analysis structure
                    variance_structure_checks = [
                        ("schedule_variance" in variance_data, "Schedule variance analysis present"),
                        ("budget_variance" in variance_data, "Budget variance analysis present"),
                        ("output_variance" in variance_data, "Output variance analysis present"),
                        ("completion_variance" in variance_data, "Completion variance analysis present"),
                        ("risk_assessment" in variance_data, "Risk assessment present"),
                        ("milestone_analysis" in variance_data, "Milestone analysis present"),
                        ("performance_indicators" in variance_data, "Performance indicators present")
                    ]
                    
                    # Verify data types and structure
                    if variance_data:
                        data_type_checks = [
                            (isinstance(variance_data.get("schedule_variance", {}), dict), "Schedule variance is structured object"),
                            (isinstance(variance_data.get("budget_variance", {}), dict), "Budget variance is structured object"),
                            (isinstance(variance_data.get("output_variance", {}), dict), "Output variance is structured object"),
                            (isinstance(variance_data.get("risk_assessment"), str), "Risk assessment is string"),
                            (isinstance(variance_data.get("milestone_analysis", {}), dict), "Milestone analysis is structured object")
                        ]
                    else:
                        data_type_checks = [(False, "Variance data is empty")]
                    
                    all_checks = variance_structure_checks + data_type_checks
                    failed_variance_checks = [check[1] for check in all_checks if not check[0]]
                    
                    if not failed_variance_checks:
                        self.log_result("Get activity variance analysis", True, 
                                      "Variance analysis structure returned correctly with all required components: schedule, budget, output, completion variance, risk assessment, milestone analysis")
                        return True
                    else:
                        self.log_result("Get activity variance analysis", False, 
                                      f"Variance analysis structure issues: {failed_variance_checks}", data)
                        return False
                else:
                    self.log_result("Get activity variance analysis", False, 
                                  "Success flag not set in response", data)
                    return False
            else:
                self.log_result("Get activity variance analysis", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get activity variance analysis", False, f"Request error: {str(e)}")
            return False

    def test_enhanced_activity_edge_cases(self):
        """Test edge cases for enhanced activity creation"""
        if not hasattr(self, 'enhanced_project_id'):
            self.log_result("Enhanced activity edge cases", False, "No project ID available")
            return False
        
        try:
            from datetime import datetime, timedelta
            
            # Test 1: Activity with empty milestones array (should be accepted)
            activity_data_empty_milestones = {
                "project_id": self.enhanced_project_id,
                "name": f"Edge Case Activity - Empty Milestones {uuid.uuid4().hex[:8]}",
                "assigned_to": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=14)).isoformat(),
                "budget_allocated": 100000.0,
                "planned_output": "Test output with no milestones",
                "target_quantity": 10.0,
                "milestones": []  # Empty array should be accepted
            }
            
            response = self.session.post(
                f"{self.base_url}/activities",
                json=activity_data_empty_milestones
            )
            
            empty_milestones_success = response.status_code == 200
            
            # Test 2: Activity with milestone dates in ISO format parsing
            activity_data_iso_dates = {
                "project_id": self.enhanced_project_id,
                "name": f"Edge Case Activity - ISO Dates {uuid.uuid4().hex[:8]}",
                "assigned_to": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=16)).isoformat(),
                "budget_allocated": 150000.0,
                "planned_output": "Test output with ISO date milestones",
                "target_quantity": 15.0,
                "milestones": [
                    {
                        "name": "ISO Date Milestone",
                        "planned_date": (datetime.now() + timedelta(days=8)).isoformat()  # ISO format
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/activities",
                json=activity_data_iso_dates
            )
            
            iso_dates_success = response.status_code == 200
            
            # Verify no ObjectId serialization issues by checking response format
            if iso_dates_success:
                data = response.json()
                no_objectid_issues = (
                    isinstance(data.get("id") or data.get("_id"), str) and
                    not str(data.get("id", "")).startswith("ObjectId(") and
                    not str(data.get("_id", "")).startswith("ObjectId(")
                )
            else:
                no_objectid_issues = False
            
            # Summary of edge case tests
            edge_case_results = [
                (empty_milestones_success, "Empty milestones array accepted"),
                (iso_dates_success, "ISO date parsing in milestones working"),
                (no_objectid_issues, "No ObjectId serialization issues")
            ]
            
            failed_edge_cases = [check[1] for check in edge_case_results if not check[0]]
            
            if not failed_edge_cases:
                self.log_result("Enhanced activity edge cases", True, 
                              "All edge cases handled correctly: empty milestones accepted, ISO date parsing working, no ObjectId serialization issues")
                return True
            else:
                self.log_result("Enhanced activity edge cases", False, 
                              f"Edge case failures: {failed_edge_cases}")
                return False
                
        except Exception as e:
            self.log_result("Enhanced activity edge cases", False, f"Request error: {str(e)}")
            return False

    def run_enhanced_activity_tests_only(self):
        """Run only the enhanced activity creation tests"""
        print("=" * 80)
        print("TESTING ENHANCED ACTIVITY CREATION ENDPOINTS ONLY")
        print("=" * 80)
        
        # Required setup tests
        setup_tests = [
            self.test_api_health,
            self.test_user_registration,
            self.test_user_login_valid
        ]
        
        # Enhanced activity tests
        enhanced_tests = [
            self.test_enhanced_activity_creation_endpoints,
            self.test_enhanced_activity_edge_cases
        ]
        
        # Run setup
        for test in setup_tests:
            if not test():
                print("❌ Setup failed - stopping tests")
                return
        
        # Run enhanced activity tests
        for test in enhanced_tests:
            test()
            print()
        
        # Summary
        print("=" * 60)
        print("📊 ENHANCED ACTIVITY TEST SUMMARY")
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

    # ==================== FINANCE PHASE 1 TESTS ====================
    
    def test_finance_config_get_default(self):
        """Test GET /api/finance/config returns default config when not configured"""
        try:
            response = self.session.get(f"{self.base_url}/finance/config")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["organization_id", "funding_sources", "cost_centers", "updated_at"]
                
                if all(field in data for field in required_fields):
                    # Check default funding sources
                    default_sources = ["World Bank", "Mastercard Foundation", "USAID", "UNDP"]
                    if all(source in data["funding_sources"] for source in default_sources):
                        # Check default cost centers
                        default_centers = ["HR", "Operations", "Field Work", "M&E", "Project officers"]
                        if all(center in data["cost_centers"] for center in default_centers):
                            self.log_result("Finance Config - Get Default", True, 
                                          f"Default config returned with {len(data['funding_sources'])} funding sources and {len(data['cost_centers'])} cost centers")
                            return True
                        else:
                            self.log_result("Finance Config - Get Default", False, "Missing default cost centers", data)
                            return False
                    else:
                        self.log_result("Finance Config - Get Default", False, "Missing default funding sources", data)
                        return False
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("Finance Config - Get Default", False, f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("Finance Config - Get Default", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance Config - Get Default", False, f"Request error: {str(e)}")
            return False

    def test_finance_config_update_and_persist(self):
        """Test PUT /api/finance/config with custom config and verify persistence"""
        try:
            # Update config with custom values
            config_data = {
                "funding_sources": ["World Bank", "USAID"],
                "cost_centers": ["HR", "Field Work"]
            }
            
            response = self.session.put(
                f"{self.base_url}/finance/config",
                json=config_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("funding_sources") == config_data["funding_sources"] and 
                    data.get("cost_centers") == config_data["cost_centers"]):
                    
                    # Verify persistence by getting config again
                    get_response = self.session.get(f"{self.base_url}/finance/config")
                    if get_response.status_code == 200:
                        get_data = get_response.json()
                        if (get_data.get("funding_sources") == config_data["funding_sources"] and 
                            get_data.get("cost_centers") == config_data["cost_centers"]):
                            self.log_result("Finance Config - Update and Persist", True, 
                                          "Config updated and persisted successfully")
                            return True
                        else:
                            self.log_result("Finance Config - Update and Persist", False, 
                                          "Config not persisted correctly", get_data)
                            return False
                    else:
                        self.log_result("Finance Config - Update and Persist", False, 
                                      f"Failed to verify persistence: HTTP {get_response.status_code}")
                        return False
                else:
                    self.log_result("Finance Config - Update and Persist", False, "Config not updated correctly", data)
                    return False
            else:
                self.log_result("Finance Config - Update and Persist", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance Config - Update and Persist", False, f"Request error: {str(e)}")
            return False

    def test_create_simple_project_for_expenses(self):
        """Create a simple project for expense testing"""
        try:
            project_data = {
                "name": f"Finance Test Project {uuid.uuid4().hex[:8]}",
                "description": "Simple project for finance testing",
                "budget_total": 10000.0
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data
            )
            
            if response.status_code == 200:
                data = response.json()
                project_id = data.get("id") or data.get("_id")
                if project_id:
                    self.finance_project_id = project_id
                    self.log_result("Create Simple Project for Expenses", True, "Project created for expense testing")
                    return True
                else:
                    self.log_result("Create Simple Project for Expenses", False, "No project ID in response", data)
                    return False
            else:
                self.log_result("Create Simple Project for Expenses", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Simple Project for Expenses", False, f"Request error: {str(e)}")
            return False

    def test_create_expense(self):
        """Test POST /api/finance/expenses with valid expense data"""
        if not hasattr(self, 'finance_project_id'):
            self.log_result("Create Expense", False, "No project ID available for expense creation")
            return False
        
        try:
            from datetime import datetime
            
            expense_data = {
                "project_id": self.finance_project_id,
                "date": datetime.now().isoformat(),
                "amount": 1234.56,
                "currency": "USD",
                "vendor": "ABC Ltd",
                "funding_source": "World Bank",
                "cost_center": "Field Work",
                "invoice_no": f"INV-{uuid.uuid4().hex[:8]}",
                "notes": "Test expense for finance system validation"
            }
            
            response = self.session.post(
                f"{self.base_url}/finance/expenses",
                json=expense_data
            )
            
            if response.status_code == 200:
                data = response.json()
                expense_id = data.get("id")
                if (expense_id and 
                    data.get("amount") == expense_data["amount"] and
                    data.get("vendor") == expense_data["vendor"] and
                    data.get("funding_source") == expense_data["funding_source"]):
                    
                    self.expense_id = expense_id
                    self.log_result("Create Expense", True, 
                                  f"Expense created successfully: {expense_data['amount']} {expense_data['currency']} to {expense_data['vendor']}")
                    return True
                else:
                    self.log_result("Create Expense", False, "Expense data mismatch", data)
                    return False
            else:
                self.log_result("Create Expense", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Expense", False, f"Request error: {str(e)}")
            return False

    def test_list_expenses_with_pagination_and_filters(self):
        """Test GET /api/finance/expenses with filters and pagination"""
        try:
            # Test with vendor filter and pagination
            params = {
                "vendor": "ABC",  # Substring search
                "page": 1,
                "page_size": 1
            }
            
            response = self.session.get(
                f"{self.base_url}/finance/expenses",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["items", "total", "page", "page_size"]
                
                if all(field in data for field in required_fields):
                    items = data["items"]
                    if isinstance(items, list):
                        # Verify pagination
                        if data["page"] == 1 and data["page_size"] == 1:
                            # Verify filtering (if items exist)
                            if len(items) > 0:
                                item = items[0]
                                if "ABC" in item.get("vendor", ""):
                                    self.log_result("List Expenses - Pagination and Filters", True, 
                                                  f"Retrieved {len(items)} expenses with pagination (page 1, size 1) and vendor filter")
                                    return True
                                else:
                                    self.log_result("List Expenses - Pagination and Filters", False, 
                                                  "Vendor filter not working correctly", data)
                                    return False
                            else:
                                self.log_result("List Expenses - Pagination and Filters", True, 
                                              "Pagination working correctly (no matching expenses found)")
                                return True
                        else:
                            self.log_result("List Expenses - Pagination and Filters", False, 
                                          "Pagination parameters not respected", data)
                            return False
                    else:
                        self.log_result("List Expenses - Pagination and Filters", False, 
                                      "Items field is not a list", data)
                        return False
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("List Expenses - Pagination and Filters", False, 
                                  f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("List Expenses - Pagination and Filters", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("List Expenses - Pagination and Filters", False, f"Request error: {str(e)}")
            return False

    def test_update_expense(self):
        """Test PUT /api/finance/expenses/{id} to update expense"""
        if not hasattr(self, 'expense_id'):
            self.log_result("Update Expense", False, "No expense ID available for update")
            return False
        
        try:
            update_data = {
                "amount": 2000.00,
                "vendor": "XYZ Corporation",
                "notes": "Updated expense for testing"
            }
            
            response = self.session.put(
                f"{self.base_url}/finance/expenses/{self.expense_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("amount") == update_data["amount"] and
                    data.get("vendor") == update_data["vendor"] and
                    data.get("notes") == update_data["notes"]):
                    
                    self.log_result("Update Expense", True, 
                                  f"Expense updated successfully: amount changed to {update_data['amount']}, vendor to {update_data['vendor']}")
                    return True
                else:
                    self.log_result("Update Expense", False, "Expense not updated correctly", data)
                    return False
            else:
                self.log_result("Update Expense", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update Expense", False, f"Request error: {str(e)}")
            return False

    def test_delete_expense(self):
        """Test DELETE /api/finance/expenses/{id} to remove expense"""
        if not hasattr(self, 'expense_id'):
            self.log_result("Delete Expense", False, "No expense ID available for deletion")
            return False
        
        try:
            response = self.session.delete(f"{self.base_url}/finance/expenses/{self.expense_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Verify deletion by trying to get the expense
                    get_response = self.session.get(
                        f"{self.base_url}/finance/expenses",
                        params={"vendor": "XYZ Corporation"}
                    )
                    if get_response.status_code == 200:
                        get_data = get_response.json()
                        items = get_data.get("items", [])
                        # Check if the deleted expense is no longer in the list
                        deleted_expense_found = any(item.get("id") == self.expense_id for item in items)
                        if not deleted_expense_found:
                            self.log_result("Delete Expense", True, "Expense deleted and confirmed removed from list")
                            return True
                        else:
                            self.log_result("Delete Expense", False, "Expense still found in list after deletion")
                            return False
                    else:
                        self.log_result("Delete Expense", True, "Expense deletion successful (verification failed but deletion response was positive)")
                        return True
                else:
                    self.log_result("Delete Expense", False, "Success flag not set in response", data)
                    return False
            else:
                self.log_result("Delete Expense", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Delete Expense", False, f"Request error: {str(e)}")
            return False

    def test_analytics_burn_rate(self):
        """Test GET /api/finance/burn-rate analytics endpoint"""
        try:
            response = self.session.get(
                f"{self.base_url}/finance/burn-rate",
                params={"period": "monthly"}
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["period", "series"]
                
                if all(field in data for field in required_fields):
                    if data["period"] == "monthly" and isinstance(data["series"], list):
                        self.log_result("Analytics - Burn Rate", True, 
                                      f"Burn rate analytics returned with {len(data['series'])} data points for monthly period")
                        return True
                    else:
                        self.log_result("Analytics - Burn Rate", False, "Invalid burn rate data structure", data)
                        return False
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("Analytics - Burn Rate", False, f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("Analytics - Burn Rate", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Analytics - Burn Rate", False, f"Request error: {str(e)}")
            return False

    def test_analytics_variance(self):
        """Test GET /api/finance/variance analytics endpoint"""
        try:
            # Test without project_id (organization-wide)
            response = self.session.get(f"{self.base_url}/finance/variance")
            
            if response.status_code == 200:
                data = response.json()
                if "by_project" in data and isinstance(data["by_project"], list):
                    # Test with project_id if we have one
                    if hasattr(self, 'finance_project_id'):
                        project_response = self.session.get(
                            f"{self.base_url}/finance/variance",
                            params={"project_id": self.finance_project_id}
                        )
                        if project_response.status_code == 200:
                            project_data = project_response.json()
                            if "by_project" in project_data:
                                self.log_result("Analytics - Variance", True, 
                                              f"Variance analytics working for both organization-wide and project-specific queries")
                                return True
                            else:
                                self.log_result("Analytics - Variance", False, 
                                              "Project-specific variance missing by_project field", project_data)
                                return False
                        else:
                            self.log_result("Analytics - Variance", False, 
                                          f"Project-specific variance failed: HTTP {project_response.status_code}")
                            return False
                    else:
                        self.log_result("Analytics - Variance", True, 
                                      "Organization-wide variance analytics working correctly")
                        return True
                else:
                    self.log_result("Analytics - Variance", False, "Missing or invalid by_project field", data)
                    return False
            else:
                self.log_result("Analytics - Variance", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Analytics - Variance", False, f"Request error: {str(e)}")
            return False

    def test_analytics_forecast(self):
        """Test GET /api/finance/forecast analytics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/finance/forecast")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["avg_monthly", "projected_spend_rest_of_year", "months_remaining"]
                
                if all(field in data for field in required_fields):
                    # Verify data types
                    if (isinstance(data["avg_monthly"], (int, float)) and
                        isinstance(data["projected_spend_rest_of_year"], (int, float)) and
                        isinstance(data["months_remaining"], int)):
                        
                        self.log_result("Analytics - Forecast", True, 
                                      f"Forecast analytics: avg monthly ${data['avg_monthly']:.2f}, projected ${data['projected_spend_rest_of_year']:.2f} for {data['months_remaining']} months")
                        return True
                    else:
                        self.log_result("Analytics - Forecast", False, "Invalid data types in forecast", data)
                        return False
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("Analytics - Forecast", False, f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("Analytics - Forecast", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Analytics - Forecast", False, f"Request error: {str(e)}")
            return False

    def test_analytics_funding_utilization(self):
        """Test GET /api/finance/funding-utilization analytics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/finance/funding-utilization")
            
            if response.status_code == 200:
                data = response.json()
                if "by_funding_source" in data and isinstance(data["by_funding_source"], list):
                    funding_sources = data["by_funding_source"]
                    # Verify structure of funding source data
                    if len(funding_sources) == 0 or all("funding_source" in fs and "spent" in fs for fs in funding_sources):
                        self.log_result("Analytics - Funding Utilization", True, 
                                      f"Funding utilization analytics returned {len(funding_sources)} funding sources")
                        return True
                    else:
                        self.log_result("Analytics - Funding Utilization", False, 
                                      "Invalid funding source data structure", data)
                        return False
                else:
                    self.log_result("Analytics - Funding Utilization", False, 
                                  "Missing or invalid by_funding_source field", data)
                    return False
            else:
                self.log_result("Analytics - Funding Utilization", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Analytics - Funding Utilization", False, f"Request error: {str(e)}")
            return False

    def test_csv_import_stub(self):
        """Test POST /api/finance/expenses/import-csv stub endpoint"""
        try:
            # Create a simple CSV content
            csv_content = "Date,Vendor,Amount,Currency\n2024-01-01,Test Vendor,100.00,USD\n"
            
            # Create multipart form data
            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
            body_parts = []
            body_parts.append(f'--{boundary}')
            body_parts.append('Content-Disposition: form-data; name="file"; filename="expenses.csv"')
            body_parts.append('Content-Type: text/csv')
            body_parts.append('')
            body_parts.append(csv_content)
            body_parts.append(f'--{boundary}--')
            
            body = '\r\n'.join(body_parts)
            
            headers = {
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            }
            
            response = self.session.post(
                f"{self.base_url}/finance/expenses/import-csv",
                data=body.encode('utf-8'),
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["status", "processed"]
                
                if all(field in data for field in expected_fields):
                    if data["status"] == "received" and data["processed"] == 0:
                        self.log_result("CSV Import Stub", True, 
                                      "CSV import stub working correctly - received file and returned expected response")
                        return True
                    else:
                        self.log_result("CSV Import Stub", False, 
                                      f"Unexpected stub response values: status={data['status']}, processed={data['processed']}")
                        return False
                else:
                    missing_fields = [field for field in expected_fields if field not in data]
                    self.log_result("CSV Import Stub", False, f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("CSV Import Stub", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("CSV Import Stub", False, f"Request error: {str(e)}")
            return False

    def test_csv_export(self):
        """Test GET /api/finance/expenses/export-csv endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/finance/expenses/export-csv")
            
            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('content-type', '')
                if 'text/csv' in content_type:
                    # Check CSV content
                    csv_content = response.text
                    lines = csv_content.strip().split('\n')
                    if len(lines) > 0:
                        # Verify CSV headers
                        headers = lines[0].split(',')
                        expected_headers = ['Expense ID', 'Project ID', 'Activity ID', 'Date', 'Vendor', 
                                          'Invoice', 'Amount', 'Currency', 'Funding Source', 'Cost Center', 'Notes']
                        
                        # Check if all expected headers are present (allowing for variations in order)
                        headers_match = all(any(expected.lower() in header.lower() for header in headers) 
                                          for expected in expected_headers)
                        
                        if headers_match:
                            self.log_result("CSV Export", True, 
                                          f"CSV export working correctly - returned {len(lines)} lines with proper headers")
                            return True
                        else:
                            self.log_result("CSV Export", False, 
                                          f"CSV headers mismatch. Expected: {expected_headers}, Got: {headers}")
                            return False
                    else:
                        self.log_result("CSV Export", True, "CSV export working (empty data)")
                        return True
                else:
                    self.log_result("CSV Export", False, f"Wrong content type: {content_type}, expected text/csv")
                    return False
            else:
                self.log_result("CSV Export", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("CSV Export", False, f"Request error: {str(e)}")
            return False

    def test_ai_insights(self):
        """Test POST /api/finance/ai/insights endpoint"""
        try:
            insights_data = {
                "anomalies": [
                    {"id": "exp-1", "amount": 2000000, "description": "Unusually large expense"},
                    {"id": "exp-2", "amount": 500000, "description": "High vendor payment"}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/finance/ai/insights",
                json=insights_data
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["ai_used", "risk_level", "recommendations", "confidence"]
                
                if all(field in data for field in required_fields):
                    # Verify data types and values
                    if (isinstance(data["ai_used"], bool) and
                        data["risk_level"] in ["low", "medium", "high"] and
                        isinstance(data["recommendations"], list) and
                        isinstance(data["confidence"], (int, float)) and
                        0 <= data["confidence"] <= 1):
                        
                        self.log_result("AI Insights", True, 
                                      f"AI insights working: risk_level={data['risk_level']}, ai_used={data['ai_used']}, confidence={data['confidence']}")
                        return True
                    else:
                        self.log_result("AI Insights", False, "Invalid data types or values in AI insights response", data)
                        return False
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("AI Insights", False, f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("AI Insights", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("AI Insights", False, f"Request error: {str(e)}")
            return False

    # ==================== FINANCE CSV REPORTS TESTS ====================
    def test_finance_csv_reports_comprehensive(self):
        """Comprehensive test of the new finance CSV report endpoints"""
        print("\n" + "="*60)
        print("FINANCE CSV REPORTS COMPREHENSIVE TESTING")
        print("="*60)
        
        success_count = 0
        total_tests = 4
        
        # Test 1: Create seed data
        if self.create_finance_seed_data():
            success_count += 1
        
        # Test 2: Project report CSV
        if self.test_project_report_csv():
            success_count += 1
        
        # Test 3: Activities report CSV  
        if self.test_activities_report_csv():
            success_count += 1
        
        # Test 4: All projects CSV
        if self.test_all_projects_report_csv():
            success_count += 1
        
        print(f"\nFINANCE CSV REPORTS TESTING COMPLETE: {success_count}/{total_tests} tests passed")
        return success_count == total_tests
    
    def create_finance_seed_data(self):
        """Create minimal seed data for finance CSV testing"""
        try:
            # Create a project first
            from datetime import datetime, timedelta
            
            project_data = {
                "name": f"Finance CSV Test Project {uuid.uuid4().hex[:8]}",
                "description": "Test project for finance CSV reports with comprehensive budget tracking",
                "project_manager_id": self.user_data["id"] if self.user_data else "system",
                "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=180)).isoformat(),
                "budget_total": 2000000.0,  # 2M RWF
                "beneficiaries_target": 1500,
                "location": "Kigali, Rwanda",
                "donor_organization": "World Bank"
            }
            
            response = self.session.post(f"{self.base_url}/projects", json=project_data)
            
            if response.status_code == 200:
                project = response.json()
                self.test_project_id = project.get("id") or project.get("_id")
                
                # Create multiple budget items for better testing
                budget_items = [
                    {
                        "project_id": self.test_project_id,
                        "category": "training",
                        "item_name": "Training Materials and Resources",
                        "description": "Educational materials for finance training",
                        "budgeted_amount": 800000.0,  # 800K RWF
                        "budget_period": "6_months"
                    },
                    {
                        "project_id": self.test_project_id,
                        "category": "equipment",
                        "item_name": "Computer Equipment",
                        "description": "Laptops and tablets for training",
                        "budgeted_amount": 1200000.0,  # 1.2M RWF
                        "budget_period": "12_months"
                    }
                ]
                
                budget_success = 0
                for budget_data in budget_items:
                    budget_response = self.session.post(f"{self.base_url}/budget", json=budget_data)
                    if budget_response.status_code == 200:
                        budget_success += 1
                
                # Create multiple expenses for different activities
                expenses = [
                    {
                        "project_id": self.test_project_id,
                        "activity_id": f"activity_training_{uuid.uuid4().hex[:6]}",
                        "date": datetime.now().isoformat(),
                        "vendor": "Training Materials Supplier Ltd",
                        "invoice_no": f"INV-TRN-{uuid.uuid4().hex[:6].upper()}",
                        "amount": 350000.0,  # 350K RWF
                        "currency": "RWF",
                        "funding_source": "World Bank",
                        "cost_center": "Training",
                        "notes": "Purchase of training materials for finance project"
                    },
                    {
                        "project_id": self.test_project_id,
                        "activity_id": f"activity_equipment_{uuid.uuid4().hex[:6]}",
                        "date": (datetime.now() - timedelta(days=5)).isoformat(),
                        "vendor": "Tech Solutions Rwanda",
                        "invoice_no": f"INV-EQP-{uuid.uuid4().hex[:6].upper()}",
                        "amount": 600000.0,  # 600K RWF
                        "currency": "RWF",
                        "funding_source": "World Bank",
                        "cost_center": "Equipment",
                        "notes": "Purchase of laptops for training program"
                    },
                    {
                        "project_id": self.test_project_id,
                        "activity_id": f"activity_logistics_{uuid.uuid4().hex[:6]}",
                        "date": (datetime.now() - timedelta(days=10)).isoformat(),
                        "vendor": "Event Logistics Co",
                        "invoice_no": f"INV-LOG-{uuid.uuid4().hex[:6].upper()}",
                        "amount": 150000.0,  # 150K RWF
                        "currency": "RWF",
                        "funding_source": "USAID",
                        "cost_center": "Operations",
                        "notes": "Venue rental and logistics for training sessions"
                    }
                ]
                
                expense_success = 0
                for expense_data in expenses:
                    expense_response = self.session.post(f"{self.base_url}/finance/expenses", json=expense_data)
                    if expense_response.status_code == 200:
                        expense_success += 1
                
                if budget_success >= 1 and expense_success >= 2:
                    self.log_result("Create Finance Seed Data", True, 
                                  f"Created project with {budget_success} budget items and {expense_success} expenses for comprehensive CSV testing")
                    return True
                else:
                    self.log_result("Create Finance Seed Data", False, 
                                  f"Insufficient seed data created: budget_items={budget_success}, expenses={expense_success}")
                    return False
            else:
                self.log_result("Create Finance Seed Data", False, 
                              f"Failed to create project: HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Create Finance Seed Data", False, f"Request error: {str(e)}")
            return False
    
    def test_project_report_csv(self):
        """Test project report CSV endpoint - GET /api/finance/reports/project-csv"""
        if not hasattr(self, 'test_project_id'):
            self.log_result("Project Report CSV", False, "No test project ID available")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/finance/reports/project-csv",
                params={"project_id": self.test_project_id}
            )
            
            if response.status_code == 200:
                csv_content = response.text
                
                # Verify it's CSV format
                if response.headers.get('content-type') == 'text/csv':
                    # Check for expected headers
                    expected_headers = ["Project ID", "Planned", "Allocated", "Actual", "Variance Amount", "Variance %"]
                    lines = csv_content.strip().split('\n')
                    
                    if len(lines) > 0:
                        header_line = lines[0]
                        
                        # Check if all expected headers are present
                        headers_present = all(header in header_line for header in expected_headers)
                        
                        if headers_present:
                            # Check for funding source section (should be present for project-specific report)
                            has_funding_section = "Funding Source" in csv_content
                            
                            # Verify data rows exist
                            data_rows = [line for line in lines[1:] if line.strip() and not line.startswith("Funding Source")]
                            
                            self.log_result("Project Report CSV", True, 
                                          f"✅ CSV report generated successfully: {len(lines)} total lines, " +
                                          f"{len(data_rows)} data rows, proper headers verified" +
                                          (", includes funding source data" if has_funding_section else ""))
                            return True
                        else:
                            missing_headers = [h for h in expected_headers if h not in header_line]
                            self.log_result("Project Report CSV", False, 
                                          f"Missing expected headers: {missing_headers}")
                            return False
                    else:
                        self.log_result("Project Report CSV", False, "Empty CSV content")
                        return False
                else:
                    self.log_result("Project Report CSV", False, 
                                  f"Wrong content type: expected 'text/csv', got '{response.headers.get('content-type')}'")
                    return False
            else:
                self.log_result("Project Report CSV", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Project Report CSV", False, f"Request error: {str(e)}")
            return False
    
    def test_activities_report_csv(self):
        """Test activities report CSV endpoint - GET /api/finance/reports/activities-csv"""
        if not hasattr(self, 'test_project_id'):
            self.log_result("Activities Report CSV", False, "No test project ID available")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/finance/reports/activities-csv",
                params={"project_id": self.test_project_id}
            )
            
            if response.status_code == 200:
                csv_content = response.text
                
                # Verify it's CSV format
                if response.headers.get('content-type') == 'text/csv':
                    # Check for expected headers
                    expected_headers = ["Activity ID", "Transactions", "Spent"]
                    lines = csv_content.strip().split('\n')
                    
                    if len(lines) > 0:
                        header_line = lines[0]
                        
                        # Check if all expected headers are present
                        headers_present = all(header in header_line for header in expected_headers)
                        
                        if headers_present:
                            # Verify data rows exist (should have activity data from expenses)
                            data_rows = [line for line in lines[1:] if line.strip()]
                            
                            self.log_result("Activities Report CSV", True, 
                                          f"✅ CSV report generated successfully: {len(lines)} total lines, " +
                                          f"{len(data_rows)} activity data rows, proper headers verified")
                            return True
                        else:
                            missing_headers = [h for h in expected_headers if h not in header_line]
                            self.log_result("Activities Report CSV", False, 
                                          f"Missing expected headers: {missing_headers}")
                            return False
                    else:
                        self.log_result("Activities Report CSV", False, "Empty CSV content")
                        return False
                else:
                    self.log_result("Activities Report CSV", False, 
                                  f"Wrong content type: expected 'text/csv', got '{response.headers.get('content-type')}'")
                    return False
            else:
                self.log_result("Activities Report CSV", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Activities Report CSV", False, f"Request error: {str(e)}")
            return False
    
    def test_all_projects_report_csv(self):
        """Test all projects report CSV endpoint - GET /api/finance/reports/all-projects-csv"""
        try:
            response = self.session.get(f"{self.base_url}/finance/reports/all-projects-csv")
            
            if response.status_code == 200:
                csv_content = response.text
                
                # Verify it's CSV format
                if response.headers.get('content-type') == 'text/csv':
                    # Check for expected headers (same as project CSV but without funding rows)
                    expected_headers = ["Project ID", "Planned", "Allocated", "Actual", "Variance Amount", "Variance %"]
                    lines = csv_content.strip().split('\n')
                    
                    if len(lines) > 0:
                        header_line = lines[0]
                        
                        # Check if all expected headers are present
                        headers_present = all(header in header_line for header in expected_headers)
                        
                        if headers_present:
                            # Should NOT have funding source section (unlike project-specific report)
                            has_funding_section = "Funding Source" in csv_content
                            
                            # Verify data rows exist (should include our test project)
                            data_rows = [line for line in lines[1:] if line.strip()]
                            
                            self.log_result("All Projects Report CSV", True, 
                                          f"✅ CSV report generated successfully: {len(lines)} total lines, " +
                                          f"{len(data_rows)} project data rows, proper headers verified" +
                                          (", correctly excludes funding source data" if not has_funding_section else ", WARNING: includes funding data"))
                            return True
                        else:
                            missing_headers = [h for h in expected_headers if h not in header_line]
                            self.log_result("All Projects Report CSV", False, 
                                          f"Missing expected headers: {missing_headers}")
                            return False
                    else:
                        self.log_result("All Projects Report CSV", False, "Empty CSV content")
                        return False
                else:
                    self.log_result("All Projects Report CSV", False, 
                                  f"Wrong content type: expected 'text/csv', got '{response.headers.get('content-type')}'")
                    return False
            else:
                self.log_result("All Projects Report CSV", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("All Projects Report CSV", False, f"Request error: {str(e)}")
            return False

    # ==================== NEW FINANCE FEATURES TESTS ====================
    
    def test_finance_xlsx_project_report(self):
        """Test GET /api/finance/reports/project-xlsx endpoint"""
        if not hasattr(self, 'project_id'):
            self.log_result("Finance XLSX Project Report", False, "No project ID available")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/finance/reports/project-xlsx",
                params={"project_id": self.project_id}
            )
            
            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('content-type', '')
                expected_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                
                if expected_type in content_type:
                    # Check content is not empty
                    content_length = len(response.content)
                    if content_length > 0:
                        self.log_result("Finance XLSX Project Report", True, 
                                      f"XLSX report generated successfully ({content_length} bytes)")
                        return True
                    else:
                        self.log_result("Finance XLSX Project Report", False, "Empty XLSX content")
                        return False
                else:
                    self.log_result("Finance XLSX Project Report", False, 
                                  f"Wrong content type: {content_type}, expected: {expected_type}")
                    return False
            else:
                self.log_result("Finance XLSX Project Report", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance XLSX Project Report", False, f"Request error: {str(e)}")
            return False
    
    def test_finance_xlsx_activities_report(self):
        """Test GET /api/finance/reports/activities-xlsx endpoint"""
        if not hasattr(self, 'project_id'):
            self.log_result("Finance XLSX Activities Report", False, "No project ID available")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/finance/reports/activities-xlsx",
                params={"project_id": self.project_id}
            )
            
            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('content-type', '')
                expected_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                
                if expected_type in content_type:
                    # Check content is not empty
                    content_length = len(response.content)
                    if content_length > 0:
                        self.log_result("Finance XLSX Activities Report", True, 
                                      f"XLSX activities report generated successfully ({content_length} bytes)")
                        return True
                    else:
                        self.log_result("Finance XLSX Activities Report", False, "Empty XLSX content")
                        return False
                else:
                    self.log_result("Finance XLSX Activities Report", False, 
                                  f"Wrong content type: {content_type}, expected: {expected_type}")
                    return False
            else:
                self.log_result("Finance XLSX Activities Report", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance XLSX Activities Report", False, f"Request error: {str(e)}")
            return False
    
    def test_finance_xlsx_all_projects_report(self):
        """Test GET /api/finance/reports/all-projects-xlsx endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/finance/reports/all-projects-xlsx")
            
            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('content-type', '')
                expected_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                
                if expected_type in content_type:
                    # Check content is not empty
                    content_length = len(response.content)
                    if content_length > 0:
                        self.log_result("Finance XLSX All Projects Report", True, 
                                      f"XLSX all projects report generated successfully ({content_length} bytes)")
                        return True
                    else:
                        self.log_result("Finance XLSX All Projects Report", False, "Empty XLSX content")
                        return False
                else:
                    self.log_result("Finance XLSX All Projects Report", False, 
                                  f"Wrong content type: {content_type}, expected: {expected_type}")
                    return False
            else:
                self.log_result("Finance XLSX All Projects Report", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance XLSX All Projects Report", False, f"Request error: {str(e)}")
            return False
    
    def test_csv_date_range_filtering(self):
        """Test CSV endpoints with date_from and date_to parameters"""
        try:
            from datetime import datetime, timedelta
            
            # Create test expenses with different dates
            today = datetime.now()
            old_date = today - timedelta(days=60)
            recent_date = today - timedelta(days=10)
            
            # Create expense outside date range
            old_expense_data = {
                "project_id": getattr(self, 'project_id', 'test-project'),
                "activity_id": getattr(self, 'activity_id', 'test-activity'),
                "date": old_date.isoformat()[:10],
                "vendor": "Old Vendor Ltd",
                "invoice_no": f"OLD-{uuid.uuid4().hex[:8]}",
                "amount": 100000.0,
                "currency": "RWF",
                "funding_source": "World Bank",
                "cost_center": "Operations",
                "notes": "Old expense for date range testing"
            }
            
            # Create expense inside date range
            recent_expense_data = {
                "project_id": getattr(self, 'project_id', 'test-project'),
                "activity_id": getattr(self, 'activity_id', 'test-activity'),
                "date": recent_date.isoformat()[:10],
                "vendor": "Recent Vendor Ltd",
                "invoice_no": f"REC-{uuid.uuid4().hex[:8]}",
                "amount": 200000.0,
                "currency": "RWF",
                "funding_source": "USAID",
                "cost_center": "Field Work",
                "notes": "Recent expense for date range testing"
            }
            
            # Create both expenses
            old_response = self.session.post(f"{self.base_url}/finance/expenses", json=old_expense_data)
            recent_response = self.session.post(f"{self.base_url}/finance/expenses", json=recent_expense_data)
            
            if old_response.status_code != 200 or recent_response.status_code != 200:
                self.log_result("CSV Date Range Filtering", False, 
                              "Failed to create test expenses for date range testing")
                return False
            
            # Test CSV export without date filter (should include both)
            unfiltered_response = self.session.get(f"{self.base_url}/finance/expenses/export-csv")
            
            if unfiltered_response.status_code != 200:
                self.log_result("CSV Date Range Filtering", False, 
                              f"Unfiltered CSV export failed: {unfiltered_response.status_code}")
                return False
            
            unfiltered_csv = unfiltered_response.text
            unfiltered_lines = [line for line in unfiltered_csv.split('\n') if line.strip()]
            unfiltered_count = len(unfiltered_lines) - 1  # Subtract header
            
            # Test CSV export with date filter (should include only recent)
            date_from = (recent_date - timedelta(days=5)).isoformat()[:10]
            date_to = (recent_date + timedelta(days=5)).isoformat()[:10]
            
            filtered_response = self.session.get(
                f"{self.base_url}/finance/expenses/export-csv",
                params={"date_from": date_from, "date_to": date_to}
            )
            
            if filtered_response.status_code != 200:
                self.log_result("CSV Date Range Filtering", False, 
                              f"Filtered CSV export failed: {filtered_response.status_code}")
                return False
            
            filtered_csv = filtered_response.text
            filtered_lines = [line for line in filtered_csv.split('\n') if line.strip()]
            filtered_count = len(filtered_lines) - 1  # Subtract header
            
            # Verify filtering worked
            if filtered_count < unfiltered_count:
                # Check that recent expense is in filtered results
                if "Recent Vendor Ltd" in filtered_csv:
                    self.log_result("CSV Date Range Filtering", True, 
                                  f"Date range filtering working: unfiltered={unfiltered_count}, filtered={filtered_count}")
                    return True
                else:
                    self.log_result("CSV Date Range Filtering", False, 
                                  "Recent expense not found in filtered results")
                    return False
            else:
                self.log_result("CSV Date Range Filtering", False, 
                              f"Date filtering not working: unfiltered={unfiltered_count}, filtered={filtered_count}")
                return False
                
        except Exception as e:
            self.log_result("CSV Date Range Filtering", False, f"Request error: {str(e)}")
            return False
    
    def test_funding_utilization_date_range(self):
        """Test GET /api/finance/funding-utilization with date_from and date_to parameters"""
        try:
            from datetime import datetime, timedelta
            
            today = datetime.now()
            date_from = (today - timedelta(days=30)).isoformat()[:10]
            date_to = today.isoformat()[:10]
            
            # Test funding utilization without date filter
            unfiltered_response = self.session.get(f"{self.base_url}/finance/funding-utilization")
            
            if unfiltered_response.status_code != 200:
                self.log_result("Funding Utilization Date Range", False, 
                              f"Unfiltered funding utilization failed: {unfiltered_response.status_code}")
                return False
            
            unfiltered_data = unfiltered_response.json()
            
            # Test funding utilization with date filter
            filtered_response = self.session.get(
                f"{self.base_url}/finance/funding-utilization",
                params={"date_from": date_from, "date_to": date_to}
            )
            
            if filtered_response.status_code != 200:
                self.log_result("Funding Utilization Date Range", False, 
                              f"Filtered funding utilization failed: {filtered_response.status_code}")
                return False
            
            filtered_data = filtered_response.json()
            
            # Verify both responses have the expected structure
            required_fields = ["total_funding", "total_utilized", "utilization_rate", "by_source"]
            
            for field in required_fields:
                if field not in unfiltered_data:
                    self.log_result("Funding Utilization Date Range", False, 
                                  f"Missing field '{field}' in unfiltered response")
                    return False
                if field not in filtered_data:
                    self.log_result("Funding Utilization Date Range", False, 
                                  f"Missing field '{field}' in filtered response")
                    return False
            
            # Check if filtering affects the results (amounts should be different if there's data outside the range)
            unfiltered_total = unfiltered_data.get("total_utilized", 0)
            filtered_total = filtered_data.get("total_utilized", 0)
            
            # If we have expenses outside the date range, filtered should be less than or equal to unfiltered
            if filtered_total <= unfiltered_total:
                self.log_result("Funding Utilization Date Range", True, 
                              f"Date range filtering working: unfiltered_total={unfiltered_total}, filtered_total={filtered_total}")
                return True
            else:
                self.log_result("Funding Utilization Date Range", False, 
                              f"Date filtering issue: filtered_total ({filtered_total}) > unfiltered_total ({unfiltered_total})")
                return False
                
        except Exception as e:
            self.log_result("Funding Utilization Date Range", False, f"Request error: {str(e)}")
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
            # Project Management System Tests - PRIORITY: DateTime Bug Fix Test
            self.test_project_dashboard_datetime_bug_fix,
            self.test_project_dashboard,
            self.test_dashboard_pydantic_validation_fix,  # NEW: Test Pydantic validation fix
            self.test_enhanced_project_dashboard_analytics,  # NEW: Test enhanced analytics
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
            # PRIORITY: FIXED Budget and Beneficiary System Tests
            self.test_budget_system_fixed,
            self.test_budget_listing_fixed,
            self.test_budget_summary_fixed,
            self.test_beneficiary_system_fixed,
            self.test_beneficiary_listing_fixed,
            self.test_integration_dashboard_data,
            # Original Budget Management tests (for comparison)
            self.test_create_budget_item,
            self.test_get_budget_items,
            self.test_get_budget_summary,
            self.test_create_kpi_indicator,
            self.test_get_kpi_indicators,
            self.test_update_kpi_value,
            # Original Beneficiary Management tests (for comparison)
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
            # ENHANCED ACTIVITY CREATION TESTING (NEW - PRIORITY)
            self.test_enhanced_activity_creation_endpoints,
            self.test_enhanced_activity_edge_cases,
            self.test_delete_project,
            # FINANCE PHASE 1 TESTS (NEW - PRIORITY)
            self.test_finance_config_get_default,
            self.test_finance_config_update_and_persist,
            self.test_create_simple_project_for_expenses,
            self.test_create_expense,
            self.test_list_expenses_with_pagination_and_filters,
            self.test_update_expense,
            self.test_delete_expense,
            self.test_analytics_burn_rate,
            self.test_analytics_variance,
            self.test_analytics_forecast,
            self.test_analytics_funding_utilization,
            self.test_csv_import_stub,
            self.test_csv_export,
            self.test_ai_insights,
            # FINANCE CSV REPORTS TESTS (NEW - PRIORITY)
            self.test_finance_csv_reports_comprehensive,
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