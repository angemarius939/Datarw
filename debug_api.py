import requests
import json

# Test the project dashboard endpoint directly
base_url = "https://expense-master-277.preview.emergentagent.com/api"

def test_auth_and_dashboard():
    # First, let's register a new user
    register_data = {
        "name": "Test Admin",
        "email": "test@datarw.com",
        "password": "password123"
    }
    
    print("📝 Registering new user...")
    register_response = requests.post(f"{base_url}/auth/register", json=register_data)
    print(f"Register response status: {register_response.status_code}")
    print(f"Register response: {register_response.text}")
    
    # Then try to login
    login_data = {
        "email": "test@datarw.com",
        "password": "password123"
    }
    
    try:
        # Login
        print("🔐 Testing login...")
        login_response = requests.post(f"{base_url}/auth/login", json=login_data)
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response: {login_response.text}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            
            if token:
                # Test dashboard with token
                print(f"\n📊 Testing dashboard with token...")
                headers = {"Authorization": f"Bearer {token}"}
                
                dashboard_response = requests.get(f"{base_url}/projects/dashboard", headers=headers)
                print(f"Dashboard response status: {dashboard_response.status_code}")
                print(f"Dashboard response: {dashboard_response.text}")
                
                if dashboard_response.status_code == 200:
                    print("✅ Dashboard working correctly!")
                else:
                    print("❌ Dashboard failed")
            else:
                print("❌ No token received")
        else:
            print("❌ Login failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_auth_and_dashboard()