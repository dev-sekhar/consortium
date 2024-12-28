"""
This file handles transaction creation and validation.
It defines the Transaction class which manages the creation and verification of transactions.
"""


class Transaction:
    def __init__(self, blockchain):
        """
        Initialize Transaction manager
        :param blockchain: Reference to the blockchain for member verification
        """
        self.blockchain = blockchain
        self.pending_transactions = []

    def create_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction
        """
        # Check if sender has permission to perform this type of transaction
        if amount < 0:  # If borrowing
            if not self.blockchain.membership.has_permission(sender, 'borrow_funds'):
                raise ValueError(
                    "Sender does not have permission to borrow funds")
        else:  # If lending
            if not self.blockchain.membership.has_permission(sender, 'lend_funds'):
                raise ValueError(
                    "Sender does not have permission to lend funds")

        # Verify both parties are registered members
        if not self.blockchain.membership.get_member_by_address(sender) or \
           not self.blockchain.membership.get_member_by_address(recipient):
            raise ValueError("Sender or recipient is not a registered member")

        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
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
