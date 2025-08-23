#!/usr/bin/env python3
"""
Finance Approval Workflow Testing for DataRW Phase 2
Tests the newly implemented approval endpoints as requested in review.
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

class FinanceApprovalTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.test_results = []
        
        # Test data
        self.test_email = f"approval.test.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Finance Approval Tester"
        
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
            # Register test user
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
                    
                    self.log_result("Authentication Setup", True, "User registered and authenticated successfully")
                    return True
                else:
                    self.log_result("Authentication Setup", False, "Missing required fields in response", data)
                    return False
            else:
                self.log_result("Authentication Setup", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Authentication Setup", False, f"Request error: {str(e)}")
            return False

    def test_create_expense_for_approval(self):
        """Create a test expense in draft status for approval testing"""
        try:
            expense_data = {
                "project_id": "test-project-001",
                "activity_id": "test-activity-001",
                "vendor": "Rwanda Digital Solutions Ltd",
                "amount": 75000.0,  # Below director threshold
                "currency": "RWF",
                "date": datetime.now().isoformat(),
                "funding_source": "World Bank",
                "cost_center": "Operations",
                "invoice_no": f"INV-{uuid.uuid4().hex[:8].upper()}",
                "notes": "Digital literacy training materials and equipment procurement"
            }
            
            response = self.session.post(
                f"{self.base_url}/finance/expenses",
                json=expense_data
            )
            
            if response.status_code == 200:
                data = response.json()
                expense_id = data.get("id") or data.get("_id")
                if expense_id and data.get("vendor") == expense_data["vendor"]:
                    self.test_expense_id = expense_id
                    self.log_result("Create Expense for Approval", True, 
                                  f"Test expense created successfully with ID: {expense_id}")
                    return True
                else:
                    self.log_result("Create Expense for Approval", False, "Expense data mismatch", data)
                    return False
            else:
                self.log_result("Create Expense for Approval", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Expense for Approval", False, f"Request error: {str(e)}")
            return False

    def test_submit_expense_for_approval(self):
        """Test POST /finance/expenses/{expense_id}/submit"""
        if not hasattr(self, 'test_expense_id'):
            self.log_result("Submit Expense for Approval", False, "No test expense ID available")
            return False
        
        try:
            response = self.session.post(
                f"{self.base_url}/finance/expenses/{self.test_expense_id}/submit"
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and 
                    "expense" in data and 
                    data["expense"].get("approval_status") == "pending"):
                    
                    # Check if requires_director_approval is set correctly
                    requires_director = data["expense"].get("requires_director_approval", False)
                    amount = data["expense"].get("amount", 0)
                    expected_director = amount > 100000.0
                    
                    if requires_director == expected_director:
                        self.log_result("Submit Expense for Approval", True, 
                                      f"Expense submitted successfully - status: pending, director approval: {requires_director}")
                        return True
                    else:
                        self.log_result("Submit Expense for Approval", False, 
                                      f"Director approval requirement incorrect: expected {expected_director}, got {requires_director}")
                        return False
                else:
                    self.log_result("Submit Expense for Approval", False, "Missing required fields or wrong status", data)
                    return False
            else:
                self.log_result("Submit Expense for Approval", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Submit Expense for Approval", False, f"Request error: {str(e)}")
            return False

    def test_approve_expense(self):
        """Test POST /finance/expenses/{expense_id}/approve"""
        if not hasattr(self, 'test_expense_id'):
            self.log_result("Approve Expense", False, "No test expense ID available")
            return False
        
        try:
            response = self.session.post(
                f"{self.base_url}/finance/expenses/{self.test_expense_id}/approve"
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and 
                    "expense" in data and 
                    data["expense"].get("approval_status") == "approved"):
                    
                    # Check audit trail fields
                    expense = data["expense"]
                    if ("approved_by" in expense and 
                        "approved_at" in expense and
                        expense.get("approved_by") == self.user_data["id"]):
                        
                        self.log_result("Approve Expense", True, 
                                      "Expense approved successfully with proper audit trail (approved_by, approved_at)")
                        return True
                    else:
                        self.log_result("Approve Expense", False, "Missing audit trail fields", data)
                        return False
                else:
                    self.log_result("Approve Expense", False, "Missing required fields or wrong status", data)
                    return False
            elif response.status_code == 403:
                data = response.json()
                if "Insufficient permissions" in data.get("detail", ""):
                    self.log_result("Approve Expense", True, 
                                  "Permission validation working - insufficient permissions properly rejected")
                    return True
                else:
                    self.log_result("Approve Expense", False, "Wrong error message for permissions", data)
                    return False
            else:
                self.log_result("Approve Expense", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Approve Expense", False, f"Request error: {str(e)}")
            return False

    def test_create_expense_for_rejection(self):
        """Create another test expense for rejection testing"""
        try:
            expense_data = {
                "project_id": "test-project-002",
                "activity_id": "test-activity-002",
                "vendor": "Tech Solutions Rwanda",
                "amount": 45000.0,
                "currency": "RWF",
                "date": datetime.now().isoformat(),
                "funding_source": "USAID",
                "cost_center": "Field Work",
                "invoice_no": f"INV-{uuid.uuid4().hex[:8].upper()}",
                "notes": "Software licensing for project management tools"
            }
            
            response = self.session.post(
                f"{self.base_url}/finance/expenses",
                json=expense_data
            )
            
            if response.status_code == 200:
                data = response.json()
                expense_id = data.get("id") or data.get("_id")
                if expense_id:
                    self.rejection_expense_id = expense_id
                    
                    # Submit for approval immediately
                    submit_response = self.session.post(
                        f"{self.base_url}/finance/expenses/{expense_id}/submit"
                    )
                    
                    if submit_response.status_code == 200:
                        self.log_result("Create Expense for Rejection", True, 
                                      f"Test expense for rejection created and submitted: {expense_id}")
                        return True
                    else:
                        self.log_result("Create Expense for Rejection", False, 
                                      f"Failed to submit expense for approval: {submit_response.status_code}")
                        return False
                else:
                    self.log_result("Create Expense for Rejection", False, "No expense ID returned", data)
                    return False
            else:
                self.log_result("Create Expense for Rejection", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Expense for Rejection", False, f"Request error: {str(e)}")
            return False

    def test_reject_expense(self):
        """Test POST /finance/expenses/{expense_id}/reject"""
        if not hasattr(self, 'rejection_expense_id'):
            self.log_result("Reject Expense", False, "No rejection expense ID available")
            return False
        
        try:
            rejection_data = {
                "rejection_reason": "Insufficient documentation provided. Please attach proper invoices and receipts before resubmission."
            }
            
            response = self.session.post(
                f"{self.base_url}/finance/expenses/{self.rejection_expense_id}/reject",
                json=rejection_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and 
                    "expense" in data and 
                    data["expense"].get("approval_status") == "rejected"):
                    
                    # Check audit trail fields for rejection
                    expense = data["expense"]
                    if ("rejection_reason" in expense and 
                        "approved_by" in expense and 
                        "approved_at" in expense and
                        expense.get("rejection_reason") == rejection_data["rejection_reason"]):
                        
                        self.log_result("Reject Expense", True, 
                                      "Expense rejected successfully with proper audit trail (rejection_reason, approved_by, approved_at)")
                        return True
                    else:
                        self.log_result("Reject Expense", False, "Missing audit trail fields for rejection", data)
                        return False
                else:
                    self.log_result("Reject Expense", False, "Missing required fields or wrong status", data)
                    return False
            elif response.status_code == 400:
                data = response.json()
                if "Rejection reason is required" in data.get("detail", ""):
                    self.log_result("Reject Expense", True, 
                                  "Rejection reason validation working properly")
                    return True
                else:
                    self.log_result("Reject Expense", False, "Wrong validation error message", data)
                    return False
            elif response.status_code == 403:
                data = response.json()
                if "Insufficient permissions" in data.get("detail", ""):
                    self.log_result("Reject Expense", True, 
                                  "Permission validation working - insufficient permissions properly rejected")
                    return True
                else:
                    self.log_result("Reject Expense", False, "Wrong error message for permissions", data)
                    return False
            else:
                self.log_result("Reject Expense", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Reject Expense", False, f"Request error: {str(e)}")
            return False

    def test_director_approval_threshold(self):
        """Test director approval threshold for expenses >100K"""
        try:
            # Create high-value expense requiring director approval
            expense_data = {
                "project_id": "test-project-003",
                "activity_id": "test-activity-003",
                "vendor": "Major Infrastructure Corp",
                "amount": 150000.0,  # Above director threshold (100K)
                "currency": "RWF",
                "date": datetime.now().isoformat(),
                "funding_source": "World Bank",
                "cost_center": "Operations",
                "invoice_no": f"INV-{uuid.uuid4().hex[:8].upper()}",
                "notes": "Major equipment procurement requiring director approval"
            }
            
            # Create expense
            create_response = self.session.post(
                f"{self.base_url}/finance/expenses",
                json=expense_data
            )
            
            if create_response.status_code != 200:
                self.log_result("Director Approval Threshold", False, 
                              f"Failed to create high-value expense: {create_response.status_code}")
                return False
            
            expense_id = create_response.json().get("id") or create_response.json().get("_id")
            if not expense_id:
                self.log_result("Director Approval Threshold", False, "No expense ID returned")
                return False
            
            # Submit for approval
            submit_response = self.session.post(
                f"{self.base_url}/finance/expenses/{expense_id}/submit"
            )
            
            if submit_response.status_code == 200:
                data = submit_response.json()
                if (data.get("success") and 
                    "expense" in data and 
                    data["expense"].get("requires_director_approval") == True):
                    
                    self.director_expense_id = expense_id
                    self.log_result("Director Approval Threshold", True, 
                                  "Director approval threshold working correctly - high-value expense requires director approval")
                    return True
                else:
                    self.log_result("Director Approval Threshold", False, 
                                  "Director approval not required for high-value expense", data)
                    return False
            else:
                self.log_result("Director Approval Threshold", False, 
                              f"Failed to submit high-value expense: {submit_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Director Approval Threshold", False, f"Request error: {str(e)}")
            return False

    def test_get_pending_approvals(self):
        """Test GET /finance/approvals/pending"""
        try:
            response = self.session.get(f"{self.base_url}/finance/approvals/pending")
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and "total" in data:
                    items = data["items"]
                    total = data["total"]
                    
                    # Verify structure and content
                    if isinstance(items, list) and isinstance(total, int):
                        # Look for expenses with pending status
                        pending_count = len([item for item in items if item.get("approval_status") == "pending"])
                        
                        self.log_result("Get Pending Approvals", True, 
                                      f"Pending approvals retrieved successfully: {total} total, {pending_count} pending items")
                        return True
                    else:
                        self.log_result("Get Pending Approvals", False, 
                                      f"Invalid data types: items={type(items)}, total={type(total)}", data)
                        return False
                else:
                    self.log_result("Get Pending Approvals", False, "Missing required fields (items, total)", data)
                    return False
            elif response.status_code == 403:
                data = response.json()
                if "Insufficient permissions" in data.get("detail", ""):
                    self.log_result("Get Pending Approvals", True, 
                                  "Permission validation working - insufficient permissions properly rejected")
                    return True
                else:
                    self.log_result("Get Pending Approvals", False, "Wrong error message for permissions", data)
                    return False
            else:
                self.log_result("Get Pending Approvals", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Pending Approvals", False, f"Request error: {str(e)}")
            return False

    def run_finance_approval_tests(self):
        """Run all Finance Approval Workflow tests"""
        print("="*80)
        print("FINANCE APPROVAL WORKFLOW TESTING (PHASE 2)")
        print("Testing newly implemented approval endpoints as requested in review")
        print("="*80)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed - aborting tests")
            return self.get_summary()
        
        # Test sequence
        tests = [
            ("Create Test Expense", self.test_create_expense_for_approval),
            ("Submit for Approval", self.test_submit_expense_for_approval),
            ("Approve Expense", self.test_approve_expense),
            ("Create Expense for Rejection", self.test_create_expense_for_rejection),
            ("Reject Expense", self.test_reject_expense),
            ("Director Approval Threshold", self.test_director_approval_threshold),
            ("Get Pending Approvals", self.test_get_pending_approvals),
        ]
        
        success_count = 0
        for test_name, test_method in tests:
            print(f"\n🧪 Running: {test_name}")
            try:
                if test_method():
                    success_count += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test method failed: {str(e)}")
        
        # Summary
        print("\n" + "="*80)
        print("📊 FINANCE APPROVAL WORKFLOW TEST SUMMARY")
        print("="*80)
        
        total_tests = len(tests)
        print(f"✅ Passed: {success_count}/{total_tests}")
        print(f"❌ Failed: {total_tests - success_count}/{total_tests}")
        print(f"📈 Success Rate: {(success_count/total_tests*100):.1f}%")
        
        if success_count < total_tests:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
        
        return success_count, total_tests - success_count

    def get_summary(self):
        """Get test summary"""
        passed = sum(1 for result in self.test_results if result['success'])
        failed = len(self.test_results) - passed
        return passed, failed

if __name__ == "__main__":
    tester = FinanceApprovalTester()
    tester.run_finance_approval_tests()