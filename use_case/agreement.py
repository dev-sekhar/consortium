from datetime import datetime
from uuid import uuid4


class Agreement:
    def __init__(self):
        self.required_agreement_fields = {
            'lender_address': str,
            'borrower_address': str,
            'terms_and_conditions': dict,
            'payment_schedule': list,
            'collateral_details': dict
        }

    def create_agreement(self, proposal_id, agreement_data):
        """Create a new agreement for a funded proposal"""
        try:
            if self.validate_agreement(agreement_data):
                agreement_data['agreement_id'] = str(uuid4())
                agreement_data['proposal_id'] = proposal_id
                agreement_data['status'] = 'pending_signatures'
                agreement_data['created_at'] = datetime.utcnow().isoformat()
                return {'status': 'success', 'agreement': agreement_data}, 201
        except ValueError as e:
            return {'status': 'error', 'message': str(e)}, 400

    def get_agreement(self, proposal_id):
        """Get agreement details for a proposal"""
        # This would typically fetch from blockchain/database
        # Placeholder for demonstration
        return {'status': 'success', 'agreement': None}, 200

    def validate_agreement(self, agreement_data):
        """Validate agreement data"""
        for field, field_type in self.required_agreement_fields.items():
            if field not in agreement_data:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(agreement_data[field], field_type):
                raise ValueError(f"{field} must be of type {
                                 field_type.__name__}")
        return True
