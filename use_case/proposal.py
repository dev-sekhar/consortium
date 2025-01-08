from decimal import Decimal
from uuid import uuid4
from datetime import datetime
import re
import json


class Proposal:
    def __init__(self):
        # Load configuration
        with open('use_case/proposal_config.json', 'r') as config_file:
            self.config = json.load(config_file)

        self.required_fields = {
            'title': str,                  # Title of the project
            'description': str,            # Detailed description
            'funding_ask': Decimal,        # Amount requested
            'minimum_funding': Decimal,    # Minimum funding needed
            'currency': str,               # Currency (USD, EUR, GBP, JPY)
            'objective': str,              # Project objectives
            'duration': str,               # Project duration
            'notes': str,                  # Additional notes
            'milestones': list,           # List of project milestones with dates
            'risk_assessment': dict,       # Risk analysis and mitigation strategies
            'team_members': list,          # List of team members and their roles
            'expected_returns': dict,      # Expected ROI and financial projections
            'collateral': dict,           # Collateral details and valuation
            'payment_schedule': list,      # Proposed repayment schedule
            'project_schedule': dict,      # Detailed project timeline and phases
            'success_criteria': list,      # List of measurable success criteria
            'documentation_url': str       # URL to additional documentation
        }
        self.allowed_currencies = self.config['currencies']['allowed']
        self.proposals = []  # Initialize empty list to store proposals

    def submit_proposal(self, data):
        """Submit a new proposal"""
        proposal = {
            **data,
            'proposal_id': str(uuid4()),
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        self.proposals.append(proposal)  # Add to proposals list
        return proposal

    def get_proposals(self):
        """Get all proposals"""
        return self.proposals  # Return the list of proposals

    def validate_proposal(self, proposal_details):
        """
        Validate and enrich the proposal details with a unique ID
        """
        # Add unique proposal ID
        proposal_details['proposal_id'] = str(uuid4())

        # Validate fields
        for field, field_type in self.required_fields.items():
            if field not in proposal_details:
                raise ValueError(f"Missing required field: {field}")

            # Check field type
            if field in ['funding_ask', 'minimum_funding']:
                try:
                    value = Decimal(str(proposal_details[field]))
                    min_amount = self.config['validation_rules']['funding']['min_amount']
                    max_amount = self.config['validation_rules']['funding']['max_amount']
                    if value < min_amount or value > max_amount:
                        raise ValueError(f"{field} must be between {
                                         min_amount} and {max_amount}")
                except:
                    raise ValueError(f"{field} must be a valid number")
            elif field in ['milestones', 'team_members', 'payment_schedule', 'success_criteria']:
                if not isinstance(proposal_details[field], list):
                    raise ValueError(f"{field} must be a list")
                if field == 'success_criteria':
                    min_count = self.config['validation_rules']['success_criteria']['min_count']
                    if len(proposal_details[field]) < min_count:
                        raise ValueError(
                            f"At least {min_count} success criteria must be defined")
            elif field in ['risk_assessment', 'expected_returns', 'collateral', 'project_schedule']:
                if not isinstance(proposal_details[field], dict):
                    raise ValueError(f"{field} must be a dictionary")

        # Validate text field lengths
        for field in ['title', 'description', 'objective']:
            min_len = self.config['validation_rules'][field]['min_length']
            max_len = self.config['validation_rules'][field]['max_length']
            if len(proposal_details[field]) < min_len or len(proposal_details[field]) > max_len:
                raise ValueError(f"{field} must be between {
                                 min_len} and {max_len} characters")

        # Validate project schedule duration
        schedule = proposal_details['project_schedule']
        try:
            start_date = datetime.strptime(schedule['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(schedule['end_date'], '%Y-%m-%d')
            duration_str = proposal_details['duration'].lower()

            # Convert duration string to months
            if 'month' in duration_str:
                max_months = int(duration_str.split()[0])
            elif 'year' in duration_str:
                max_months = int(duration_str.split()[0]) * 12
            else:
                raise ValueError(
                    "Duration must be specified in months or years")

            # Calculate actual duration in months
            actual_months = ((end_date.year - start_date.year)
                             * 12) + (end_date.month - start_date.month)

            if actual_months > max_months:
                raise ValueError(
                    "Project schedule duration exceeds specified project duration")

        except ValueError as e:
            raise ValueError(f"Invalid project schedule: {str(e)}")

        # Validate currency
        if proposal_details['currency'] not in self.allowed_currencies:
            raise ValueError(f"Currency must be one of: {
                             ', '.join(self.allowed_currencies)}")

        # Validate minimum funding is less than or equal to funding ask
        if Decimal(str(proposal_details['minimum_funding'])) > Decimal(str(proposal_details['funding_ask'])):
            raise ValueError(
                "Minimum funding cannot be greater than funding ask")

        return True
