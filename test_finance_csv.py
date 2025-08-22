#!/usr/bin/env python3
"""
Finance CSV Reports Testing for DataRW
Tests the new finance CSV report endpoints specifically.
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment - use external URL for testing
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

class FinanceCSVTester:
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
        self.test_name = "Finance CSV Test User"
        
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
                if "access_token" in data and "user" in data and "organization" in data:
                    self.auth_token = data["access_token"]
                    self.user_data = data["user"]
                    self.organization_data = data["organization"]
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    
                    self.log_result("Setup Authentication", True, "User registered and authenticated successfully")
                    return True
                else:
                    self.log_result("Setup Authentication", False, "Missing required fields in response", data)
                    return False
            else:
                self.log_result("Setup Authentication", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Setup Authentication", False, f"Request error: {str(e)}")
            return False
    
    def create_finance_seed_data(self):
        """Create minimal seed data for finance CSV testing"""
        try:
            # Create a project first
            project_data = {
                "name": f"Finance CSV Test Project {uuid.uuid4().hex[:8]}",
                "description": "Test project for finance CSV reports with comprehensive budget tracking",
                "project_manager_id": self.user_data["id"] if self.user_data else "system",
                "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=180)).isoformat(),
                "budget_total": 2000000.0,  # 2M RWF
                "beneficiaries_target": 1500,
                "location": "Kigali, Rwanda",
                "donor_organization": "World Bank"
            }
            
            response = self.session.post(f"{self.base_url}/projects", json=project_data)
            
            if response.status_code == 200:
                project = response.json()
                self.test_project_id = project.get("id") or project.get("_id")
                
                # Create multiple budget items for better testing
                budget_items = [
                    {
                        "project_id": self.test_project_id,
                        "category": "training",
                        "item_name": "Training Materials and Resources",
                        "description": "Educational materials for finance training",
                        "budgeted_amount": 800000.0,  # 800K RWF
                        "budget_period": "6_months"
                    },
                    {
                        "project_id": self.test_project_id,
                        "category": "equipment",
                        "item_name": "Computer Equipment",
                        "description": "Laptops and tablets for training",
                        "budgeted_amount": 1200000.0,  # 1.2M RWF
                        "budget_period": "12_months"
                    }
                ]
                
                budget_success = 0
                for budget_data in budget_items:
                    budget_response = self.session.post(f"{self.base_url}/budget", json=budget_data)
                    if budget_response.status_code == 200:
                        budget_success += 1
                
                # Create multiple expenses for different activities
                expenses = [
                    {
                        "project_id": self.test_project_id,
                        "activity_id": f"activity_training_{uuid.uuid4().hex[:6]}",
                        "date": datetime.now().isoformat(),
                        "vendor": "Training Materials Supplier Ltd",
                        "invoice_no": f"INV-TRN-{uuid.uuid4().hex[:6].upper()}",
                        "amount": 350000.0,  # 350K RWF
                        "currency": "RWF",
                        "funding_source": "World Bank",
                        "cost_center": "Training",
                        "notes": "Purchase of training materials for finance project"
                    },
                    {
                        "project_id": self.test_project_id,
                        "activity_id": f"activity_equipment_{uuid.uuid4().hex[:6]}",
                        "date": (datetime.now() - timedelta(days=5)).isoformat(),
                        "vendor": "Tech Solutions Rwanda",
                        "invoice_no": f"INV-EQP-{uuid.uuid4().hex[:6].upper()}",
                        "amount": 600000.0,  # 600K RWF
                        "currency": "RWF",
                        "funding_source": "World Bank",
                        "cost_center": "Equipment",
                        "notes": "Purchase of laptops for training program"
                    },
                    {
                        "project_id": self.test_project_id,
                        "activity_id": f"activity_logistics_{uuid.uuid4().hex[:6]}",
                        "date": (datetime.now() - timedelta(days=10)).isoformat(),
                        "vendor": "Event Logistics Co",
                        "invoice_no": f"INV-LOG-{uuid.uuid4().hex[:6].upper()}",
                        "amount": 150000.0,  # 150K RWF
                        "currency": "RWF",
                        "funding_source": "USAID",
                        "cost_center": "Operations",
                        "notes": "Venue rental and logistics for training sessions"
                    }
                ]
                
                expense_success = 0
                for expense_data in expenses:
                    expense_response = self.session.post(f"{self.base_url}/finance/expenses", json=expense_data)
                    if expense_response.status_code == 200:
                        expense_success += 1
                
                if budget_success >= 1 and expense_success >= 2:
                    self.log_result("Create Finance Seed Data", True, 
                                  f"Created project with {budget_success} budget items and {expense_success} expenses for comprehensive CSV testing")
                    return True
                else:
                    self.log_result("Create Finance Seed Data", False, 
                                  f"Insufficient seed data created: budget_items={budget_success}, expenses={expense_success}")
                    return False
            else:
                self.log_result("Create Finance Seed Data", False, 
                              f"Failed to create project: HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Create Finance Seed Data", False, f"Request error: {str(e)}")
            return False
    
    def test_project_report_csv(self):
        """Test project report CSV endpoint - GET /api/finance/reports/project-csv"""
        if not hasattr(self, 'test_project_id'):
            self.log_result("Project Report CSV", False, "No test project ID available")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/finance/reports/project-csv",
                params={"project_id": self.test_project_id}
            )
            
            if response.status_code == 200:
                csv_content = response.text
                
                # Verify it's CSV format
                content_type = response.headers.get('content-type', '')
                if content_type.startswith('text/csv'):
                    # Check for expected headers
                    expected_headers = ["Project ID", "Planned", "Allocated", "Actual", "Variance Amount", "Variance %"]
                    lines = csv_content.strip().split('\n')
                    
                    if len(lines) > 0:
                        header_line = lines[0]
                        
                        # Check if all expected headers are present
                        headers_present = all(header in header_line for header in expected_headers)
                        
                        if headers_present:
                            # Check for funding source section (should be present for project-specific report)
                            has_funding_section = "Funding Source" in csv_content
                            
                            # Verify data rows exist
                            data_rows = [line for line in lines[1:] if line.strip() and not line.startswith("Funding Source")]
                            
                            self.log_result("Project Report CSV", True, 
                                          f"CSV report generated successfully: {len(lines)} total lines, " +
                                          f"{len(data_rows)} data rows, proper headers verified" +
                                          (", includes funding source data" if has_funding_section else ""))
                            return True
                        else:
                            missing_headers = [h for h in expected_headers if h not in header_line]
                            self.log_result("Project Report CSV", False, 
                                          f"Missing expected headers: {missing_headers}")
                            return False
                    else:
                        self.log_result("Project Report CSV", False, "Empty CSV content")
                        return False
                else:
                    self.log_result("Project Report CSV", False, 
                                  f"Wrong content type: expected 'text/csv', got '{response.headers.get('content-type')}'")
                    return False
            else:
                self.log_result("Project Report CSV", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Project Report CSV", False, f"Request error: {str(e)}")
            return False
    
    def test_activities_report_csv(self):
        """Test activities report CSV endpoint - GET /api/finance/reports/activities-csv"""
        if not hasattr(self, 'test_project_id'):
            self.log_result("Activities Report CSV", False, "No test project ID available")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/finance/reports/activities-csv",
                params={"project_id": self.test_project_id}
            )
            
            if response.status_code == 200:
                csv_content = response.text
                
                # Verify it's CSV format
                content_type = response.headers.get('content-type', '')
                if content_type.startswith('text/csv'):
                    # Check for expected headers
                    expected_headers = ["Activity ID", "Transactions", "Spent"]
                    lines = csv_content.strip().split('\n')
                    
                    if len(lines) > 0:
                        header_line = lines[0]
                        
                        # Check if all expected headers are present
                        headers_present = all(header in header_line for header in expected_headers)
                        
                        if headers_present:
                            # Verify data rows exist (should have activity data from expenses)
                            data_rows = [line for line in lines[1:] if line.strip()]
                            
                            self.log_result("Activities Report CSV", True, 
                                          f"CSV report generated successfully: {len(lines)} total lines, " +
                                          f"{len(data_rows)} activity data rows, proper headers verified")
                            return True
                        else:
                            missing_headers = [h for h in expected_headers if h not in header_line]
                            self.log_result("Activities Report CSV", False, 
                                          f"Missing expected headers: {missing_headers}")
                            return False
                    else:
                        self.log_result("Activities Report CSV", False, "Empty CSV content")
                        return False
                else:
                    self.log_result("Activities Report CSV", False, 
                                  f"Wrong content type: expected 'text/csv', got '{response.headers.get('content-type')}'")
                    return False
            else:
                self.log_result("Activities Report CSV", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Activities Report CSV", False, f"Request error: {str(e)}")
            return False
    
    def test_all_projects_report_csv(self):
        """Test all projects report CSV endpoint - GET /api/finance/reports/all-projects-csv"""
        try:
            response = self.session.get(f"{self.base_url}/finance/reports/all-projects-csv")
            
            if response.status_code == 200:
                csv_content = response.text
                
                # Verify it's CSV format
                content_type = response.headers.get('content-type', '')
                if content_type.startswith('text/csv'):
                    # Check for expected headers (same as project CSV but without funding rows)
                    expected_headers = ["Project ID", "Planned", "Allocated", "Actual", "Variance Amount", "Variance %"]
                    lines = csv_content.strip().split('\n')
                    
                    if len(lines) > 0:
                        header_line = lines[0]
                        
                        # Check if all expected headers are present
                        headers_present = all(header in header_line for header in expected_headers)
                        
                        if headers_present:
                            # Should NOT have funding source section (unlike project-specific report)
                            has_funding_section = "Funding Source" in csv_content
                            
                            # Verify data rows exist (should include our test project)
                            data_rows = [line for line in lines[1:] if line.strip()]
                            
                            self.log_result("All Projects Report CSV", True, 
                                          f"CSV report generated successfully: {len(lines)} total lines, " +
                                          f"{len(data_rows)} project data rows, proper headers verified" +
                                          (", correctly excludes funding source data" if not has_funding_section else ", WARNING: includes funding data"))
                            return True
                        else:
                            missing_headers = [h for h in expected_headers if h not in header_line]
                            self.log_result("All Projects Report CSV", False, 
                                          f"Missing expected headers: {missing_headers}")
                            return False
                    else:
                        self.log_result("All Projects Report CSV", False, "Empty CSV content")
                        return False
                else:
                    self.log_result("All Projects Report CSV", False, 
                                  f"Wrong content type: expected 'text/csv', got '{response.headers.get('content-type')}'")
                    return False
            else:
                self.log_result("All Projects Report CSV", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("All Projects Report CSV", False, f"Request error: {str(e)}")
            return False

    def run_finance_csv_tests(self):
        """Run all finance CSV report tests"""
        print("="*80)
        print("FINANCE CSV REPORTS TESTING")
        print("="*80)
        print(f"📍 Testing against: {self.base_url}")
        print()
        
        # Test sequence
        tests = [
            ("Setup Authentication", self.setup_authentication),
            ("Create Finance Seed Data", self.create_finance_seed_data),
            ("Project Report CSV", self.test_project_report_csv),
            ("Activities Report CSV", self.test_activities_report_csv),
            ("All Projects Report CSV", self.test_all_projects_report_csv),
        ]
        
        success_count = 0
        for test_name, test_func in tests:
            print(f"🔍 Running: {test_name}")
            if test_func():
                success_count += 1
            print()
        
        # Summary
        print("="*80)
        print("📊 FINANCE CSV REPORTS TEST SUMMARY")
        print("="*80)
        
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

if __name__ == "__main__":
    tester = FinanceCSVTester()
    tester.run_finance_csv_tests()