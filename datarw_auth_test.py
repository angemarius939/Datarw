#!/usr/bin/env python3
"""
DataRW Backend Authentication and Registration Testing
Focused testing for the specific review request requirements.
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
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://datarw-insights.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class DataRWAuthTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.test_results = []
        
        # Test data with realistic information
        self.test_email = f"john.doe.{uuid.uuid4().hex[:8]}@test.com"
        self.test_password = "password123"
        self.test_name = "John Doe"
        
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
        print(f"{status}: {test_name}")
        print(f"   Message: {message}")
        if details and not success:
            print(f"   Details: {details}")
        print()
    
    def test_registration_valid_data(self):
        """Test Registration Endpoint with valid data"""
        try:
            registration_data = {
                "name": self.test_name,
                "email": self.test_email,
                "password": self.test_password
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=registration_data
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                required_fields = ["access_token", "token_type", "expires_in", "user", "organization"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Store auth data for subsequent tests
                    self.auth_token = data["access_token"]
                    self.user_data = data["user"]
                    self.organization_data = data["organization"]
                    
                    # Set authorization header
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    
                    # Verify user data
                    user = data["user"]
                    if (user.get("name") == self.test_name and 
                        user.get("email") == self.test_email and
                        "id" in user):
                        
                        self.log_result(
                            "Registration with Valid Data", 
                            True, 
                            f"Successfully registered user with JWT token. User ID: {user['id']}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Registration with Valid Data", 
                            False, 
                            "User data mismatch in response", 
                            data
                        )
                        return False
                else:
                    self.log_result(
                        "Registration with Valid Data", 
                        False, 
                        f"Missing required fields: {missing_fields}", 
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Registration with Valid Data", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Registration with Valid Data", 
                False, 
                f"Request error: {str(e)}"
            )
            return False
    
    def test_registration_duplicate_email(self):
        """Test Registration with duplicate email"""
        try:
            registration_data = {
                "name": "Another User",
                "email": self.test_email,  # Same email as previous test
                "password": "differentpassword123"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=registration_data
            )
            
            if response.status_code == 400:
                data = response.json()
                error_detail = data.get("detail", "")
                
                if "Email already registered" in error_detail:
                    self.log_result(
                        "Registration with Duplicate Email", 
                        True, 
                        f"Properly rejected duplicate email with error: '{error_detail}'"
                    )
                    return True
                else:
                    self.log_result(
                        "Registration with Duplicate Email", 
                        False, 
                        f"Wrong error message: '{error_detail}'", 
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Registration with Duplicate Email", 
                    False, 
                    f"Expected HTTP 400, got {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Registration with Duplicate Email", 
                False, 
                f"Request error: {str(e)}"
            )
            return False
    
    def test_login_valid_credentials(self):
        """Test Login with registered credentials"""
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
                
                # Check for JWT token
                if "access_token" in data and "user" in data:
                    # Update token
                    self.auth_token = data["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    
                    self.log_result(
                        "Login with Valid Credentials", 
                        True, 
                        f"Successfully logged in. Token received: {data['access_token'][:20]}..."
                    )
                    return True
                else:
                    self.log_result(
                        "Login with Valid Credentials", 
                        False, 
                        "Missing access_token or user in response", 
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Login with Valid Credentials", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Login with Valid Credentials", 
                False, 
                f"Request error: {str(e)}"
            )
            return False
    
    def test_login_wrong_credentials(self):
        """Test Login with wrong credentials"""
        try:
            login_data = {
                "email": self.test_email,
                "password": "wrongpassword123"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data
            )
            
            if response.status_code == 401:
                data = response.json()
                error_detail = data.get("detail", "")
                
                if "Incorrect email or password" in error_detail:
                    self.log_result(
                        "Login with Wrong Credentials", 
                        True, 
                        f"Properly rejected wrong credentials with error: '{error_detail}'"
                    )
                    return True
                else:
                    self.log_result(
                        "Login with Wrong Credentials", 
                        False, 
                        f"Wrong error message: '{error_detail}'", 
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Login with Wrong Credentials", 
                    False, 
                    f"Expected HTTP 401, got {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Login with Wrong Credentials", 
                False, 
                f"Request error: {str(e)}"
            )
            return False
    
    def test_protected_endpoint_organizations_me(self):
        """Test GET /api/organizations/me with valid JWT token"""
        try:
            response = self.session.get(f"{self.base_url}/organizations/me")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required organization fields
                required_fields = ["name", "plan"]
                if all(field in data for field in required_fields):
                    self.log_result(
                        "Protected Endpoint - Organizations/Me (Authorized)", 
                        True, 
                        f"Successfully accessed organization data. Plan: {data.get('plan')}, Name: {data.get('name')}"
                    )
                    return True
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result(
                        "Protected Endpoint - Organizations/Me (Authorized)", 
                        False, 
                        f"Missing required fields: {missing_fields}", 
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Protected Endpoint - Organizations/Me (Authorized)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Protected Endpoint - Organizations/Me (Authorized)", 
                False, 
                f"Request error: {str(e)}"
            )
            return False
    
    def test_protected_endpoint_users(self):
        """Test GET /api/users with valid JWT token"""
        try:
            response = self.session.get(f"{self.base_url}/users")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    # Check first user has required fields
                    user = data[0]
                    required_fields = ["id", "email", "name", "role"]
                    if all(field in user for field in required_fields):
                        self.log_result(
                            "Protected Endpoint - Users (Authorized)", 
                            True, 
                            f"Successfully accessed users list. Found {len(data)} users"
                        )
                        return True
                    else:
                        missing_fields = [field for field in required_fields if field not in user]
                        self.log_result(
                            "Protected Endpoint - Users (Authorized)", 
                            False, 
                            f"User missing required fields: {missing_fields}", 
                            data
                        )
                        return False
                else:
                    self.log_result(
                        "Protected Endpoint - Users (Authorized)", 
                        False, 
                        "Expected non-empty list of users", 
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Protected Endpoint - Users (Authorized)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Protected Endpoint - Users (Authorized)", 
                False, 
                f"Request error: {str(e)}"
            )
            return False
    
    def test_protected_endpoints_without_auth(self):
        """Test protected endpoints fail without authorization"""
        # Remove authorization header temporarily
        original_headers = self.session.headers.copy()
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
        
        try:
            # Test organizations/me without auth
            response1 = self.session.get(f"{self.base_url}/organizations/me")
            
            # Test users without auth
            response2 = self.session.get(f"{self.base_url}/users")
            
            # Both should return 401 or 403
            auth_failed_1 = response1.status_code in [401, 403]
            auth_failed_2 = response2.status_code in [401, 403]
            
            if auth_failed_1 and auth_failed_2:
                self.log_result(
                    "Protected Endpoints Without Authorization", 
                    True, 
                    f"Both endpoints properly rejected unauthorized access (HTTP {response1.status_code}, {response2.status_code})"
                )
                return True
            else:
                self.log_result(
                    "Protected Endpoints Without Authorization", 
                    False, 
                    f"Expected 401/403, got organizations/me: {response1.status_code}, users: {response2.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Protected Endpoints Without Authorization", 
                False, 
                f"Request error: {str(e)}"
            )
            return False
        finally:
            # Restore authorization header
            self.session.headers.update(original_headers)
    
    def test_irembopay_payment_plans(self):
        """Test GET /api/payments/plans"""
        try:
            response = self.session.get(f"{self.base_url}/payments/plans")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected plan structure
                expected_plans = ["Basic", "Professional", "Enterprise"]
                if isinstance(data, dict) and all(plan in data for plan in expected_plans):
                    # Check Basic plan structure
                    basic_plan = data.get("Basic", {})
                    if "amount" in basic_plan and "features" in basic_plan:
                        self.log_result(
                            "IremboPay Payment Plans", 
                            True, 
                            f"Successfully retrieved payment plans. Basic plan: {basic_plan.get('amount')} RWF"
                        )
                        return True
                    else:
                        self.log_result(
                            "IremboPay Payment Plans", 
                            False, 
                            "Basic plan missing required fields", 
                            data
                        )
                        return False
                else:
                    self.log_result(
                        "IremboPay Payment Plans", 
                        False, 
                        f"Expected plans {expected_plans}, got: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}", 
                        data
                    )
                    return False
            else:
                self.log_result(
                    "IremboPay Payment Plans", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "IremboPay Payment Plans", 
                False, 
                f"Request error: {str(e)}"
            )
            return False
    
    def test_irembopay_widget_config(self):
        """Test GET /api/payments/widget-config"""
        try:
            response = self.session.get(f"{self.base_url}/payments/widget-config")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required widget config fields
                required_fields = ["widget_url", "public_key", "is_production"]
                if all(field in data for field in required_fields):
                    self.log_result(
                        "IremboPay Widget Configuration", 
                        True, 
                        f"Successfully retrieved widget config. Production: {data.get('is_production')}"
                    )
                    return True
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result(
                        "IremboPay Widget Configuration", 
                        False, 
                        f"Missing required fields: {missing_fields}", 
                        data
                    )
                    return False
            else:
                self.log_result(
                    "IremboPay Widget Configuration", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "IremboPay Widget Configuration", 
                False, 
                f"Request error: {str(e)}"
            )
            return False
    
    def test_survey_creation(self):
        """Test POST /api/surveys with valid data"""
        try:
            survey_data = {
                "title": f"Customer Satisfaction Survey {uuid.uuid4().hex[:8]}",
                "description": "A survey to measure customer satisfaction with our services",
                "questions": [
                    {
                        "type": "text",
                        "question": "What is your name?",
                        "required": True
                    },
                    {
                        "type": "multiple_choice",
                        "question": "How satisfied are you with our service?",
                        "required": True,
                        "options": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/surveys",
                json=survey_data
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check survey was created with correct data
                survey_id = data.get("id") or data.get("_id")
                if (data.get("title") == survey_data["title"] and 
                    data.get("description") == survey_data["description"] and
                    survey_id):
                    
                    self.survey_id = survey_id
                    self.log_result(
                        "Survey Creation", 
                        True, 
                        f"Successfully created survey. ID: {survey_id}"
                    )
                    return True
                else:
                    self.log_result(
                        "Survey Creation", 
                        False, 
                        "Survey data mismatch", 
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Survey Creation", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Survey Creation", 
                False, 
                f"Request error: {str(e)}"
            )
            return False
    
    def test_survey_listing(self):
        """Test GET /api/surveys"""
        try:
            response = self.session.get(f"{self.base_url}/surveys")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    self.log_result(
                        "Survey Listing", 
                        True, 
                        f"Successfully retrieved surveys list. Found {len(data)} surveys"
                    )
                    return True
                else:
                    self.log_result(
                        "Survey Listing", 
                        False, 
                        "Expected list of surveys", 
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Survey Listing", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Survey Listing", 
                False, 
                f"Request error: {str(e)}"
            )
            return False
    
    def test_survey_limit_enforcement(self):
        """Test survey limit enforcement"""
        try:
            # Create surveys up to the limit (Basic plan has 4 survey limit)
            surveys_created = 0
            limit_reached = False
            
            for i in range(5):  # Try to create 5 surveys (should fail on 5th for Basic plan)
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
                    error_detail = data.get("detail", "")
                    if "Survey limit reached" in error_detail:
                        limit_reached = True
                        break
                    else:
                        self.log_result(
                            "Survey Limit Enforcement", 
                            False, 
                            f"Wrong error message: '{error_detail}'", 
                            data
                        )
                        return False
                else:
                    self.log_result(
                        "Survey Limit Enforcement", 
                        False, 
                        f"Unexpected response: HTTP {response.status_code}: {response.text}"
                    )
                    return False
            
            if limit_reached:
                self.log_result(
                    "Survey Limit Enforcement", 
                    True, 
                    f"Survey limit properly enforced after {surveys_created} surveys"
                )
                return True
            else:
                self.log_result(
                    "Survey Limit Enforcement", 
                    False, 
                    f"Created {surveys_created} surveys without limit enforcement"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Survey Limit Enforcement", 
                False, 
                f"Request error: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all tests in the specified order"""
        print("🚀 DataRW Backend Authentication & Registration Testing")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Test sequence - order matters for dependencies
        tests = [
            self.test_registration_valid_data,
            self.test_registration_duplicate_email,
            self.test_login_valid_credentials,
            self.test_login_wrong_credentials,
            self.test_protected_endpoint_organizations_me,
            self.test_protected_endpoint_users,
            self.test_protected_endpoints_without_auth,
            self.test_irembopay_payment_plans,
            self.test_irembopay_widget_config,
            self.test_survey_creation,
            self.test_survey_listing,
            self.test_survey_limit_enforcement
        ]
        
        for test in tests:
            test()
        
        # Summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
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
    tester = DataRWAuthTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()