#!/usr/bin/env python3
"""
Focused test for Enhanced Project Dashboard Analytics
Tests the new analytics fields: activity_insights, performance_trends, risk_indicators, completion_analytics
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

class EnhancedAnalyticsTest:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        
        # Test data
        self.test_email = f"analytics.test.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Analytics Test User"
        
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
    
    def test_enhanced_project_dashboard_analytics(self):
        """Test enhanced project dashboard analytics endpoint with new analytics fields"""
        try:
            response = self.session.get(f"{self.base_url}/projects/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and "data" in data):
                    dashboard_data = data["data"]
                    
                    # Verify all original required dashboard fields are present
                    original_fields = [
                        "total_projects", "active_projects", "completed_projects", 
                        "overdue_activities", "budget_utilization", "kpi_performance", 
                        "recent_activities", "projects_by_status", "budget_by_category"
                    ]
                    
                    # Verify all NEW enhanced analytics fields are present
                    new_analytics_fields = [
                        "activity_insights", "performance_trends", 
                        "risk_indicators", "completion_analytics"
                    ]
                    
                    all_required_fields = original_fields + new_analytics_fields
                    missing_fields = [field for field in all_required_fields if field not in dashboard_data]
                    
                    if missing_fields:
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      f"Missing required fields: {missing_fields}", data)
                        return False
                    
                    print(f"✅ All required fields present: {len(all_required_fields)} fields")
                    print(f"   Original fields: {len(original_fields)}")
                    print(f"   New analytics fields: {len(new_analytics_fields)}")
                    
                    # Verify structure and data types of each NEW analytics section
                    
                    # 1. Activity Insights validation
                    activity_insights = dashboard_data.get("activity_insights", {})
                    if not isinstance(activity_insights, dict):
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      f"activity_insights should be dict, got {type(activity_insights)}", data)
                        return False
                    
                    expected_activity_fields = ["activity_status_breakdown", "completion_trend_weekly", 
                                              "avg_completion_days", "total_activities"]
                    activity_missing = [field for field in expected_activity_fields if field not in activity_insights]
                    if activity_missing:
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      f"activity_insights missing fields: {activity_missing}", data)
                        return False
                    
                    print(f"✅ Activity Insights: {len(expected_activity_fields)} fields present")
                    
                    # 2. Performance Trends validation
                    performance_trends = dashboard_data.get("performance_trends", {})
                    if not isinstance(performance_trends, dict):
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      f"performance_trends should be dict, got {type(performance_trends)}", data)
                        return False
                    
                    expected_performance_fields = ["budget_trend_monthly", "kpi_trend_monthly"]
                    performance_missing = [field for field in expected_performance_fields if field not in performance_trends]
                    if performance_missing:
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      f"performance_trends missing fields: {performance_missing}", data)
                        return False
                    
                    # Verify budget_trend_monthly is a list
                    if not isinstance(performance_trends["budget_trend_monthly"], list):
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      "budget_trend_monthly should be a list", data)
                        return False
                    
                    print(f"✅ Performance Trends: {len(expected_performance_fields)} fields present")
                    
                    # 3. Risk Indicators validation
                    risk_indicators = dashboard_data.get("risk_indicators", {})
                    if not isinstance(risk_indicators, dict):
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      f"risk_indicators should be dict, got {type(risk_indicators)}", data)
                        return False
                    
                    expected_risk_fields = ["budget_risk", "timeline_risk", "performance_risk"]
                    risk_missing = [field for field in expected_risk_fields if field not in risk_indicators]
                    if risk_missing:
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      f"risk_indicators missing fields: {risk_missing}", data)
                        return False
                    
                    # Verify each risk indicator has proper structure
                    for risk_type in expected_risk_fields:
                        risk_data = risk_indicators[risk_type]
                        if not isinstance(risk_data, dict):
                            self.log_result("Enhanced Project Dashboard Analytics", False, 
                                          f"{risk_type} should be dict", data)
                            return False
                        
                        # Each risk indicator should have threshold and description
                        # Check for different possible field names
                        has_threshold = any(key in risk_data for key in ["threshold", "threshold_days"])
                        if not has_threshold or "description" not in risk_data:
                            print(f"DEBUG: {risk_type} data: {risk_data}")
                            self.log_result("Enhanced Project Dashboard Analytics", False, 
                                          f"{risk_type} missing threshold or description. Available keys: {list(risk_data.keys())}", data)
                            return False
                    
                    print(f"✅ Risk Indicators: {len(expected_risk_fields)} fields present with proper structure")
                    
                    # 4. Completion Analytics validation
                    completion_analytics = dashboard_data.get("completion_analytics", {})
                    if not isinstance(completion_analytics, dict):
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      f"completion_analytics should be dict, got {type(completion_analytics)}", data)
                        return False
                    
                    expected_completion_fields = ["project_success_rate", "on_time_completion_rate", 
                                                "avg_planned_duration_days", "avg_actual_duration_days",
                                                "avg_schedule_variance_days", "total_completed_projects", 
                                                "total_closed_projects"]
                    completion_missing = [field for field in expected_completion_fields if field not in completion_analytics]
                    if completion_missing:
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      f"completion_analytics missing fields: {completion_missing}", data)
                        return False
                    
                    # Verify numeric fields are actually numeric
                    numeric_fields = ["project_success_rate", "on_time_completion_rate", 
                                    "avg_planned_duration_days", "avg_actual_duration_days", 
                                    "avg_schedule_variance_days"]
                    for field in numeric_fields:
                        value = completion_analytics[field]
                        if not isinstance(value, (int, float)):
                            self.log_result("Enhanced Project Dashboard Analytics", False, 
                                          f"completion_analytics.{field} should be numeric, got {type(value)}", data)
                            return False
                    
                    print(f"✅ Completion Analytics: {len(expected_completion_fields)} fields present with correct data types")
                    
                    # Verify datetime operations work correctly (check recent_activities timestamps)
                    recent_activities = dashboard_data.get("recent_activities", [])
                    if isinstance(recent_activities, list):
                        for activity in recent_activities:
                            if "updated_at" in activity:
                                try:
                                    # Verify the datetime string is valid ISO format
                                    datetime.fromisoformat(activity["updated_at"].replace('Z', '+00:00'))
                                except ValueError:
                                    self.log_result("Enhanced Project Dashboard Analytics", False, 
                                                  f"Invalid datetime format in recent_activities: {activity['updated_at']}", data)
                                    return False
                    
                    print(f"✅ Datetime operations working correctly")
                    
                    # Print sample data for verification
                    print("\n📊 SAMPLE ANALYTICS DATA:")
                    print(f"   Activity Insights - Total Activities: {activity_insights.get('total_activities', 0)}")
                    print(f"   Performance Trends - Budget Trend Points: {len(performance_trends.get('budget_trend_monthly', []))}")
                    print(f"   Risk Indicators - Budget Risk Projects: {risk_indicators.get('budget_risk', {}).get('high_utilization_projects', 0)}")
                    print(f"   Completion Analytics - Success Rate: {completion_analytics.get('project_success_rate', 0)}%")
                    
                    # Verify all analytics calculations completed without errors
                    self.log_result("Enhanced Project Dashboard Analytics", True, 
                                  "Enhanced dashboard analytics working correctly - all 4 new analytics sections present with proper structure and data types")
                    return True
                else:
                    self.log_result("Enhanced Project Dashboard Analytics", False, 
                                  "Missing success/data fields in response", data)
                    return False
            else:
                # Check specifically for analytics calculation errors
                if response.status_code == 500:
                    error_text = response.text
                    if "activity_insights" in error_text or "performance_trends" in error_text or \
                       "risk_indicators" in error_text or "completion_analytics" in error_text:
                        self.log_result("Enhanced Project Dashboard Analytics", False, 
                                      "CRITICAL: Error in new analytics calculation methods", error_text)
                        return False
                
                self.log_result("Enhanced Project Dashboard Analytics", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Enhanced Project Dashboard Analytics", False, f"Request error: {str(e)}")
            return False
    
    def run_test(self):
        """Run the enhanced analytics test"""
        print("🚀 ENHANCED PROJECT DASHBOARD ANALYTICS TEST")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping test")
            return False
        
        print("\n🔍 Testing Enhanced Analytics Endpoint...")
        result = self.test_enhanced_project_dashboard_analytics()
        
        print("\n" + "=" * 80)
        if result:
            print("✅ ENHANCED ANALYTICS TEST PASSED")
            print("All 4 new analytics sections are working correctly:")
            print("   • activity_insights")
            print("   • performance_trends") 
            print("   • risk_indicators")
            print("   • completion_analytics")
        else:
            print("❌ ENHANCED ANALYTICS TEST FAILED")
        
        return result

if __name__ == "__main__":
    tester = EnhancedAnalyticsTest()
    tester.run_test()