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
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <dict> Created transaction
        """
        # Verify both sender and recipient are registered members
        if sender not in self.blockchain.registered_members or \
           recipient not in self.blockchain.registered_members:
            raise ValueError("Sender or recipient is not a registered member")

        # Create the transaction
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
