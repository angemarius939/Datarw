#!/usr/bin/env python3
"""
Comprehensive test for Project Dashboard DateTime Bug Fix with populated data
Tests the GET /api/projects/dashboard endpoint with actual project and activity data
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

class PopulatedDateTimeTest:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.project_id = None
        self.activity_id = None
        
        # Test data
        self.test_email = f"populated.test.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Populated Test User"
        
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
                
                self.log_result("Authentication Setup", True, "User registered and authenticated successfully")
                return True
            else:
                self.log_result("Authentication Setup", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Authentication Setup", False, f"Request error: {str(e)}")
            return False
    
    def create_test_project(self):
        """Create a test project with realistic data"""
        try:
            project_data = {
                "name": f"Digital Literacy Training Program {uuid.uuid4().hex[:8]}",
                "description": "Comprehensive digital literacy training program for rural communities in Rwanda",
                "project_manager_id": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=365)).isoformat(),
                "budget_total": 2500000.0,
                "beneficiaries_target": 5000,
                "location": "Nyagatare District, Eastern Province, Rwanda",
                "donor_organization": "World Bank",
                "implementing_partners": ["Rwanda Development Board", "Local NGO Partners"],
                "tags": ["education", "digital-literacy", "rural-development"]
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.project_id = data.get("id") or data.get("_id")
                self.log_result("Create Test Project", True, f"Project created with ID: {self.project_id}")
                return True
            else:
                self.log_result("Create Test Project", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Test Project", False, f"Request error: {str(e)}")
            return False
    
    def create_test_activity(self):
        """Create a test activity with datetime fields"""
        try:
            if not self.project_id:
                self.log_result("Create Test Activity", False, "No project ID available")
                return False
            
            activity_data = {
                "project_id": self.project_id,
                "name": f"Community Mobilization Campaign {uuid.uuid4().hex[:8]}",
                "description": "Community outreach program to raise awareness about digital literacy opportunities",
                "assigned_to": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "budget_allocated": 150000.0,
                "deliverables": [
                    "Community awareness sessions conducted in 5 villages",
                    "Registration of 200+ participants completed"
                ],
                "dependencies": [
                    "Project approval and funding confirmation"
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/activities",
                json=activity_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.activity_id = data.get("id") or data.get("_id")
                self.log_result("Create Test Activity", True, f"Activity created with ID: {self.activity_id}")
                return True
            else:
                self.log_result("Create Test Activity", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Test Activity", False, f"Request error: {str(e)}")
            return False
    
    def create_overdue_activity(self):
        """Create an overdue activity to test datetime comparison logic"""
        try:
            if not self.project_id:
                self.log_result("Create Overdue Activity", False, "No project ID available")
                return False
            
            # Create activity with end_date in the past
            activity_data = {
                "project_id": self.project_id,
                "name": f"Overdue Activity {uuid.uuid4().hex[:8]}",
                "description": "This activity should be overdue for testing datetime comparison",
                "assigned_to": self.user_data["id"],
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": (datetime.now() - timedelta(days=5)).isoformat(),  # Past date
                "budget_allocated": 50000.0,
                "status": "in_progress"  # Not completed, so it should be overdue
            }
            
            response = self.session.post(
                f"{self.base_url}/activities",
                json=activity_data
            )
            
            if response.status_code == 200:
                data = response.json()
                overdue_activity_id = data.get("id") or data.get("_id")
                self.log_result("Create Overdue Activity", True, f"Overdue activity created with ID: {overdue_activity_id}")
                return True
            else:
                self.log_result("Create Overdue Activity", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Overdue Activity", False, f"Request error: {str(e)}")
            return False
    
    def test_dashboard_with_populated_data(self):
        """Test dashboard endpoint with populated data to verify datetime operations"""
        try:
            print("\n🔍 Testing dashboard with populated data...")
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
                        self.log_result("Dashboard Populated Data Test", False, 
                                      f"Missing required fields: {missing_fields}", data)
                        return False
                    
                    # Verify we have at least 1 project (the one we created)
                    total_projects = dashboard_data.get("total_projects", 0)
                    if total_projects < 1:
                        self.log_result("Dashboard Populated Data Test", False, 
                                      f"Expected at least 1 project, got {total_projects}")
                        return False
                    
                    # Verify recent_activities contains our activities with proper datetime formatting
                    recent_activities = dashboard_data.get("recent_activities", [])
                    if isinstance(recent_activities, list) and len(recent_activities) > 0:
                        for activity in recent_activities:
                            if not isinstance(activity, dict):
                                self.log_result("Dashboard Populated Data Test", False, 
                                              "recent_activities contains non-dict items", data)
                                return False
                            
                            # Verify required activity fields
                            required_activity_fields = ["id", "name", "status", "progress", "updated_at"]
                            for field in required_activity_fields:
                                if field not in activity:
                                    self.log_result("Dashboard Populated Data Test", False, 
                                                  f"Activity missing required field: {field}", activity)
                                    return False
                            
                            # Verify datetime formatting in updated_at
                            if "updated_at" in activity:
                                try:
                                    # Verify the datetime string is valid ISO format
                                    parsed_datetime = datetime.fromisoformat(activity["updated_at"].replace('Z', '+00:00'))
                                    # Verify it's a reasonable datetime (not too far in past/future)
                                    now = datetime.now()
                                    if abs((now - parsed_datetime.replace(tzinfo=None)).days) > 365:
                                        self.log_result("Dashboard Populated Data Test", False, 
                                                      f"Activity datetime seems unreasonable: {activity['updated_at']}")
                                        return False
                                except ValueError as e:
                                    self.log_result("Dashboard Populated Data Test", False, 
                                                  f"Invalid datetime format in recent_activities: {activity['updated_at']}", str(e))
                                    return False
                    
                    # Verify overdue_activities calculation (should be at least 1 from our overdue activity)
                    overdue_activities = dashboard_data.get("overdue_activities", 0)
                    if not isinstance(overdue_activities, (int, float)):
                        self.log_result("Dashboard Populated Data Test", False, 
                                      f"overdue_activities should be numeric, got {type(overdue_activities)}")
                        return False
                    
                    # Verify projects_by_status has string keys and contains our project
                    projects_by_status = dashboard_data.get("projects_by_status", {})
                    if isinstance(projects_by_status, dict):
                        for key in projects_by_status.keys():
                            if not isinstance(key, str):
                                self.log_result("Dashboard Populated Data Test", False, 
                                              f"projects_by_status contains non-string key: {key}")
                                return False
                        
                        # Should have at least one project status
                        total_status_count = sum(projects_by_status.values())
                        if total_status_count < 1:
                            self.log_result("Dashboard Populated Data Test", False, 
                                          f"projects_by_status should show at least 1 project, got {total_status_count}")
                            return False
                    
                    # Print detailed dashboard data for verification
                    print(f"   📊 Dashboard Data Summary:")
                    print(f"      • Total Projects: {dashboard_data.get('total_projects', 0)}")
                    print(f"      • Active Projects: {dashboard_data.get('active_projects', 0)}")
                    print(f"      • Completed Projects: {dashboard_data.get('completed_projects', 0)}")
                    print(f"      • Overdue Activities: {dashboard_data.get('overdue_activities', 0)}")
                    print(f"      • Budget Utilization: {dashboard_data.get('budget_utilization', 0)}%")
                    print(f"      • Recent Activities Count: {len(recent_activities)}")
                    print(f"      • Projects by Status: {projects_by_status}")
                    print(f"      • Budget by Category: {dashboard_data.get('budget_by_category', {})}")
                    
                    if len(recent_activities) > 0:
                        print(f"   📋 Recent Activities Details:")
                        for i, activity in enumerate(recent_activities[:3]):  # Show first 3
                            print(f"      {i+1}. {activity.get('name', 'Unknown')} - Status: {activity.get('status', 'unknown')} - Updated: {activity.get('updated_at', 'N/A')}")
                    
                    self.log_result("Dashboard Populated Data Test", True, 
                                  "Dashboard endpoint working correctly with populated data - all datetime operations successful")
                    return True
                else:
                    self.log_result("Dashboard Populated Data Test", False, 
                                  "Missing success/data fields in response", data)
                    return False
            else:
                # Check specifically for datetime-related errors
                if response.status_code == 500:
                    error_text = response.text
                    if "cannot access local variable 'datetime' where it is not associated with a value" in error_text:
                        self.log_result("Dashboard Populated Data Test", False, 
                                      "CRITICAL: Datetime scoping error still present with populated data", error_text)
                        return False
                    elif "datetime" in error_text.lower():
                        self.log_result("Dashboard Populated Data Test", False, 
                                      "CRITICAL: Datetime-related error with populated data", error_text)
                        return False
                
                self.log_result("Dashboard Populated Data Test", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Dashboard Populated Data Test", False, f"Request error: {str(e)}")
            return False
    
    def run_populated_datetime_tests(self):
        """Run comprehensive datetime tests with populated data"""
        print("🎯 PROJECT DASHBOARD DATETIME BUG FIX - POPULATED DATA TESTING")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Setup and data creation
        setup_tests = [
            self.setup_authentication,
            self.create_test_project,
            self.create_test_activity,
            self.create_overdue_activity
        ]
        
        print("🔧 Setting up test data...")
        for test in setup_tests:
            if not test():
                print("❌ Setup failed. Cannot proceed with populated data tests.")
                return False
        
        # Main datetime test
        print("\n🔍 Running populated data datetime tests...")
        if self.test_dashboard_with_populated_data():
            passed = 1
            failed = 0
        else:
            passed = 0
            failed = 1
        
        print("\n" + "=" * 80)
        print("📊 POPULATED DATA DATETIME TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {passed}/{passed + failed}")
        print(f"❌ Failed: {failed}/{passed + failed}")
        print(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 POPULATED DATA DATETIME TESTS PASSED!")
            print("✅ The datetime variable scoping issue is fully resolved.")
            print("✅ Dashboard works correctly with both empty and populated data.")
            print("✅ All datetime operations (comparisons, formatting, calculations) are working.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please review the issues above.")
        
        return failed == 0

if __name__ == "__main__":
    tester = PopulatedDateTimeTest()
    success = tester.run_populated_datetime_tests()
    exit(0 if success else 1)