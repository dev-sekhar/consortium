"""
This file handles transaction creation and validation.
It defines the Transaction class which manages the creation and verification of transactions.
"""

from time import time
from use_case.proposal import Proposal


class Transaction:
    def __init__(self, blockchain):
        """
        Initialize Transaction manager
        :param blockchain: Reference to the blockchain for member verification
        """
        self.blockchain = blockchain
        self.pending_transactions = []
        self.proposal_validator = Proposal()

    def create_transaction(self, sender, recipient=None, amount=None, type=None, proposal_details=None):
        """
        Creates a new transaction
        """
        if type == "submit_proposal":
            if not self.blockchain.membership.has_permission(sender, 'submit_proposal'):
                raise ValueError(
                    "Sender does not have permission to submit proposals")

            # Validate proposal details
            self.proposal_validator.validate_proposal(proposal_details)

            transaction = {
                'type': 'submit_proposal',
                'sender': sender,
                'proposal_details': proposal_details,
                'timestamp': time()
            }
        else:
            # Regular transaction validation
            if amount < 0:  # If borrowing
                if not self.blockchain.membership.has_permission(sender, 'borrow_funds'):
                    raise ValueError(
                        "Sender does not have permission to borrow funds")
            else:  # If lending
                if not self.blockchain.membership.has_permission(sender, 'lend_funds'):
                    raise ValueError(
                        "Sender does not have permission to lend funds")

            transaction = {
                'type': 'transfer',
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
                'timestamp': time()
            }

        self.pending_transactions.append(transaction)
        return transaction

    def get_pending_transactions(self):
        """
        Get all pending transactions
        :return: <list> List of pending transactions
        """
        return self.pending_transactions

    def clear_pending_transactions(self):
        """
        Clear the list of pending transactions (called after block creation)
        """
        self.pending_transactions = []
