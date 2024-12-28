"""
This file contains the core logic for the blockchain.
It defines the Blockchain class which manages the chain of blocks and transactions.
"""

import hashlib
import json
from time import time
from convert_to_ethereum_address import convert_to_ethereum_address
from consensus import ProofOfVote
from transaction import Transaction


class Blockchain:
    def __init__(self):
        self.chain = []
        self.membership = None  # Initialize as None first
        self.transaction_manager = Transaction(self)
        self.consensus = ProofOfVote()
        # Create the genesis block
        self.new_block(previous_hash='1')

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        """
        transaction = self.transaction_manager.create_transaction(
            sender, recipient, amount)
        return self.last_block['index'] + 1

    def new_block(self, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.transaction_manager.get_pending_transactions(),
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Calculate block hash immediately
        block['hash'] = self.hash(block)

        # Clear pending transactions
        self.transaction_manager.clear_pending_transactions()

        self.chain.append(block)
        return block

    def register_member(self, address):
        """Register a new member address"""
        if address not in self.registered_members:
            self.registered_members.append(address)

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

    def propose_block(self, proposer):
        """
        Propose a new block using the consensus mechanism
        """
        block = self.consensus.propose_block(
            self.chain,
            self.transaction_manager.get_pending_transactions(),
            proposer,
            self.membership
        )
        return block

    def vote_for_block(self, block_index, voter_address):
        """
        Vote for a proposed block
        """
        block, approved = self.consensus.vote_for_block(
            block_index,
            voter_address,
            self.membership
        )

        if approved:
            block['hash'] = self.hash(block)
            self.chain.append(block)
            self.transaction_manager.clear_pending_transactions()
            self.consensus.remove_block(block)

        return block

    def set_membership(self, membership):
        """Set the membership instance after initialization"""
        self.membership = membership


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
        address = convert_to_ethereum_address(public_key_pem)
        member = {'address': address, 'name': name}
        self.members.append(member)
        # Register the member in the blockchain
        self.blockchain.register_member(address)
        return member

    # Other methods remain unchanged
