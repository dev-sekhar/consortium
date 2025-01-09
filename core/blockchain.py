"""
This file contains the core logic for the blockchain.
It defines the Blockchain class which manages the chain of blocks and transactions.
"""

import hashlib
import json
import time as timestamp  # Rename the import to avoid conflict
from datetime import datetime
from utilities.convert_to_ethereum_address import generate_ethereum_address, validate_ethereum_address
from .consensus import Consensus
import os
from utils.hashing_util import hash_block  # Update the import path


class Blockchain:
    def __init__(self, config):
        self.chain = []
        self.members = []
        self.pending_transactions = []
        self.config = config

        # Convert block interval to seconds
        interval_value = config['blockchain']['block_creation']['interval']['value']
        interval_unit = config['blockchain']['block_creation']['interval']['unit']
        self.block_interval = self.convert_to_seconds(
            interval_value, interval_unit)

        self.last_block_time = 0
        self.max_transactions = config['blockchain']['max_transactions_per_block']

        # Create genesis block
        self.create_genesis_block()

    def convert_to_seconds(self, value, unit):
        """Convert time units to seconds"""
        units = {
            'seconds': 1,
            'minutes': 60,
            'hours': 3600,
            'days': 86400
        }
        return value * units.get(unit.lower(), 1)

    def initialize(self):
        """Initialize blockchain after config is set"""
        if not self.config:
            raise ValueError("Config must be set before initialization")

        # Initialize consensus with config
        self.consensus.initialize(self.config)

        # Create the genesis block using config values
        genesis_config = self.config['blockchain']['genesis_block']
        self.new_block(previous_hash=genesis_config['previous_hash'])

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            config_path = os.path.join(
                'use_case', 'config', 'timing_config.json')
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            # Default configuration
            return {
                "voting": {
                    "timeout": {
                        "value": 72,
                        "unit": "hours"
                    },
                    "reminder": {
                        "value": 48,
                        "unit": "hours"
                    }
                }
            }

    def new_block(self, previous_hash=None):
        """Create a new block in the blockchain"""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': timestamp.time(),
            'transactions': self.current_transactions,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, data):
        """Create a new transaction pending consensus"""
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Create block proposal for transaction
        block_data = {
            'type': 'transaction',
            'transaction': transaction
        }

        # Propose new block through consensus
        proposed_block = self.propose_block(block_data)

        return transaction

    def register_node(self, address):
        """Add a new node to the set of nodes"""
        self.nodes.add(address)

    def set_membership(self, membership):
        """Set the membership handler"""
        self.membership = membership

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """
        Returns the last Block in the chain
        :return: <dict> Last Block
        """
        return self.chain[-1]

    def propose_block(self, block_data):
        """
        Propose a new block using the consensus mechanism
        """
        block = self.consensus.propose_block(
            self.chain,
            self.pending_transactions,
            block_data,
            self.members
        )
        return block

    def vote_for_block(self, block_index, voter_address):
        """
        Vote for a proposed block
        """
        block, approved = self.consensus.vote_for_block(
            block_index,
            voter_address,
            self.members
        )

        if approved:
            block['hash'] = self.hash(block)
            self.chain.append(block)
            self.pending_transactions = []
            self.consensus.reset_votes()

        return block

    def add_member(self, member):
        """Add a new member to the blockchain"""
        # Add timestamp as Unix timestamp (integer) and generate Ethereum address
        member['address'] = generate_ethereum_address()
        member['timestamp'] = int(datetime.utcnow().timestamp())

        self.members.append(member)
        return member

    def update_member(self, member):
        """Update an existing member's data"""
        for i, m in enumerate(self.members):
            if m['address'] == member['address']:
                # Ensure timestamp remains as Unix timestamp if not provided
                if 'timestamp' not in member:
                    member['timestamp'] = self.members[i]['timestamp']
                self.members[i] = member
                return
        raise ValueError(f"Member not found with address: {member['address']}")

    def get_members(self):
        """Get all members grouped by status"""
        active = []
        pending = []
        rejected = []

        for member in self.members:
            if member['status'] == 'active':
                active.append(member)
            elif member['status'] == 'pending':
                pending.append(member)
            elif member['status'] == 'rejected':
                rejected.append(member)

        return {
            'active': active,
            'pending': pending,
            'rejected': rejected,
            'total_count': {
                'active': len(active),
                'pending': len(pending),
                'rejected': len(rejected)
            }
        }

    def get_active_members(self):
        """Get only active members"""
        return [m for m in self.members if m['status'] == 'active']

    def get_pending_members(self):
        """Get only pending members"""
        return [m for m in self.members if m['status'] == 'pending']

    def generate_address(self):
        """Generate a unique address for a member"""
        import uuid
        return f"0x{uuid.uuid4().hex[:40]}"

    def clear_members(self):
        """Clear all members from the blockchain"""
        self.members = []
        return {"status": "success", "message": "All members cleared"}

    def add_transaction(self, transaction):
        """Add transaction to pending pool"""
        self.pending_transactions.append({
            'data': transaction,
            'timestamp': int(timestamp.time())
        })
        print(f"\nTransaction added to pool: {transaction}")

    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = {
            'index': 1,
            'timestamp': int(timestamp.time()),
            'transactions': [],
            'previous_hash': '0',
            'hash': hash_block({
                'index': 1,
                'timestamp': int(timestamp.time()),
                'transactions': [],
                'previous_hash': '0'
            })
        }
        self.chain.append(genesis_block)
        self.last_block_time = genesis_block['timestamp']
        print(f"\nGenesis block created at {
              genesis_block['timestamp']} with hash: {genesis_block['hash']}")

    def create_block(self):
        """Create a new block with all pending transactions"""
        if not self.pending_transactions:
            return None

        current_time = int(timestamp.time())
        time_since_last = current_time - self.last_block_time

        if time_since_last < self.block_interval:
            # Only log when a block is created or when transactions are pending
            if self.pending_transactions and not hasattr(self, '_last_log_time'):
                self._last_log_time = current_time
                print(f"\nWaiting for next block. {
                      len(self.pending_transactions)} transaction(s) pending.")
                print(f"Next block in {
                      self.block_interval - time_since_last} seconds")
            return None

        block = {
            'index': len(self.chain) + 1,
            'timestamp': current_time,
            'transactions': self.pending_transactions.copy(),
            # Use the hash of the last block
            'previous_hash': self.chain[-1]['hash'],
            'hash': '',  # Placeholder for the hash
        }

        # Calculate the hash for the new block
        block['hash'] = hash_block(block)

        self.pending_transactions = []  # Clear pool after creating block
        self.last_block_time = current_time
        if hasattr(self, '_last_log_time'):
            delattr(self, '_last_log_time')

        print(f"\nCreated block #{block['index']} with {
              len(block['transactions'])} transaction(s) and hash: {block['hash']}")
        return block

    def add_block(self, block):
        """Add a block to the chain"""
        self.chain.append(block)
        print(f"\nBlock #{block['index']} added to chain")
        print(f"Total blocks: {len(self.chain)}")


class Membership:
    def __init__(self):
        self.blockchain = Blockchain()
        self.members = []

    def add_member(self, name):
        """
        Manually add a member to the list of approved members.
        :param name: <str> Name of the member
        :return: <dict> Member object
        """
        public_key, private_key = self.generate_key_pair()
        public_key_pem = self.serialize_public_key(public_key)
        address = generate_ethereum_address(public_key_pem)
        member = {'address': address, 'name': name}
        self.members.append(member)
        # Register the member in the blockchain
        self.blockchain.register_member(address)
        return member

    # Other methods remain unchanged
