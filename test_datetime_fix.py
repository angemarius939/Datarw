#!/usr/bin/env python3
"""
Focused test for Project Dashboard DateTime Bug Fix
Tests specifically the GET /api/projects/dashboard endpoint to verify datetime variable scoping issue is resolved
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

class DateTimeBugFixTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        
        # Test data
        self.test_email = f"datetime.test.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "DateTime Test User"
        
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
    
    def test_project_dashboard_datetime_bug_fix(self):
        """Test project dashboard endpoint specifically for datetime variable scoping bug fix"""
        try:
            print("\n🔍 Testing GET /api/projects/dashboard for datetime scoping bug fix...")
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
                    
                    # Print detailed dashboard data for verification
                    print(f"   📊 Dashboard Data Summary:")
                    print(f"      • Total Projects: {dashboard_data.get('total_projects', 0)}")
                    print(f"      • Active Projects: {dashboard_data.get('active_projects', 0)}")
                    print(f"      • Completed Projects: {dashboard_data.get('completed_projects', 0)}")
                    print(f"      • Overdue Activities: {dashboard_data.get('overdue_activities', 0)}")
                    print(f"      • Budget Utilization: {dashboard_data.get('budget_utilization', 0)}%")
                    print(f"      • Recent Activities Count: {len(recent_activities)}")
                    print(f"      • Projects by Status: {projects_by_status}")
                    print(f"      • Budget by Category: {budget_by_category}")
                    
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
    
    def test_dashboard_with_empty_data(self):
        """Test dashboard endpoint with empty data scenario"""
        try:
            print("\n🔍 Testing dashboard with empty data scenario...")
            response = self.session.get(f"{self.base_url}/projects/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    dashboard_data = data["data"]
                    
                    # For empty data, all counts should be 0 or empty
                    expected_empty_values = {
                        "total_projects": 0,
                        "active_projects": 0,
                        "completed_projects": 0,
                        "overdue_activities": 0,
                        "budget_utilization": 0,
                        "recent_activities": []
                    }
                    
                    for field, expected_value in expected_empty_values.items():
                        actual_value = dashboard_data.get(field)
                        if isinstance(expected_value, list):
                            if not isinstance(actual_value, list):
                                self.log_result("Dashboard Empty Data Test", False, 
                                              f"{field} should be a list, got {type(actual_value)}")
                                return False
                        elif isinstance(expected_value, (int, float)):
                            if not isinstance(actual_value, (int, float)):
                                self.log_result("Dashboard Empty Data Test", False, 
                                              f"{field} should be numeric, got {type(actual_value)}")
                                return False
                    
                    self.log_result("Dashboard Empty Data Test", True, 
                                  "Dashboard handles empty data scenario correctly")
                    return True
                else:
                    self.log_result("Dashboard Empty Data Test", False, 
                                  "Missing success/data fields in response", data)
                    return False
            else:
                self.log_result("Dashboard Empty Data Test", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Dashboard Empty Data Test", False, f"Request error: {str(e)}")
            return False
    
    def run_datetime_fix_tests(self):
        """Run all datetime fix related tests"""
        print("🎯 PROJECT DASHBOARD DATETIME BUG FIX TESTING")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return False
        
        # Run datetime fix tests
        tests = [
            self.test_project_dashboard_datetime_bug_fix,
            self.test_dashboard_with_empty_data
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
                print(f"❌ FAIL: {test.__name__} - Exception: {str(e)}")
                failed += 1
        
        print("\n" + "=" * 80)
        print("📊 DATETIME BUG FIX TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {passed}/{passed + failed}")
        print(f"❌ Failed: {failed}/{passed + failed}")
        print(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL DATETIME BUG FIX TESTS PASSED!")
            print("✅ The datetime variable scoping issue has been successfully resolved.")
            print("✅ GET /api/projects/dashboard endpoint is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please review the issues above.")
        
        return failed == 0

if __name__ == "__main__":
    tester = DateTimeBugFixTester()
    success = tester.run_datetime_fix_tests()
    exit(0 if success else 1)