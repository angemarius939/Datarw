#!/usr/bin/env python3
"""
Simple test for the specific activity endpoints mentioned in review request
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

print(f"Using API URL: {API_BASE_URL}")

def test_activity_endpoints():
    """Test the specific activity endpoints"""
    session = requests.Session()
    
    print("=== TESTING ACTIVITY ENDPOINTS ===")
    
    # Step 1: Register and authenticate
    print("\n1. Setting up authentication...")
    test_email = f"test.{uuid.uuid4().hex[:8]}@example.com"
    
    reg_data = {
        "email": test_email,
        "password": "TestPassword123!",
        "name": "Test User"
    }
    
    try:
        response = session.post(f"{API_BASE_URL}/auth/register", json=reg_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            user_id = data["user"]["id"]
            session.headers.update({"Authorization": f"Bearer {token}"})
            print("✅ Authentication successful")
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Step 2: Create a project
    print("\n2. Creating test project...")
    project_data = {
        "name": f"Test Project {uuid.uuid4().hex[:8]}",
        "description": "Test project for activity testing",
        "project_manager_id": user_id,
        "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
        "budget_total": 100000.0,
        "beneficiaries_target": 50,
        "location": "Test Location",
        "donor_organization": "Test Donor"
    }
    
    try:
        response = session.post(f"{API_BASE_URL}/projects", json=project_data, timeout=10)
        if response.status_code == 200:
            project_id = response.json().get("id") or response.json().get("_id")
            print("✅ Project created successfully")
        else:
            print(f"❌ Project creation failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Project creation error: {e}")
        return
    
    # Step 3: Create an activity
    print("\n3. Creating test activity...")
    activity_data = {
        "project_id": project_id,
        "name": f"Test Activity {uuid.uuid4().hex[:8]}",
        "description": "Test activity for endpoint testing",
        "assigned_to": user_id,
        "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "budget_allocated": 10000.0,
        "deliverables": ["Test deliverable"],
        "dependencies": ["Test dependency"]
    }
    
    try:
        response = session.post(f"{API_BASE_URL}/activities", json=activity_data, timeout=10)
        if response.status_code == 200:
            activity_id = response.json().get("id") or response.json().get("_id")
            print("✅ Activity created successfully")
        else:
            print(f"❌ Activity creation failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Activity creation error: {e}")
        return
    
    # Step 4: Test GET /api/activities (main focus of review request)
    print("\n4. Testing GET /api/activities (validation fix)...")
    try:
        response = session.get(f"{API_BASE_URL}/activities", timeout=10)
        if response.status_code == 200:
            activities = response.json()
            print(f"✅ GET /api/activities successful - retrieved {len(activities)} activities")
            
            # Check for normalized fields
            if activities:
                activity = activities[0]
                missing_fields = []
                if "planned_start_date" not in activity:
                    missing_fields.append("planned_start_date")
                if "planned_end_date" not in activity:
                    missing_fields.append("planned_end_date")
                if "last_updated_by" not in activity:
                    missing_fields.append("last_updated_by")
                
                if missing_fields:
                    print(f"⚠️  Missing normalized fields: {missing_fields}")
                else:
                    print("✅ All normalized fields present")
        else:
            print(f"❌ GET /api/activities failed: {response.status_code}")
            print(f"   Error: {response.text}")
            if "validation" in response.text.lower():
                print("   🔍 VALIDATION ERROR DETECTED - Fix not working")
    except Exception as e:
        print(f"❌ GET /api/activities error: {e}")
    
    # Step 5: Test PUT /api/activities/{id}/progress (UUID compatibility)
    print("\n5. Testing PUT /api/activities/{id}/progress (UUID compatibility)...")
    progress_data = {
        "progress_percentage": 25.0,
        "completion_variance": 0.0,
        "schedule_variance_days": 0,
        "risk_level": "low",
        "status": "in_progress"
    }
    
    try:
        response = session.put(f"{API_BASE_URL}/activities/{activity_id}/progress", 
                             json=progress_data, timeout=10)
        if response.status_code == 200:
            print("✅ PUT /api/activities/{id}/progress successful - UUID compatibility working")
        else:
            print(f"❌ PUT /api/activities/{id}/progress failed: {response.status_code}")
            print(f"   Error: {response.text}")
            if "ObjectId" in response.text:
                print("   🔍 OBJECTID/UUID MISMATCH DETECTED - Fix not working")
    except Exception as e:
        print(f"❌ PUT /api/activities/{id}/progress error: {e}")
    
    # Step 6: Test GET /api/activities/{id}/variance (UUID compatibility)
    print("\n6. Testing GET /api/activities/{id}/variance (UUID compatibility)...")
    try:
        response = session.get(f"{API_BASE_URL}/activities/{activity_id}/variance", timeout=10)
        if response.status_code == 200:
            print("✅ GET /api/activities/{id}/variance successful - UUID compatibility working")
        else:
            print(f"❌ GET /api/activities/{id}/variance failed: {response.status_code}")
            print(f"   Error: {response.text}")
            if "ObjectId" in response.text:
                print("   🔍 OBJECTID/UUID MISMATCH DETECTED - Fix not working")
    except Exception as e:
        print(f"❌ GET /api/activities/{id}/variance error: {e}")
    
    print("\n=== ACTIVITY ENDPOINTS TEST COMPLETE ===")

if __name__ == "__main__":
    test_activity_endpoints()