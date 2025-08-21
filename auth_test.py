#!/usr/bin/env python3
"""
Focused Authentication Testing for DataRW
Tests the authentication system endpoints as requested in the review.
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

class AuthenticationTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.test_results = []
        
        # Test data - using fresh email as requested
        self.test_email = f"backend.test.{uuid.uuid4().hex[:8]}@example.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Backend Test User"
        
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
    
    def test_user_registration(self):
        """Test POST /api/auth/register with valid user data"""
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
                
                # Verify it returns JWT token, user data, and organization data
                required_fields = ["access_token", "user", "organization"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Store for later tests
                    self.auth_token = data["access_token"]
                    self.user_data = data["user"]
                    self.organization_data = data["organization"]
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    
                    # Verify user data structure (organization_id is in JWT token, not user object)
                    user_fields = ["id", "email", "name", "role"]
                    user_missing = [field for field in user_fields if field not in self.user_data]
                    
                    # Verify organization data structure  
                    org_fields = ["id", "name", "plan"]
                    org_missing = [field for field in org_fields if field not in self.organization_data]
                    
                    if not user_missing and not org_missing:
                        self.log_result("User Registration", True, 
                                      f"Registration successful - JWT token, user data, and organization data returned")
                        return True
                    else:
                        self.log_result("User Registration", False, 
                                      f"Missing user fields: {user_missing}, org fields: {org_missing}", data)
                        return False
                else:
                    self.log_result("User Registration", False, f"Missing required fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("User Registration", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("User Registration", False, f"Request error: {str(e)}")
            return False
    
    def test_duplicate_email_handling(self):
        """Test duplicate email handling (should return 400 error)"""
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
                    self.log_result("Duplicate Email Handling", True, 
                                  "Properly rejected duplicate email with 400 error")
                    return True
                else:
                    self.log_result("Duplicate Email Handling", False, 
                                  "Wrong error message for duplicate email", data)
                    return False
            else:
                self.log_result("Duplicate Email Handling", False, 
                              f"Expected 400, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Duplicate Email Handling", False, f"Request error: {str(e)}")
            return False
    
    def test_user_login_valid(self):
        """Test POST /api/auth/login with registered user credentials"""
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
                
                # Verify it returns valid JWT token and user data
                required_fields = ["access_token", "user"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Update token in case it changed
                    self.auth_token = data["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    
                    # Verify last_login field is updated (check if user has last_login)
                    user = data["user"]
                    if "last_login" in user:
                        self.log_result("User Login Valid", True, 
                                      "Login successful - JWT token and user data returned, last_login updated")
                    else:
                        self.log_result("User Login Valid", True, 
                                      "Login successful - JWT token and user data returned")
                    return True
                else:
                    self.log_result("User Login Valid", False, f"Missing required fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("User Login Valid", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("User Login Valid", False, f"Request error: {str(e)}")
            return False
    
    def test_user_login_invalid(self):
        """Test login with invalid credentials (should return 401 error)"""
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
                    self.log_result("User Login Invalid", True, 
                                  "Properly rejected invalid credentials with 401 error")
                    return True
                else:
                    self.log_result("User Login Invalid", False, 
                                  "Wrong error message for invalid credentials", data)
                    return False
            else:
                self.log_result("User Login Invalid", False, 
                              f"Expected 401, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("User Login Invalid", False, f"Request error: {str(e)}")
            return False
    
    def test_protected_endpoint_organizations_me(self):
        """Test GET /api/organizations/me with valid JWT token"""
        try:
            response = self.session.get(f"{self.base_url}/organizations/me")
            
            if response.status_code == 200:
                data = response.json()
                # Check for required organization fields
                required_fields = ["id", "name", "plan"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_result("Protected Endpoint Organizations/Me", True, 
                                  "Successfully accessed with valid JWT token")
                    return True
                else:
                    self.log_result("Protected Endpoint Organizations/Me", False, 
                                  f"Missing required fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("Protected Endpoint Organizations/Me", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Protected Endpoint Organizations/Me", False, f"Request error: {str(e)}")
            return False
    
    def test_protected_endpoint_users(self):
        """Test GET /api/users with valid JWT token"""
        try:
            response = self.session.get(f"{self.base_url}/users")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check if users have required fields
                    user = data[0]
                    required_fields = ["id", "email", "name", "role"]
                    missing_fields = [field for field in required_fields if field not in user]
                    
                    if not missing_fields:
                        self.log_result("Protected Endpoint Users", True, 
                                      f"Successfully accessed with valid JWT token - retrieved {len(data)} users")
                        return True
                    else:
                        self.log_result("Protected Endpoint Users", False, 
                                      f"User missing required fields: {missing_fields}", data)
                        return False
                else:
                    self.log_result("Protected Endpoint Users", True, 
                                  "Successfully accessed with valid JWT token - no users found")
                    return True
            else:
                self.log_result("Protected Endpoint Users", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Protected Endpoint Users", False, f"Request error: {str(e)}")
            return False
    
    def test_unauthorized_access_organizations_me(self):
        """Test GET /api/organizations/me without JWT token (should return 403)"""
        try:
            # Create a session without authorization header
            temp_session = requests.Session()
            
            response = temp_session.get(f"{self.base_url}/organizations/me")
            
            if response.status_code == 403:
                self.log_result("Unauthorized Access Organizations/Me", True, 
                              "Properly rejected unauthorized request with 403 error")
                return True
            elif response.status_code == 401:
                self.log_result("Unauthorized Access Organizations/Me", True, 
                              "Properly rejected unauthorized request with 401 error")
                return True
            else:
                self.log_result("Unauthorized Access Organizations/Me", False, 
                              f"Expected 403/401, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Unauthorized Access Organizations/Me", False, f"Request error: {str(e)}")
            return False
    
    def test_unauthorized_access_users(self):
        """Test GET /api/users without JWT token (should return 403)"""
        try:
            # Create a session without authorization header
            temp_session = requests.Session()
            
            response = temp_session.get(f"{self.base_url}/users")
            
            if response.status_code == 403:
                self.log_result("Unauthorized Access Users", True, 
                              "Properly rejected unauthorized request with 403 error")
                return True
            elif response.status_code == 401:
                self.log_result("Unauthorized Access Users", True, 
                              "Properly rejected unauthorized request with 401 error")
                return True
            else:
                self.log_result("Unauthorized Access Users", False, 
                              f"Expected 403/401, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Unauthorized Access Users", False, f"Request error: {str(e)}")
            return False
    
    def test_database_service_functionality(self):
        """Test database service functionality - verify user and organization creation"""
        try:
            # This test verifies that the database service properly handles string IDs
            # and that user/organization creation works correctly
            
            if not self.user_data or not self.organization_data:
                self.log_result("Database Service Functionality", False, 
                              "No user or organization data available from registration")
                return False
            
            # Verify user has string ID (not MongoDB ObjectId)
            user_id = self.user_data.get("id")
            org_id = self.organization_data.get("id")
            
            if not user_id or not org_id:
                self.log_result("Database Service Functionality", False, 
                              "Missing user or organization ID")
                return False
            
            # Verify IDs are strings and not ObjectId format
            if isinstance(user_id, str) and isinstance(org_id, str):
                # Test user lookup by email functionality
                login_data = {
                    "email": self.test_email,
                    "password": self.test_password
                }
                
                response = self.session.post(
                    f"{self.base_url}/auth/login",
                    json=login_data
                )
                
                if response.status_code == 200:
                    self.log_result("Database Service Functionality", True, 
                                  "User creation, organization creation, and user lookup by email all working correctly with string IDs")
                    return True
                else:
                    self.log_result("Database Service Functionality", False, 
                                  "User lookup by email failed", response.text)
                    return False
            else:
                self.log_result("Database Service Functionality", False, 
                              f"IDs are not strings - user_id: {type(user_id)}, org_id: {type(org_id)}")
                return False
                
        except Exception as e:
            self.log_result("Database Service Functionality", False, f"Request error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting DataRW Authentication System Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        tests = [
            self.test_user_registration,
            self.test_duplicate_email_handling,
            self.test_user_login_valid,
            self.test_user_login_invalid,
            self.test_protected_endpoint_organizations_me,
            self.test_protected_endpoint_users,
            self.test_unauthorized_access_organizations_me,
            self.test_unauthorized_access_users,
            self.test_database_service_functionality
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL: {test.__name__} - Unexpected error: {str(e)}")
                failed += 1
        
        print("\n" + "=" * 60)
        print("📊 AUTHENTICATION TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed > 0:
            print(f"\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
        
        return passed, failed

if __name__ == "__main__":
    tester = AuthenticationTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)