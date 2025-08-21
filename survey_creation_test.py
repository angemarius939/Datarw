#!/usr/bin/env python3
"""
Focused Survey Creation Testing for DataRW
Tests specifically requested survey creation functionality:
1. Login to get auth token
2. Test survey creation endpoint
3. Test getting surveys
4. Test survey limits
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
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://monitoring-eval-app.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class SurveyCreationTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.test_results = []
        
        # Generate unique user credentials for testing
        self.test_email = f"survey.test.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SurveyTest123!"
        self.test_name = "Survey Test User"
        
    def log_result(self, test_name, success, message, response_data=None):
        """Log test result with detailed response"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'response_data': response_data,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   Message: {message}")
        if response_data:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()
    
    def test_user_registration(self):
        """Step 0: Register a new user first"""
        print("👤 Step 0: Register a new user")
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
            
            print(f"   Request: POST {self.base_url}/auth/register")
            print(f"   Payload: {json.dumps(registration_data, indent=2)}")
            print(f"   Status Code: {response.status_code}")
            
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
                    
                    self.log_result("User Registration", True, 
                                  f"User registered successfully. Token: {self.auth_token[:20]}...", data)
                    return True
                else:
                    self.log_result("User Registration", False, 
                                  "Missing required fields in response", data)
                    return False
            else:
                error_data = response.json() if response.content else {"error": "No response body"}
                self.log_result("User Registration", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
        except Exception as e:
            self.log_result("User Registration", False, f"Request error: {str(e)}")
            return False

    def test_login_for_auth_token(self):
        """Step 1: Login to get auth token"""
        print("🔐 Step 1: Login to get auth token")
        try:
            login_data = {
                "email": self.test_email,
                "password": self.test_password
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data
            )
            
            print(f"   Request: POST {self.base_url}/auth/login")
            print(f"   Payload: {json.dumps(login_data, indent=2)}")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.user_data = data["user"]
                    self.organization_data = data.get("organization", {})
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    
                    self.log_result("Login for Auth Token", True, 
                                  f"Successfully logged in. Token: {self.auth_token[:20]}...", data)
                    return True
                else:
                    self.log_result("Login for Auth Token", False, 
                                  "Missing required fields in response", data)
                    return False
            else:
                error_data = response.json() if response.content else {"error": "No response body"}
                self.log_result("Login for Auth Token", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
        except Exception as e:
            self.log_result("Login for Auth Token", False, f"Request error: {str(e)}")
            return False
    
    def test_survey_creation_endpoint(self):
        """Step 2: Test survey creation endpoint with specific test data"""
        print("📝 Step 2: Test survey creation endpoint")
        try:
            survey_data = {
                "title": "Test Survey",
                "description": "Test description",
                "questions": [
                    {
                        "type": "text",
                        "question": "What is your name?",
                        "required": True
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/surveys",
                json=survey_data
            )
            
            print(f"   Request: POST {self.base_url}/surveys")
            print(f"   Headers: Authorization: Bearer {self.auth_token[:20]}...")
            print(f"   Payload: {json.dumps(survey_data, indent=2)}")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                # Handle both 'id' and '_id' field names
                survey_id = data.get("id") or data.get("_id")
                if survey_id and data.get("title") == survey_data["title"]:
                    self.survey_id = survey_id
                    self.log_result("Survey Creation", True, 
                                  f"Survey created successfully with ID: {self.survey_id}", data)
                    return True
                else:
                    self.log_result("Survey Creation", False, 
                                  f"Survey data mismatch or missing ID. Expected title: {survey_data['title']}, Got title: {data.get('title')}, ID: {survey_id}", data)
                    return False
            else:
                error_data = response.json() if response.content else {"error": "No response body"}
                self.log_result("Survey Creation", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
        except Exception as e:
            self.log_result("Survey Creation", False, f"Request error: {str(e)}")
            return False
    
    def test_getting_surveys(self):
        """Step 3: Test getting surveys"""
        print("📋 Step 3: Test getting surveys")
        try:
            response = self.session.get(f"{self.base_url}/surveys")
            
            print(f"   Request: GET {self.base_url}/surveys")
            print(f"   Headers: Authorization: Bearer {self.auth_token[:20]}...")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check if our created survey appears in the list
                    survey_found = False
                    if hasattr(self, 'survey_id'):
                        survey_found = any(survey.get("id") == self.survey_id or survey.get("_id") == self.survey_id for survey in data)
                    
                    message = f"Retrieved {len(data)} surveys"
                    if survey_found:
                        message += f". Created survey (ID: {self.survey_id}) found in list."
                    elif hasattr(self, 'survey_id'):
                        message += f". WARNING: Created survey (ID: {self.survey_id}) NOT found in list."
                    
                    self.log_result("Get Surveys", True, message, data)
                    return True
                else:
                    self.log_result("Get Surveys", False, 
                                  "Response is not a list", data)
                    return False
            else:
                error_data = response.json() if response.content else {"error": "No response body"}
                self.log_result("Get Surveys", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
        except Exception as e:
            self.log_result("Get Surveys", False, f"Request error: {str(e)}")
            return False
    
    def test_survey_limits(self):
        """Step 4: Test survey limits by creating multiple surveys"""
        print("🚫 Step 4: Test survey limits")
        try:
            surveys_created = 0
            limit_reached = False
            
            # Try to create multiple surveys to test limits
            for i in range(6):  # Try to create 6 surveys to test limit
                survey_data = {
                    "title": f"Limit Test Survey {i+1}",
                    "description": f"Survey {i+1} for testing limits",
                    "questions": [
                        {
                            "type": "text",
                            "question": f"Question {i+1}: What do you think?",
                            "required": True
                        }
                    ]
                }
                
                response = self.session.post(
                    f"{self.base_url}/surveys",
                    json=survey_data
                )
                
                print(f"   Attempt {i+1}: POST {self.base_url}/surveys")
                print(f"   Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    surveys_created += 1
                    data = response.json()
                    survey_id = data.get("id") or data.get("_id")
                    print(f"   ✅ Survey {i+1} created successfully (ID: {survey_id})")
                elif response.status_code == 400:
                    data = response.json()
                    if "Survey limit reached" in data.get("detail", ""):
                        limit_reached = True
                        self.log_result("Survey Limit Enforcement", True, 
                                      f"Survey limit properly enforced after {surveys_created} surveys. Error: {data.get('detail')}", 
                                      {"surveys_created": surveys_created, "limit_response": data})
                        return True
                    else:
                        self.log_result("Survey Limit Enforcement", False, 
                                      f"Wrong error message for limit. Got: {data.get('detail')}", data)
                        return False
                else:
                    error_data = response.json() if response.content else {"error": "No response body"}
                    self.log_result("Survey Limit Enforcement", False, 
                                  f"Unexpected response: {response.status_code}", error_data)
                    return False
            
            # If we get here, limit wasn't enforced
            self.log_result("Survey Limit Enforcement", False, 
                          f"Created {surveys_created} surveys without limit enforcement", 
                          {"surveys_created": surveys_created})
            return False
            
        except Exception as e:
            self.log_result("Survey Limit Enforcement", False, f"Request error: {str(e)}")
            return False
    
    def run_survey_creation_tests(self):
        """Run the specific survey creation tests requested"""
        print("🚀 Starting Survey Creation Functionality Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Test sequence as requested (with registration first)
        tests = [
            ("Step 0: Register a new user", self.test_user_registration),
            ("Step 1: Login to get auth token", self.test_login_for_auth_token),
            ("Step 2: Test survey creation endpoint", self.test_survey_creation_endpoint),
            ("Step 3: Test getting surveys", self.test_getting_surveys),
            ("Step 4: Test survey limits", self.test_survey_limits)
        ]
        
        for step_name, test_func in tests:
            print(f"\n{step_name}")
            print("-" * 80)
            success = test_func()
            if not success:
                print(f"❌ {step_name} failed. Continuing with remaining tests...")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 SURVEY CREATION TEST SUMMARY")
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
        
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = SurveyCreationTester()
    passed, failed = tester.run_survey_creation_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()