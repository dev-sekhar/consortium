from decimal import Decimal


class Proposal:
    def __init__(self):
        self.required_fields = {
            'title': str,
            'description': str,
            'funding_ask': Decimal,
            'minimum_funding': Decimal,
            'currency': str,
            'objective': str,
            'duration': str,
            'notes': str
        }
        self.allowed_currencies = ['USD', 'EUR', 'GBP', 'JPY']

    def validate_proposal(self, proposal_details):
        """
        Validate the proposal details
        """
        # Check all required fields are present
        for field, field_type in self.required_fields.items():
            if field not in proposal_details:
                raise ValueError(f"Missing required field: {field}")

            # Check field type
            if field in ['funding_ask', 'minimum_funding']:
                try:
                    value = Decimal(str(proposal_details[field]))
                    if value <= 0:
                        raise ValueError(f"{field} must be greater than 0")
                except:
                    raise ValueError(f"{field} must be a valid number")
            else:
                if not isinstance(proposal_details[field], field_type):
                    raise ValueError(f"{field} must be of type {
                                     field_type.__name__}")

        # Validate currency
        if proposal_details['currency'] not in self.allowed_currencies:
            raise ValueError(f"Currency must be one of: {
                             ', '.join(self.allowed_currencies)}")

        # Validate minimum funding is less than or equal to funding ask
        if Decimal(str(proposal_details['minimum_funding'])) > Decimal(str(proposal_details['funding_ask'])):
            raise ValueError(
                "Minimum funding cannot be greater than funding ask")

        # Validate title and description length
        if len(proposal_details['title']) < 5 or len(proposal_details['title']) > 100:
            raise ValueError("Title must be between 5 and 100 characters")

        if len(proposal_details['description']) < 50 or len(proposal_details['description']) > 5000:
            raise ValueError(
                "Description must be between 50 and 5000 characters")

        if len(proposal_details['objective']) < 50 or len(proposal_details['objective']) > 1000:
            raise ValueError(
                "Objective must be between 50 and 1000 characters")

        return True
