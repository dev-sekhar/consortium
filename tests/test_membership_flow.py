"""
Membership Flow Test Script

This script tests the complete membership flow including:
- Initial member addition
- Membership requests
- Voting process
- Auto-rejection mechanism

The test follows these steps:
1. Add first lender (founding member)
2. Add remaining members (3 lenders, 4 borrowers)
3. Vote on membership requests (approve 5, leave 2 for auto-reject)
4. Monitor auto-reject process
5. Generate test report
"""

import requests
import json
import time
from datetime import datetime
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TestStatus(Enum):
    """Enum for test execution status"""
    PASSED = "✅ PASSED"
    FAILED = "❌ FAILED"
    PENDING = "⏳ PENDING"


@dataclass
class TestResult:
    """Data class for storing test results"""
    status: TestStatus
    message: str
    details: Optional[Dict[str, Any]] = None


class MembershipTest:
    """
    Test class for membership flow validation

    Attributes:
        base_url: API endpoint base URL
        address_file: File to store test addresses
        addresses: Dictionary to store member addresses
        test_results: Dictionary to store test results
    """

    def __init__(self):
        """Initialize test environment and storage"""
        self.base_url = "http://localhost:5000"
        self.address_file = "test_addresses.json"
        self.addresses = {
            "lenders": {},
            "borrowers": {}
        }
        self.test_results = {}
        self._init_test_results()

    def _init_test_results(self) -> None:
        """Initialize test results with pending status"""
        self.test_results = {
            "add_first_member": TestResult(TestStatus.PENDING, "Not started"),
            "add_remaining_members": TestResult(TestStatus.PENDING, "Not started"),
            "approve_selected_members": TestResult(TestStatus.PENDING, "Not started"),
            "auto_reject": TestResult(TestStatus.PENDING, "Not started")
        }

    def add_first_member(self) -> None:
        """
        Add the first lender (founding member)

        This member will have voting rights for subsequent requests
        """
        print("\n1. Adding first lender...")
        try:
            response = requests.post(
                f"{self.base_url}/membership/add",
                json={"name": "Lender One", "role": "lender"}
            )
            data = response.json()

            if 'member' in data and 'address' in data['member']:
                self.addresses["lenders"]["one"] = data['member']['address']
                self.test_results["add_first_member"] = TestResult(
                    TestStatus.PASSED,
                    f"Lender One added successfully with address: {
                        data['member']['address']}",
                    {"address": data['member']['address']}
                )
            else:
                raise KeyError(f"Invalid response format: {data}")

        except Exception as e:
            self.test_results["add_first_member"] = TestResult(
                TestStatus.FAILED,
                f"Failed to add first member: {str(e)}"
            )
            raise

        self._save_addresses()

    def add_remaining_members(self) -> None:
        """
        Add remaining members as requests

        Adds:
        - 3 additional lenders
        - 4 borrowers
        - 2 additional members for manual rejection
        All added as pending requests requiring approval
        """
        print("\n2. Adding remaining members...")
        try:
            successful_requests = 0

            # Add Lenders
            for name in ["Two", "Three", "Four"]:
                response = requests.post(
                    f"{self.base_url}/membership/request",
                    json={"name": f"Lender {name}", "role": "lender"}
                )
                data = response.json()

                if 'request' in data:
                    self.addresses["lenders"][name.lower()] = {
                        "address": data["request"]["address"],
                        "request_id": data["request"]["request_id"]
                    }
                    successful_requests += 1

            # Add Borrowers
            for name in ["One", "Two", "Three", "Four"]:
                response = requests.post(
                    f"{self.base_url}/membership/request",
                    json={"name": f"Borrower {name}", "role": "borrower"}
                )
                data = response.json()

                if 'request' in data:
                    self.addresses["borrowers"][name.lower()] = {
                        "address": data["request"]["address"],
                        "request_id": data["request"]["request_id"]
                    }
                    successful_requests += 1

            # Add members for manual rejection
            for name in ["Manual Reject One", "Manual Reject Two"]:
                response = requests.post(
                    f"{self.base_url}/membership/request",
                    json={"name": name, "role": "borrower"}
                )
                data = response.json()

                if 'request' in data:
                    self.addresses["manual_reject"] = self.addresses.get(
                        "manual_reject", {})
                    self.addresses["manual_reject"][name.lower().replace(" ", "_")] = {
                        "address": data["request"]["address"],
                        "request_id": data["request"]["request_id"]
                    }
                    successful_requests += 1

            expected_requests = 9  # 7 regular + 2 manual reject
            self.test_results["add_remaining_members"] = TestResult(
                TestStatus.PASSED if successful_requests == expected_requests else TestStatus.FAILED,
                f"Added {successful_requests}/{expected_requests} member requests",
                {"successful_requests": successful_requests}
            )

        except Exception as e:
            self.test_results["add_remaining_members"] = TestResult(
                TestStatus.FAILED,
                f"Failed to add remaining members: {str(e)}"
            )
            raise

        self._save_addresses()

    def manually_reject_members(self) -> None:
        """
        Manually reject specific membership requests
        """
        print("\n3. Manually rejecting selected members...")
        try:
            voter_address = self.addresses["lenders"]["one"]
            successful_rejections = 0

            # Reject manual reject candidates
            for name in ["manual_reject_one", "manual_reject_two"]:
                request_id = self.addresses["manual_reject"][name]["request_id"]
                response = requests.post(
                    f"{self.base_url}/membership/vote",
                    json={
                        "request_id": request_id,
                        "voter_address": voter_address,
                        "action": "reject"
                    }
                )
                if response.status_code == 200:
                    successful_rejections += 1
                    print(f"Manually rejected {name}")

            self.test_results["manual_rejections"] = TestResult(
                TestStatus.PASSED if successful_rejections == 2 else TestStatus.FAILED,
                f"Manually rejected {successful_rejections}/2 members",
                {"successful_rejections": successful_rejections}
            )

        except Exception as e:
            self.test_results["manual_rejections"] = TestResult(
                TestStatus.FAILED,
                f"Failed to manually reject members: {str(e)}"
            )

    def approve_selected_members(self) -> None:
        """
        Vote on membership requests

        Approves:
        - 2 lenders (Two and Three)
        - 3 borrowers (One, Two, and Three)
        Leaves:
        - 1 lender (Four) for auto-reject
        - 1 borrower (Four) for auto-reject
        """
        print("\n4. Approving selected members...")
        try:
            voter_address = self.addresses["lenders"]["one"]
            successful_votes = 0

            # Vote on selected members
            for member_type, names in {
                "lenders": ["two", "three"],
                "borrowers": ["one", "two", "three"]
            }.items():
                for name in names:
                    request_id = self.addresses[member_type][name]["request_id"]
                    response = requests.post(
                        f"{self.base_url}/membership/vote",
                        json={
                            "request_id": request_id,
                            "voter_address": voter_address,
                            "action": "approve"
                        }
                    )
                    if response.status_code == 200:
                        successful_votes += 1

            self.test_results["approve_selected_members"] = TestResult(
                TestStatus.PASSED if successful_votes == 5 else TestStatus.FAILED,
                f"Approved {successful_votes}/5 members",
                {"successful_votes": successful_votes}
            )

        except Exception as e:
            self.test_results["approve_selected_members"] = TestResult(
                TestStatus.FAILED,
                f"Failed to approve members: {str(e)}"
            )

    def monitor_auto_reject(self, duration: int = 300) -> None:
        """Monitor auto-reject status and reminders"""
        try:
            lender_four_id = self.addresses["lenders"]["four"]["request_id"]
            borrower_four_id = self.addresses["borrowers"]["four"]["request_id"]

            start_time = time.time()
            rejected_count = 0
            reminder_count = 0
            tracked_requests = {
                lender_four_id: {"reminded": False, "rejected": False},
                borrower_four_id: {"reminded": False, "rejected": False}
            }

            while time.time() - start_time < duration:
                for request_id in tracked_requests:
                    response = requests.get(
                        f"{self.base_url}/membership/request/{request_id}/status"
                    )
                    data = response.json()

                    # Track reminders
                    if (data.get('auto_reject_info', {}).get('reminder_sent') and
                            not tracked_requests[request_id]["reminded"]):
                        reminder_count += 1
                        tracked_requests[request_id]["reminded"] = True
                        print(f"Reminder tracked for request {request_id}")

                    # Track rejections
                    if (data.get('status') == 'rejected' and
                            not tracked_requests[request_id]["rejected"]):
                        rejected_count += 1
                        tracked_requests[request_id]["rejected"] = True
                        print(f"Rejection tracked for request {request_id}")

                if all(req["rejected"] for req in tracked_requests.values()):
                    break

                time.sleep(10)

            self.test_results["reminders"] = TestResult(
                TestStatus.PASSED if reminder_count == 2 else TestStatus.FAILED,
                f"Sent {reminder_count}/2 reminders",
                {"reminder_count": reminder_count}
            )

            self.test_results["auto_reject"] = TestResult(
                TestStatus.PASSED if rejected_count == 2 else TestStatus.FAILED,
                f"Auto-rejected {rejected_count}/2 requests",
                {"rejected_count": rejected_count}
            )

        except Exception as e:
            self.test_results["auto_reject"] = TestResult(
                TestStatus.FAILED,
                f"Failed to monitor auto-reject: {str(e)}"
            )

    def generate_report(self) -> None:
        """
        Generate detailed test execution report

        Includes:
        - Overall test status
        - Individual test results
        - Detailed analysis of each phase
        - Recommendations if issues found
        """
        print("\n=== Test Execution Report ===")
        print("\nTest Results:")

        all_passed = True
        for test_name, result in self.test_results.items():
            print(f"{test_name}: {result.status.value}")
            print(f"  Message: {result.message}")
            if result.details:
                print(f"  Details: {json.dumps(result.details, indent=2)}")
            all_passed = all_passed and (result.status == TestStatus.PASSED)

        print("\nOverall Status:",
              "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED")

        if not all_passed:
            print("\nRecommendations:")
            for test_name, result in self.test_results.items():
                if result.status == TestStatus.FAILED:
                    print(f"- Investigate {test_name}: {result.message}")

    def cleanup(self) -> None:
        """Remove test artifacts"""
        if os.path.exists(self.address_file):
            os.remove(self.address_file)
            print("\nTest address file cleaned up")

    def _save_addresses(self) -> None:
        """Save member addresses to file for reference"""
        with open(self.address_file, 'w') as f:
            json.dump(self.addresses, f, indent=2)
            print(f"Addresses saved to {self.address_file}")

    def run_test(self) -> None:
        """
        Execute complete test flow

        Flow:
        1. Add first member
        2. Add remaining members (including manual reject candidates)
        3. Manually reject specific members
        4. Vote on selected members
        5. Monitor auto-reject process
        6. Generate report
        7. Cleanup
        """
        try:
            self.add_first_member()
            time.sleep(2)

            self.add_remaining_members()
            time.sleep(2)

            self.manually_reject_members()
            time.sleep(2)

            self.approve_selected_members()
            time.sleep(2)

            self.monitor_auto_reject(duration=180)  # 3 minutes

        finally:
            self.generate_report()
            self.cleanup()


if __name__ == "__main__":
    test = MembershipTest()
    test.run_test()
