#!/usr/bin/env python3
"""
Focused Server-Side Pagination Testing for DataRW Phase 2
Tests the newly implemented server-side pagination for large datasets
"""

import requests
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment - use external URL for testing
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

class PaginationTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.project_id = None
        self.test_results = []
        
        # Test data
        self.test_email = f"pagination.test.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Pagination Test User"
        
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
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                self.log_result("Authentication Setup", True, "User registered and authenticated successfully")
                return True
            else:
                self.log_result("Authentication Setup", False, f"Registration failed: HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Authentication Setup", False, f"Authentication error: {str(e)}")
            return False
    
    def setup_test_project(self):
        """Create a test project for activities and beneficiaries testing"""
        try:
            project_data = {
                "name": "Pagination Test Project",
                "description": "Test project for pagination testing",
                "project_manager_id": self.user_data["id"],
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "budget_total": 1000000.0,
                "beneficiaries_target": 1000,
                "location": "Test Location",
                "donor_organization": "Test Donor"
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data
            )
            
            if response.status_code == 200:
                self.project_id = response.json().get("id")
                self.log_result("Test Project Setup", True, f"Test project created with ID: {self.project_id}")
                return True
            else:
                self.log_result("Test Project Setup", False, f"Project creation failed: HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Test Project Setup", False, f"Project setup error: {str(e)}")
            return False
    
    def test_surveys_pagination(self):
        """Test GET /api/surveys?page=1&page_size=10&status=draft - Test surveys pagination with filtering"""
        try:
            print("\n" + "="*60)
            print("TESTING SURVEYS PAGINATION WITH FILTERING")
            print("="*60)
            
            # First create some test surveys to ensure we have data
            for i in range(15):
                survey_data = {
                    "title": f"Pagination Test Survey {i+1}",
                    "description": f"Test survey {i+1} for pagination testing",
                    "status": "draft" if i % 2 == 0 else "active",
                    "questions": [
                        {
                            "type": "short_text",
                            "question": f"Test question {i+1}",
                            "required": True
                        }
                    ]
                }
                
                create_response = self.session.post(
                    f"{self.base_url}/surveys",
                    json=survey_data
                )
                
                if create_response.status_code != 200:
                    # If survey creation fails, continue with existing data
                    break
            
            # Test pagination with filtering
            response = self.session.get(
                f"{self.base_url}/surveys",
                params={
                    "page": 1,
                    "page_size": 10,
                    "status": "draft"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify pagination structure
                required_fields = ["items", "total", "page", "page_size", "total_pages"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Surveys Pagination", False, 
                                  f"Missing pagination fields: {missing_fields}", data)
                    return False
                
                # Verify pagination metadata
                if data["page"] != 1:
                    self.log_result("Surveys Pagination", False, 
                                  f"Expected page=1, got {data['page']}", data)
                    return False
                
                if data["page_size"] != 10:
                    self.log_result("Surveys Pagination", False, 
                                  f"Expected page_size=10, got {data['page_size']}", data)
                    return False
                
                # Verify items array
                items = data.get("items", [])
                if not isinstance(items, list):
                    self.log_result("Surveys Pagination", False, 
                                  "Items should be an array", data)
                    return False
                
                if len(items) > data["page_size"]:
                    self.log_result("Surveys Pagination", False, 
                                  f"Items count ({len(items)}) exceeds page_size ({data['page_size']})", data)
                    return False
                
                # Verify filtering works (status=draft)
                for item in items:
                    if item.get("status") != "draft":
                        self.log_result("Surveys Pagination", False, 
                                      f"Filtering failed: found non-draft survey {item.get('id')}", data)
                        return False
                
                # Verify total_pages calculation
                expected_total_pages = (data["total"] + data["page_size"] - 1) // data["page_size"]
                if data["total_pages"] != expected_total_pages:
                    self.log_result("Surveys Pagination", False, 
                                  f"Incorrect total_pages calculation: expected {expected_total_pages}, got {data['total_pages']}", data)
                    return False
                
                self.log_result("Surveys Pagination", True, 
                              f"✅ VERIFIED: Pagination structure, filtering (status=draft), metadata - {len(items)} items, total={data['total']}, pages={data['total_pages']}")
                return True
            else:
                self.log_result("Surveys Pagination", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Surveys Pagination", False, f"Request error: {str(e)}")
            return False

    def test_activities_pagination(self):
        """Test GET /api/activities?page=1&page_size=5 - Test activities pagination (without project filtering for now)"""
        try:
            print("\n" + "="*60)
            print("TESTING ACTIVITIES PAGINATION")
            print("="*60)
            
            # Test pagination without project filtering (since project creation endpoint is not available)
            response = self.session.get(
                f"{self.base_url}/activities",
                params={
                    "page": 1,
                    "page_size": 5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify pagination structure
                required_fields = ["items", "total", "page", "page_size", "total_pages"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Activities Pagination", False, 
                                  f"Missing pagination fields: {missing_fields}", data)
                    return False
                
                # Verify pagination metadata
                if data["page"] != 1:
                    self.log_result("Activities Pagination", False, 
                                  f"Expected page=1, got {data['page']}", data)
                    return False
                
                if data["page_size"] != 5:
                    self.log_result("Activities Pagination", False, 
                                  f"Expected page_size=5, got {data['page_size']}", data)
                    return False
                
                # Verify items array
                items = data.get("items", [])
                if not isinstance(items, list):
                    self.log_result("Activities Pagination", False, 
                                  "Items should be an array", data)
                    return False
                
                if len(items) > data["page_size"]:
                    self.log_result("Activities Pagination", False, 
                                  f"Items count ({len(items)}) exceeds page_size ({data['page_size']})", data)
                    return False
                
                # Verify total_pages calculation
                expected_total_pages = (data["total"] + data["page_size"] - 1) // data["page_size"]
                if data["total_pages"] != expected_total_pages:
                    self.log_result("Activities Pagination", False, 
                                  f"Incorrect total_pages calculation: expected {expected_total_pages}, got {data['total_pages']}", data)
                    return False
                
                self.log_result("Activities Pagination", True, 
                              f"✅ VERIFIED: Pagination structure and metadata - {len(items)} items, total={data['total']}, pages={data['total_pages']}")
                return True
            else:
                self.log_result("Activities Pagination", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Activities Pagination", False, f"Request error: {str(e)}")
            return False

    def test_beneficiaries_pagination(self):
        """Test GET /api/beneficiaries?page=1&page_size=5 - Test beneficiaries pagination (without project filtering for now)"""
        try:
            print("\n" + "="*60)
            print("TESTING BENEFICIARIES PAGINATION")
            print("="*60)
            
            # Test pagination without project filtering (since project creation endpoint is not available)
            response = self.session.get(
                f"{self.base_url}/beneficiaries",
                params={
                    "page": 1,
                    "page_size": 5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify pagination structure
                required_fields = ["items", "total", "page", "page_size", "total_pages"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Beneficiaries Pagination", False, 
                                  f"Missing pagination fields: {missing_fields}", data)
                    return False
                
                # Verify pagination metadata
                if data["page"] != 1:
                    self.log_result("Beneficiaries Pagination", False, 
                                  f"Expected page=1, got {data['page']}", data)
                    return False
                
                if data["page_size"] != 5:
                    self.log_result("Beneficiaries Pagination", False, 
                                  f"Expected page_size=5, got {data['page_size']}", data)
                    return False
                
                # Verify items array
                items = data.get("items", [])
                if not isinstance(items, list):
                    self.log_result("Beneficiaries Pagination", False, 
                                  "Items should be an array", data)
                    return False
                
                if len(items) > data["page_size"]:
                    self.log_result("Beneficiaries Pagination", False, 
                                  f"Items count ({len(items)}) exceeds page_size ({data['page_size']})", data)
                    return False
                
                # Verify total_pages calculation
                expected_total_pages = (data["total"] + data["page_size"] - 1) // data["page_size"]
                if data["total_pages"] != expected_total_pages:
                    self.log_result("Beneficiaries Pagination", False, 
                                  f"Incorrect total_pages calculation: expected {expected_total_pages}, got {data['total_pages']}", data)
                    return False
                
                self.log_result("Beneficiaries Pagination", True, 
                              f"✅ VERIFIED: Pagination structure and metadata - {len(items)} items, total={data['total']}, pages={data['total_pages']}")
                return True
            else:
                self.log_result("Beneficiaries Pagination", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Beneficiaries Pagination", False, f"Request error: {str(e)}")
            return False

    def test_finance_expenses_pagination(self):
        """Test GET /api/finance/expenses?page=1&page_size=5 - Verify existing finance pagination still works"""
        try:
            print("\n" + "="*60)
            print("TESTING FINANCE EXPENSES PAGINATION (VERIFY EXISTING STILL WORKS)")
            print("="*60)
            
            # Create some test expenses
            for i in range(7):
                expense_data = {
                    "date": "2024-01-01T00:00:00",
                    "vendor": f"Test Vendor {i+1}",
                    "amount": 100000.0 + (i * 50000),
                    "currency": "RWF",
                    "funding_source": "World Bank" if i % 2 == 0 else "USAID",
                    "cost_center": "Operations",
                    "invoice_no": f"INV-{uuid.uuid4().hex[:8]}",
                    "notes": f"Test expense {i+1} for pagination testing"
                }
                
                create_response = self.session.post(
                    f"{self.base_url}/finance/expenses",
                    json=expense_data
                )
                
                if create_response.status_code != 200:
                    # If expense creation fails, continue with existing data
                    break
            
            # Test pagination
            response = self.session.get(
                f"{self.base_url}/finance/expenses",
                params={
                    "page": 1,
                    "page_size": 5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify pagination structure
                required_fields = ["items", "total", "page", "page_size", "total_pages"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Finance Expenses Pagination", False, 
                                  f"Missing pagination fields: {missing_fields}", data)
                    return False
                
                # Verify pagination metadata
                if data["page"] != 1:
                    self.log_result("Finance Expenses Pagination", False, 
                                  f"Expected page=1, got {data['page']}", data)
                    return False
                
                if data["page_size"] != 5:
                    self.log_result("Finance Expenses Pagination", False, 
                                  f"Expected page_size=5, got {data['page_size']}", data)
                    return False
                
                # Verify items array
                items = data.get("items", [])
                if not isinstance(items, list):
                    self.log_result("Finance Expenses Pagination", False, 
                                  "Items should be an array", data)
                    return False
                
                if len(items) > data["page_size"]:
                    self.log_result("Finance Expenses Pagination", False, 
                                  f"Items count ({len(items)}) exceeds page_size ({data['page_size']})", data)
                    return False
                
                # Test filtering with vendor parameter
                filter_response = self.session.get(
                    f"{self.base_url}/finance/expenses",
                    params={
                        "page": 1,
                        "page_size": 5,
                        "vendor": "Test Vendor"
                    }
                )
                
                if filter_response.status_code == 200:
                    filter_data = filter_response.json()
                    filter_items = filter_data.get("items", [])
                    
                    # Verify filtering works
                    for item in filter_items:
                        if "Test Vendor" not in item.get("vendor", ""):
                            self.log_result("Finance Expenses Pagination", False, 
                                          f"Filtering failed: found expense with vendor {item.get('vendor')}", filter_data)
                            return False
                
                self.log_result("Finance Expenses Pagination", True, 
                              f"✅ VERIFIED: Pagination structure, filtering (vendor), metadata - {len(items)} items, total={data['total']}, pages={data['total_pages']}")
                return True
            else:
                self.log_result("Finance Expenses Pagination", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Finance Expenses Pagination", False, f"Request error: {str(e)}")
            return False

    def test_authentication_protection(self):
        """Test that all pagination endpoints are properly protected by authentication"""
        try:
            print("\n" + "="*60)
            print("TESTING AUTHENTICATION PROTECTION FOR ALL PAGINATION ENDPOINTS")
            print("="*60)
            
            # Remove authorization header temporarily
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            endpoints_to_test = [
                "/surveys?page=1&page_size=10",
                "/activities?page=1&page_size=5",
                "/beneficiaries?page=1&page_size=5",
                "/finance/expenses?page=1&page_size=5"
            ]
            
            all_protected = True
            for endpoint in endpoints_to_test:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code not in [401, 403]:
                    self.log_result("Pagination Auth Protection", False, 
                                  f"Endpoint {endpoint} not properly protected: HTTP {response.status_code}")
                    all_protected = False
                    break
            
            # Restore headers
            self.session.headers.update(original_headers)
            
            if all_protected:
                self.log_result("Pagination Auth Protection", True, 
                              "✅ VERIFIED: All pagination endpoints properly protected by authentication")
                return True
            else:
                return False
                
        except Exception as e:
            # Restore headers in case of error
            self.session.headers.update(original_headers)
            self.log_result("Pagination Auth Protection", False, f"Request error: {str(e)}")
            return False

    def run_pagination_tests(self):
        """Run comprehensive server-side pagination tests as requested in review"""
        print("="*80)
        print("SERVER-SIDE PAGINATION TESTING - PHASE 2")
        print("Testing newly implemented server-side pagination for large datasets")
        print("="*80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return
        
        # Note: Project creation endpoint not available, so we'll test pagination without project filtering
        print("ℹ️  Note: Testing pagination without project filtering (project creation endpoint not available)")
        
        success_count = 0
        total_tests = 5
        
        # Test 1: Surveys pagination with filtering
        if self.test_surveys_pagination():
            success_count += 1
        
        # Test 2: Activities pagination
        if self.test_activities_pagination():
            success_count += 1
        
        # Test 3: Beneficiaries pagination
        if self.test_beneficiaries_pagination():
            success_count += 1
        
        # Test 4: Finance expenses pagination (verify existing still works)
        if self.test_finance_expenses_pagination():
            success_count += 1
        
        # Test 5: Authentication protection for all pagination endpoints
        if self.test_authentication_protection():
            success_count += 1
        
        print("\n" + "="*80)
        print("PAGINATION TESTING SUMMARY")
        print("="*80)
        print(f"✅ Passed: {success_count}/{total_tests} tests")
        print(f"📈 Success Rate: {(success_count/total_tests*100):.1f}%")
        
        if success_count == total_tests:
            print("\n🎉 ALL PAGINATION TESTS PASSED!")
            print("✅ Server-side pagination is working correctly for all endpoints")
            print("✅ Proper pagination metadata returned (total, page, page_size, total_pages)")
            print("✅ Items array with correct number of items (≤ page_size)")
            print("✅ Authentication protection verified")
            print("✅ Filtering parameters working correctly")
        else:
            print(f"\n⚠️  {total_tests - success_count} pagination tests failed. Check the output above for details.")
        
        return success_count == total_tests

if __name__ == "__main__":
    tester = PaginationTester()
    tester.run_pagination_tests()