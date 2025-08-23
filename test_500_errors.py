#!/usr/bin/env python3
"""
Quick 500 Error Testing Script for DataRW Dashboard Endpoints
Focuses specifically on identifying which endpoints are causing 500 errors in the frontend.
"""

import sys
import os
sys.path.append('/app')

from backend_test import DataRWAPITester

def main():
    print("🚨 URGENT: DataRW 500 Error Detection")
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
    
    # Run the 500 error detection
    error_endpoints = tester.test_dashboard_endpoints_for_500_errors()
    
    # Generate final report
    print("\n" + "="*80)
    print("FINAL 500 ERROR REPORT")
    print("="*80)
    
    if error_endpoints:
        print(f"🚨 FOUND {len(error_endpoints)} ENDPOINTS WITH 500 ERRORS:")
        for i, error in enumerate(error_endpoints, 1):
            print(f"\n{i}. {error['endpoint']}")
            print(f"   Status: {error['status_code']}")
            print(f"   URL: {error['url']}")
            print(f"   Error: {error['error'][:200]}...")
            if len(error['error']) > 200:
                print(f"   [Error truncated - full error is {len(error['error'])} characters]")
    else:
        print("✅ NO 500 ERRORS DETECTED")
        print("All tested endpoints are either working correctly or returning expected error codes.")
    
    print(f"\n📊 Test Summary:")
    print(f"   Total endpoints tested: 6")
    print(f"   Endpoints with 500 errors: {len(error_endpoints)}")
    print(f"   Working endpoints: {6 - len(error_endpoints)}")

if __name__ == "__main__":
    main()