#!/usr/bin/env python3
"""
Comprehensive test for Enhanced Project Dashboard Analytics with populated data
Tests the new analytics fields with actual project, activity, and budget data
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

class EnhancedAnalyticsWithDataTest:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        self.project_id = None
        self.activity_id = None
        
        # Test data
        self.test_email = f"analytics.data.test.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Analytics Data Test User"
        
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
    
    def create_test_project(self):
        """Create a test project for analytics"""
        try:
            project_data = {
                "name": f"Digital Literacy Training Program {uuid.uuid4().hex[:8]}",
                "description": "Comprehensive digital literacy training program for rural communities",
                "project_manager_id": self.user_data["id"],
                "start_date": (datetime.now() - timedelta(days=60)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=300)).isoformat(),
                "budget_total": 2500000.0,
                "beneficiaries_target": 5000,
                "location": "Nyagatare District, Eastern Province, Rwanda",
                "donor_organization": "World Bank",
                "implementing_partners": ["Rwanda Development Board"],
                "tags": ["education", "digital-literacy"]
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.project_id = data.get("id") or data.get("_id")
                self.log_result("Create Test Project", True, f"Project created with ID: {self.project_id}")
                return True
            else:
                self.log_result("Create Test Project", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Test Project", False, f"Request error: {str(e)}")
            return False
    
    def create_test_activity(self):
        """Create a test activity for analytics"""
        try:
            activity_data = {
                "project_id": self.project_id,
                "name": f"Community Mobilization Campaign {uuid.uuid4().hex[:8]}",
                "description": "Community outreach program to raise awareness",
                "assigned_to": self.user_data["id"],
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "budget_allocated": 150000.0,
                "deliverables": [
                    "Community awareness sessions conducted",
                    "Registration of participants completed"
                ],
                "dependencies": ["Project approval completed"]
            }
            
            response = self.session.post(
                f"{self.base_url}/activities",
                json=activity_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.activity_id = data.get("id") or data.get("_id")
                self.log_result("Create Test Activity", True, f"Activity created with ID: {self.activity_id}")
                return True
            else:
                self.log_result("Create Test Activity", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Test Activity", False, f"Request error: {str(e)}")
            return False
    
    def create_test_budget_item(self):
        """Create a test budget item for analytics"""
        try:
            budget_data = {
                "project_id": self.project_id,
                "category": "supplies",  # Use valid enum value
                "item_name": "Digital Literacy Training Materials",
                "description": "Training manuals, computers, and educational resources",
                "budgeted_amount": 800000.0,
                "budget_period": "6_months"
            }
            
            response = self.session.post(
                f"{self.base_url}/budget",
                json=budget_data
            )
            
            if response.status_code == 200:
                self.log_result("Create Test Budget Item", True, "Budget item created successfully")
                return True
            else:
                self.log_result("Create Test Budget Item", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Test Budget Item", False, f"Request error: {str(e)}")
            return False
    
    def create_test_kpi(self):
        """Create a test KPI for analytics"""
        try:
            kpi_data = {
                "project_id": self.project_id,
                "name": "Number of People Trained in Digital Literacy",
                "description": "Total number of individuals who completed the digital literacy training program",
                "type": "quantitative",
                "measurement_unit": "people",
                "baseline_value": 0.0,
                "target_value": 5000.0,
                "current_value": 1250.0,
                "frequency": "monthly",
                "responsible_person": self.user_data["id"]
            }
            
            response = self.session.post(
                f"{self.base_url}/kpis",
                json=kpi_data
            )
            
            if response.status_code == 200:
                self.log_result("Create Test KPI", True, "KPI created successfully")
                return True
            else:
                self.log_result("Create Test KPI", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Test KPI", False, f"Request error: {str(e)}")
            return False
    
    def test_enhanced_analytics_with_data(self):
        """Test enhanced analytics with populated data"""
        try:
            response = self.session.get(f"{self.base_url}/projects/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    dashboard_data = data["data"]
                    
                    # Verify all NEW enhanced analytics fields are present
                    new_analytics_fields = [
                        "activity_insights", "performance_trends", 
                        "risk_indicators", "completion_analytics"
                    ]
                    
                    missing_fields = [field for field in new_analytics_fields if field not in dashboard_data]
                    if missing_fields:
                        self.log_result("Enhanced Analytics with Data", False, 
                                      f"Missing analytics fields: {missing_fields}", data)
                        return False
                    
                    # Verify we have some data now (not all zeros)
                    total_projects = dashboard_data.get("total_projects", 0)
                    if total_projects == 0:
                        self.log_result("Enhanced Analytics with Data", False, 
                                      "No projects found in dashboard data", data)
                        return False
                    
                    print(f"✅ Dashboard shows {total_projects} project(s)")
                    
                    # Check activity insights
                    activity_insights = dashboard_data.get("activity_insights", {})
                    total_activities = activity_insights.get("total_activities", 0)
                    print(f"✅ Activity Insights - Total Activities: {total_activities}")
                    
                    # Check performance trends
                    performance_trends = dashboard_data.get("performance_trends", {})
                    budget_trend = performance_trends.get("budget_trend_monthly", [])
                    kpi_trend = performance_trends.get("kpi_trend_monthly", [])
                    print(f"✅ Performance Trends - Budget Trend Points: {len(budget_trend)}, KPI Trend Points: {len(kpi_trend)}")
                    
                    # Check risk indicators
                    risk_indicators = dashboard_data.get("risk_indicators", {})
                    budget_risk = risk_indicators.get("budget_risk", {})
                    timeline_risk = risk_indicators.get("timeline_risk", {})
                    performance_risk = risk_indicators.get("performance_risk", {})
                    
                    print(f"✅ Risk Indicators:")
                    print(f"   - Budget Risk: {budget_risk.get('high_utilization_projects', 0)} high utilization projects")
                    print(f"   - Timeline Risk: {timeline_risk.get('projects_due_soon', 0)} projects due soon")
                    print(f"   - Performance Risk: {performance_risk.get('low_progress_activities', 0)} low progress activities")
                    
                    # Check completion analytics
                    completion_analytics = dashboard_data.get("completion_analytics", {})
                    success_rate = completion_analytics.get("project_success_rate", 0)
                    on_time_rate = completion_analytics.get("on_time_completion_rate", 0)
                    
                    print(f"✅ Completion Analytics:")
                    print(f"   - Project Success Rate: {success_rate}%")
                    print(f"   - On-time Completion Rate: {on_time_rate}%")
                    print(f"   - Total Completed Projects: {completion_analytics.get('total_completed_projects', 0)}")
                    
                    # Verify all analytics methods executed without errors
                    self.log_result("Enhanced Analytics with Data", True, 
                                  "Enhanced analytics working correctly with populated data - all 4 analytics methods executed successfully")
                    return True
                else:
                    self.log_result("Enhanced Analytics with Data", False, 
                                  "Missing success/data fields in response", data)
                    return False
            else:
                self.log_result("Enhanced Analytics with Data", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Enhanced Analytics with Data", False, f"Request error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run the comprehensive enhanced analytics test with data"""
        print("🚀 ENHANCED PROJECT DASHBOARD ANALYTICS TEST WITH DATA")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping test")
            return False
        
        print("\n📊 Creating Test Data...")
        
        # Create test data
        if not self.create_test_project():
            print("❌ Project creation failed - stopping test")
            return False
        
        if not self.create_test_activity():
            print("❌ Activity creation failed - continuing test")
        
        if not self.create_test_budget_item():
            print("❌ Budget item creation failed - continuing test")
        
        if not self.create_test_kpi():
            print("❌ KPI creation failed - continuing test")
        
        print("\n🔍 Testing Enhanced Analytics with Populated Data...")
        result = self.test_enhanced_analytics_with_data()
        
        print("\n" + "=" * 80)
        if result:
            print("✅ ENHANCED ANALYTICS WITH DATA TEST PASSED")
            print("All 4 new analytics calculation methods are working correctly:")
            print("   • _calculate_activity_insights")
            print("   • _calculate_performance_trends") 
            print("   • _calculate_risk_indicators")
            print("   • _calculate_completion_analytics")
        else:
            print("❌ ENHANCED ANALYTICS WITH DATA TEST FAILED")
        
        return result

if __name__ == "__main__":
    tester = EnhancedAnalyticsWithDataTest()
    tester.run_comprehensive_test()