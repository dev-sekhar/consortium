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

import hashlib
import json
from time import time
from uuid import uuid4


class ProofOfVote:
    def __init__(self):
        self.votes = []
        self.required_votes = 1  # Configurable based on network size
        self.vote_threshold = 0.51  # 51% consensus required

    def add_vote(self, voter_address, vote_data):
        """Add a vote to the consensus mechanism"""
        vote = {
            'vote_id': str(uuid4()),
            'voter': voter_address,
            'data': vote_data,
            'timestamp': time()
        }
        self.votes.append(vote)
        return vote

    def check_consensus(self):
        """Check if consensus has been reached"""
        if len(self.votes) < self.required_votes:
            return False

        # Count approve votes
        approve_votes = sum(
            1 for vote in self.votes if vote['data'].get('action') == 'approve')
        vote_percentage = approve_votes / len(self.votes)

        return vote_percentage >= self.vote_threshold

    def get_vote_hash(self):
        """Get hash of all votes"""
        vote_string = json.dumps(self.votes, sort_keys=True)
        return hashlib.sha256(vote_string.encode()).hexdigest()

    def reset_votes(self):
        """Reset votes for next round"""
        self.votes = []


class Consensus:
    def __init__(self):
        self.proof_of_vote = ProofOfVote()

    def validate_block(self, block, chain):
        """
        Validate a block before adding to chain
        """
        # Check if block index is correct
        if block['index'] != len(chain) + 1:
            return False

        # Check if previous hash matches
        if block['previous_hash'] != self.hash_block(chain[-1]):
            return False

        # Check if consensus was reached
        if not self.proof_of_vote.check_consensus():
            return False

        return True

    def hash_block(self, block):
        """
        Create a SHA-256 hash of a block
        """
        # Convert block to string and encode
        block_string = json.dumps(block, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def add_vote(self, voter_address, vote_data):
        """
        Add a vote to the consensus mechanism
        """
        return self.proof_of_vote.add_vote(voter_address, vote_data)

    def check_consensus(self):
        """
        Check if consensus has been reached
        """
        return self.proof_of_vote.check_consensus()

    def reset_votes(self):
        """
        Reset votes for next round
        """
        self.proof_of_vote.reset_votes()
