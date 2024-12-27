"""
Consensus Mechanism: Proof of Vote (PoV)

This file implements a voting-based consensus mechanism for a consortium blockchain.
Instead of using computational work (like in PoW) or stake (like in PoS), 
this mechanism requires a minimum number of member votes to validate and add new blocks.

Key features:
- Only registered members can propose and vote on blocks
- Blocks require a minimum number of votes to be approved
- Tracks pending blocks that are awaiting votes
- Prevents double voting by tracking voter addresses
"""

from time import time


class ProofOfVote:
    def __init__(self, min_votes_required=2):
        """
        Initialize the PoV consensus mechanism

        Args:
            min_votes_required (int): Minimum number of votes needed to approve a block
                                    Defaults to 2 votes for basic consensus
        """
        self.pending_blocks = []  # List to store blocks awaiting votes
        self.min_votes_required = min_votes_required

    def propose_block(self, chain, transactions, proposer):
        """
        Propose a new block for voting by consortium members

        Args:
            chain (list): The current blockchain
            transactions (list): List of transactions to include in the block
            proposer (str): Address of the member proposing the block

        Returns:
            dict: The newly created block with pending status
        """
        if not chain:
            raise ValueError("Chain cannot be empty - Genesis block required")

        block = {
            'index': len(chain) + 1,
            'timestamp': time(),
            'transactions': transactions,
            # Previous block must have a hash
            'previous_hash': chain[-1]['hash'],
            'proposer': proposer,
            'votes': [],
            'status': 'pending'
            # Hash will be set when block is approved
        }
        self.pending_blocks.append(block)
        return block

    def vote_for_block(self, block_index, voter_address, registered_members):
        """
        Record a member's vote for a pending block

        Args:
            block_index (int): Index of the block being voted on
            voter_address (str): Address of the voting member
            registered_members (list): List of all registered member addresses

        Returns:
            tuple: (block, approved) where block is the voted block and 
                  approved is True if block received enough votes

        Raises:
            ValueError: If voter is not a registered member
        """
        if voter_address not in registered_members:
            raise ValueError("Only registered members can vote")

        for block in self.pending_blocks:
            if block['index'] == block_index:
                # Prevent double voting
                if voter_address not in block['votes']:
                    block['votes'].append(voter_address)

                    # Check if block has received enough votes
                    if len(block['votes']) >= self.min_votes_required:
                        block['status'] = 'approved'
                        return block, True  # Block approved
                    return block, False  # Vote recorded, not yet approved
        return None, False  # Block not found

    def get_pending_blocks(self):
        """
        Get all blocks that are waiting for votes

        Returns:
            list: List of pending blocks
        """
        return self.pending_blocks

    def remove_block(self, block):
        """
        Remove a block from the pending list (called after block is approved)

        Args:
            block (dict): The block to remove from pending list
        """
        self.pending_blocks.remove(block)
