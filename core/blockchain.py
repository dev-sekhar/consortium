"""
This file contains the core logic for the blockchain.
It defines the Blockchain class which manages the chain of blocks and transactions.
"""

import hashlib
import json
from time import time
from uuid import uuid4
from datetime import datetime
from decimal import Decimal
from utilities.convert_to_ethereum_address import generate_ethereum_address, validate_ethereum_address
from .consensus import Consensus


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.consensus = Consensus()

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash):
        """Create a new block in the blockchain"""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, data):
        """Add a new transaction to the list of transactions"""
        if not validate_ethereum_address(sender):
            raise ValueError("Invalid sender address")
        if recipient and not validate_ethereum_address(recipient):
            raise ValueError("Invalid recipient address")

        transaction = {
            'sender': sender,
            'recipient': recipient,
            'data': data,
            'timestamp': datetime.utcnow().isoformat(),
            'transaction_id': str(uuid4())
        }

        self.current_transactions.append(transaction)
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
