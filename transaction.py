"""
This file defines the Transaction class.
It represents a transaction in the blockchain.
"""

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount