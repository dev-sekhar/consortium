"""
This file handles membership requests and voting.
It defines the Membership class which manages membership requests and the list of members.
"""

import json
import time
from uuid import uuid4
from datetime import datetime
from typing import List, Dict, Any

from utilities.convert_to_ethereum_address import generate_ethereum_address, validate_ethereum_address


class Membership:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.members = []
        self.pending_requests = []
        self.rejected_requests = []

        # Load configuration
        with open('core/membership_config.json', 'r') as config_file:
            self.config = json.load(config_file)

        # Load existing members from blockchain
        self._load_from_blockchain()

    def _load_from_blockchain(self):
        """Load members and requests from blockchain"""
        for block in self.blockchain.chain:
            for transaction in block['transactions']:
                if transaction['data']['type'] == 'member_added':
                    member = transaction['data']['member']
                    if member not in self.members:
                        self.members.append(member)
                elif transaction['data']['type'] == 'membership_requested':
                    request = transaction['data']['request']
                    if request not in self.pending_requests:
                        self.pending_requests.append(request)

    def add_member(self, member_data):
        """Add a new member directly (for first member/genesis)"""
        # Generate Ethereum address for first member
        eth_address = generate_ethereum_address()
        member_data['address'] = eth_address['address']

        if not validate_ethereum_address(member_data['address']):
            raise ValueError("Invalid Ethereum address")

        member = {
            'member_id': str(uuid4()),
            'address': member_data['address'],
            'name': member_data['name'],
            'role': member_data['role'],
            'joined_date': datetime.utcnow().isoformat(),
            'status': 'active'
        }

        # Add to blockchain first
        self.blockchain.new_transaction(
            sender=member['address'],
            recipient=member['address'],
            data={
                'type': 'member_added',
                'member': member
            }
        )

        # Add to members list
        self.members.append(member)

        # Return both member info and private key
        return {
            'member': member,
            'private_key': eth_address['private_key']
        }

    def request_membership(self, request_data):
        """Request to join the consortium"""
        eth_address = generate_ethereum_address()

        request = {
            'request_id': str(uuid4()),
            'address': eth_address['address'],
            'name': request_data['name'],
            'role': request_data['role'],
            'status': 'pending',
            'timestamp': datetime.utcnow().isoformat(),
            'votes': []
        }

        # Add to blockchain first
        self.blockchain.new_transaction(
            sender=request['address'],
            recipient=None,
            data={
                'type': 'membership_requested',
                'request': request
            }
        )

        # Add to pending requests
        self.pending_requests.append(request)

        return {
            'request': request,
            'private_key': eth_address['private_key']
        }

    def vote_on_request(self, request_id, voter_address, action):
        """Vote on a membership request"""
        # Check if voter is a member and is a lender
        voter = self.get_member(voter_address)
        if not voter:
            raise ValueError("Only members can vote")
        if voter['role'] != 'lender':
            raise ValueError("Only lenders can vote")

        request = next(
            (req for req in self.pending_requests if req['request_id'] == request_id),
            None
        )

        if not request:
            raise ValueError("Request not found")

        if any(vote['voter'] == voter_address for vote in request['votes']):
            raise ValueError("Already voted on this request")

        # Get total number of active lenders who can vote
        total_active_lenders = len(
            [m for m in self.members if m['status'] == 'active' and m['role'] == 'lender'])

        vote = {
            'voter': voter_address,
            'action': action,
            'timestamp': datetime.utcnow().isoformat()
        }

        request['votes'].append(vote)

        # Add vote to blockchain
        self.blockchain.new_transaction(
            sender=voter_address,
            recipient=request['address'],
            data={
                'type': 'membership_vote',
                'vote': vote,
                'request_id': request_id
            }
        )

        # Count votes
        approve_votes = sum(
            1 for vote in request['votes'] if vote['action'] == 'approve')
        reject_votes = sum(
            1 for vote in request['votes'] if vote['action'] == 'reject')

        # Calculate required votes based on total lenders
        required_votes = max(
            1, int(total_active_lenders * self.config['voting']['approval_threshold']))

        # Check if enough votes to make a decision
        if approve_votes >= required_votes:
            # Add as member
            new_member = {
                'member_id': str(uuid4()),
                'address': request['address'],
                'name': request['name'],
                'role': request['role'],
                'joined_date': datetime.utcnow().isoformat(),
                'status': 'active'
            }
            self.members.append(new_member)

            # Add to blockchain
            self.blockchain.new_transaction(
                sender=voter_address,
                recipient=request['address'],
                data={
                    'type': 'member_added',
                    'member': new_member
                }
            )

            # Remove from pending
            self.pending_requests.remove(request)

        elif reject_votes >= required_votes:
            # Add rejection to blockchain
            self.blockchain.new_transaction(
                sender=voter_address,
                recipient=request['address'],
                data={
                    'type': 'membership_rejected',
                    'request': request
                }
            )

            # Remove from pending
            self.pending_requests.remove(request)

        return {
            'request': request,
            'total_lenders': total_active_lenders,
            'required_votes': required_votes,
            'current_approve_votes': approve_votes,
            'current_reject_votes': reject_votes
        }

    def is_member(self, address):
        """Check if an address belongs to a member"""
        return any(member['address'] == address for member in self.members)

    def get_member(self, address):
        """Get member details by address"""
        return next(
            (member for member in self.members if member['address'] == address),
            None
        )

    def get_members(self, status=None):
        """Get all members, optionally filtered by status"""
        if status:
            return [member for member in self.members if member['status'] == status]
        return self.members

    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get all pending membership requests"""
        return self.pending_requests

    def get_rejected_requests(self) -> List[Dict[str, Any]]:
        """Get all rejected membership requests"""
        return self.rejected_requests

    def update_request_status(self, request_id: str, status: str, reason: str = None) -> bool:
        """
        Update the status of a membership request

        Args:
            request_id: The ID of the request to update
            status: New status ('approved', 'rejected')
            reason: Optional reason for the status change

        Returns:
            bool: True if update was successful, False otherwise
        """
        # Find request in pending requests
        request = next(
            (req for req in self.pending_requests if req['request_id'] == request_id),
            None
        )

        if not request:
            return False

        # Update request status
        request['status'] = status
        request['update_time'] = datetime.utcnow().isoformat()
        if reason:
            request['update_reason'] = reason

        # Move to appropriate list based on status
        if status == 'rejected':
            self.pending_requests.remove(request)
            self.rejected_requests.append(request)

        return True
