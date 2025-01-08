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
    def __init__(self, config):
        self.config = config
        self.current_proposal = None
        self.votes = {
            'approve': [],
            'reject': []
        }
        self.proposal_timestamp = None

        # Get config values directly from config
        self.vote_threshold = config['voting']['consensus']['threshold']

        # Convert timeout to seconds
        timeout_value = config['voting']['timeout']['value']
        timeout_unit = config['voting']['timeout']['unit']
        self.vote_timeout = self.convert_to_seconds(
            timeout_value, timeout_unit)

        # Convert auto-reject timeout to seconds
        if config['auto_reject']['enabled']:
            ar_timeout_value = config['auto_reject']['timeout']['value']
            ar_timeout_unit = config['auto_reject']['timeout']['unit']
            self.auto_reject_timeout = self.convert_to_seconds(
                ar_timeout_value, ar_timeout_unit)
        else:
            self.auto_reject_timeout = None

        print(f"\nInitialized ProofOfVote with:")
        print(f"Vote threshold: {self.vote_threshold}")
        print(f"Vote timeout: {self.vote_timeout} seconds")
        print(f"Auto-reject timeout: {self.auto_reject_timeout} seconds")

    def convert_to_seconds(self, value, unit):
        """Convert time units to seconds"""
        units = {
            'seconds': 1,
            'minutes': 60,
            'hours': 3600,
            'days': 86400
        }
        return value * units.get(unit.lower(), 1)

    def check_timeout(self):
        """Check if voting has timed out"""
        if not self.proposal_timestamp:
            return False

        elapsed_time = time.time() - self.proposal_timestamp

        # Check auto-reject first if enabled
        if self.auto_reject_timeout and elapsed_time > self.auto_reject_timeout:
            print(
                f"\nAuto-reject timeout reached after {elapsed_time} seconds")
            return 'auto_reject'

        # Then check voting timeout
        if elapsed_time > self.vote_timeout:
            print(f"\nVoting timeout reached after {elapsed_time} seconds")
            return 'vote_timeout'

        return False

    def check_consensus(self):
        """Check if consensus has been reached"""
        active_lenders = self.get_active_lenders()
        required_votes = len(active_lenders)
        total_votes = len(self.votes['approve']) + len(self.votes['reject'])

        print(f"\nChecking consensus:")
        print(f"Required votes: {required_votes}")
        print(f"Total votes: {total_votes}")
        print(f"Approve votes: {len(self.votes['approve'])}")
        print(f"Reject votes: {len(self.votes['reject'])}")

        # Check timeouts
        timeout_status = self.check_timeout()
        if timeout_status:
            if timeout_status == 'auto_reject':
                print("Auto-reject timeout reached. Proposal rejected.")
                return False
            elif timeout_status == 'vote_timeout':
                if total_votes > 0:
                    approve_percentage = len(
                        self.votes['approve']) / total_votes
                    print(f"Voting timed out. Deciding based on {
                          total_votes} votes cast")
                    print(f"Approve percentage: {approve_percentage}")
                    return approve_percentage >= self.vote_threshold
                else:
                    print("Voting timed out with no votes. Auto-rejecting.")
                    return False

        # If not timed out, check if all required votes received
        if total_votes >= required_votes:
            approve_percentage = len(self.votes['approve']) / total_votes
            print(f"All votes received. Approve percentage: {
                  approve_percentage}")
            return approve_percentage >= self.vote_threshold

        # Still waiting for votes
        print(f"Still waiting for {required_votes - total_votes} votes")
        return None

    def get_active_lenders(self):
        # Implementation of get_active_lenders method
        pass


class Consensus:
    def __init__(self):
        self.proof_of_vote = None
        self.current_block = None
        self.blockchain = None  # Will be set during initialize

    def initialize(self, config):
        """Initialize consensus with config"""
        self.config = config
        self.proof_of_vote = ProofOfVote(config)  # Pass config directly
        self.blockchain = self.blockchain

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
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

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

    def propose_block(self, chain, pending_transactions, block_data, members):
        """Propose a new block"""
        # Create block
        block = {
            'index': len(chain) + 1,
            'timestamp': time(),
            'data': block_data,
            # Use '1' for genesis block
            'previous_hash': self.hash_block(chain[-1]) if chain else '1',
            'status': 'pending'
        }

        # Initialize voting for this block
        if self.proof_of_vote:
            self.proof_of_vote.reset_votes()
        self.current_block = block

        return block

    def vote_for_block(self, block_index, voter_address, members):
        """Vote on a proposed block"""
        if not self.current_block:
            raise ValueError("No block currently proposed")

        # Add vote if ProofOfVote is initialized
        if self.proof_of_vote:
            self.proof_of_vote.add_vote(voter_address, {'action': 'approve'})

            # Check if consensus reached
            if self.proof_of_vote.check_consensus():
                self.current_block['status'] = 'approved'
                return self.current_block, True
        else:
            # Auto-approve if ProofOfVote not initialized (for genesis block)
            self.current_block['status'] = 'approved'
            return self.current_block, True

        return self.current_block, False
