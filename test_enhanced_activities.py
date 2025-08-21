#!/usr/bin/env python3
"""
Test Enhanced Activity Creation Endpoints
Tests the CreateActivityModal refactor with milestones, planned/actual outputs, assigned person dropdown
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend_test import DataRWAPITester

def main():
    """Run enhanced activity creation tests"""
    tester = DataRWAPITester()
    
    print("=" * 80)
    print("TESTING ENHANCED ACTIVITY CREATION ENDPOINTS")
    print("CreateActivityModal refactor with milestones, planned/actual outputs")
    print("=" * 80)
    
    # Run the enhanced activity tests only
    tester.run_enhanced_activity_tests_only()

if __name__ == "__main__":
    main()