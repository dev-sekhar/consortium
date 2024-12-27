"""
This file contains the core logic for the blockchain.
It defines the Blockchain class which manages the chain of blocks and transactions.
"""

import hashlib
import json
from time import time
from convert_to_ethereum_address import convert_to_ethereum_address


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.registered_members = []  # Add this line to initialize the list
        # Create the genesis block
        self.new_block(previous_hash='1')

    def new_block(self, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        if sender not in self.registered_members or recipient not in self.registered_members:
            raise ValueError("Sender or recipient is not a registered member")

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

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
