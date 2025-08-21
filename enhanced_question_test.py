#!/usr/bin/env python3
"""
Enhanced Question Types Test for DataRW
Tests the enhanced question types functionality.
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
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://monitoring-eval-app.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class EnhancedQuestionTypesTest:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.organization_data = None
        
        # Test data
        self.test_email = f"enhanced.test.{uuid.uuid4().hex[:8]}@datarw.com"
        self.test_password = "SecurePassword123!"
        self.test_name = "Enhanced Test User"
        
    def log_result(self, test_name, success, message):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
    
    def setup_authentication(self):
        """Setup authentication"""
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
                self.auth_token = data["access_token"]
                self.user_data = data["user"]
                self.organization_data = data["organization"]
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                self.log_result("Authentication Setup", True, "User registered and authenticated")
                return True
            else:
                self.log_result("Authentication Setup", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Authentication Setup", False, f"Request error: {str(e)}")
            return False

    def test_enhanced_question_types(self):
        """Test creating survey with all enhanced question types"""
        try:
            survey_data = {
                "title": "Enhanced Question Types Test Survey",
                "description": "Testing all enhanced question types supported by the system",
                "questions": [
                    {
                        "type": "multiple_choice_single",
                        "question": "What is your preferred communication method?",
                        "required": True,
                        "options": ["Email", "Phone", "Text", "In-person"]
                    },
                    {
                        "type": "multiple_choice_multiple",
                        "question": "Which services have you used? (Select all that apply)",
                        "required": False,
                        "options": ["Consulting", "Training", "Support", "Development"],
                        "multiple_selection": True
                    },
                    {
                        "type": "likert_scale",
                        "question": "I am satisfied with the current service quality",
                        "required": True,
                        "scale_labels": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
                    },
                    {
                        "type": "matrix_grid",
                        "question": "Rate the following aspects of our service",
                        "required": True,
                        "matrix_rows": ["Quality", "Speed", "Friendliness", "Value"],
                        "matrix_columns": ["Poor", "Fair", "Good", "Excellent"]
                    },
                    {
                        "type": "slider",
                        "question": "On a scale of 0-100, how likely are you to recommend us?",
                        "required": False,
                        "scale_min": 0,
                        "scale_max": 100,
                        "slider_step": 5
                    },
                    {
                        "type": "date_picker",
                        "question": "When did you first use our service?",
                        "required": False,
                        "date_format": "YYYY-MM-DD"
                    },
                    {
                        "type": "dropdown",
                        "question": "What is your industry?",
                        "required": False,
                        "options": ["Technology", "Healthcare", "Finance", "Education", "Other"]
                    },
                    {
                        "type": "yes_no",
                        "question": "Would you recommend our service to others?",
                        "required": True
                    },
                    {
                        "type": "numeric_scale",
                        "question": "How many years of experience do you have?",
                        "required": False,
                        "scale_min": 0,
                        "scale_max": 50
                    },
                    {
                        "type": "ranking",
                        "question": "Rank these features by importance",
                        "required": False,
                        "options": ["Price", "Quality", "Speed", "Support"]
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/surveys",
                json=survey_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data or "_id" in data:
                    questions = data.get("questions", [])
                    if len(questions) == 10:  # All question types created
                        self.log_result("Enhanced Question Types", True, 
                                      f"Survey with {len(questions)} enhanced question types created successfully")
                        return True
                    else:
                        self.log_result("Enhanced Question Types", False, 
                                      f"Expected 10 questions, got {len(questions)}")
                        return False
                else:
                    self.log_result("Enhanced Question Types", False, "Survey data missing ID")
                    return False
            else:
                self.log_result("Enhanced Question Types", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Enhanced Question Types", False, f"Request error: {str(e)}")
            return False

    def run_test(self):
        """Run the enhanced question types test"""
        print(f"🔧 Starting Enhanced Question Types Test")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        if not self.setup_authentication():
            print("❌ Authentication failed - cannot proceed")
            return False
        
        result = self.test_enhanced_question_types()
        
        print("=" * 60)
        if result:
            print("✅ Enhanced Question Types Test: PASSED")
        else:
            print("❌ Enhanced Question Types Test: FAILED")
        
        return result

def main():
    """Main test execution"""
    tester = EnhancedQuestionTypesTest()
    success = tester.run_test()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()