#!/usr/bin/env python3
"""
Focused test for GET /api/activities/{activity_id}/variance endpoint
Testing datetime parsing fix only as requested in review.
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
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

class VarianceEndpointTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        
        # Test data
        self.test_email = f"variance.test.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Variance Test User"
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def setup_authentication(self):
        """Setup authentication for testing"""
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
                self.log_result("Authentication Setup", False, f"Registration failed: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Authentication Setup", False, f"Request error: {str(e)}")
            return False
    
    def create_test_project(self):
        """Create a test project for activity creation"""
        try:
            from datetime import datetime, timedelta
            
            project_data = {
                "name": f"Variance Test Project {uuid.uuid4().hex[:8]}",
                "description": "Test project for variance endpoint testing",
                "project_manager_id": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
                "budget_total": 1000000.0,
                "beneficiaries_target": 100,
                "location": "Test Location",
                "donor_organization": "Test Donor"
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data
            )
            
            if response.status_code == 200:
                data = response.json()
                project_id = data.get("id") or data.get("_id")
                if project_id:
                    self.project_id = project_id
                    self.log_result("Create Test Project", True, "Test project created successfully")
                    return True
                else:
                    self.log_result("Create Test Project", False, "No project ID in response", data)
                    return False
            else:
                self.log_result("Create Test Project", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Test Project", False, f"Request error: {str(e)}")
            return False
    
    def create_test_activity(self):
        """Create a test activity with enhanced fields for variance testing"""
        try:
            from datetime import datetime, timedelta
            
            activity_data = {
                "project_id": self.project_id,
                "name": f"Variance Test Activity {uuid.uuid4().hex[:8]}",
                "description": "Test activity for variance analysis endpoint testing",
                "assigned_to": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "planned_start_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "planned_end_date": (datetime.now() + timedelta(days=25)).isoformat(),
                "budget_allocated": 50000.0,
                "deliverables": ["Test deliverable 1", "Test deliverable 2"],
                "milestones": [
                    {
                        "name": "Test Milestone 1",
                        "target_date": (datetime.now() + timedelta(days=10)).isoformat()
                    },
                    {
                        "name": "Test Milestone 2", 
                        "target_date": (datetime.now() + timedelta(days=20)).isoformat()
                    }
                ],
                "planned_outputs": [
                    {
                        "output_name": "Test Output 1",
                        "planned_quantity": 10,
                        "unit": "pieces"
                    }
                ],
                "actual_outputs": [
                    {
                        "output_name": "Test Output 1",
                        "actual_quantity": 8,
                        "unit": "pieces"
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/activities",
                json=activity_data
            )
            
            if response.status_code == 200:
                data = response.json()
                activity_id = data.get("id") or data.get("_id")
                if activity_id:
                    self.activity_id = activity_id
                    self.log_result("Create Test Activity", True, f"Test activity created with ID: {activity_id}")
                    return True
                else:
                    self.log_result("Create Test Activity", False, "No activity ID in response", data)
                    return False
            else:
                self.log_result("Create Test Activity", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Test Activity", False, f"Request error: {str(e)}")
            return False
    
    def test_variance_endpoint_datetime_fix(self):
        """Test GET /api/activities/{activity_id}/variance for datetime parsing fix"""
        try:
            response = self.session.get(f"{self.base_url}/activities/{self.activity_id}/variance")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    variance_data = data.get("data", {})
                    
                    # Check for expected variance analysis fields
                    expected_fields = [
                        "schedule_variance_days",
                        "budget_variance_percentage", 
                        "output_variance_percentage",
                        "completion_variance",
                        "risk_assessment"  # Changed from risk_level to risk_assessment
                    ]
                    
                    missing_fields = [field for field in expected_fields if field not in variance_data]
                    if missing_fields:
                        self.log_result("Variance Endpoint DateTime Fix", False, 
                                      f"Missing variance fields: {missing_fields}", variance_data)
                        return False
                    
                    # Verify numeric fields are properly calculated
                    numeric_fields = ["schedule_variance_days", "budget_variance_percentage", "output_variance_percentage"]
                    for field in numeric_fields:
                        value = variance_data.get(field)
                        if not isinstance(value, (int, float)):
                            self.log_result("Variance Endpoint DateTime Fix", False, 
                                          f"Field {field} should be numeric, got {type(value)}: {value}", variance_data)
                            return False
                    
                    # Check that datetime parsing worked (no datetime comparison errors)
                    schedule_variance = variance_data.get("schedule_variance_days")
                    if isinstance(schedule_variance, (int, float)):
                        self.log_result("Variance Endpoint DateTime Fix", True, 
                                      f"✅ DATETIME PARSING FIX SUCCESSFUL: Variance endpoint working correctly with schedule_variance_days: {schedule_variance}")
                        return True
                    else:
                        self.log_result("Variance Endpoint DateTime Fix", False, 
                                      f"Schedule variance calculation failed: {schedule_variance}", variance_data)
                        return False
                else:
                    self.log_result("Variance Endpoint DateTime Fix", False, "Success flag not set in response", data)
                    return False
            else:
                # Check for specific datetime parsing errors
                if response.status_code == 500:
                    error_text = response.text
                    if "'>' not supported between instances of 'NoneType' and datetime" in error_text:
                        self.log_result("Variance Endpoint DateTime Fix", False, 
                                      "❌ DATETIME PARSING ERROR STILL PRESENT: NoneType datetime comparison error", error_text)
                        return False
                    elif "datetime" in error_text.lower() and "parsing" in error_text.lower():
                        self.log_result("Variance Endpoint DateTime Fix", False, 
                                      "❌ DATETIME PARSING ERROR: Other datetime-related error", error_text)
                        return False
                    else:
                        self.log_result("Variance Endpoint DateTime Fix", False, 
                                      f"HTTP 500 error (not datetime-related): {response.status_code}", error_text)
                        return False
                else:
                    self.log_result("Variance Endpoint DateTime Fix", False, 
                                  f"HTTP {response.status_code}", response.text)
                    return False
        except Exception as e:
            self.log_result("Variance Endpoint DateTime Fix", False, f"Request error: {str(e)}")
            return False
    
    def run_variance_test(self):
        """Run the focused variance endpoint test"""
        print("🔍 FOCUSED VARIANCE ENDPOINT TESTING - DATETIME PARSING FIX VERIFICATION")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            return False
        
        if not self.create_test_project():
            return False
        
        if not self.create_test_activity():
            return False
        
        # Main test
        result = self.test_variance_endpoint_datetime_fix()
        
        print("=" * 80)
        if result:
            print("🎉 VARIANCE ENDPOINT DATETIME FIX VERIFICATION: SUCCESS")
            print(f"✅ Activity ID {self.activity_id} variance analysis working correctly")
        else:
            print("❌ VARIANCE ENDPOINT DATETIME FIX VERIFICATION: FAILED")
            print(f"❌ Activity ID {self.activity_id} variance analysis has issues")
        
        return result

if __name__ == "__main__":
    tester = VarianceEndpointTester()
    success = tester.run_variance_test()
    exit(0 if success else 1)