#!/usr/bin/env python3
"""
Focused Project Management Creation Endpoints Test
Tests the specific endpoints requested in the review:
1. POST /api/projects - Project creation
2. POST /api/activities - Activity creation  
3. POST /api/kpis - KPI creation
4. POST /api/beneficiaries - Beneficiary creation
5. POST /api/budget - Budget item creation
6. GET /api/users - Users endpoint for dropdown population
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
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://datarw-bugfix.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class ProjectManagementTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.test_results = []
        
        # Test data with realistic values
        self.test_email = f"project.manager.{uuid.uuid4().hex[:8]}@rwandaeducation.org"
        self.test_password = "ProjectManager2024!"
        self.test_name = "Marie Uwimana"
        
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
                self.auth_token = data["access_token"]
                self.user_data = data["user"]
                self.organization_data = data["organization"]
                
                # Set authorization header
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                self.log_result("Authentication Setup", True, "User authenticated successfully")
                return True
            else:
                self.log_result("Authentication Setup", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Authentication Setup", False, f"Request error: {str(e)}")
            return False
    
    def test_create_project(self):
        """Test POST /api/projects - Create a new project with realistic data"""
        try:
            project_data = {
                "title": "Digital Literacy Training Program",
                "description": "A comprehensive program to improve digital literacy skills among rural communities in Rwanda, focusing on basic computer skills, internet usage, and digital financial services.",
                "sector": "Education",
                "donor": "World Bank",
                "implementation_start": (datetime.now() + timedelta(days=30)).isoformat(),
                "implementation_end": (datetime.now() + timedelta(days=730)).isoformat(),  # 2 years
                "total_budget": 2500000.0,  # 2.5M RWF
                "budget_currency": "RWF",
                "location": "Nyagatare District, Eastern Province",
                "target_beneficiaries": 5000,
                "team_members": []
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data
            )
            
            if response.status_code == 200:
                data = response.json()
                project_id = data.get("id") or data.get("_id")
                if project_id and data.get("title") == project_data["title"]:
                    self.project_id = project_id
                    self.log_result("Create Project", True, 
                                  f"Project '{project_data['title']}' created successfully with ID: {project_id}")
                    return True
                else:
                    self.log_result("Create Project", False, "Project data mismatch", data)
                    return False
            else:
                self.log_result("Create Project", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Project", False, f"Request error: {str(e)}")
            return False
    
    def test_create_activity(self):
        """Test POST /api/activities - Create project activity"""
        if not hasattr(self, 'project_id'):
            self.log_result("Create Activity", False, "No project ID available")
            return False
        
        try:
            activity_data = {
                "project_id": self.project_id,
                "title": "Community Mobilization and Awareness Campaign",
                "description": "Conduct community meetings and awareness campaigns to inform target beneficiaries about the digital literacy training program and encourage participation.",
                "responsible_user_id": self.user_data["id"],
                "start_date": (datetime.now() + timedelta(days=15)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=60)).isoformat(),
                "budget_allocated": 150000.0,  # 150K RWF
                "deliverables": [
                    "Community meeting reports",
                    "Beneficiary registration database",
                    "Awareness materials distributed",
                    "Local leader engagement documentation"
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/activities",
                json=activity_data
            )
            
            if response.status_code == 200:
                data = response.json()
                activity_id = data.get("id") or data.get("_id")
                if activity_id and data.get("title") == activity_data["title"]:
                    self.activity_id = activity_id
                    self.log_result("Create Activity", True, 
                                  f"Activity '{activity_data['title']}' created successfully")
                    return True
                else:
                    self.log_result("Create Activity", False, "Activity data mismatch", data)
                    return False
            else:
                self.log_result("Create Activity", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Activity", False, f"Request error: {str(e)}")
            return False
    
    def test_create_kpi(self):
        """Test POST /api/kpis - Create KPI indicator"""
        if not hasattr(self, 'project_id'):
            self.log_result("Create KPI", False, "No project ID available")
            return False
        
        try:
            kpi_data = {
                "project_id": self.project_id,
                "name": "Number of People Trained in Digital Literacy",
                "description": "Total number of community members who have completed the basic digital literacy training program and passed the assessment",
                "indicator_type": "quantitative",
                "level": "output",
                "baseline_value": 0.0,
                "target_value": 5000.0,
                "unit_of_measurement": "people",
                "frequency": "Monthly",
                "responsible_user_id": self.user_data["id"],
                "data_source": "Training attendance records and assessment results",
                "collection_method": "Digital attendance system and online assessments"
            }
            
            response = self.session.post(
                f"{self.base_url}/kpis",
                json=kpi_data
            )
            
            if response.status_code == 200:
                data = response.json()
                kpi_id = data.get("id") or data.get("_id")
                if kpi_id and data.get("name") == kpi_data["name"]:
                    self.kpi_id = kpi_id
                    self.log_result("Create KPI", True, 
                                  f"KPI '{kpi_data['name']}' created successfully")
                    return True
                else:
                    self.log_result("Create KPI", False, "KPI data mismatch", data)
                    return False
            else:
                self.log_result("Create KPI", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create KPI", False, f"Request error: {str(e)}")
            return False
    
    def test_create_beneficiary(self):
        """Test POST /api/beneficiaries - Create beneficiary"""
        try:
            beneficiary_data = {
                "unique_id": f"DLT-{uuid.uuid4().hex[:8].upper()}",
                "first_name": "Jean Baptiste",
                "last_name": "Nzeyimana",
                "date_of_birth": (datetime.now() - timedelta(days=365*28)).isoformat(),  # 28 years old
                "gender": "Male",
                "location": "Nyagatare Sector, Nyagatare District",
                "contact_phone": "+250788456789",
                "household_size": 6,
                "education_level": "Primary",
                "employment_status": "Farmer"
            }
            
            response = self.session.post(
                f"{self.base_url}/beneficiaries",
                json=beneficiary_data
            )
            
            if response.status_code == 200:
                data = response.json()
                beneficiary_id = data.get("id") or data.get("_id")
                if beneficiary_id and data.get("unique_id") == beneficiary_data["unique_id"]:
                    self.beneficiary_id = beneficiary_id
                    self.log_result("Create Beneficiary", True, 
                                  f"Beneficiary '{beneficiary_data['first_name']} {beneficiary_data['last_name']}' created successfully")
                    return True
                else:
                    self.log_result("Create Beneficiary", False, "Beneficiary data mismatch", data)
                    return False
            else:
                self.log_result("Create Beneficiary", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Beneficiary", False, f"Request error: {str(e)}")
            return False
    
    def test_create_budget_item(self):
        """Test POST /api/budget - Create budget item"""
        if not hasattr(self, 'project_id'):
            self.log_result("Create Budget Item", False, "No project ID available")
            return False
        
        try:
            budget_data = {
                "project_id": self.project_id,
                "category": "training",
                "description": "Training materials, venue rental, and trainer fees for digital literacy sessions",
                "budgeted_amount": 800000.0,  # 800K RWF
                "currency": "RWF",
                "period_start": datetime.now().isoformat(),
                "period_end": (datetime.now() + timedelta(days=180)).isoformat(),  # 6 months
                "responsible_user_id": self.user_data["id"]
            }
            
            response = self.session.post(
                f"{self.base_url}/budget",
                json=budget_data
            )
            
            if response.status_code == 200:
                data = response.json()
                budget_id = data.get("id") or data.get("_id")
                if budget_id and data.get("category") == budget_data["category"]:
                    self.budget_item_id = budget_id
                    self.log_result("Create Budget Item", True, 
                                  f"Budget item for '{budget_data['category']}' created successfully (Amount: {budget_data['budgeted_amount']} RWF)")
                    return True
                else:
                    self.log_result("Create Budget Item", False, "Budget item data mismatch", data)
                    return False
            else:
                self.log_result("Create Budget Item", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Budget Item", False, f"Request error: {str(e)}")
            return False
    
    def test_get_users(self):
        """Test GET /api/users - Get users for dropdown population"""
        try:
            response = self.session.get(f"{self.base_url}/users")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check if users have required fields for dropdown
                    user = data[0]
                    required_fields = ["id", "name", "email", "role"]
                    
                    # Handle both 'id' and '_id' fields
                    user_id = user.get("id") or user.get("_id")
                    if user_id and all(field in user or field == "id" for field in required_fields):
                        self.log_result("Get Users", True, 
                                      f"Retrieved {len(data)} users with required fields for dropdown population")
                        return True
                    else:
                        missing_fields = [field for field in required_fields if field not in user and field != "id"]
                        self.log_result("Get Users", False, f"Missing required fields: {missing_fields}", user)
                        return False
                else:
                    self.log_result("Get Users", False, "No users found or invalid response", data)
                    return False
            else:
                self.log_result("Get Users", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Users", False, f"Request error: {str(e)}")
            return False
    
    def run_project_management_tests(self):
        """Run all project management creation tests"""
        print(f"🚀 Starting Project Management Creation Endpoints Test")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Setup authentication first
        if not self.setup_authentication():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Test sequence - order matters for dependencies
        tests = [
            ("1. Create Project", self.test_create_project),
            ("2. Create Activity", self.test_create_activity),
            ("3. Create KPI", self.test_create_kpi),
            ("4. Create Beneficiary", self.test_create_beneficiary),
            ("5. Create Budget Item", self.test_create_budget_item),
            ("6. Get Users", self.test_get_users),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            if test_func():
                passed += 1
            else:
                failed += 1
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 PROJECT MANAGEMENT TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed > 0:
            print(f"\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
        else:
            print(f"\n🎉 All project management creation endpoints are working correctly!")
            print(f"✅ Projects can be created with realistic data")
            print(f"✅ Activities can be linked to projects")
            print(f"✅ KPIs can be defined with proper metrics")
            print(f"✅ Beneficiaries can be registered with demographics")
            print(f"✅ Budget items can be allocated to projects")
            print(f"✅ Users endpoint provides data for dropdowns")

if __name__ == "__main__":
    tester = ProjectManagementTester()
    tester.run_project_management_tests()