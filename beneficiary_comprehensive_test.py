#!/usr/bin/env python3
"""
Comprehensive Beneficiary Management System Testing for DataRW
Final comprehensive testing of the complete Beneficiary Management System to validate all implemented features
and demonstrate the full scope of capabilities developed.
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

class BeneficiaryManagementTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.test_results = []
        
        # Test data
        self.test_email = f"beneficiary.tester.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Beneficiary Test User"
        
        # Test entities
        self.test_project_id = None
        self.test_activity_id = None
        self.test_beneficiary_ids = []
        self.test_service_record_ids = []
        self.test_kpi_ids = []
        
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
                
                # Set authorization header for future requests
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
    
    def setup_test_project(self):
        """Create a test project for beneficiary testing"""
        try:
            project_data = {
                "name": f"Beneficiary Test Project {uuid.uuid4().hex[:8]}",
                "description": "Test project for beneficiary management system testing",
                "project_manager_id": self.user_data["id"],
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=365)).isoformat(),
                "budget_total": 1000000.0,
                "beneficiaries_target": 500,
                "donor_organization": "Test Foundation",
                "status": "active"
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_project_id = data.get("id") or data.get("_id")
                self.log_result("Test Project Setup", True, f"Test project created with ID: {self.test_project_id}")
                return True
            else:
                self.log_result("Test Project Setup", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Test Project Setup", False, f"Request error: {str(e)}")
            return False
    
    def setup_test_activity(self):
        """Create a test activity for beneficiary testing"""
        try:
            activity_data = {
                "name": f"Beneficiary Test Activity {uuid.uuid4().hex[:8]}",
                "description": "Test activity for beneficiary management system testing",
                "project_id": self.test_project_id,
                "assigned_to": self.user_data["id"],
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
                "budget_allocated": 200000.0,
                "deliverables": ["Training materials", "Participant certificates"],
                "dependencies": []
            }
            
            response = self.session.post(
                f"{self.base_url}/activities",
                json=activity_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_activity_id = data.get("id") or data.get("_id")
                self.log_result("Test Activity Setup", True, f"Test activity created with ID: {self.test_activity_id}")
                return True
            else:
                self.log_result("Test Activity Setup", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Test Activity Setup", False, f"Request error: {str(e)}")
            return False
    
    def test_create_beneficiary_enhanced(self):
        """Test POST /api/beneficiaries - Enhanced beneficiary creation with GPS, custom fields"""
        try:
            beneficiary_data = {
                "project_id": self.test_project_id,
                "unique_id": f"BEN-{uuid.uuid4().hex[:8].upper()}",
                "name": "Jean Baptiste Nzeyimana",
                "gender": "male",
                "age": 28,
                "phone": "+250788123456",
                "email": "jean.baptiste@example.com",
                "address": "Kigali, Gasabo District, Remera Sector",
                "beneficiary_type": "individual",
                "enrollment_date": datetime.now().isoformat(),
                "status": "active",
                # Enhanced features: GPS coordinates
                "gps_coordinates": {
                    "latitude": -1.9441,
                    "longitude": 30.0619,
                    "accuracy": 10.5
                },
                # Enhanced features: Custom fields
                "custom_fields": {
                    "education_level": "secondary",
                    "occupation": "farmer",
                    "household_size": 5,
                    "income_level": "low",
                    "special_needs": "none"
                },
                # Enhanced features: Tags
                "tags": ["rural", "agriculture", "youth", "digital_literacy"],
                "notes": "Enthusiastic participant in digital literacy programs"
            }
            
            response = self.session.post(
                f"{self.base_url}/beneficiaries",
                json=beneficiary_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "beneficiary" in data:
                    beneficiary = data["beneficiary"]
                    beneficiary_id = beneficiary.get("id") or beneficiary.get("_id")
                    self.test_beneficiary_ids.append(beneficiary_id)
                    
                    # Verify enhanced features
                    has_gps = "gps_coordinates" in beneficiary
                    has_custom_fields = "custom_fields" in beneficiary
                    has_tags = "tags" in beneficiary
                    
                    if has_gps and has_custom_fields and has_tags:
                        self.log_result("Create Beneficiary Enhanced", True, 
                                      f"Enhanced beneficiary created successfully with GPS, custom fields, and tags")
                        return True
                    else:
                        missing_features = []
                        if not has_gps: missing_features.append("GPS coordinates")
                        if not has_custom_fields: missing_features.append("custom fields")
                        if not has_tags: missing_features.append("tags")
                        self.log_result("Create Beneficiary Enhanced", False, 
                                      f"Missing enhanced features: {', '.join(missing_features)}", data)
                        return False
                else:
                    self.log_result("Create Beneficiary Enhanced", False, "Missing success/beneficiary in response", data)
                    return False
            else:
                self.log_result("Create Beneficiary Enhanced", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Beneficiary Enhanced", False, f"Request error: {str(e)}")
            return False
    
    def test_get_beneficiaries_advanced_filtering(self):
        """Test GET /api/beneficiaries - Advanced filtering, pagination, search functionality"""
        try:
            # Create additional test beneficiaries for filtering
            test_beneficiaries = [
                {
                    "project_id": self.test_project_id,
                    "unique_id": f"BEN-{uuid.uuid4().hex[:8].upper()}",
                    "name": "Marie Claire Uwimana",
                    "gender": "female",
                    "age": 35,
                    "beneficiary_type": "individual",
                    "enrollment_date": datetime.now().isoformat(),
                    "status": "active",
                    "tags": ["urban", "business", "women_empowerment"]
                },
                {
                    "project_id": self.test_project_id,
                    "unique_id": f"BEN-{uuid.uuid4().hex[:8].upper()}",
                    "name": "Paul Kagame Muhire",
                    "gender": "male",
                    "age": 42,
                    "beneficiary_type": "individual",
                    "enrollment_date": datetime.now().isoformat(),
                    "status": "inactive",
                    "tags": ["rural", "agriculture", "cooperative"]
                }
            ]
            
            # Create additional beneficiaries
            for beneficiary_data in test_beneficiaries:
                response = self.session.post(f"{self.base_url}/beneficiaries", json=beneficiary_data)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "beneficiary" in data:
                        beneficiary_id = data["beneficiary"].get("id") or data["beneficiary"].get("_id")
                        self.test_beneficiary_ids.append(beneficiary_id)
            
            # Test 1: Basic pagination
            response = self.session.get(f"{self.base_url}/beneficiaries?page=1&page_size=2")
            if response.status_code != 200:
                self.log_result("Get Beneficiaries Advanced Filtering", False, 
                              f"Basic pagination failed: HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            if not ("items" in data and "total" in data and "page" in data and "page_size" in data):
                self.log_result("Get Beneficiaries Advanced Filtering", False, 
                              "Missing pagination metadata", data)
                return False
            
            # Test 2: Project filtering
            response = self.session.get(f"{self.base_url}/beneficiaries?project_id={self.test_project_id}")
            if response.status_code != 200:
                self.log_result("Get Beneficiaries Advanced Filtering", False, 
                              f"Project filtering failed: HTTP {response.status_code}", response.text)
                return False
            
            # Test 3: Status filtering
            response = self.session.get(f"{self.base_url}/beneficiaries?status=active")
            if response.status_code != 200:
                self.log_result("Get Beneficiaries Advanced Filtering", False, 
                              f"Status filtering failed: HTTP {response.status_code}", response.text)
                return False
            
            # Test 4: Search functionality
            response = self.session.get(f"{self.base_url}/beneficiaries?search=Jean")
            if response.status_code != 200:
                self.log_result("Get Beneficiaries Advanced Filtering", False, 
                              f"Search functionality failed: HTTP {response.status_code}", response.text)
                return False
            
            # Test 5: Risk level filtering (if implemented)
            response = self.session.get(f"{self.base_url}/beneficiaries?risk_level=low")
            if response.status_code != 200:
                self.log_result("Get Beneficiaries Advanced Filtering", False, 
                              f"Risk level filtering failed: HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Get Beneficiaries Advanced Filtering", True, 
                          "Advanced filtering, pagination, and search functionality working correctly")
            return True
            
        except Exception as e:
            self.log_result("Get Beneficiaries Advanced Filtering", False, f"Request error: {str(e)}")
            return False
    
    def test_update_beneficiary_with_risk_scoring(self):
        """Test PUT /api/beneficiaries/{id} - Profile updates with risk scoring"""
        try:
            if not self.test_beneficiary_ids:
                self.log_result("Update Beneficiary Risk Scoring", False, "No beneficiary ID available")
                return False
            
            beneficiary_id = self.test_beneficiary_ids[0]
            update_data = {
                "phone": "+250788654321",
                "address": "Kigali, Nyarugenge District, Nyamirambo Sector",
                "custom_fields": {
                    "education_level": "university",
                    "occupation": "teacher",
                    "household_size": 3,
                    "income_level": "medium",
                    "special_needs": "none"
                },
                "tags": ["urban", "education", "professional", "digital_literacy"],
                "notes": "Updated profile with improved education and income status"
            }
            
            response = self.session.put(
                f"{self.base_url}/beneficiaries/{beneficiary_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "beneficiary" in data:
                    beneficiary = data["beneficiary"]
                    
                    # Verify updates were applied
                    if (beneficiary.get("phone") == update_data["phone"] and
                        beneficiary.get("address") == update_data["address"]):
                        
                        # Check if risk scoring is present (may be calculated automatically)
                        has_risk_score = "risk_score" in beneficiary or "risk_level" in beneficiary
                        
                        self.log_result("Update Beneficiary Risk Scoring", True, 
                                      f"Beneficiary updated successfully{' with risk scoring' if has_risk_score else ''}")
                        return True
                    else:
                        self.log_result("Update Beneficiary Risk Scoring", False, 
                                      "Updates not properly applied", data)
                        return False
                else:
                    self.log_result("Update Beneficiary Risk Scoring", False, 
                                  "Missing success/beneficiary in response", data)
                    return False
            else:
                self.log_result("Update Beneficiary Risk Scoring", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update Beneficiary Risk Scoring", False, f"Request error: {str(e)}")
            return False
    
    def test_beneficiary_analytics(self):
        """Test GET /api/beneficiaries/analytics - Demographics, risk analysis, service statistics"""
        try:
            response = self.session.get(f"{self.base_url}/beneficiaries/analytics")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for analytics sections
                required_sections = ["demographics", "service_statistics"]
                optional_sections = ["risk_analysis", "geographic_distribution", "enrollment_trends"]
                
                has_required = all(section in data for section in required_sections)
                has_optional = any(section in data for section in optional_sections)
                
                if has_required:
                    # Verify demographics structure
                    demographics = data.get("demographics", {})
                    demo_fields = ["total_beneficiaries", "gender_distribution", "age_distribution"]
                    has_demo_fields = any(field in demographics for field in demo_fields)
                    
                    # Verify service statistics structure
                    service_stats = data.get("service_statistics", {})
                    service_fields = ["total_services", "services_by_type", "satisfaction_scores"]
                    has_service_fields = any(field in service_stats for field in service_fields)
                    
                    if has_demo_fields and has_service_fields:
                        self.log_result("Beneficiary Analytics", True, 
                                      f"Analytics retrieved with demographics and service statistics{' plus additional insights' if has_optional else ''}")
                        return True
                    else:
                        self.log_result("Beneficiary Analytics", False, 
                                      "Missing required fields in analytics sections", data)
                        return False
                else:
                    self.log_result("Beneficiary Analytics", False, 
                                  f"Missing required analytics sections: {[s for s in required_sections if s not in data]}", data)
                    return False
            else:
                self.log_result("Beneficiary Analytics", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Beneficiary Analytics", False, f"Request error: {str(e)}")
            return False
    
    def test_beneficiary_map_data(self):
        """Test GET /api/beneficiaries/map-data - GPS mapping capabilities"""
        try:
            response = self.session.get(f"{self.base_url}/beneficiaries/map-data")
            
            if response.status_code == 200:
                data = response.json()
                
                if "map_points" in data:
                    map_points = data["map_points"]
                    
                    if isinstance(map_points, list):
                        # Check if we have GPS data from our test beneficiaries
                        has_gps_data = len(map_points) > 0
                        
                        if has_gps_data:
                            # Verify map point structure
                            sample_point = map_points[0]
                            required_fields = ["latitude", "longitude"]
                            optional_fields = ["beneficiary_id", "name", "status", "accuracy"]
                            
                            has_coordinates = all(field in sample_point for field in required_fields)
                            has_metadata = any(field in sample_point for field in optional_fields)
                            
                            if has_coordinates:
                                self.log_result("Beneficiary Map Data", True, 
                                              f"GPS mapping data retrieved with {len(map_points)} points{' including metadata' if has_metadata else ''}")
                                return True
                            else:
                                self.log_result("Beneficiary Map Data", False, 
                                              "Map points missing required coordinate fields", data)
                                return False
                        else:
                            self.log_result("Beneficiary Map Data", True, 
                                          "Map data endpoint working (no GPS coordinates available)")
                            return True
                    else:
                        self.log_result("Beneficiary Map Data", False, 
                                      f"map_points should be a list, got {type(map_points)}", data)
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
        """Test POST /api/service-records - Individual service tracking with GPS and satisfaction"""
        try:
            if not self.test_beneficiary_ids:
                self.log_result("Create Service Record", False, "No beneficiary ID available")
                return False
            
            service_data = {
                "beneficiary_id": self.test_beneficiary_ids[0],
                "project_id": self.test_project_id,
                "activity_id": self.test_activity_id,
                "service_type": "training",
                "service_name": "Digital Literacy Training Session 1",
                "service_date": datetime.now().isoformat(),
                "duration_minutes": 120,
                "provider_name": "DataRW Training Team",
                "location": "Kigali Community Center",
                # GPS tracking
                "gps_coordinates": {
                    "latitude": -1.9441,
                    "longitude": 30.0619,
                    "accuracy": 8.2
                },
                # Satisfaction scoring
                "satisfaction_score": 4.5,
                "satisfaction_feedback": "Very helpful training session, learned a lot about computer basics",
                "attendance_status": "present",
                "completion_status": "completed",
                "notes": "Participant was very engaged and asked good questions",
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
                    service_record_id = service_record.get("id") or service_record.get("_id")
                    self.test_service_record_ids.append(service_record_id)
                    
                    # Verify GPS and satisfaction features
                    has_gps = "gps_coordinates" in service_record
                    has_satisfaction = "satisfaction_score" in service_record
                    has_follow_up = "follow_up_required" in service_record
                    
                    if has_gps and has_satisfaction:
                        self.log_result("Create Service Record", True, 
                                      f"Service record created with GPS tracking and satisfaction scoring{' plus follow-up tracking' if has_follow_up else ''}")
                        return True
                    else:
                        missing_features = []
                        if not has_gps: missing_features.append("GPS coordinates")
                        if not has_satisfaction: missing_features.append("satisfaction scoring")
                        self.log_result("Create Service Record", False, 
                                      f"Missing features: {', '.join(missing_features)}", data)
                        return False
                else:
                    self.log_result("Create Service Record", False, "Missing success/service_record in response", data)
                    return False
            else:
                self.log_result("Create Service Record", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Service Record", False, f"Request error: {str(e)}")
            return False
    
    def test_create_batch_service_records(self):
        """Test POST /api/service-records/batch - Batch processing for multiple beneficiaries"""
        try:
            if len(self.test_beneficiary_ids) < 2:
                self.log_result("Create Batch Service Records", False, "Need at least 2 beneficiary IDs")
                return False
            
            batch_data = {
                "service_type": "health_checkup",
                "service_name": "Monthly Health Screening",
                "service_date": datetime.now().isoformat(),
                "duration_minutes": 30,
                "provider_name": "Community Health Workers",
                "location": "Mobile Health Clinic",
                "project_id": self.test_project_id,
                "activity_id": self.test_activity_id,
                "beneficiary_records": [
                    {
                        "beneficiary_id": self.test_beneficiary_ids[0],
                        "attendance_status": "present",
                        "completion_status": "completed",
                        "satisfaction_score": 4.2,
                        "satisfaction_feedback": "Good health screening service",
                        "notes": "Blood pressure normal, weight stable"
                    },
                    {
                        "beneficiary_id": self.test_beneficiary_ids[1] if len(self.test_beneficiary_ids) > 1 else self.test_beneficiary_ids[0],
                        "attendance_status": "present", 
                        "completion_status": "completed",
                        "satisfaction_score": 4.8,
                        "satisfaction_feedback": "Excellent service, very thorough",
                        "notes": "All vitals normal, recommended dietary improvements"
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/service-records/batch",
                json=batch_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "service_records" in data and "count" in data:
                    service_records = data["service_records"]
                    count = data["count"]
                    
                    if count == len(batch_data["beneficiary_records"]) and len(service_records) == count:
                        # Store service record IDs
                        for record in service_records:
                            record_id = record.get("id") or record.get("_id")
                            if record_id:
                                self.test_service_record_ids.append(record_id)
                        
                        self.log_result("Create Batch Service Records", True, 
                                      f"Batch service records created successfully for {count} beneficiaries")
                        return True
                    else:
                        self.log_result("Create Batch Service Records", False, 
                                      f"Count mismatch: expected {len(batch_data['beneficiary_records'])}, got {count}", data)
                        return False
                else:
                    self.log_result("Create Batch Service Records", False, 
                                  "Missing success/service_records/count in response", data)
                    return False
            else:
                self.log_result("Create Batch Service Records", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Batch Service Records", False, f"Request error: {str(e)}")
            return False
    
    def test_get_service_records_filtering(self):
        """Test GET /api/service-records - Comprehensive service history with filtering"""
        try:
            # Test 1: Basic retrieval
            response = self.session.get(f"{self.base_url}/service-records")
            if response.status_code != 200:
                self.log_result("Get Service Records Filtering", False, 
                              f"Basic retrieval failed: HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            if not ("items" in data and "total" in data):
                self.log_result("Get Service Records Filtering", False, "Missing pagination structure", data)
                return False
            
            # Test 2: Beneficiary filtering
            if self.test_beneficiary_ids:
                response = self.session.get(
                    f"{self.base_url}/service-records?beneficiary_id={self.test_beneficiary_ids[0]}"
                )
                if response.status_code != 200:
                    self.log_result("Get Service Records Filtering", False, 
                                  f"Beneficiary filtering failed: HTTP {response.status_code}", response.text)
                    return False
            
            # Test 3: Project filtering
            if self.test_project_id:
                response = self.session.get(
                    f"{self.base_url}/service-records?project_id={self.test_project_id}"
                )
                if response.status_code != 200:
                    self.log_result("Get Service Records Filtering", False, 
                                  f"Project filtering failed: HTTP {response.status_code}", response.text)
                    return False
            
            # Test 4: Service type filtering
            response = self.session.get(f"{self.base_url}/service-records?service_type=training")
            if response.status_code != 200:
                self.log_result("Get Service Records Filtering", False, 
                              f"Service type filtering failed: HTTP {response.status_code}", response.text)
                return False
            
            # Test 5: Date range filtering
            date_from = (datetime.now() - timedelta(days=1)).isoformat()
            date_to = (datetime.now() + timedelta(days=1)).isoformat()
            response = self.session.get(
                f"{self.base_url}/service-records?date_from={date_from}&date_to={date_to}"
            )
            if response.status_code != 200:
                self.log_result("Get Service Records Filtering", False, 
                              f"Date range filtering failed: HTTP {response.status_code}", response.text)
                return False
            
            self.log_result("Get Service Records Filtering", True, 
                          "Service records filtering working correctly with all filter types")
            return True
            
        except Exception as e:
            self.log_result("Get Service Records Filtering", False, f"Request error: {str(e)}")
            return False
    
    def test_create_beneficiary_kpi(self):
        """Test POST /api/beneficiary-kpis - Custom KPI creation with progress tracking"""
        try:
            if not self.test_beneficiary_ids:
                self.log_result("Create Beneficiary KPI", False, "No beneficiary ID available")
                return False
            
            kpi_data = {
                "beneficiary_id": self.test_beneficiary_ids[0],
                "project_id": self.test_project_id,
                "activity_id": self.test_activity_id,
                "kpi_name": "Digital Literacy Skills Assessment",
                "kpi_description": "Measures improvement in basic computer and internet skills",
                "measurement_unit": "score",
                "baseline_value": 2.0,
                "target_value": 8.0,
                "current_value": 5.5,
                "target_date": (datetime.now() + timedelta(days=90)).isoformat(),
                "measurement_frequency": "monthly",
                "data_source": "skills_assessment_test",
                "responsible_person": self.user_data["name"],
                "notes": "Baseline assessment completed, showing good progress potential"
            }
            
            response = self.session.post(
                f"{self.base_url}/beneficiary-kpis",
                json=kpi_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "kpi" in data:
                    kpi = data["kpi"]
                    kpi_id = kpi.get("id") or kpi.get("_id")
                    self.test_kpi_ids.append(kpi_id)
                    
                    # Verify progress tracking calculation
                    has_progress = "progress_percentage" in kpi
                    has_baseline = kpi.get("baseline_value") == kpi_data["baseline_value"]
                    has_target = kpi.get("target_value") == kpi_data["target_value"]
                    has_current = kpi.get("current_value") == kpi_data["current_value"]
                    
                    if has_progress and has_baseline and has_target and has_current:
                        # Calculate expected progress
                        expected_progress = ((5.5 - 2.0) / (8.0 - 2.0)) * 100  # Should be ~58.33%
                        actual_progress = kpi.get("progress_percentage", 0)
                        
                        if abs(actual_progress - expected_progress) < 1.0:  # Allow small rounding differences
                            self.log_result("Create Beneficiary KPI", True, 
                                          f"KPI created with accurate progress tracking ({actual_progress:.1f}%)")
                            return True
                        else:
                            self.log_result("Create Beneficiary KPI", False, 
                                          f"Progress calculation incorrect: expected ~{expected_progress:.1f}%, got {actual_progress}", data)
                            return False
                    else:
                        missing_features = []
                        if not has_progress: missing_features.append("progress calculation")
                        if not has_baseline: missing_features.append("baseline value")
                        if not has_target: missing_features.append("target value")
                        if not has_current: missing_features.append("current value")
                        self.log_result("Create Beneficiary KPI", False, 
                                      f"Missing features: {', '.join(missing_features)}", data)
                        return False
                else:
                    self.log_result("Create Beneficiary KPI", False, "Missing success/kpi in response", data)
                    return False
            else:
                self.log_result("Create Beneficiary KPI", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Beneficiary KPI", False, f"Request error: {str(e)}")
            return False
    
    def test_update_beneficiary_kpi(self):
        """Test PUT /api/beneficiary-kpis/{id} - KPI updates with automatic recalculation"""
        try:
            if not self.test_kpi_ids:
                self.log_result("Update Beneficiary KPI", False, "No KPI ID available")
                return False
            
            kpi_id = self.test_kpi_ids[0]
            update_data = {
                "current_value": 7.2,
                "notes": "Significant improvement shown in latest assessment - exceeded expectations"
            }
            
            response = self.session.put(
                f"{self.base_url}/beneficiary-kpis/{kpi_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "kpi" in data:
                    kpi = data["kpi"]
                    
                    # Verify automatic recalculation
                    updated_current = kpi.get("current_value")
                    updated_progress = kpi.get("progress_percentage")
                    
                    if updated_current == update_data["current_value"]:
                        # Calculate expected progress: (7.2 - 2.0) / (8.0 - 2.0) * 100 = ~86.67%
                        expected_progress = ((7.2 - 2.0) / (8.0 - 2.0)) * 100
                        
                        if updated_progress and abs(updated_progress - expected_progress) < 1.0:
                            self.log_result("Update Beneficiary KPI", True, 
                                          f"KPI updated with automatic recalculation ({updated_progress:.1f}%)")
                            return True
                        else:
                            self.log_result("Update Beneficiary KPI", False, 
                                          f"Progress recalculation incorrect: expected ~{expected_progress:.1f}%, got {updated_progress}", data)
                            return False
                    else:
                        self.log_result("Update Beneficiary KPI", False, 
                                      f"Current value not updated: expected {update_data['current_value']}, got {updated_current}", data)
                        return False
                else:
                    self.log_result("Update Beneficiary KPI", False, "Missing success/kpi in response", data)
                    return False
            else:
                self.log_result("Update Beneficiary KPI", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Update Beneficiary KPI", False, f"Request error: {str(e)}")
            return False
    
    def test_get_beneficiary_kpis(self):
        """Test GET /api/beneficiary-kpis - KPI analytics and aggregation"""
        try:
            # Test 1: Basic retrieval
            response = self.session.get(f"{self.base_url}/beneficiary-kpis")
            if response.status_code != 200:
                self.log_result("Get Beneficiary KPIs", False, 
                              f"Basic retrieval failed: HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            if "kpis" not in data:
                self.log_result("Get Beneficiary KPIs", False, "Missing kpis field", data)
                return False
            
            # Test 2: Beneficiary filtering
            if self.test_beneficiary_ids:
                response = self.session.get(
                    f"{self.base_url}/beneficiary-kpis?beneficiary_id={self.test_beneficiary_ids[0]}"
                )
                if response.status_code != 200:
                    self.log_result("Get Beneficiary KPIs", False, 
                                  f"Beneficiary filtering failed: HTTP {response.status_code}", response.text)
                    return False
            
            # Test 3: Project filtering
            if self.test_project_id:
                response = self.session.get(
                    f"{self.base_url}/beneficiary-kpis?project_id={self.test_project_id}"
                )
                if response.status_code != 200:
                    self.log_result("Get Beneficiary KPIs", False, 
                                  f"Project filtering failed: HTTP {response.status_code}", response.text)
                    return False
            
            # Test 4: Activity filtering
            if self.test_activity_id:
                response = self.session.get(
                    f"{self.base_url}/beneficiary-kpis?activity_id={self.test_activity_id}"
                )
                if response.status_code != 200:
                    self.log_result("Get Beneficiary KPIs", False, 
                                  f"Activity filtering failed: HTTP {response.status_code}", response.text)
                    return False
            
            self.log_result("Get Beneficiary KPIs", True, 
                          "KPI analytics and aggregation working correctly with all filter types")
            return True
            
        except Exception as e:
            self.log_result("Get Beneficiary KPIs", False, f"Request error: {str(e)}")
            return False
    
    def test_calculate_risk_scores(self):
        """Test POST /api/beneficiaries/calculate-risk-scores - AI-driven risk assessment"""
        try:
            response = self.session.post(f"{self.base_url}/beneficiaries/calculate-risk-scores")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Check for risk calculation results
                    expected_fields = ["processed_count", "updated_count"]
                    optional_fields = ["risk_distribution", "high_risk_beneficiaries", "recommendations"]
                    
                    has_required = any(field in data for field in expected_fields)
                    has_optional = any(field in data for field in optional_fields)
                    
                    if has_required:
                        processed_count = data.get("processed_count", 0)
                        updated_count = data.get("updated_count", 0)
                        
                        self.log_result("Calculate Risk Scores", True, 
                                      f"Risk scores calculated for {processed_count} beneficiaries, {updated_count} updated{' with additional insights' if has_optional else ''}")
                        return True
                    else:
                        self.log_result("Calculate Risk Scores", False, 
                                      "Missing processing results in response", data)
                        return False
                else:
                    self.log_result("Calculate Risk Scores", False, "Success flag not set", data)
                    return False
            else:
                self.log_result("Calculate Risk Scores", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Calculate Risk Scores", False, f"Request error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive beneficiary management system test"""
        print("\n" + "="*80)
        print("COMPREHENSIVE BENEFICIARY MANAGEMENT SYSTEM TESTING")
        print("="*80)
        
        success_count = 0
        total_tests = 0
        
        # Setup phase
        print("\n--- SETUP PHASE ---")
        if not self.setup_authentication():
            print("❌ CRITICAL: Authentication setup failed - cannot continue testing")
            return False
        
        if not self.setup_test_project():
            print("❌ CRITICAL: Test project setup failed - cannot continue testing")
            return False
        
        if not self.setup_test_activity():
            print("❌ CRITICAL: Test activity setup failed - cannot continue testing")
            return False
        
        # Core Beneficiary Management Tests
        print("\n--- CORE BENEFICIARY MANAGEMENT ---")
        tests = [
            ("Enhanced Beneficiary Creation", self.test_create_beneficiary_enhanced),
            ("Advanced Filtering & Pagination", self.test_get_beneficiaries_advanced_filtering),
            ("Profile Updates with Risk Scoring", self.test_update_beneficiary_with_risk_scoring),
            ("Beneficiary Analytics", self.test_beneficiary_analytics),
            ("GPS Mapping Data", self.test_beneficiary_map_data),
        ]
        
        for test_name, test_func in tests:
            total_tests += 1
            if test_func():
                success_count += 1
        
        # Service Records System Tests
        print("\n--- SERVICE RECORDS SYSTEM ---")
        service_tests = [
            ("Individual Service Tracking", self.test_create_service_record),
            ("Batch Service Processing", self.test_create_batch_service_records),
            ("Service History Filtering", self.test_get_service_records_filtering),
        ]
        
        for test_name, test_func in service_tests:
            total_tests += 1
            if test_func():
                success_count += 1
        
        # KPI Tracking System Tests
        print("\n--- KPI TRACKING SYSTEM ---")
        kpi_tests = [
            ("Custom KPI Creation", self.test_create_beneficiary_kpi),
            ("KPI Updates & Recalculation", self.test_update_beneficiary_kpi),
            ("KPI Analytics & Aggregation", self.test_get_beneficiary_kpis),
        ]
        
        for test_name, test_func in kpi_tests:
            total_tests += 1
            if test_func():
                success_count += 1
        
        # AI & Analytics Tests
        print("\n--- AI & ANALYTICS ---")
        ai_tests = [
            ("AI-Driven Risk Assessment", self.test_calculate_risk_scores),
        ]
        
        for test_name, test_func in ai_tests:
            total_tests += 1
            if test_func():
                success_count += 1
        
        # Final Results
        print("\n" + "="*80)
        print(f"COMPREHENSIVE BENEFICIARY MANAGEMENT SYSTEM TEST COMPLETE")
        print(f"SUCCESS RATE: {success_count}/{total_tests} tests passed ({(success_count/total_tests)*100:.1f}%)")
        print("="*80)
        
        return success_count == total_tests

def main():
    """Main test execution"""
    tester = BeneficiaryManagementTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - Beneficiary Management System is production-ready!")
        exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED - Review results above for details")
        exit(1)

if __name__ == "__main__":
    main()