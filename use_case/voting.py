from datetime import datetime
from uuid import uuid4


class Voting:
    def __init__(self):
        self.required_vote_fields = {
            'voter_address': str,
            'vote': str,
            'comments': str
        }
        self.allowed_votes = ['approve', 'reject', 'abstain']

    def submit_vote(self, proposal_id, vote_data):
        """Submit a vote for a proposal"""
        try:
            if self.validate_vote(vote_data):
                vote_data['vote_id'] = str(uuid4())
                vote_data['proposal_id'] = proposal_id
                vote_data['timestamp'] = datetime.utcnow().isoformat()
                return {'status': 'success', 'vote': vote_data}, 201
        except ValueError as e:
            return {'status': 'error', 'message': str(e)}, 400

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
