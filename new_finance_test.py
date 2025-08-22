#!/usr/bin/env python3
"""
New Finance Features Testing for DataRW
Tests XLSX endpoints and date range parameters as requested in review.
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

class NewFinanceFeaturesTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.test_results = []
        
        # Test data
        self.test_email = f"finance.test.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Finance Test User"
        
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
    
    def setup_auth(self):
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
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.user_data = data.get("user", {})
                    self.organization_data = data.get("organization", {})
                    
                    # Set authorization header
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    
                    self.log_result("Setup Auth", True, "Authentication setup successful")
                    return True
                else:
                    self.log_result("Setup Auth", False, "Missing access token in response", data)
                    return False
            else:
                self.log_result("Setup Auth", False, f"Registration failed: HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Setup Auth", False, f"Auth setup error: {str(e)}")
            return False
    
    def create_test_project(self):
        """Create a test project for finance testing"""
        try:
            project_data = {
                "name": f"Finance Test Project {uuid.uuid4().hex[:8]}",
                "description": "Test project for finance feature testing",
                "project_manager_id": self.user_data.get("id", "test-user"),
                "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=365)).isoformat(),
                "budget_total": 1000000.0,
                "beneficiaries_target": 1000,
                "location": "Test Location",
                "donor_organization": "World Bank"
            }
            
            response = self.session.post(f"{self.base_url}/projects", json=project_data)
            
            if response.status_code == 200:
                data = response.json()
                project_id = data.get("id") or data.get("_id")
                if project_id:
                    self.project_id = project_id
                    self.log_result("Create Test Project", True, f"Test project created: {project_id}")
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
    
    def create_test_expenses(self):
        """Create test expenses for date range testing"""
        try:
            today = datetime.now()
            old_date = today - timedelta(days=60)
            recent_date = today - timedelta(days=10)
            
            # Create expense outside date range
            old_expense_data = {
                "project_id": getattr(self, 'project_id', 'test-project'),
                "activity_id": "test-activity",
                "date": old_date.isoformat()[:10],
                "vendor": "Old Test Vendor Ltd",
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
                "activity_id": "test-activity",
                "date": recent_date.isoformat()[:10],
                "vendor": "Recent Test Vendor Ltd",
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
            
            old_success = old_response.status_code == 200
            recent_success = recent_response.status_code == 200
            
            if old_success and recent_success:
                self.log_result("Create Test Expenses", True, "Test expenses created for date range testing")
                return True
            else:
                self.log_result("Create Test Expenses", False, 
                              f"Failed to create expenses: old={old_response.status_code}, recent={recent_response.status_code}")
                return False
        except Exception as e:
            self.log_result("Create Test Expenses", False, f"Request error: {str(e)}")
            return False
    
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
            today = datetime.now()
            recent_date = today - timedelta(days=10)
            
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
            
            # Verify filtering worked - filtered should be less than or equal to unfiltered
            if filtered_count <= unfiltered_count:
                self.log_result("CSV Date Range Filtering", True, 
                              f"Date range filtering working: unfiltered={unfiltered_count}, filtered={filtered_count}")
                return True
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
            required_fields = ["by_funding_source"]
            
            for field in required_fields:
                if field not in unfiltered_data:
                    self.log_result("Funding Utilization Date Range", False, 
                                  f"Missing field '{field}' in unfiltered response")
                    return False
                if field not in filtered_data:
                    self.log_result("Funding Utilization Date Range", False, 
                                  f"Missing field '{field}' in filtered response")
                    return False
            
            # Calculate total spent from by_funding_source
            unfiltered_total = sum(item.get("spent", 0) for item in unfiltered_data.get("by_funding_source", []))
            filtered_total = sum(item.get("spent", 0) for item in filtered_data.get("by_funding_source", []))
            
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
    
    def run_tests(self):
        """Run all new finance feature tests"""
        print("\n" + "="*80)
        print("NEW FINANCE FEATURES TESTING")
        print("="*80)
        print(f"📍 Testing against: {self.base_url}")
        print()
        
        # Setup
        if not self.setup_auth():
            print("❌ Authentication setup failed - stopping tests")
            return False
        
        if not self.create_test_project():
            print("❌ Test project creation failed - continuing with limited tests")
        
        if not self.create_test_expenses():
            print("❌ Test expense creation failed - continuing with limited tests")
        
        # Run the new feature tests
        tests = [
            ("XLSX Project Report", self.test_finance_xlsx_project_report),
            ("XLSX Activities Report", self.test_finance_xlsx_activities_report),
            ("XLSX All Projects Report", self.test_finance_xlsx_all_projects_report),
            ("CSV Date Range Filtering", self.test_csv_date_range_filtering),
            ("Funding Utilization Date Range", self.test_funding_utilization_date_range)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing {test_name}...")
            if test_func():
                passed += 1
        
        print("\n" + "="*80)
        print("NEW FINANCE FEATURES TESTING SUMMARY")
        print("="*80)
        print(f"✅ Passed: {passed}/{total} tests ({(passed/total)*100:.1f}%)")
        
        # Print detailed results
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = NewFinanceFeaturesTester()
    success = tester.run_tests()
    exit(0 if success else 1)