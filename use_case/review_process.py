from datetime import datetime
from uuid import uuid4


class ReviewProcess:
    def __init__(self):
        self.required_review_fields = {
            'reviewer_address': str,
            'technical_assessment': dict,
            'financial_assessment': dict,
            'risk_assessment': dict,
            'recommendation': str,
            'comments': str
        }

    def submit_review(self, proposal_id, review_data):
        """Submit a review for a proposal"""
        try:
            if self.validate_review(review_data):
                review_data['review_id'] = str(uuid4())
                review_data['proposal_id'] = proposal_id
                review_data['timestamp'] = datetime.utcnow().isoformat()
                return {'status': 'success', 'review': review_data}, 201
        except ValueError as e:
            return {'status': 'error', 'message': str(e)}, 400

    def validate_review(self, review_data):
        """Validate review data"""
        for field, field_type in self.required_review_fields.items():
            if field not in review_data:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(review_data[field], field_type):
                raise ValueError(f"{field} must be of type {
                                 field_type.__name__}")
        return True
