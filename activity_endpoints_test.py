#!/usr/bin/env python3
"""
Focused Backend API Testing for Activity Endpoints
Tests the specific activity endpoints mentioned in the review request:
- GET /api/activities (validation errors for legacy activities)
- PUT /api/activities/{activity_id}/progress (UUID/ObjectId compatibility)
- GET /api/activities/{activity_id}/variance (UUID/ObjectId compatibility)
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

class ActivityEndpointsTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.test_results = []
        
        # Test data
        self.test_email = f"activity.test.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Activity Test User"
        
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
        """Setup authentication for testing"""
        try:
            # Register a test user
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
                
                self.log_result("Setup Authentication", True, "User registered and authenticated successfully")
                return True
            else:
                self.log_result("Setup Authentication", False, f"Registration failed: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Setup Authentication", False, f"Authentication setup error: {str(e)}")
            return False
    
    def create_test_project(self):
        """Create a test project for activities"""
        try:
            project_data = {
                "name": f"Activity Test Project {uuid.uuid4().hex[:8]}",
                "description": "Test project for activity endpoint testing",
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
                self.project_id = data.get("id") or data.get("_id")
                self.log_result("Create Test Project", True, "Test project created successfully")
                return True
            else:
                self.log_result("Create Test Project", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Test Project", False, f"Request error: {str(e)}")
            return False
    
    def create_test_activity(self):
        """Create a test activity with enhanced fields"""
        try:
            activity_data = {
                "project_id": self.project_id,
                "name": f"Enhanced Test Activity {uuid.uuid4().hex[:8]}",
                "description": "Test activity with enhanced fields for endpoint testing",
                "assigned_to": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "budget_allocated": 50000.0,
                "deliverables": ["Test deliverable 1", "Test deliverable 2"],
                "dependencies": ["Test dependency"],
                "milestones": [
                    {
                        "name": "Test Milestone 1",
                        "planned_date": (datetime.now() + timedelta(days=15)).isoformat()
                    }
                ],
                "planned_output": "Test planned output",
                "target_quantity": 100,
                "actual_output": "Initial actual output",
                "achieved_quantity": 0,
                "risk_level": "medium"
            }
            
            response = self.session.post(
                f"{self.base_url}/activities",
                json=activity_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.activity_id = data.get("id") or data.get("_id")
                self.log_result("Create Test Activity", True, "Enhanced test activity created successfully")
                return True
            else:
                self.log_result("Create Test Activity", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Test Activity", False, f"Request error: {str(e)}")
            return False
    
    def test_get_activities_validation_fix(self):
        """Test GET /api/activities - should no longer throw validation errors for legacy activities"""
        try:
            response = self.session.get(f"{self.base_url}/activities")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check if activities have normalized fields
                    for activity in data:
                        # Check for required normalized fields
                        if "planned_start_date" not in activity:
                            self.log_result("GET Activities Validation Fix", False, 
                                          "Activity missing planned_start_date field", activity)
                            return False
                        
                        if "planned_end_date" not in activity:
                            self.log_result("GET Activities Validation Fix", False, 
                                          "Activity missing planned_end_date field", activity)
                            return False
                        
                        if "last_updated_by" not in activity:
                            self.log_result("GET Activities Validation Fix", False, 
                                          "Activity missing last_updated_by field", activity)
                            return False
                        
                        # Check for proper id normalization (should be string, not ObjectId)
                        activity_id = activity.get("id") or activity.get("_id")
                        if not activity_id or not isinstance(activity_id, str):
                            self.log_result("GET Activities Validation Fix", False, 
                                          "Activity ID not properly normalized", activity)
                            return False
                    
                    self.log_result("GET Activities Validation Fix", True, 
                                  f"Retrieved {len(data)} activities with normalized fields - validation errors fixed")
                    return True
                else:
                    self.log_result("GET Activities Validation Fix", False, "Response is not a list", data)
                    return False
            else:
                # Check for specific validation errors
                if response.status_code == 500:
                    error_text = response.text
                    if "validation" in error_text.lower() or "pydantic" in error_text.lower():
                        self.log_result("GET Activities Validation Fix", False, 
                                      "CRITICAL: Validation errors still present in GET activities", error_text)
                        return False
                
                self.log_result("GET Activities Validation Fix", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("GET Activities Validation Fix", False, f"Request error: {str(e)}")
            return False
    
    def test_update_activity_progress_uuid_compatibility(self):
        """Test PUT /api/activities/{activity_id}/progress - should work with both UUID and ObjectId"""
        if not hasattr(self, 'activity_id'):
            self.log_result("Update Activity Progress UUID", False, "No activity ID available")
            return False
        
        try:
            progress_data = {
                "progress_percentage": 45.0,
                "completion_variance": 5.0,
                "schedule_variance_days": -2,
                "risk_level": "low",
                "status": "in_progress",
                "notes": "Progress update test - UUID compatibility check"
            }
            
            response = self.session.put(
                f"{self.base_url}/activities/{self.activity_id}/progress",
                json=progress_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Verify the update was successful
                    updated_data = data.get("data", {})
                    if (updated_data.get("progress_percentage") == progress_data["progress_percentage"] and
                        updated_data.get("status") == progress_data["status"]):
                        self.log_result("Update Activity Progress UUID", True, 
                                      "Activity progress updated successfully with UUID ID - ObjectId/UUID compatibility working")
                        return True
                    else:
                        self.log_result("Update Activity Progress UUID", False, 
                                      "Progress data not updated correctly", data)
                        return False
                else:
                    self.log_result("Update Activity Progress UUID", False, 
                                  "Success flag not set in response", data)
                    return False
            else:
                # Check for specific ObjectId/UUID errors
                if response.status_code == 500:
                    error_text = response.text
                    if "ObjectId" in error_text and "UUID" in error_text:
                        self.log_result("Update Activity Progress UUID", False, 
                                      "CRITICAL: ObjectId/UUID mismatch error still present", error_text)
                        return False
                    elif "invalid ObjectId" in error_text.lower():
                        self.log_result("Update Activity Progress UUID", False, 
                                      "CRITICAL: Backend still expects ObjectId format", error_text)
                        return False
                
                self.log_result("Update Activity Progress UUID", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update Activity Progress UUID", False, f"Request error: {str(e)}")
            return False
    
    def test_get_activity_variance_uuid_compatibility(self):
        """Test GET /api/activities/{activity_id}/variance - should work with both UUID and ObjectId"""
        if not hasattr(self, 'activity_id'):
            self.log_result("Get Activity Variance UUID", False, "No activity ID available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/activities/{self.activity_id}/variance")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    variance_data = data.get("data", {})
                    
                    # Check for expected variance analysis structure
                    expected_fields = ["schedule_variance", "budget_variance", "performance_variance", "risk_assessment"]
                    missing_fields = [field for field in expected_fields if field not in variance_data]
                    
                    if not missing_fields:
                        self.log_result("Get Activity Variance UUID", True, 
                                      "Activity variance analysis retrieved successfully with UUID ID - ObjectId/UUID compatibility working")
                        return True
                    else:
                        self.log_result("Get Activity Variance UUID", False, 
                                      f"Missing variance fields: {missing_fields}", data)
                        return False
                else:
                    self.log_result("Get Activity Variance UUID", False, 
                                  "Success flag not set in response", data)
                    return False
            else:
                # Check for specific ObjectId/UUID errors
                if response.status_code == 500:
                    error_text = response.text
                    if "ObjectId" in error_text and "UUID" in error_text:
                        self.log_result("Get Activity Variance UUID", False, 
                                      "CRITICAL: ObjectId/UUID mismatch error still present", error_text)
                        return False
                    elif "invalid ObjectId" in error_text.lower():
                        self.log_result("Get Activity Variance UUID", False, 
                                      "CRITICAL: Backend still expects ObjectId format", error_text)
                        return False
                elif response.status_code == 404:
                    self.log_result("Get Activity Variance UUID", False, 
                                  "Activity not found - possible ID lookup issue", response.text)
                    return False
                
                self.log_result("Get Activity Variance UUID", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Activity Variance UUID", False, f"Request error: {str(e)}")
            return False
    
    def run_focused_tests(self):
        """Run the focused activity endpoint tests"""
        print("=" * 80)
        print("FOCUSED ACTIVITY ENDPOINTS TESTING")
        print("Testing specific endpoints mentioned in review request")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            return False
        
        if not self.create_test_project():
            return False
        
        if not self.create_test_activity():
            return False
        
        # Run the specific tests mentioned in review request
        tests = [
            self.test_get_activities_validation_fix,
            self.test_update_activity_progress_uuid_compatibility,
            self.test_get_activity_variance_uuid_compatibility
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("\n" + "=" * 80)
        print(f"FOCUSED TESTING RESULTS: {passed}/{total} tests passed")
        print("=" * 80)
        
        # Print summary
        print("\n### FOCUSED TEST SUMMARY ###")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        return passed == total

def main():
    """Main function to run focused activity endpoint tests"""
    tester = ActivityEndpointsTester()
    success = tester.run_focused_tests()
    
    if success:
        print("\n🎉 All focused activity endpoint tests passed!")
        return 0
    else:
        print("\n❌ Some focused activity endpoint tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())