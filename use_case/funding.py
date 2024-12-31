from datetime import datetime
from decimal import Decimal
from uuid import uuid4


class Funding:
    def __init__(self):
        self.required_funding_fields = {
            'lender_address': str,
            'amount': Decimal,
            'currency': str,
            'terms': dict
        }

    def submit_funding(self, proposal_id, funding_data):
        """Submit funding for a proposal"""
        try:
            if self.validate_funding(funding_data):
                funding_data['funding_id'] = str(uuid4())
                funding_data['proposal_id'] = proposal_id
                funding_data['timestamp'] = datetime.utcnow().isoformat()
                return {'status': 'success', 'funding': funding_data}, 201
        except ValueError as e:
            return {'status': 'error', 'message': str(e)}, 400

    def validate_funding(self, funding_data):
        """Validate funding data"""
        for field, field_type in self.required_funding_fields.items():
            if field not in funding_data:
                raise ValueError(f"Missing required field: {field}")
            if field == 'amount':
                try:
                    value = Decimal(str(funding_data[field]))
                    if value <= 0:
                        raise ValueError("Amount must be greater than 0")
                except:
                    raise ValueError("Amount must be a valid number")
            elif not isinstance(funding_data[field], field_type):
                raise ValueError(f"{field} must be of type {
                                 field_type.__name__}")
        return True
