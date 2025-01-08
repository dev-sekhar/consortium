class MembershipVoting:
    def __init__(self):
        self.member_votes = {}  # Track votes per member
        self.required_vote_fields = {
            'voter_address': str,
            'vote': str
        }
        self.allowed_votes = ['approve', 'reject']

    def cast_vote(self, member_address, voter_data, active_members):
        """Cast a vote for a member

        Args:
            member_address: Address of member being voted on
            voter_data: Dict containing voter_address and vote
            active_members: List of currently active members
        """
        try:
            if not self.validate_vote(voter_data):
                raise ValueError("Invalid vote data")

            if member_address not in self.member_votes:
                self.member_votes[member_address] = {
                    'votes': {},
                    'required_votes': (len(active_members) // 2) + 1
                }

            voter_address = voter_data['voter_address']
            if voter_address in self.member_votes[member_address]['votes']:
                raise ValueError("Member has already voted")

            self.member_votes[member_address]['votes'][voter_address] = voter_data['vote']

            vote_count = len([v for v in self.member_votes[member_address]['votes'].values()
                              if v == 'approve'])

            return {
                'member_address': member_address,
                'votes_received': vote_count,
                'required_votes': self.member_votes[member_address]['required_votes'],
                'has_passed': vote_count >= self.member_votes[member_address]['required_votes']
            }

        except Exception as e:
            raise ValueError(f"Failed to cast vote: {str(e)}")

    def validate_vote(self, vote_data):
        """Validate vote data"""
        for field, field_type in self.required_vote_fields.items():
            if field not in vote_data:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(vote_data[field], field_type):
                raise ValueError(f"{field} must be of type {
                                 field_type.__name__}")

        if vote_data['vote'].lower() not in self.allowed_votes:
            raise ValueError(f"Vote must be one of: {
                             ', '.join(self.allowed_votes)}")
        return True

    def get_vote_status(self, member_address):
        """Get current voting status for a member"""
        if member_address not in self.member_votes:
            raise ValueError("No votes found for this member")

        votes = self.member_votes[member_address]
        approve_count = len(
            [v for v in votes['votes'].values() if v == 'approve'])

        return {
            'total_votes': len(votes['votes']),
            'approve_votes': approve_count,
            'required_votes': votes['required_votes'],
            'has_passed': approve_count >= votes['required_votes']
        }
