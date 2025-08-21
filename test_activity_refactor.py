#!/usr/bin/env python3
"""
Test Enhanced Activity Creation Endpoints - CreateActivityModal Refactor
Tests the specific endpoints affected by the CreateActivityModal refactor
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

class EnhancedActivityTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.project_id = None
        self.activity_id = None
        
        # Test data
        self.test_email = f"activity.test.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Activity Test User"
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
        return success
    
    def setup_authentication(self):
        """Setup authentication for testing"""
        print("🔧 Setting up authentication...")
        
        # Register user
        registration_data = {
            "email": self.test_email,
            "password": self.test_password,
            "name": self.test_name
        }
        
        response = self.session.post(f"{self.base_url}/auth/register", json=registration_data)
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data["access_token"]
            self.user_data = data["user"]
            self.organization_data = data["organization"]
            
            # Set authorization header
            self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
            print("✅ Authentication setup successful")
            return True
        else:
            print(f"❌ Authentication setup failed: {response.status_code}")
            return False
    
    def test_get_users_for_dropdown(self):
        """Test 1: GET /api/users – ensure it returns user list with id,name,email"""
        print("\n1️⃣ Testing GET /api/users for assigned person dropdown...")
        
        try:
            response = self.session.get(f"{self.base_url}/users")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    user = data[0]
                    required_fields = ["id", "name", "email"]
                    missing_fields = [field for field in required_fields if field not in user]
                    
                    if not missing_fields:
                        return self.log_result("GET /api/users", True, 
                                             f"Retrieved {len(data)} users with required fields (id, name, email)")
                    else:
                        return self.log_result("GET /api/users", False, 
                                             f"Missing required fields: {missing_fields}")
                else:
                    return self.log_result("GET /api/users", False, "No users found or invalid response")
            else:
                return self.log_result("GET /api/users", False, f"HTTP {response.status_code}")
        except Exception as e:
            return self.log_result("GET /api/users", False, f"Request error: {str(e)}")
    
    def test_create_minimal_project(self):
        """Test 2: POST /api/projects – create a minimal project to link activities"""
        print("\n2️⃣ Testing POST /api/projects for minimal project creation...")
        
        try:
            project_data = {
                "name": f"Activity Test Project {uuid.uuid4().hex[:8]}",
                "description": "Minimal project for testing enhanced activity creation",
                "project_manager_id": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
                "budget_total": 1000000.0,
                "beneficiaries_target": 100
            }
            
            response = self.session.post(f"{self.base_url}/projects", json=project_data)
            
            if response.status_code == 200:
                data = response.json()
                project_id = data.get("id") or data.get("_id")
                if project_id and data.get("name") == project_data["name"]:
                    self.project_id = project_id
                    return self.log_result("POST /api/projects", True, 
                                         f"Minimal project created successfully (ID: {project_id})")
                else:
                    return self.log_result("POST /api/projects", False, "Project data mismatch")
            else:
                return self.log_result("POST /api/projects", False, f"HTTP {response.status_code}")
        except Exception as e:
            return self.log_result("POST /api/projects", False, f"Request error: {str(e)}")
    
    def test_create_enhanced_activity(self):
        """Test 3: POST /api/activities – create activity with enhanced fields"""
        print("\n3️⃣ Testing POST /api/activities with enhanced fields...")
        
        if not self.project_id:
            return self.log_result("POST /api/activities", False, "No project ID available")
        
        try:
            # Enhanced activity data with all new fields
            activity_data = {
                "project_id": self.project_id,
                "name": f"Enhanced Digital Training Workshop {uuid.uuid4().hex[:8]}",
                "description": "Comprehensive digital literacy training with milestone tracking",
                "assigned_to": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=21)).isoformat(),
                "budget_allocated": 250000.0,
                
                # Enhanced output tracking
                "planned_output": "50 participants trained in basic digital skills with certification",
                "target_quantity": 50.0,
                
                # Milestones array with name and planned_date
                "milestones": [
                    {
                        "name": "Training materials preparation completed",
                        "planned_date": (datetime.now() + timedelta(days=5)).isoformat(),
                        "description": "All training materials prepared"
                    },
                    {
                        "name": "Participant registration completed",
                        "planned_date": (datetime.now() + timedelta(days=10)).isoformat(),
                        "description": "50 participants registered"
                    }
                ],
                
                # Initial actual output and achieved quantity
                "actual_output": "Training preparation phase initiated",
                "achieved_quantity": 0.0,
                
                # Status and risk tracking
                "status_notes": "Activity created with comprehensive milestone tracking",
                "risk_level": "low"
            }
            
            response = self.session.post(f"{self.base_url}/activities", json=activity_data)
            
            if response.status_code == 200:
                data = response.json()
                activity_id = data.get("id") or data.get("_id")
                
                # Verify enhanced fields
                validation_checks = [
                    (data.get("name") == activity_data["name"], "Activity name matches"),
                    (data.get("organization_id") is not None, "Organization ID set"),
                    (data.get("planned_start_date") is not None, "Planned start date fallback set"),
                    (data.get("planned_end_date") is not None, "Planned end date fallback set"),
                    (data.get("progress_percentage") == 0.0, "Progress percentage default 0"),
                    (data.get("last_updated_by") == self.user_data["id"], "Last updated by auto-stamped"),
                    (isinstance(data.get("milestones", []), list), "Milestones array present"),
                    (len(data.get("milestones", [])) == 2, "All milestones saved"),
                    (data.get("planned_output") == activity_data["planned_output"], "Planned output saved"),
                    (data.get("target_quantity") == activity_data["target_quantity"], "Target quantity saved")
                ]
                
                failed_checks = [check[1] for check in validation_checks if not check[0]]
                
                if activity_id and not failed_checks:
                    self.activity_id = activity_id
                    return self.log_result("POST /api/activities", True, 
                                         f"Enhanced activity created with all required fields (ID: {activity_id})")
                else:
                    return self.log_result("POST /api/activities", False, 
                                         f"Validation failed: {failed_checks}")
            else:
                return self.log_result("POST /api/activities", False, f"HTTP {response.status_code}")
        except Exception as e:
            return self.log_result("POST /api/activities", False, f"Request error: {str(e)}")
    
    def test_get_activities_serialization(self):
        """Test 4: GET /api/activities – ensure activity appears and fields serialize correctly"""
        print("\n4️⃣ Testing GET /api/activities field serialization...")
        
        try:
            response = self.session.get(f"{self.base_url}/activities")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Find our enhanced activity
                    enhanced_activity = None
                    if self.activity_id:
                        enhanced_activity = next((act for act in data 
                                                if act.get("id") == self.activity_id or 
                                                   act.get("_id") == self.activity_id), None)
                    
                    if enhanced_activity:
                        # Verify field serialization (strings for ids/dates as ISO)
                        serialization_checks = [
                            (isinstance(enhanced_activity.get("id") or enhanced_activity.get("_id"), str), 
                             "Activity ID serialized as string"),
                            (isinstance(enhanced_activity.get("organization_id"), str), 
                             "Organization ID serialized as string"),
                            ("T" in str(enhanced_activity.get("start_date", "")), 
                             "Start date in ISO format"),
                            ("T" in str(enhanced_activity.get("created_at", "")), 
                             "Created at in ISO format"),
                            (isinstance(enhanced_activity.get("milestones", []), list), 
                             "Milestones serialized as array"),
                            (isinstance(enhanced_activity.get("progress_percentage"), (int, float)), 
                             "Progress percentage as number")
                        ]
                        
                        failed_serialization = [check[1] for check in serialization_checks if not check[0]]
                        
                        if not failed_serialization:
                            return self.log_result("GET /api/activities", True, 
                                                 "Enhanced activity appears with proper field serialization")
                        else:
                            return self.log_result("GET /api/activities", False, 
                                                 f"Serialization issues: {failed_serialization}")
                    else:
                        return self.log_result("GET /api/activities", False, 
                                             "Enhanced activity not found in activities list")
                else:
                    return self.log_result("GET /api/activities", False, 
                                         "No activities found or invalid response")
            else:
                return self.log_result("GET /api/activities", False, f"HTTP {response.status_code}")
        except Exception as e:
            return self.log_result("GET /api/activities", False, f"Request error: {str(e)}")
    
    def test_update_activity_progress(self):
        """Test 5: PUT /api/activities/{activity_id}/progress – update progress"""
        print("\n5️⃣ Testing PUT /api/activities/{activity_id}/progress...")
        
        if not self.activity_id:
            return self.log_result("PUT /api/activities/progress", False, "No activity ID available")
        
        try:
            progress_data = {
                "achieved_quantity": 25.0,  # 25 out of 50 participants (50% progress)
                "status_notes": "Training sessions 1-3 completed successfully. 25 participants completed basic modules.",
                "actual_output": "25 participants completed basic digital skills training",
                "comments": "Excellent participant engagement. Good progress in basic computer operations."
            }
            
            response = self.session.put(
                f"{self.base_url}/activities/{self.activity_id}/progress",
                json=progress_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    result_data = data.get("data", {})
                    
                    # Verify progress update results
                    progress_checks = [
                        (result_data.get("progress_percentage") == 50.0, 
                         "Progress percentage auto-calculated (25/50 = 50%)"),
                        (isinstance(result_data.get("completion_variance"), (int, float)), 
                         "Completion variance calculated"),
                        (isinstance(result_data.get("schedule_variance_days"), int), 
                         "Schedule variance days calculated"),
                        (result_data.get("risk_level") in ["low", "medium", "high"], 
                         "Risk level assessed")
                    ]
                    
                    failed_checks = [check[1] for check in progress_checks if not check[0]]
                    
                    if not failed_checks:
                        return self.log_result("PUT /api/activities/progress", True, 
                                             f"Progress updated: {result_data.get('progress_percentage')}% complete")
                    else:
                        return self.log_result("PUT /api/activities/progress", False, 
                                             f"Progress validation failed: {failed_checks}")
                else:
                    return self.log_result("PUT /api/activities/progress", False, 
                                         "Success flag not set in response")
            else:
                return self.log_result("PUT /api/activities/progress", False, f"HTTP {response.status_code}")
        except Exception as e:
            return self.log_result("PUT /api/activities/progress", False, f"Request error: {str(e)}")
    
    def test_get_activity_variance_analysis(self):
        """Test 6: GET /api/activities/{activity_id}/variance – returns variance analysis"""
        print("\n6️⃣ Testing GET /api/activities/{activity_id}/variance...")
        
        if not self.activity_id:
            return self.log_result("GET /api/activities/variance", False, "No activity ID available")
        
        try:
            response = self.session.get(f"{self.base_url}/activities/{self.activity_id}/variance")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    variance_data = data.get("data", {})
                    
                    # Verify variance analysis structure
                    variance_checks = [
                        ("schedule_variance" in variance_data, "Schedule variance analysis present"),
                        ("budget_variance" in variance_data, "Budget variance analysis present"),
                        ("output_variance" in variance_data, "Output variance analysis present"),
                        ("completion_variance" in variance_data, "Completion variance analysis present"),
                        ("risk_assessment" in variance_data, "Risk assessment present")
                    ]
                    
                    failed_checks = [check[1] for check in variance_checks if not check[0]]
                    
                    if not failed_checks:
                        return self.log_result("GET /api/activities/variance", True, 
                                             "Variance analysis structure returned correctly")
                    else:
                        return self.log_result("GET /api/activities/variance", False, 
                                             f"Variance structure issues: {failed_checks}")
                else:
                    return self.log_result("GET /api/activities/variance", False, 
                                         "Success flag not set in response")
            else:
                return self.log_result("GET /api/activities/variance", False, f"HTTP {response.status_code}")
        except Exception as e:
            return self.log_result("GET /api/activities/variance", False, f"Request error: {str(e)}")
    
    def test_edge_cases(self):
        """Test edge cases: empty milestones, ISO date parsing, ObjectId serialization"""
        print("\n🔍 Testing edge cases...")
        
        if not self.project_id:
            return self.log_result("Edge cases", False, "No project ID available")
        
        try:
            # Test empty milestones array
            activity_data_empty = {
                "project_id": self.project_id,
                "name": f"Edge Case Activity {uuid.uuid4().hex[:8]}",
                "assigned_to": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=14)).isoformat(),
                "budget_allocated": 100000.0,
                "planned_output": "Test output with no milestones",
                "target_quantity": 10.0,
                "milestones": []  # Empty array should be accepted
            }
            
            response = self.session.post(f"{self.base_url}/activities", json=activity_data_empty)
            empty_milestones_ok = response.status_code == 200
            
            # Test ISO date parsing in milestones
            activity_data_iso = {
                "project_id": self.project_id,
                "name": f"ISO Date Test Activity {uuid.uuid4().hex[:8]}",
                "assigned_to": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=16)).isoformat(),
                "budget_allocated": 150000.0,
                "milestones": [
                    {
                        "name": "ISO Date Milestone",
                        "planned_date": (datetime.now() + timedelta(days=8)).isoformat()
                    }
                ]
            }
            
            response = self.session.post(f"{self.base_url}/activities", json=activity_data_iso)
            iso_dates_ok = response.status_code == 200
            
            # Check for ObjectId serialization issues
            if iso_dates_ok:
                data = response.json()
                no_objectid_issues = (
                    isinstance(data.get("id") or data.get("_id"), str) and
                    not str(data.get("id", "")).startswith("ObjectId(")
                )
            else:
                no_objectid_issues = False
            
            edge_case_results = [
                (empty_milestones_ok, "Empty milestones array accepted"),
                (iso_dates_ok, "ISO date parsing working"),
                (no_objectid_issues, "No ObjectId serialization issues")
            ]
            
            failed_edge_cases = [check[1] for check in edge_case_results if not check[0]]
            
            if not failed_edge_cases:
                return self.log_result("Edge cases", True, 
                                     "All edge cases handled correctly")
            else:
                return self.log_result("Edge cases", False, 
                                     f"Edge case failures: {failed_edge_cases}")
                
        except Exception as e:
            return self.log_result("Edge cases", False, f"Request error: {str(e)}")
    
    def run_all_tests(self):
        """Run all enhanced activity creation tests"""
        print("=" * 80)
        print("TESTING ENHANCED ACTIVITY CREATION ENDPOINTS")
        print("CreateActivityModal refactor with milestones, planned/actual outputs")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping tests")
            return
        
        # Run tests in sequence
        results = []
        results.append(self.test_get_users_for_dropdown())
        results.append(self.test_create_minimal_project())
        results.append(self.test_create_enhanced_activity())
        results.append(self.test_get_activities_serialization())
        results.append(self.test_update_activity_progress())
        results.append(self.test_get_activity_variance_analysis())
        results.append(self.test_edge_cases())
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📈 Success Rate: {(passed/total*100):.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Enhanced activity creation endpoints are working correctly.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please check the details above.")

def main():
    """Run enhanced activity creation tests"""
    tester = EnhancedActivityTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()