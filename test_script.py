from core.blockchain import Blockchain
from core.membership import Membership
from core.network import create_app
from use_case.proposal import Proposal
from use_case.review_process import ReviewProcess
from use_case.voting import Voting
from use_case.funding import Funding
from use_case.agreement import Agreement
from utilities.convert_to_ethereum_address import generate_ethereum_address
import json
import time


def test_green_lending_flow():
    print("\n=== Starting Green Lending Platform Test ===\n")

    # Initialize blockchain and components
    blockchain = Blockchain()
    membership = Membership(blockchain)  # Create membership instance
    blockchain.set_membership(membership)  # Set membership in blockchain

    proposal_handler = Proposal()
    review_handler = ReviewProcess()
    voting_handler = Voting()
    funding_handler = Funding()
    agreement_handler = Agreement()

    # Generate test addresses
    print("Generating test addresses...")
    lender = generate_ethereum_address()
    borrower = generate_ethereum_address()
    reviewer = generate_ethereum_address()

    print(f"Lender Address: {lender['address']}")
    print(f"Borrower Address: {borrower['address']}")
    print(f"Reviewer Address: {reviewer['address']}")

    # 1. Register members
    print("\n1. Registering members...")
    # Add lender
    lender_data = {
        "name": "Lender One",
        "role": "lender",
        "address": lender['address']
    }
    blockchain.membership.add_member(lender_data)

    # Add borrower
    borrower_data = {
        "name": "Borrower One",
        "role": "borrower",
        "address": borrower['address']
    }
    blockchain.membership.add_member(borrower_data)

    # Add reviewer
    reviewer_data = {
        "name": "Reviewer One",
        "role": "reviewer",
        "address": reviewer['address']
    }
    blockchain.membership.add_member(reviewer_data)

    print("Members registered successfully")

    # 2. Submit proposal
    print("\n2. Submitting proposal...")
    proposal_data = {
        "title": "Green Energy Project",
        "description": "Implementation of solar panels in residential areas",
        "objective": "To provide sustainable and cost-effective energy solutions",
        "funding_ask": 100000,
        "minimum_funding": 75000,
        "currency": "USD",
        "duration": "6 months",
        "notes": "Project includes installation costs",
        "documentation_url": "https://example.com/docs",
        "milestones": [
            {"phase": "Planning", "date": "2024-Q2"}
        ],
        "risk_assessment": {
            "technical_risks": "Medium"
        },
        "team_members": [
            {"name": "John Doe", "role": "Project Manager"}
        ],
        "expected_returns": {
            "roi": "15%"
        },
        "collateral": {
            "type": "Property",
            "value": "150000 USD"
        },
        "payment_schedule": [
            {"date": "2024-Q4", "amount": 25000}
        ],
        "project_schedule": {
            "start_date": "2024-01-15",
            "end_date": "2024-07-15"
        },
        "success_criteria": [
            {
                "criterion": "Energy Cost Reduction",
                "target": "30% reduction"
            },
            {
                "criterion": "Carbon Footprint",
                "target": "20% reduction"
            },
            {
                "criterion": "System Uptime",
                "target": "99.9%"
            }
        ]
    }

    response, status = proposal_handler.submit_proposal(proposal_data)
    proposal_id = response['proposal']['proposal_id']
    print(f"Proposal submitted with ID: {proposal_id}")

    # 3. Submit review
    print("\n3. Submitting review...")
    review_data = {
        "reviewer_address": reviewer['address'],
        "technical_assessment": {"score": 8, "comments": "Technically sound"},
        "financial_assessment": {"score": 7, "comments": "Financially viable"},
        "risk_assessment": {"score": 7, "comments": "Acceptable risk level"},
        "recommendation": "approve",
        "comments": "Recommend approval with standard monitoring"
    }

    review_handler.submit_review(proposal_id, review_data)
    print("Review submitted successfully")

    # 4. Submit votes
    print("\n4. Submitting votes...")
    vote_data = {
        "voter_address": lender['address'],
        "vote": "approve",
        "comments": "Project aligns with our green energy initiative"
    }

    voting_handler.submit_vote(proposal_id, vote_data)
    print("Vote submitted successfully")

    # 5. Submit funding
    print("\n5. Submitting funding...")
    funding_data = {
        "lender_address": lender['address'],
        "amount": 100000,
        "currency": "USD",
        "terms": {
            "interest_rate": "5%",
            "duration": "6 months",
            "payment_schedule": "quarterly"
        }
    }

    funding_handler.submit_funding(proposal_id, funding_data)
    print("Funding submitted successfully")

    # 6. Create agreement
    print("\n6. Creating agreement...")
    agreement_data = {
        "lender_address": lender['address'],
        "borrower_address": borrower['address'],
        "terms_and_conditions": {
            "interest_rate": "5%",
            "duration": "6 months",
            "total_amount": 100000
        },
        "payment_schedule": [
            {"date": "2024-Q4", "amount": 25000}
        ],
        "collateral_details": {
            "type": "Property",
            "value": "150000 USD"
        }
    }

    agreement_handler.create_agreement(proposal_id, agreement_data)
    print("Agreement created successfully")

    print("\n=== Test Completed Successfully ===")


if __name__ == "__main__":
    test_green_lending_flow()
