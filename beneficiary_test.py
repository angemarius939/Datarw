#!/usr/bin/env python3
"""
Comprehensive Beneficiary Management System Testing for DataRW
Tests all beneficiary-related backend endpoints including authentication, beneficiary CRUD,
service records, KPIs, analytics, and GPS mapping functionality.
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
# Use the external URL for testing as specified in the environment
API_BASE_URL = f"{BACKEND_URL}/api"

class BeneficiaryAPITester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.test_results = []
        
        # Test data
        self.test_email = f"test.user.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Test User"
        
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
    
    def test_api_health(self):
        """Test API health endpoint"""
        try:
            # Test a simple API endpoint to verify API is working
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json={"test": "data"}  # Invalid data to trigger validation
            )
            
            # If we get a validation error, the API is working
            if response.status_code == 422:
                data = response.json()
                if "detail" in data and isinstance(data["detail"], list):
                    self.log_result("API Health Check", True, "API is responding with proper validation")
                    return True
            
            self.log_result("API Health Check", False, f"Unexpected response: {response.status_code}", response.text)
            return False
            
        except Exception as e:
            self.log_result("API Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration with valid data"""
        try:
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
                    
                    self.log_result("User Registration", True, "User registered successfully")
                    return True
                else:
                    self.log_result("User Registration", False, "Missing required fields in response", data)
                    return False
            else:
                self.log_result("User Registration", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("User Registration", False, f"Request error: {str(e)}")
            return False
    
    def test_user_login_valid(self):
        """Test user login with valid credentials"""
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
                if "access_token" in data and "user" in data:
                    # Update token in case it changed
                    self.auth_token = data["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    self.log_result("Valid Login", True, "Login successful")
                    return True
                else:
                    self.log_result("Valid Login", False, "Missing required fields in response", data)
                    return False
            else:
                self.log_result("Valid Login", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Valid Login", False, f"Request error: {str(e)}")
            return False

    # -------------------- Beneficiary Management System Tests --------------------
    def test_beneficiary_management_system(self):
        """Comprehensive test of the Beneficiary Management System endpoints"""
        print("\n" + "="*80)
        print("BENEFICIARY MANAGEMENT SYSTEM TESTING")
        print("="*80)
        
        success_count = 0
        total_tests = 12
        
        # Test 1: POST /api/beneficiaries - Create new beneficiary
        if self.test_create_beneficiary_enhanced():
            success_count += 1
        
        # Test 2: GET /api/beneficiaries - List beneficiaries with filtering and pagination
        if self.test_get_beneficiaries_enhanced():
            success_count += 1
        
        # Test 3: GET /api/beneficiaries/{id} - Get specific beneficiary
        if self.test_get_specific_beneficiary():
            success_count += 1
        
        # Test 4: PUT /api/beneficiaries/{id} - Update beneficiary
        if self.test_update_beneficiary():
            success_count += 1
        
        # Test 5: GET /api/beneficiaries/analytics - Get analytics
        if self.test_beneficiary_analytics():
            success_count += 1
        
        # Test 6: GET /api/beneficiaries/map-data - Get GPS data
        if self.test_beneficiary_map_data():
            success_count += 1
        
        # Test 7: POST /api/service-records - Create service record
        if self.test_create_service_record():
            success_count += 1
        
        # Test 8: POST /api/service-records/batch - Create batch service records
        if self.test_create_batch_service_records():
            success_count += 1
        
        # Test 9: GET /api/service-records - List service records
        if self.test_get_service_records():
            success_count += 1
        
        # Test 10: POST /api/beneficiary-kpis - Create beneficiary KPI
        if self.test_create_beneficiary_kpi():
            success_count += 1
        
        # Test 11: GET /api/beneficiary-kpis - Get beneficiary KPIs
        if self.test_get_beneficiary_kpis():
            success_count += 1
        
        # Test 12: PUT /api/beneficiary-kpis/{id} - Update KPI values
        if self.test_update_beneficiary_kpi():
            success_count += 1
        
        print(f"\nBENEFICIARY MANAGEMENT SYSTEM TESTING COMPLETE: {success_count}/{total_tests} tests passed")
        return success_count == total_tests

    def test_create_beneficiary_enhanced(self):
        """Test creating a new beneficiary with enhanced profile data"""
        try:
            beneficiary_data = {
                "name": f"Uwimana Marie {uuid.uuid4().hex[:6]}",
                "first_name": "Marie",
                "last_name": "Uwimana",
                "gender": "female",
                "age": 28,
                "date_of_birth": (datetime.now() - timedelta(days=28*365)).isoformat(),
                "contact_phone": "+250788123456",
                "contact_email": f"marie.uwimana.{uuid.uuid4().hex[:6]}@example.com",
                "national_id": f"1199580012345{uuid.uuid4().hex[:3]}",
                "address": "Kigali, Gasabo District, Remera Sector",
                "gps_latitude": -1.9441,
                "gps_longitude": 30.0619,
                "project_ids": [],
                "activity_ids": [],
                "custom_fields": {
                    "education_level": "secondary",
                    "household_size": 4,
                    "income_level": "low"
                },
                "tags": ["rural", "female-headed-household", "priority"]
            }
            
            response = self.session.post(
                f"{self.base_url}/beneficiaries",
                json=beneficiary_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "beneficiary" in data:
                    beneficiary = data["beneficiary"]
                    self.test_beneficiary_id = beneficiary.get("id")
                    
                    # Verify enhanced profile data
                    required_fields = ["name", "gender", "gps_latitude", "gps_longitude", "custom_fields"]
                    if all(field in beneficiary for field in required_fields):
                        self.log_result("Create Beneficiary Enhanced", True, 
                                      f"Beneficiary created with enhanced profile: {beneficiary['name']}")
                        return True
                    else:
                        missing = [f for f in required_fields if f not in beneficiary]
                        self.log_result("Create Beneficiary Enhanced", False, 
                                      f"Missing enhanced fields: {missing}", data)
                        return False
                else:
                    self.log_result("Create Beneficiary Enhanced", False, "Invalid response structure", data)
                    return False
            else:
                self.log_result("Create Beneficiary Enhanced", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Beneficiary Enhanced", False, f"Request error: {str(e)}")
            return False

    def test_get_beneficiaries_enhanced(self):
        """Test getting beneficiaries with filtering, pagination, and search"""
        try:
            # Test basic listing
            response = self.session.get(f"{self.base_url}/beneficiaries")
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and "total" in data and "page" in data:
                    # Test pagination
                    page_response = self.session.get(f"{self.base_url}/beneficiaries?page=1&page_size=5")
                    if page_response.status_code == 200:
                        page_data = page_response.json()
                        if len(page_data.get("items", [])) <= 5:
                            # Test search functionality
                            search_response = self.session.get(f"{self.base_url}/beneficiaries?search=Marie")
                            if search_response.status_code == 200:
                                self.log_result("Get Beneficiaries Enhanced", True, 
                                              f"Retrieved {data['total']} beneficiaries with pagination and search")
                                return True
                            else:
                                self.log_result("Get Beneficiaries Enhanced", False, 
                                              f"Search failed: HTTP {search_response.status_code}")
                                return False
                        else:
                            self.log_result("Get Beneficiaries Enhanced", False, 
                                          f"Pagination not working: got {len(page_data.get('items', []))} items")
                            return False
                    else:
                        self.log_result("Get Beneficiaries Enhanced", False, 
                                      f"Pagination failed: HTTP {page_response.status_code}")
                        return False
                else:
                    self.log_result("Get Beneficiaries Enhanced", False, "Missing pagination fields", data)
                    return False
            else:
                self.log_result("Get Beneficiaries Enhanced", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Beneficiaries Enhanced", False, f"Request error: {str(e)}")
            return False

    def test_get_specific_beneficiary(self):
        """Test getting a specific beneficiary by ID"""
        if not hasattr(self, 'test_beneficiary_id') or not self.test_beneficiary_id:
            self.log_result("Get Specific Beneficiary", False, "No beneficiary ID from previous test")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/beneficiaries/{self.test_beneficiary_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "name" in data and "id" in data:
                    self.log_result("Get Specific Beneficiary", True, 
                                  f"Retrieved beneficiary: {data['name']}")
                    return True
                else:
                    self.log_result("Get Specific Beneficiary", False, "Missing required fields", data)
                    return False
            else:
                self.log_result("Get Specific Beneficiary", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Specific Beneficiary", False, f"Request error: {str(e)}")
            return False

    def test_update_beneficiary(self):
        """Test updating beneficiary information"""
        if not hasattr(self, 'test_beneficiary_id') or not self.test_beneficiary_id:
            self.log_result("Update Beneficiary", False, "No beneficiary ID from previous test")
            return False
        
        try:
            update_data = {
                "contact_phone": "+250788654321",
                "address": "Kigali, Nyarugenge District, Nyamirambo Sector",
                "custom_fields": {
                    "education_level": "university",
                    "household_size": 5,
                    "income_level": "medium"
                },
                "tags": ["urban", "female-headed-household", "priority", "educated"]
            }
            
            response = self.session.put(
                f"{self.base_url}/beneficiaries/{self.test_beneficiary_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "beneficiary" in data:
                    beneficiary = data["beneficiary"]
                    if beneficiary.get("contact_phone") == update_data["contact_phone"]:
                        self.log_result("Update Beneficiary", True, "Beneficiary updated successfully")
                        return True
                    else:
                        self.log_result("Update Beneficiary", False, "Update not reflected", data)
                        return False
                else:
                    self.log_result("Update Beneficiary", False, "Invalid response structure", data)
                    return False
            else:
                self.log_result("Update Beneficiary", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update Beneficiary", False, f"Request error: {str(e)}")
            return False

    def test_beneficiary_analytics(self):
        """Test getting beneficiary analytics and insights"""
        try:
            response = self.session.get(f"{self.base_url}/beneficiaries/analytics")
            
            if response.status_code == 200:
                data = response.json()
                required_sections = ["summary", "demographics", "services"]
                if all(section in data for section in required_sections):
                    summary = data["summary"]
                    demographics = data["demographics"]
                    
                    # Verify analytics structure
                    if ("total_beneficiaries" in summary and 
                        "gender_distribution" in demographics and
                        "age_distribution" in demographics):
                        self.log_result("Beneficiary Analytics", True, 
                                      f"Analytics retrieved: {summary['total_beneficiaries']} beneficiaries")
                        return True
                    else:
                        self.log_result("Beneficiary Analytics", False, "Missing analytics fields", data)
                        return False
                else:
                    missing = [s for s in required_sections if s not in data]
                    self.log_result("Beneficiary Analytics", False, f"Missing sections: {missing}", data)
                    return False
            else:
                self.log_result("Beneficiary Analytics", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Beneficiary Analytics", False, f"Request error: {str(e)}")
            return False

    def test_beneficiary_map_data(self):
        """Test getting GPS location data for mapping"""
        try:
            response = self.session.get(f"{self.base_url}/beneficiaries/map-data")
            
            if response.status_code == 200:
                data = response.json()
                if "map_points" in data:
                    map_points = data["map_points"]
                    if isinstance(map_points, list):
                        # Check if any points have GPS coordinates
                        gps_points = [p for p in map_points if p.get("latitude") and p.get("longitude")]
                        self.log_result("Beneficiary Map Data", True, 
                                      f"Retrieved {len(map_points)} map points, {len(gps_points)} with GPS")
                        return True
                    else:
                        self.log_result("Beneficiary Map Data", False, "map_points is not a list", data)
                        return False
                else:
                    self.log_result("Beneficiary Map Data", False, "Missing map_points field", data)
                    return False
            else:
                self.log_result("Beneficiary Map Data", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Beneficiary Map Data", False, f"Request error: {str(e)}")
            return False

    def test_create_service_record(self):
        """Test creating individual service record"""
        if not hasattr(self, 'test_beneficiary_id') or not self.test_beneficiary_id:
            self.log_result("Create Service Record", False, "No beneficiary ID from previous test")
            return False
        
        try:
            service_data = {
                "beneficiary_id": self.test_beneficiary_id,
                "project_id": "test-project-001",
                "service_type": "training",
                "service_name": "Digital Literacy Training Session",
                "service_description": "Basic computer skills and internet usage training",
                "service_date": datetime.now().isoformat(),
                "service_location": "Kigali Community Center",
                "gps_latitude": -1.9441,
                "gps_longitude": 30.0619,
                "staff_responsible": self.user_data["id"],
                "staff_name": self.user_data["name"],
                "resources_used": ["laptops", "training_materials", "internet"],
                "cost": 25.0,
                "outcome": "completed",
                "notes": "Participant showed good progress in basic computer skills",
                "satisfaction_score": 4,
                "follow_up_required": True,
                "follow_up_date": (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            response = self.session.post(
                f"{self.base_url}/service-records",
                json=service_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "service_record" in data:
                    service_record = data["service_record"]
                    self.test_service_record_id = service_record.get("id")
                    self.log_result("Create Service Record", True, 
                                  f"Service record created: {service_record.get('service_name')}")
                    return True
                else:
                    self.log_result("Create Service Record", False, "Invalid response structure", data)
                    return False
            else:
                self.log_result("Create Service Record", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Service Record", False, f"Request error: {str(e)}")
            return False

    def test_create_batch_service_records(self):
        """Test creating batch service records for multiple beneficiaries"""
        if not hasattr(self, 'test_beneficiary_id') or not self.test_beneficiary_id:
            self.log_result("Create Batch Service Records", False, "No beneficiary ID from previous test")
            return False
        
        try:
            batch_data = {
                "beneficiary_ids": [self.test_beneficiary_id],  # Using existing beneficiary
                "project_id": "test-project-001",
                "service_type": "distribution",
                "service_name": "Monthly Food Distribution",
                "service_description": "Distribution of food packages to beneficiary households",
                "service_date": datetime.now().isoformat(),
                "service_location": "Community Distribution Center",
                "gps_latitude": -1.9441,
                "gps_longitude": 30.0619,
                "staff_responsible": self.user_data["id"],
                "staff_name": self.user_data["name"],
                "resources_used": ["food_packages", "transport", "volunteers"],
                "cost_per_beneficiary": 15.0,
                "notes": "Monthly food distribution completed successfully"
            }
            
            response = self.session.post(
                f"{self.base_url}/service-records/batch",
                json=batch_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "service_records" in data and "count" in data:
                    count = data["count"]
                    self.log_result("Create Batch Service Records", True, 
                                  f"Created {count} batch service records")
                    return True
                else:
                    self.log_result("Create Batch Service Records", False, "Invalid response structure", data)
                    return False
            else:
                self.log_result("Create Batch Service Records", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Batch Service Records", False, f"Request error: {str(e)}")
            return False

    def test_get_service_records(self):
        """Test listing service records with filtering"""
        try:
            # Test basic listing
            response = self.session.get(f"{self.base_url}/service-records")
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and "total" in data:
                    # Test filtering by beneficiary
                    if hasattr(self, 'test_beneficiary_id') and self.test_beneficiary_id:
                        filter_response = self.session.get(
                            f"{self.base_url}/service-records?beneficiary_id={self.test_beneficiary_id}"
                        )
                        if filter_response.status_code == 200:
                            filter_data = filter_response.json()
                            self.log_result("Get Service Records", True, 
                                          f"Retrieved {data['total']} service records with filtering")
                            return True
                        else:
                            self.log_result("Get Service Records", False, 
                                          f"Filtering failed: HTTP {filter_response.status_code}")
                            return False
                    else:
                        self.log_result("Get Service Records", True, 
                                      f"Retrieved {data['total']} service records")
                        return True
                else:
                    self.log_result("Get Service Records", False, "Missing required fields", data)
                    return False
            else:
                self.log_result("Get Service Records", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Service Records", False, f"Request error: {str(e)}")
            return False

    def test_create_beneficiary_kpi(self):
        """Test creating beneficiary-specific KPI"""
        if not hasattr(self, 'test_beneficiary_id') or not self.test_beneficiary_id:
            self.log_result("Create Beneficiary KPI", False, "No beneficiary ID from previous test")
            return False
        
        try:
            kpi_data = {
                "beneficiary_id": self.test_beneficiary_id,
                "project_id": "test-project-001",
                "kpi_name": "Digital Literacy Score",
                "kpi_description": "Measures progress in digital literacy skills",
                "kpi_type": "percentage",
                "unit_of_measure": "percentage",
                "baseline_value": 20.0,
                "target_value": 80.0,
                "current_value": 45.0,
                "measurement_frequency": "monthly"
            }
            
            response = self.session.post(
                f"{self.base_url}/beneficiary-kpis",
                json=kpi_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "kpi" in data:
                    kpi = data["kpi"]
                    self.test_kpi_id = kpi.get("id")
                    
                    # Verify progress calculation
                    if "progress_percentage" in kpi:
                        self.log_result("Create Beneficiary KPI", True, 
                                      f"KPI created: {kpi['kpi_name']} with {kpi.get('progress_percentage', 0):.1f}% progress")
                        return True
                    else:
                        self.log_result("Create Beneficiary KPI", False, "Missing progress calculation", data)
                        return False
                else:
                    self.log_result("Create Beneficiary KPI", False, "Invalid response structure", data)
                    return False
            else:
                self.log_result("Create Beneficiary KPI", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Beneficiary KPI", False, f"Request error: {str(e)}")
            return False

    def test_get_beneficiary_kpis(self):
        """Test getting beneficiary KPIs with filtering"""
        try:
            # Test basic listing
            response = self.session.get(f"{self.base_url}/beneficiary-kpis")
            
            if response.status_code == 200:
                data = response.json()
                if "kpis" in data:
                    kpis = data["kpis"]
                    
                    # Test filtering by beneficiary
                    if hasattr(self, 'test_beneficiary_id') and self.test_beneficiary_id:
                        filter_response = self.session.get(
                            f"{self.base_url}/beneficiary-kpis?beneficiary_id={self.test_beneficiary_id}"
                        )
                        if filter_response.status_code == 200:
                            self.log_result("Get Beneficiary KPIs", True, 
                                          f"Retrieved {len(kpis)} KPIs with filtering")
                            return True
                        else:
                            self.log_result("Get Beneficiary KPIs", False, 
                                          f"Filtering failed: HTTP {filter_response.status_code}")
                            return False
                    else:
                        self.log_result("Get Beneficiary KPIs", True, f"Retrieved {len(kpis)} KPIs")
                        return True
                else:
                    self.log_result("Get Beneficiary KPIs", False, "Missing kpis field", data)
                    return False
            else:
                self.log_result("Get Beneficiary KPIs", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Get Beneficiary KPIs", False, f"Request error: {str(e)}")
            return False

    def test_update_beneficiary_kpi(self):
        """Test updating KPI values"""
        if not hasattr(self, 'test_kpi_id') or not self.test_kpi_id:
            self.log_result("Update Beneficiary KPI", False, "No KPI ID from previous test")
            return False
        
        try:
            update_data = {
                "current_value": 65.0,
                "target_value": 85.0,
                "measurement_date": datetime.now().isoformat(),
                "next_measurement_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "notes": "Significant improvement in digital literacy skills observed"
            }
            
            response = self.session.put(
                f"{self.base_url}/beneficiary-kpis/{self.test_kpi_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "kpi" in data:
                    kpi = data["kpi"]
                    if kpi.get("current_value") == update_data["current_value"]:
                        progress = kpi.get("progress_percentage", 0)
                        self.log_result("Update Beneficiary KPI", True, 
                                      f"KPI updated: current value {kpi['current_value']}, progress {progress:.1f}%")
                        return True
                    else:
                        self.log_result("Update Beneficiary KPI", False, "Update not reflected", data)
                        return False
                else:
                    self.log_result("Update Beneficiary KPI", False, "Invalid response structure", data)
                    return False
            else:
                self.log_result("Update Beneficiary KPI", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update Beneficiary KPI", False, f"Request error: {str(e)}")
            return False

    def run_beneficiary_tests_only(self):
        """Run only the beneficiary management system tests"""
        print("="*80)
        print("BENEFICIARY MANAGEMENT SYSTEM TESTING")
        print("="*80)
        
        # Test API health first
        if not self.test_api_health():
            print("❌ API is not responding. Stopping tests.")
            return False
        
        # Run authentication tests
        if not self.test_user_registration():
            print("❌ User registration failed. Cannot proceed with tests.")
            return False
        
        if not self.test_user_login_valid():
            print("❌ User login failed. Cannot proceed with tests.")
            return False
        
        # Run beneficiary management system tests
        beneficiary_success = self.test_beneficiary_management_system()
        
        # Print summary
        total_tests = 3 + 12  # 3 setup tests + 12 beneficiary tests
        total_passed = 3 + (12 if beneficiary_success else 0)  # Assuming setup passed
        
        print("\n" + "="*80)
        print(f"BENEFICIARY TESTING COMPLETE: {total_passed}/{total_tests} tests passed")
        print(f"Success Rate: {(total_passed/total_tests)*100:.1f}%")
        print("="*80)
        
        return total_passed == total_tests


if __name__ == "__main__":
    tester = BeneficiaryAPITester()
    
    # Run only beneficiary management tests as requested
    success = tester.run_beneficiary_tests_only()
    
    # Print final summary
    if success:
        print("\n🎉 ALL BENEFICIARY TESTS PASSED! The Beneficiary Management System is working correctly.")
    else:
        print("\n⚠️  SOME BENEFICIARY TESTS FAILED. Please check the results above.")
        
    # Print test results summary
    print(f"\nTest Results Summary:")
    for result in tester.test_results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['test']}: {result['message']}")
    
    exit(0 if success else 1)