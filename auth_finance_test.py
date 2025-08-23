#!/usr/bin/env python3
"""
Focused Backend API Testing for Auth and Finance Endpoints
Tests specific endpoints requested in the review request
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

class AuthFinanceTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.test_results = []
        
        # Test data
        self.test_email = f"authfinance.test.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Auth Finance Test User"
        
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
    
    def test_health_check(self):
        """Step 1: Verify FastAPI is up (GET /api/health)"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "ok":
                    self.log_result("Health Check", True, "FastAPI server is up and running")
                    return True
                else:
                    self.log_result("Health Check", False, "Invalid health response", data)
                    return False
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Step 2: POST /api/auth/register with sample payload"""
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
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.user_data = data["user"]
                    self.organization_data = data.get("organization")
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    
                    self.log_result("User Registration", True, 
                                  f"User registered successfully. Token: {self.auth_token[:20]}...")
                    return True
                else:
                    self.log_result("User Registration", False, "Missing token/user in response", data)
                    return False
            else:
                self.log_result("User Registration", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("User Registration", False, f"Request error: {str(e)}")
            return False
    
    def test_user_login(self):
        """Step 3: POST /api/auth/login with same credentials"""
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
                if "access_token" in data:
                    # Update token in case it changed
                    self.auth_token = data["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    self.log_result("User Login", True, "Login successful, token received")
                    return True
                else:
                    self.log_result("User Login", False, "Missing token in response", data)
                    return False
            else:
                self.log_result("User Login", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("User Login", False, f"Request error: {str(e)}")
            return False
    
    def test_organizations_me(self):
        """Step 4: GET /api/organizations/me with Bearer token"""
        try:
            response = self.session.get(f"{self.base_url}/organizations/me")
            
            if response.status_code == 200:
                data = response.json()
                org_id = data.get("id") or data.get("_id")
                if org_id and "name" in data:
                    self.log_result("Organizations Me", True, "Organization info retrieved successfully")
                    return True
                else:
                    self.log_result("Organizations Me", False, "Missing required org fields", data)
                    return False
            else:
                self.log_result("Organizations Me", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Organizations Me", False, f"Request error: {str(e)}")
            return False
    
    def test_users_endpoint_auth(self):
        """Step 5: Ensure /api/users requires auth"""
        try:
            # First test without token
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            response_no_token = self.session.get(f"{self.base_url}/users")
            
            # Restore headers
            self.session.headers.update(original_headers)
            
            # Test with token
            response_with_token = self.session.get(f"{self.base_url}/users")
            
            # Check results
            no_token_protected = response_no_token.status_code in [401, 403]
            with_token_success = response_with_token.status_code == 200
            
            if no_token_protected and with_token_success:
                self.log_result("Users Endpoint Auth", True, 
                              f"Properly protected: no token={response_no_token.status_code}, with token={response_with_token.status_code}")
                return True
            elif not no_token_protected:
                self.log_result("Users Endpoint Auth", False, 
                              f"Not properly protected: no token returned {response_no_token.status_code}")
                return False
            else:
                self.log_result("Users Endpoint Auth", False, 
                              f"Token access failed: {response_with_token.status_code}")
                return False
        except Exception as e:
            self.log_result("Users Endpoint Auth", False, f"Request error: {str(e)}")
            return False
    
    def test_finance_config_get(self):
        """Step 6a: GET /api/finance/config to fetch config"""
        try:
            response = self.session.get(f"{self.base_url}/finance/config")
            
            if response.status_code == 200:
                data = response.json()
                if "funding_sources" in data and "cost_centers" in data:
                    self.finance_config = data
                    self.log_result("Finance Config Get", True, 
                                  f"Config retrieved: {len(data['funding_sources'])} funding sources, {len(data['cost_centers'])} cost centers")
                    return True
                else:
                    self.log_result("Finance Config Get", False, "Missing config fields", data)
                    return False
            else:
                self.log_result("Finance Config Get", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance Config Get", False, f"Request error: {str(e)}")
            return False
    
    def test_finance_config_update(self):
        """Step 6b: PUT /api/finance/config to update lists (add USAID)"""
        try:
            if not hasattr(self, 'finance_config'):
                self.log_result("Finance Config Update", False, "No config data from previous test")
                return False
            
            # Add USAID to funding sources if not already present
            updated_config = self.finance_config.copy()
            if "USAID" not in updated_config["funding_sources"]:
                updated_config["funding_sources"].append("USAID")
            
            response = self.session.put(
                f"{self.base_url}/finance/config",
                json=updated_config
            )
            
            if response.status_code == 200:
                data = response.json()
                if "USAID" in data.get("funding_sources", []):
                    self.log_result("Finance Config Update", True, "Successfully added USAID to funding sources")
                    return True
                else:
                    self.log_result("Finance Config Update", False, "USAID not found in updated config", data)
                    return False
            else:
                self.log_result("Finance Config Update", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance Config Update", False, f"Request error: {str(e)}")
            return False
    
    def test_finance_expenses_create(self):
        """Step 7a: POST /api/finance/expenses to create one"""
        try:
            expense_data = {
                "vendor": "Test Vendor Ltd",
                "amount": 150000.0,
                "funding_source": "USAID",
                "cost_center": "Operations",
                "description": "Test expense for API testing",
                "expense_date": datetime.now().isoformat(),
                "project_id": None,
                "activity_id": None
            }
            
            response = self.session.post(
                f"{self.base_url}/finance/expenses",
                json=expense_data
            )
            
            if response.status_code == 200:
                data = response.json()
                expense_id = data.get("id") or data.get("_id")
                if expense_id:
                    self.expense_id = expense_id
                    self.log_result("Finance Expenses Create", True, f"Expense created successfully: {expense_id}")
                    return True
                else:
                    self.log_result("Finance Expenses Create", False, "No expense ID in response", data)
                    return False
            else:
                self.log_result("Finance Expenses Create", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance Expenses Create", False, f"Request error: {str(e)}")
            return False
    
    def test_finance_expenses_list(self):
        """Step 7b: GET /api/finance/expenses with pagination and filters"""
        try:
            # Test with pagination parameters
            params = {
                "page": 1,
                "page_size": 10,
                "vendor": "Test"  # Filter by vendor substring
            }
            
            response = self.session.get(
                f"{self.base_url}/finance/expenses",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                if "expenses" in data and "total" in data:
                    expenses = data["expenses"]
                    total = data["total"]
                    self.log_result("Finance Expenses List", True, 
                                  f"Retrieved {len(expenses)} expenses out of {total} total")
                    return True
                else:
                    self.log_result("Finance Expenses List", False, "Missing pagination fields", data)
                    return False
            else:
                self.log_result("Finance Expenses List", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance Expenses List", False, f"Request error: {str(e)}")
            return False
    
    def test_finance_expenses_update(self):
        """Step 7c: PUT /api/finance/expenses/{id} to edit"""
        try:
            if not hasattr(self, 'expense_id'):
                self.log_result("Finance Expenses Update", False, "No expense ID from previous test")
                return False
            
            update_data = {
                "amount": 175000.0,
                "vendor": "Updated Test Vendor Ltd",
                "notes": "Updated expense for testing"
            }
            
            response = self.session.put(
                f"{self.base_url}/finance/expenses/{self.expense_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("amount") == update_data["amount"]:
                    self.log_result("Finance Expenses Update", True, "Expense updated successfully")
                    return True
                else:
                    self.log_result("Finance Expenses Update", False, "Amount not updated", data)
                    return False
            else:
                self.log_result("Finance Expenses Update", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance Expenses Update", False, f"Request error: {str(e)}")
            return False
    
    def test_finance_expenses_delete(self):
        """Step 7d: DELETE to remove expense"""
        try:
            if not hasattr(self, 'expense_id'):
                self.log_result("Finance Expenses Delete", False, "No expense ID from previous test")
                return False
            
            response = self.session.delete(f"{self.base_url}/finance/expenses/{self.expense_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result("Finance Expenses Delete", True, "Expense deleted successfully")
                    return True
                else:
                    self.log_result("Finance Expenses Delete", False, "Delete not confirmed", data)
                    return False
            else:
                self.log_result("Finance Expenses Delete", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance Expenses Delete", False, f"Request error: {str(e)}")
            return False
    
    def test_finance_reports_pdf(self):
        """Step 8: GET /api/finance/reports/all-projects-pdf"""
        try:
            response = self.session.get(f"{self.base_url}/finance/reports/all-projects-pdf")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type:
                    pdf_size = len(response.content)
                    self.log_result("Finance Reports PDF", True, 
                                  f"PDF report generated successfully ({pdf_size} bytes)")
                    return True
                else:
                    self.log_result("Finance Reports PDF", False, 
                                  f"Wrong content type: {content_type}")
                    return False
            else:
                self.log_result("Finance Reports PDF", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance Reports PDF", False, f"Request error: {str(e)}")
            return False
    
    def test_cors_and_api_prefix(self):
        """Step 9: Confirm CORS and /api prefix routing"""
        try:
            # Test CORS headers
            response = self.session.options(f"{self.base_url}/health")
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers')
            }
            
            # Test /api prefix routing
            api_prefix_works = True
            try:
                # This should fail (no /api prefix)
                no_prefix_response = self.session.get(f"{BACKEND_URL}/health")
                if no_prefix_response.status_code == 200:
                    api_prefix_works = False
            except:
                pass  # Expected to fail
            
            # Test with /api prefix (should work)
            with_prefix_response = self.session.get(f"{self.base_url}/health")
            prefix_works = with_prefix_response.status_code == 200
            
            if prefix_works:
                self.log_result("CORS and API Prefix", True, 
                              f"API prefix routing working, CORS headers: {cors_headers}")
                return True
            else:
                self.log_result("CORS and API Prefix", False, 
                              "API prefix routing not working properly")
                return False
        except Exception as e:
            self.log_result("CORS and API Prefix", False, f"Request error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all auth and finance tests as requested in review"""
        print("🎯 AUTH AND FINANCE ENDPOINTS TESTING")
        print(f"📍 Testing against: {self.base_url}")
        print("="*80)
        
        tests = [
            ("1. Health Check", self.test_health_check),
            ("2. User Registration", self.test_user_registration),
            ("3. User Login", self.test_user_login),
            ("4. Organizations/Me", self.test_organizations_me),
            ("5. Users Auth Check", self.test_users_endpoint_auth),
            ("6a. Finance Config Get", self.test_finance_config_get),
            ("6b. Finance Config Update", self.test_finance_config_update),
            ("7a. Finance Expenses Create", self.test_finance_expenses_create),
            ("7b. Finance Expenses List", self.test_finance_expenses_list),
            ("7c. Finance Expenses Update", self.test_finance_expenses_update),
            ("7d. Finance Expenses Delete", self.test_finance_expenses_delete),
            ("8. Finance Reports PDF", self.test_finance_reports_pdf),
            ("9. CORS and API Prefix", self.test_cors_and_api_prefix)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            if test_func():
                passed += 1
        
        print(f"\n{'='*80}")
        print(f"🎯 AUTH AND FINANCE TESTING COMPLETE: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        # Summary of results
        print(f"\n📊 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = AuthFinanceTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)