"""
This file handles membership requests and voting.
It defines the Membership class which manages membership requests and the list of members.
"""

import json
from eth_utils import to_checksum_address
from cryptography.hazmat.primitives import hashes
import os
from blockchain import Blockchain
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from convert_to_ethereum_address import convert_to_ethereum_address


class Membership:
    def __init__(self, blockchain):
        """
        Initialize with blockchain reference
        """
        self.blockchain = blockchain
        self.members = []
        self.pending_requests = []
        self.rejected_requests = []
        self.config = self._load_config()

    def _load_config(self):
        """
        Load membership configuration from JSON file
        """
        with open('membership_config.json', 'r') as f:
            return json.load(f)

    def generate_key_pair(self):
        """
        Generate a public-private key pair.
        :return: <tuple> (public_key, private_key)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return public_key, private_key

    def serialize_public_key(self, public_key):
        """
        Serialize the public key to PEM format.
        :param public_key: <RSAPublicKey> Public key
        :return: <str> Serialized public key
        """
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    def add_first_member(self, name, role):
        """
        Add the first member without voting
        """
        if role != self.config['first_member_category']:
            raise ValueError(f"First member must be a {
                             self.config['first_member_category']}")

        if self.members:
            raise ValueError("First member already exists")

        if role not in self.config['member_categories']:
            raise ValueError(f"Invalid role. Must be one of: {
                             list(self.config['member_categories'].keys())}")

        address = self._generate_address()
        member = {
            'name': name,
            'address': address,
            'role': role,
            'status': 'approved'
        }
        self.members.append(member)
        return member

    def request_membership(self, name, role):
        """
        Request new membership
        """
        if role not in self.config['member_categories']:
            raise ValueError(f"Invalid role. Must be one of: {
                             list(self.config['member_categories'].keys())}")

        address = self._generate_address()
        request = {
            'name': name,
            'address': address,
            'role': role,
            'status': 'pending'
        }
        self.pending_requests.append(request)
        return request

    def vote_on_request(self, request_address, voter_address, action):
        """
        Vote on a membership request
        """
        # Verify voter has voting permission
        voter = self.get_member_by_address(voter_address)
        if not voter or voter['role'] not in self.config['voting_categories']:
            raise ValueError(f"Only {', '.join(
                self.config['voting_categories'])} can vote on membership requests")

        request = self._find_request(request_address)
        if not request:
            raise ValueError("Request not found")

        if action == 'approve':
            self.members.append(request)
            self.pending_requests.remove(request)
            request['status'] = 'approved'
        elif action == 'reject':
            self.rejected_requests.append(request)
            self.pending_requests.remove(request)
            request['status'] = 'rejected'
        else:
            raise ValueError("Invalid action")

        return request

    def has_permission(self, address, permission):
        """
        Check if a member has a specific permission
        """
        member = self.get_member_by_address(address)
        if not member:
            return False

        member_permissions = self.config['member_categories'][member['role']]['permissions']
        return permission in member_permissions

    def _generate_address(self):
        """
        Generate a new Ethereum address
        """
        public_key, private_key = self.generate_key_pair()
        public_key_pem = self.serialize_public_key(public_key)
        return convert_to_ethereum_address(public_key_pem)

    def _find_request(self, request_address):
        """
        Find a membership request by address
        """
        for request in self.pending_requests:
            if request['address'] == request_address:
                return request
        return None

    def get_member_by_address(self, address):
        """
        Get a member by address
        """
        for member in self.members:
            if member['address'] == address:
                return member
        return None

    def get_addresses(self):
        """
        Get the list of member addresses.
        :return: <list> List of addresses
        """
        return [member['address'] for member in self.members]
