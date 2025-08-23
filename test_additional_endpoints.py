#!/usr/bin/env python3
"""
Additional endpoint testing to find potential 500 errors
"""

import sys
import os
import requests
import json
sys.path.append('/app')

from backend_test import DataRWAPITester

def test_additional_endpoints(tester):
    """Test additional endpoints that might be causing 500 errors"""
    
    additional_endpoints = [
        ("GET /api/health", f"{tester.base_url}/health"),
        ("GET /api/users", f"{tester.base_url}/users"),
        ("GET /api/organizations/me", f"{tester.base_url}/organizations/me"),
        ("GET /api/finance/config", f"{tester.base_url}/finance/config"),
        ("GET /api/finance/expenses", f"{tester.base_url}/finance/expenses"),
        ("GET /api/finance/burn-rate", f"{tester.base_url}/finance/burn-rate"),
        ("GET /api/finance/variance", f"{tester.base_url}/finance/variance"),
        ("GET /api/finance/forecast", f"{tester.base_url}/finance/forecast"),
        ("GET /api/finance/funding-utilization", f"{tester.base_url}/finance/funding-utilization"),
    ]
    
    print("\n" + "="*80)
    print("TESTING ADDITIONAL ENDPOINTS FOR 500 ERRORS")
    print("="*80)
    
    error_endpoints = []
    success_count = 0
    
    for endpoint_name, url in additional_endpoints:
        try:
            print(f"\n🔍 Testing {endpoint_name}...")
            response = tester.session.get(url)
            
            if response.status_code == 500:
                print(f"❌ {endpoint_name} - HTTP 500 ERROR FOUND!")
                error_text = response.text
                print(f"   Error Details: {error_text[:500]}...")
                
                error_endpoints.append({
                    'endpoint': endpoint_name,
                    'url': url,
                    'status_code': response.status_code,
                    'error': error_text[:1000]
                })
            
            elif response.status_code == 200:
                print(f"✅ {endpoint_name} - Working correctly (HTTP 200)")
                success_count += 1
                
                # Try to parse response
                try:
                    data = response.json()
                    if endpoint_name == "GET /api/health":
                        print(f"   📊 Health status: {data.get('status', 'unknown')}")
                    elif endpoint_name == "GET /api/users":
                        print(f"   📊 Users found: {len(data) if isinstance(data, list) else 'N/A'}")
                    elif endpoint_name == "GET /api/finance/config":
                        print(f"   📊 Finance config loaded")
                except Exception as e:
                    print(f"   ⚠️  Response parsing error: {str(e)}")
            
            else:
                print(f"⚠️  {endpoint_name} - HTTP {response.status_code}")
                if response.status_code in [401, 403]:
                    print(f"   Authentication/Authorization issue")
                elif response.status_code == 404:
                    print(f"   Endpoint not found")
                else:
                    print(f"   Response: {response.text[:200]}...")
                    
        except Exception as e:
            print(f"❌ {endpoint_name} - Connection/Request Error: {str(e)}")
            error_endpoints.append({
                'endpoint': endpoint_name,
                'url': url,
                'status_code': 'CONNECTION_ERROR',
                'error': str(e)
            })
    
    return error_endpoints, success_count

def test_post_endpoints_with_invalid_data(tester):
    """Test POST endpoints with invalid data to see if they cause 500 errors"""
    
    print("\n" + "="*80)
    print("TESTING POST ENDPOINTS WITH INVALID DATA FOR 500 ERRORS")
    print("="*80)
    
    post_tests = [
        ("POST /api/projects", f"{tester.base_url}/projects", {"invalid": "data"}),
        ("POST /api/activities", f"{tester.base_url}/activities", {"invalid": "data"}),
        ("POST /api/beneficiaries", f"{tester.base_url}/beneficiaries", {"invalid": "data"}),
        ("POST /api/finance/expenses", f"{tester.base_url}/finance/expenses", {"invalid": "data"}),
    ]
    
    error_endpoints = []
    
    for endpoint_name, url, data in post_tests:
        try:
            print(f"\n🔍 Testing {endpoint_name} with invalid data...")
            response = tester.session.post(url, json=data)
            
            if response.status_code == 500:
                print(f"❌ {endpoint_name} - HTTP 500 ERROR FOUND!")
                error_text = response.text
                print(f"   Error Details: {error_text[:500]}...")
                
                error_endpoints.append({
                    'endpoint': endpoint_name,
                    'url': url,
                    'status_code': response.status_code,
                    'error': error_text[:1000]
                })
            
            elif response.status_code == 422:
                print(f"✅ {endpoint_name} - Proper validation error (HTTP 422)")
            elif response.status_code == 400:
                print(f"✅ {endpoint_name} - Proper bad request error (HTTP 400)")
            else:
                print(f"⚠️  {endpoint_name} - HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                    
        except Exception as e:
            print(f"❌ {endpoint_name} - Connection/Request Error: {str(e)}")
    
    return error_endpoints

def main():
    print("🔍 EXTENDED 500 Error Detection for DataRW")
    print("="*60)
    
    tester = DataRWAPITester()
    
    # Test API health first
    if not tester.test_api_health():
        print("❌ Cannot connect to API - check if backend is running")
        return
    
    # Set up authentication for protected endpoints
    print("\n🔐 Setting up authentication...")
    if not tester.test_user_registration():
        print("❌ Authentication setup failed")
        return
    
    print("✅ Authentication successful")
    
    # Test additional endpoints
    additional_errors, additional_success = test_additional_endpoints(tester)
    
    # Test POST endpoints with invalid data
    post_errors = test_post_endpoints_with_invalid_data(tester)
    
    # Combine all errors
    all_errors = additional_errors + post_errors
    
    # Generate final report
    print("\n" + "="*80)
    print("EXTENDED 500 ERROR REPORT")
    print("="*80)
    
    if all_errors:
        print(f"🚨 FOUND {len(all_errors)} ENDPOINTS WITH 500 ERRORS:")
        for i, error in enumerate(all_errors, 1):
            print(f"\n{i}. {error['endpoint']}")
            print(f"   Status: {error['status_code']}")
            print(f"   URL: {error['url']}")
            print(f"   Error: {error['error'][:200]}...")
    else:
        print("✅ NO 500 ERRORS DETECTED IN EXTENDED TESTING")
        print("All tested endpoints are handling requests properly.")
    
    print(f"\n📊 Extended Test Summary:")
    print(f"   Additional GET endpoints tested: 9")
    print(f"   POST endpoints tested: 4") 
    print(f"   Total endpoints with 500 errors: {len(all_errors)}")
    print(f"   Working GET endpoints: {additional_success}")

if __name__ == "__main__":
    main()