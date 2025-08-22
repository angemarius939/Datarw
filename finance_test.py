#!/usr/bin/env python3
"""
Finance Phase 1 Backend Testing
Tests the newly added finance endpoints as requested in the review.
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

class FinanceAPITester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
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
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    self.log_result("Setup Authentication", True, "User registered and authenticated")
                    return True
                else:
                    self.log_result("Setup Authentication", False, "No access token in response", data)
                    return False
            else:
                self.log_result("Setup Authentication", False, f"Registration failed: HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Setup Authentication", False, f"Setup error: {str(e)}")
            return False

    def test_finance_config_get_default(self):
        """Test GET /api/finance/config returns default config when not configured"""
        try:
            response = self.session.get(f"{self.base_url}/finance/config")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["organization_id", "funding_sources", "cost_centers", "updated_at"]
                
                if all(field in data for field in required_fields):
                    # Check default funding sources
                    default_sources = ["World Bank", "Mastercard Foundation", "USAID", "UNDP"]
                    if all(source in data["funding_sources"] for source in default_sources):
                        # Check default cost centers
                        default_centers = ["HR", "Operations", "Field Work", "M&E", "Project officers"]
                        if all(center in data["cost_centers"] for center in default_centers):
                            self.log_result("Finance Config - Get Default", True, 
                                          f"Default config returned with {len(data['funding_sources'])} funding sources and {len(data['cost_centers'])} cost centers")
                            return True
                        else:
                            self.log_result("Finance Config - Get Default", False, "Missing default cost centers", data)
                            return False
                    else:
                        self.log_result("Finance Config - Get Default", False, "Missing default funding sources", data)
                        return False
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("Finance Config - Get Default", False, f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("Finance Config - Get Default", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance Config - Get Default", False, f"Request error: {str(e)}")
            return False

    def test_finance_config_update_and_persist(self):
        """Test PUT /api/finance/config with custom config and verify persistence"""
        try:
            # Update config with custom values
            config_data = {
                "funding_sources": ["World Bank", "USAID"],
                "cost_centers": ["HR", "Field Work"]
            }
            
            response = self.session.put(
                f"{self.base_url}/finance/config",
                json=config_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("funding_sources") == config_data["funding_sources"] and 
                    data.get("cost_centers") == config_data["cost_centers"]):
                    
                    # Verify persistence by getting config again
                    get_response = self.session.get(f"{self.base_url}/finance/config")
                    if get_response.status_code == 200:
                        get_data = get_response.json()
                        if (get_data.get("funding_sources") == config_data["funding_sources"] and 
                            get_data.get("cost_centers") == config_data["cost_centers"]):
                            self.log_result("Finance Config - Update and Persist", True, 
                                          "Config updated and persisted successfully")
                            return True
                        else:
                            self.log_result("Finance Config - Update and Persist", False, 
                                          "Config not persisted correctly", get_data)
                            return False
                    else:
                        self.log_result("Finance Config - Update and Persist", False, 
                                      f"Failed to verify persistence: HTTP {get_response.status_code}")
                        return False
                else:
                    self.log_result("Finance Config - Update and Persist", False, "Config not updated correctly", data)
                    return False
            else:
                self.log_result("Finance Config - Update and Persist", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance Config - Update and Persist", False, f"Request error: {str(e)}")
            return False

    def create_simple_project(self):
        """Create a simple project for expense testing"""
        try:
            project_data = {
                "name": f"Finance Test Project {uuid.uuid4().hex[:8]}",
                "description": "Simple project for finance testing",
                "budget_total": 10000.0
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
                    self.log_result("Create Simple Project", True, "Project created for expense testing")
                    return True
                else:
                    self.log_result("Create Simple Project", False, "No project ID in response", data)
                    return False
            else:
                self.log_result("Create Simple Project", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Simple Project", False, f"Request error: {str(e)}")
            return False

    def test_create_expense(self):
        """Test POST /api/finance/expenses with valid expense data"""
        if not hasattr(self, 'project_id'):
            self.log_result("Create Expense", False, "No project ID available for expense creation")
            return False
        
        try:
            expense_data = {
                "project_id": self.project_id,
                "date": datetime.now().isoformat(),
                "amount": 1234.56,
                "currency": "USD",
                "vendor": "ABC Ltd",
                "funding_source": "World Bank",
                "cost_center": "Field Work",
                "invoice_no": f"INV-{uuid.uuid4().hex[:8]}",
                "notes": "Test expense for finance system validation"
            }
            
            response = self.session.post(
                f"{self.base_url}/finance/expenses",
                json=expense_data
            )
            
            if response.status_code == 200:
                data = response.json()
                expense_id = data.get("id")
                if (expense_id and 
                    data.get("amount") == expense_data["amount"] and
                    data.get("vendor") == expense_data["vendor"] and
                    data.get("funding_source") == expense_data["funding_source"]):
                    
                    self.expense_id = expense_id
                    self.log_result("Create Expense", True, 
                                  f"Expense created successfully: {expense_data['amount']} {expense_data['currency']} to {expense_data['vendor']}")
                    return True
                else:
                    self.log_result("Create Expense", False, "Expense data mismatch", data)
                    return False
            else:
                self.log_result("Create Expense", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Expense", False, f"Request error: {str(e)}")
            return False

    def test_list_expenses_with_pagination_and_filters(self):
        """Test GET /api/finance/expenses with filters and pagination"""
        try:
            # Test with vendor filter and pagination
            params = {
                "vendor": "ABC",  # Substring search
                "page": 1,
                "page_size": 1
            }
            
            response = self.session.get(
                f"{self.base_url}/finance/expenses",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["items", "total", "page", "page_size"]
                
                if all(field in data for field in required_fields):
                    items = data["items"]
                    if isinstance(items, list):
                        # Verify pagination
                        if data["page"] == 1 and data["page_size"] == 1:
                            self.log_result("List Expenses - Pagination and Filters", True, 
                                          f"Retrieved {len(items)} expenses with pagination (page 1, size 1) and vendor filter")
                            return True
                        else:
                            self.log_result("List Expenses - Pagination and Filters", False, 
                                          "Pagination parameters not respected", data)
                            return False
                    else:
                        self.log_result("List Expenses - Pagination and Filters", False, 
                                      "Items field is not a list", data)
                        return False
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("List Expenses - Pagination and Filters", False, 
                                  f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("List Expenses - Pagination and Filters", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("List Expenses - Pagination and Filters", False, f"Request error: {str(e)}")
            return False

    def test_update_expense(self):
        """Test PUT /api/finance/expenses/{id} to update expense"""
        if not hasattr(self, 'expense_id'):
            self.log_result("Update Expense", False, "No expense ID available for update")
            return False
        
        try:
            update_data = {
                "amount": 2000.00,
                "vendor": "XYZ Corporation",
                "notes": "Updated expense for testing"
            }
            
            response = self.session.put(
                f"{self.base_url}/finance/expenses/{self.expense_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("amount") == update_data["amount"] and
                    data.get("vendor") == update_data["vendor"] and
                    data.get("notes") == update_data["notes"]):
                    
                    self.log_result("Update Expense", True, 
                                  f"Expense updated successfully: amount changed to {update_data['amount']}, vendor to {update_data['vendor']}")
                    return True
                else:
                    self.log_result("Update Expense", False, "Expense not updated correctly", data)
                    return False
            else:
                self.log_result("Update Expense", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update Expense", False, f"Request error: {str(e)}")
            return False

    def test_delete_expense(self):
        """Test DELETE /api/finance/expenses/{id} to remove expense"""
        if not hasattr(self, 'expense_id'):
            self.log_result("Delete Expense", False, "No expense ID available for deletion")
            return False
        
        try:
            response = self.session.delete(f"{self.base_url}/finance/expenses/{self.expense_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result("Delete Expense", True, "Expense deleted successfully")
                    return True
                else:
                    self.log_result("Delete Expense", False, "Success flag not set in response", data)
                    return False
            else:
                self.log_result("Delete Expense", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Delete Expense", False, f"Request error: {str(e)}")
            return False

    def test_analytics_burn_rate(self):
        """Test GET /api/finance/burn-rate analytics endpoint"""
        try:
            response = self.session.get(
                f"{self.base_url}/finance/burn-rate",
                params={"period": "monthly"}
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["period", "series"]
                
                if all(field in data for field in required_fields):
                    if data["period"] == "monthly" and isinstance(data["series"], list):
                        self.log_result("Analytics - Burn Rate", True, 
                                      f"Burn rate analytics returned with {len(data['series'])} data points for monthly period")
                        return True
                    else:
                        self.log_result("Analytics - Burn Rate", False, "Invalid burn rate data structure", data)
                        return False
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("Analytics - Burn Rate", False, f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("Analytics - Burn Rate", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Analytics - Burn Rate", False, f"Request error: {str(e)}")
            return False

    def test_analytics_variance(self):
        """Test GET /api/finance/variance analytics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/finance/variance")
            
            if response.status_code == 200:
                data = response.json()
                if "by_project" in data and isinstance(data["by_project"], list):
                    self.log_result("Analytics - Variance", True, 
                                  f"Variance analytics working with {len(data['by_project'])} projects")
                    return True
                else:
                    self.log_result("Analytics - Variance", False, "Missing or invalid by_project field", data)
                    return False
            else:
                self.log_result("Analytics - Variance", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Analytics - Variance", False, f"Request error: {str(e)}")
            return False

    def test_analytics_forecast(self):
        """Test GET /api/finance/forecast analytics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/finance/forecast")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["avg_monthly", "projected_spend_rest_of_year", "months_remaining"]
                
                if all(field in data for field in required_fields):
                    self.log_result("Analytics - Forecast", True, 
                                  f"Forecast analytics: avg monthly ${data['avg_monthly']:.2f}, projected ${data['projected_spend_rest_of_year']:.2f} for {data['months_remaining']} months")
                    return True
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("Analytics - Forecast", False, f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("Analytics - Forecast", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Analytics - Forecast", False, f"Request error: {str(e)}")
            return False

    def test_analytics_funding_utilization(self):
        """Test GET /api/finance/funding-utilization analytics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/finance/funding-utilization")
            
            if response.status_code == 200:
                data = response.json()
                if "by_funding_source" in data and isinstance(data["by_funding_source"], list):
                    self.log_result("Analytics - Funding Utilization", True, 
                                  f"Funding utilization analytics returned {len(data['by_funding_source'])} funding sources")
                    return True
                else:
                    self.log_result("Analytics - Funding Utilization", False, 
                                  "Missing or invalid by_funding_source field", data)
                    return False
            else:
                self.log_result("Analytics - Funding Utilization", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Analytics - Funding Utilization", False, f"Request error: {str(e)}")
            return False

    def test_csv_import_stub(self):
        """Test POST /api/finance/expenses/import-csv stub endpoint"""
        try:
            # Create a simple CSV content
            csv_content = "Date,Vendor,Amount,Currency\n2024-01-01,Test Vendor,100.00,USD\n"
            
            # Create multipart form data
            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
            body_parts = []
            body_parts.append(f'--{boundary}')
            body_parts.append('Content-Disposition: form-data; name="file"; filename="expenses.csv"')
            body_parts.append('Content-Type: text/csv')
            body_parts.append('')
            body_parts.append(csv_content)
            body_parts.append(f'--{boundary}--')
            
            body = '\r\n'.join(body_parts)
            
            headers = {
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            }
            
            response = self.session.post(
                f"{self.base_url}/finance/expenses/import-csv",
                data=body.encode('utf-8'),
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["status", "processed"]
                
                if all(field in data for field in expected_fields):
                    if data["status"] == "received" and data["processed"] == 0:
                        self.log_result("CSV Import Stub", True, 
                                      "CSV import stub working correctly - received file and returned expected response")
                        return True
                    else:
                        self.log_result("CSV Import Stub", False, 
                                      f"Unexpected stub response values: status={data['status']}, processed={data['processed']}")
                        return False
                else:
                    missing_fields = [field for field in expected_fields if field not in data]
                    self.log_result("CSV Import Stub", False, f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("CSV Import Stub", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("CSV Import Stub", False, f"Request error: {str(e)}")
            return False

    def test_csv_export(self):
        """Test GET /api/finance/expenses/export-csv endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/finance/expenses/export-csv")
            
            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('content-type', '')
                if 'text/csv' in content_type:
                    # Check CSV content
                    csv_content = response.text
                    lines = csv_content.strip().split('\n')
                    if len(lines) > 0:
                        # Verify CSV headers
                        headers = lines[0].split(',')
                        expected_headers = ['Expense ID', 'Project ID', 'Activity ID', 'Date', 'Vendor', 
                                          'Invoice', 'Amount', 'Currency', 'Funding Source', 'Cost Center', 'Notes']
                        
                        # Check if all expected headers are present (allowing for variations in order)
                        headers_match = all(any(expected.lower() in header.lower() for header in headers) 
                                          for expected in expected_headers)
                        
                        if headers_match:
                            self.log_result("CSV Export", True, 
                                          f"CSV export working correctly - returned {len(lines)} lines with proper headers")
                            return True
                        else:
                            self.log_result("CSV Export", False, 
                                          f"CSV headers mismatch. Expected: {expected_headers}, Got: {headers}")
                            return False
                    else:
                        self.log_result("CSV Export", True, "CSV export working (empty data)")
                        return True
                else:
                    self.log_result("CSV Export", False, f"Wrong content type: {content_type}, expected text/csv")
                    return False
            else:
                self.log_result("CSV Export", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("CSV Export", False, f"Request error: {str(e)}")
            return False

    def test_ai_insights(self):
        """Test POST /api/finance/ai/insights endpoint"""
        try:
            insights_data = {
                "anomalies": [
                    {"id": "exp-1", "amount": 2000000, "description": "Unusually large expense"},
                    {"id": "exp-2", "amount": 500000, "description": "High vendor payment"}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/finance/ai/insights",
                json=insights_data
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["ai_used", "risk_level", "recommendations", "confidence"]
                
                if all(field in data for field in required_fields):
                    # Verify data types and values
                    if (isinstance(data["ai_used"], bool) and
                        data["risk_level"] in ["low", "medium", "high"] and
                        isinstance(data["recommendations"], list) and
                        isinstance(data["confidence"], (int, float)) and
                        0 <= data["confidence"] <= 1):
                        
                        self.log_result("AI Insights", True, 
                                      f"AI insights working: risk_level={data['risk_level']}, ai_used={data['ai_used']}, confidence={data['confidence']}")
                        return True
                    else:
                        self.log_result("AI Insights", False, "Invalid data types or values in AI insights response", data)
                        return False
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("AI Insights", False, f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_result("AI Insights", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("AI Insights", False, f"Request error: {str(e)}")
            return False

    def run_finance_tests(self):
        """Run all finance tests in sequence"""
        print("=" * 80)
        print("FINANCE PHASE 1 BACKEND API TESTING")
        print("=" * 80)
        print(f"📍 Testing against: {self.base_url}")
        print()
        
        # Setup authentication
        if not self.setup_auth():
            print("❌ Authentication setup failed - stopping tests")
            return
        
        # Create project for expense testing
        if not self.create_simple_project():
            print("❌ Project creation failed - stopping expense tests")
            return
        
        # Finance Config Tests
        print("\n🔧 FINANCE CONFIG TESTS")
        print("-" * 40)
        self.test_finance_config_get_default()
        self.test_finance_config_update_and_persist()
        
        # Expenses CRUD Tests
        print("\n💰 EXPENSES CRUD TESTS")
        print("-" * 40)
        self.test_create_expense()
        self.test_list_expenses_with_pagination_and_filters()
        self.test_update_expense()
        self.test_delete_expense()
        
        # Analytics Tests
        print("\n📊 ANALYTICS TESTS")
        print("-" * 40)
        self.test_analytics_burn_rate()
        self.test_analytics_variance()
        self.test_analytics_forecast()
        self.test_analytics_funding_utilization()
        
        # CSV Tests
        print("\n📄 CSV IMPORT/EXPORT TESTS")
        print("-" * 40)
        self.test_csv_import_stub()
        self.test_csv_export()
        
        # AI Insights Tests
        print("\n🤖 AI INSIGHTS TESTS")
        print("-" * 40)
        self.test_ai_insights()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 FINANCE TEST SUMMARY")
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

if __name__ == "__main__":
    tester = FinanceAPITester()
    tester.run_finance_tests()