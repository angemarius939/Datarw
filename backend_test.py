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

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://data-collector-15.preview.emergentagent.com')
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
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "DataRW API is running" in data.get("message", ""):
                    self.log_result("API Health Check", True, "API is running successfully")
                    return True
                else:
                    self.log_result("API Health Check", False, "Unexpected response format", data)
                    return False
            else:
                self.log_result("API Health Check", False, f"HTTP {response.status_code}", response.text)
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
                if "id" in data and "name" in data and "plan" in data:
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
                        "type": "text",
                        "question": "What is your name?",
                        "required": True
                    },
                    {
                        "type": "multiple_choice",
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
                if "id" in data and data.get("title") == survey_data["title"]:
                    self.survey_id = data["id"]
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
                if data.get("id") == self.survey_id:
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
                    self.new_user_id = data["id"]
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

def main():
    """Main test execution"""
    tester = DataRWAPITester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()