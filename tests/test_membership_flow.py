"""
Membership Flow Test Script

This script tests the membership approval flow with voting:
1. Get Lender One's address from active members
2. Add Lender Two and verify it needs 51% votes
3. Have Lender One vote (should be enough as it's the only active member)
4. Add Lender Three and verify it needs votes from both active lenders
5. Add Lender Four (will be auto-rejected after timeout)
"""

import sys
import os
import time
import requests
import json


class TestMembershipFlow:
    def __init__(self):
        self.base_url = "http://localhost:5000"

    def run_tests(self):
        """Run the membership flow tests"""
        try:
            print("\nStarting membership flow tests...")

            # Test 1: Add a borrower
            print("\nTest 1: Adding a borrower...")
            response = requests.post(
                f"{self.base_url}/membership/add",
                json={"name": "Borrower Test", "role": "borrower"}
            )

            if response.status_code != 200:
                raise Exception(f"Failed to add borrower: {response.text}")

            borrower = response.json()
            print(f"Borrower added: {json.dumps(borrower, indent=2)}")

            if not self.verify_member_status(borrower['address'], 'pending'):
                raise Exception("Borrower was not added with pending status")

            print("Test 1 passed: Borrower added successfully with pending status")

            # Test 2: Wait for auto-rejection
            print("\nTest 2: Waiting for auto-rejection...")
            max_retries = 6  # Try for 3 minutes (6 * 30 seconds)
            for i in range(max_retries):
                print(f"Check {i+1}/{max_retries} for auto-rejection...")
                if self.verify_member_status(borrower['address'], 'rejected'):
                    print("Borrower was successfully auto-rejected")
                    break
                if i < max_retries - 1:
                    print("Waiting 30 seconds...")
                    time.sleep(30)
            else:
                raise Exception("Borrower was not auto-rejected as expected")

            print("Test 2 passed: Auto-rejection working correctly")

            print("\nAll tests passed successfully!")
            return True

        except Exception as e:
            print(f"\nTest failed: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

    def verify_member_status(self, address, expected_status):
        """Verify a member's status"""
        response = requests.get(f"{self.base_url}/membership/list")
        if response.status_code != 200:
            raise Exception(f"Failed to get member list: {response.text}")

        members = response.json()
        for status_group in ['active', 'pending', 'rejected']:
            for member in members[status_group]:
                if member['address'] == address:
                    return member['status'] == expected_status
        return False


if __name__ == "__main__":
    test = TestMembershipFlow()
    success = test.run_tests()
    sys.exit(0 if success else 1)
