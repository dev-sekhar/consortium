"""
This file handles membership requests and voting.
It defines the Membership class which manages membership requests and the list of members.
"""

from typing import Dict, Any, List
import time as timestamp  # Ensure this import is present
from core.blockchain import Blockchain
from eth_account import Account
from .membership_voting import MembershipVoting
import time
from datetime import datetime
from utilities.convert_to_ethereum_address import generate_ethereum_address, validate_ethereum_address


class Membership:
    def __init__(self, blockchain):
        """Initialize membership storage"""
        self.blockchain = blockchain
        self.voting = MembershipVoting()
        self.pending_requests = []
        self.rejected_requests = []
        self.members = []
        self.request_timeout = 30  # 30 seconds timeout for pending requests

    def add_member(self, name, role):
        """Add a new member pending consensus"""
        try:
            print(f"\nAdding new member in Membership class:")
            print(f"Name: {name}")
            print(f"Role: {role}")

            # Create member with pending status
            member = {
                'address': generate_ethereum_address(),
                'name': name,
                'role': role,
                'status': 'pending',
                'timestamp': int(time.time())
            }

            print(f"Generated address: {member['address']}")

            # Validate the generated address
            if not validate_ethereum_address(member['address']):
                raise ValueError(f"Invalid Ethereum address generated: {
                                 member['address']}")

            # Add to blockchain members list
            if self.blockchain and hasattr(self.blockchain, 'members'):
                print("Adding member to blockchain members list")
                self.blockchain.members.append(member)
            else:
                raise ValueError(
                    "Blockchain or members list not properly initialized")

            print(f"Current blockchain members: {self.blockchain.members}")

            return member

        except Exception as e:
            print(f"Error in Membership.add_member: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

    def approve_member(self, member_address, approver_address):
        """Cast a vote to approve a member"""
        try:
            # Debug logging
            print(f"\nApproving member:")
            print(f"Member address: {member_address}")
            print(f"Approver address: {approver_address}")

            # Verify approver is an active lender
            if not self.is_active_lender(approver_address):
                raise ValueError("Only active lenders can vote")

            # Get the pending member
            members = self.get_members()
            print(f"\nCurrent members: {members}")  # Debug log

            pending_member = None
            for member in members['pending']:
                if member['address'] == member_address:
                    pending_member = member
                    break

            if not pending_member:
                raise ValueError(f"No pending request found for address: {
                                 member_address}")

            # Calculate required votes (51% of active lenders)
            active_lenders = [m for m in members['active']
                              if m['role'] == 'lender']
            required_votes = (len(active_lenders) // 2) + 1

            # For now, with single vote approval
            pending_member['status'] = 'active'
            pending_member['approved_at'] = int(time.time())

            # Update the member in blockchain
            self.blockchain.update_member(pending_member)

            return pending_member

        except Exception as e:
            import traceback
            print(f"\nError in approve_member:")
            print(traceback.format_exc())
            raise

    def is_active_lender(self, address):
        """Check if address belongs to an active lender"""
        members = self.get_members()
        # Debug logging
        print(f"\nChecking active lender status:")
        print(f"Address to check: {address}")
        print(f"Active members: {members['active']}")

        # Make sure we're working with the list of active members
        active_members = members.get('active', [])
        if not isinstance(active_members, list):
            print(f"Warning: active_members is not a list: {
                  type(active_members)}")
            return False

        # Check if the address belongs to an active lender
        for member in active_members:
            if isinstance(member, dict):  # Ensure we're working with a dictionary
                if member.get('address') == address and member.get('role') == 'lender':
                    print(f"Found active lender: {member.get('name')}")
                    return True

        print("No matching active lender found")
        return False

    def is_pending_member(self, address):
        """Check if address belongs to a pending member"""
        pending = self.get_pending_requests()
        return any(m['address'] == address for m in pending)

    def get_pending_member(self, address):
        """Get a pending member by address"""
        pending = self.get_pending_requests()
        return next((m for m in pending if m['address'] == address), None)

    def reject_member(self, member_address, approver_address):
        """Reject a pending member"""
        try:
            # Debug logging
            print(f"\nRejecting member:")
            print(f"Member address: {member_address}")
            print(f"Approver address: {approver_address}")

            # Verify approver is an active lender
            if not self.is_active_lender(approver_address):
                raise ValueError("Only active lenders can reject members")

            # Get the pending member
            members = self.get_members()
            print(f"\nCurrent members: {members}")  # Debug log

            pending_member = None
            for member in members['pending']:
                if member['address'] == member_address:
                    pending_member = member
                    break

            if not pending_member:
                raise ValueError(f"No pending request found for address: {
                                 member_address}")

            # Update member status
            pending_member['status'] = 'rejected'
            pending_member['rejected_at'] = int(time.time())
            pending_member['rejected_by'] = approver_address

            # Update the member in blockchain
            self.blockchain.update_member(pending_member)

            return pending_member

        except Exception as e:
            import traceback
            print(f"\nError in reject_member:")
            print(traceback.format_exc())
            raise

    def get_members(self):
        """Get all members"""
        return self.blockchain.get_members()

    def get_pending_requests(self):
        """Get pending membership requests"""
        return self.blockchain.get_pending_members()

    def get_rejected_requests(self) -> List[Dict[str, Any]]:
        """Get all rejected membership requests"""
        return self.rejected_requests

    def clear_all_members(self):
        """Clear all members from the system"""
        return self.blockchain.clear_members()

    def monitor_pending_requests(self):
        """Monitor pending requests and auto-reject if they timeout"""
        while True:
            try:
                if not self.blockchain or not self.blockchain.config:
                    print("Waiting for blockchain and config initialization...")
                    time.sleep(5)
                    continue

                members = self.blockchain.members  # Get members directly
                current_time = int(time.time())

                # Get timeout in seconds from auto_reject config
                timeout_minutes = self.blockchain.config['auto_reject']['timeout']['value']
                timeout_seconds = timeout_minutes * 60  # Convert minutes to seconds

                # Debug logging
                print("\nChecking pending members...")
                print(f"Current time: {current_time}")
                print(f"Timeout: {timeout_seconds} seconds")
                print(f"Total members: {len(members)}")

                # Check each member
                for member in members:
                    if member['status'] == 'pending':
                        request_age = current_time - member['timestamp']

                        # Debug logging
                        print(f"\nChecking pending member: {member['name']}")
                        print(f"Request age: {request_age} seconds")
                        print(f"Member timestamp: {member['timestamp']}")

                        # Auto-reject if request has timed out
                        if request_age > timeout_seconds:
                            print(
                                f"\nAuto-rejecting {member['name']} due to timeout")
                            member['status'] = 'rejected'
                            member['rejected_at'] = current_time
                            member['rejected_by'] = 'auto-reject'
                            member['rejection_reason'] = 'timeout'

                # Sleep for 10 seconds before next check
                time.sleep(10)

            except Exception as e:
                print(f"Error in monitor_pending_requests: {str(e)}")
                import traceback
                print(traceback.format_exc())
                time.sleep(5)

    def check_pending_members(self):
        """Check for pending members that need auto-rejection"""
        try:
            current_time = int(time.time())

            # Get members by status
            pending_members = [
                m for m in self.blockchain.members if m['status'] == 'pending']
            active_members = [
                m for m in self.blockchain.members if m['status'] == 'active']
            rejected_members = [
                m for m in self.blockchain.members if m['status'] == 'rejected']

            # Print member statistics
            print("\nMember Statistics:")
            print(f"Active members: {len(active_members)} ({
                  [m['name'] for m in active_members]})")
            print(f"Pending members: {len(pending_members)} ({
                  [m['name'] for m in pending_members]})")
            print(f"Rejected members: {len(rejected_members)} ({
                  [m['name'] for m in rejected_members]})")

            # Check for auto-rejection if there are pending members
            if pending_members:
                print("\nChecking pending members for auto-rejection...")
                print(f"Current time: {current_time}")
                print(
                    f"Auto-reject timeout: {self.auto_reject_timeout} seconds")

                for member in pending_members:
                    elapsed_time = current_time - member['timestamp']
                    if elapsed_time > self.auto_reject_timeout:
                        self.auto_reject_member(member)

        except Exception as e:
            print(f"Error checking pending members: {str(e)}")
            raise

    def vote_for_member(self, member_address, voter_address, vote_type):
        """Process a vote for a member"""
        try:
            # Find target member
            target_member = None
            for member in self.blockchain.members:
                if member['address'] == member_address:
                    target_member = member
                    break

            if not target_member:
                raise Exception('Member not found')

            if target_member['status'] != 'pending':
                raise Exception('Member is not in pending status')

            # Initialize votes if not present
            if 'votes' not in target_member:
                target_member['votes'] = {'approve': [], 'reject': []}

            # Check if already voted
            if voter_address in target_member['votes']['approve'] or voter_address in target_member['votes']['reject']:
                raise Exception('Already voted')

            # Add vote
            target_member['votes'][vote_type].append(voter_address)

            # Count active lenders
            active_lenders = [m for m in self.blockchain.members
                              if m['status'] == 'active' and m['role'] == 'lender']
            required_votes = len(active_lenders)

            # Check if enough votes
            if len(target_member['votes'][vote_type]) >= required_votes:
                target_member['status'] = 'active' if vote_type == 'approve' else 'rejected'
                target_member['approved_at'] = int(timestamp.time())
                target_member['approved_by'] = ','.join(
                    target_member['votes'][vote_type])
                print(f"Member {target_member['name']} approved with {
                      len(target_member['votes']['approve'])} votes")

                # Add transaction to pending pool
                self.blockchain.add_transaction({
                    'type': 'member_approved' if vote_type == 'approve' else 'member_rejected',
                    'member': target_member,
                    'timestamp': int(timestamp.time())
                })
                return True
            else:
                print(f"Member {target_member['name']} has {
                      len(target_member['votes'][vote_type])} of {required_votes} required votes")
                return False

        except Exception as e:
            print(f"Error in vote_for_member: {str(e)}")
            raise
