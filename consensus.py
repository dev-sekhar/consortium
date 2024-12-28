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

    def propose_block(self, chain, transactions, proposer, membership):
        """
        Propose a new block for voting
        """
        if not membership.has_permission(proposer, 'propose_block'):
            raise ValueError(
                "Member does not have permission to propose blocks")

        block = {
            'index': len(chain) + 1,
            'timestamp': time(),
            'transactions': transactions,
            'previous_hash': chain[-1]['hash'] if chain else None,
            'proposer': proposer,
            'votes': [],
            'status': 'pending',
            'hash': None
        }
        self.pending_blocks.append(block)
        return block

    def vote_for_block(self, block_index, voter_address, membership):
        """
        Record a vote for a pending block
        """
        if not membership.has_permission(voter_address, 'vote_on_block'):
            raise ValueError(
                "Member does not have permission to vote on blocks")

        for block in self.pending_blocks:
            if block['index'] == block_index:
                if voter_address not in block['votes']:
                    block['votes'].append(voter_address)

                    if len(block['votes']) >= self.min_votes_required:
                        block['status'] = 'approved'
                        return block, True
                    return block, False
        return None, False

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
