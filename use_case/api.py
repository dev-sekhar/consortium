from flask import Blueprint, jsonify, request
from core.blockchain import Blockchain
from core.membership import Membership
from .proposal import Proposal
from .review_process import ReviewProcess
from .voting import Voting
from .funding import Funding
from .agreement import Agreement
from utilities.convert_to_ethereum_address import generate_ethereum_address

api = Blueprint('api', __name__)
blockchain = Blockchain()
membership = Membership(blockchain)
blockchain.set_membership(membership)

# Membership Routes


@api.route('/membership/add', methods=['POST'])
def add_member():
    # Check if there are any existing members
    existing_members = membership.get_members()
    if len(existing_members) > 0:
        return jsonify({
            'message': 'First member already exists. Please use /membership/request for new members.',
            'error': 'Method not allowed for subsequent members'
        }), 405

    values = request.get_json()
    required = ['name', 'role']
    if not all(k in values for k in required):
        return 'Missing values', 400

    result = membership.add_member(values)
    response = {
        'message': 'First member added',
        'member': result['member'],
        'private_key': result['private_key']
    }
    return jsonify(response), 201


@api.route('/membership/members', methods=['GET'])
def get_members():
    response = {
        'members': membership.get_members()
    }
    return jsonify(response), 200


@api.route('/membership/request', methods=['POST'])
def request_membership():
    values = request.get_json()
    required = ['name', 'role']
    if not all(k in values for k in required):
        return 'Missing values', 400

    result = membership.request_membership(values)
    response = {
        'message': 'Membership requested',
        'request': result['request'],
        'private_key': result['private_key']
    }
    return jsonify(response), 201


@api.route('/membership/pending_requests', methods=['GET'])
def get_membership_requests():
    response = {
        'requests': membership.get_pending_requests()
    }
    return jsonify(response), 200


@api.route('/membership/vote', methods=['POST'])
def vote_on_membership():
    values = request.get_json()
    required = ['request_address', 'voter_address', 'action']
    if not all(k in values for k in required):
        return 'Missing values', 400

    result = membership.vote_on_request(
        request_id=values['request_address'],
        voter_address=values['voter_address'],
        action=values['action']
    )
    response = {
        'message': 'Vote recorded',
        'request': result
    }
    return jsonify(response), 200

# Existing Proposal Routes


@api.route('/proposals', methods=['GET', 'POST'])
def handle_proposals():
    if request.method == 'POST':
        return Proposal().submit_proposal(request.get_json())
    else:
        status = request.args.get('status')
        return Proposal().get_proposals(status)


@api.route('/proposals/<proposal_id>/review', methods=['POST'])
def review_proposal(proposal_id):
    return ReviewProcess().submit_review(proposal_id, request.get_json())


@api.route('/proposals/<proposal_id>/vote', methods=['POST'])
def vote_proposal(proposal_id):
    return Voting().submit_vote(proposal_id, request.get_json())


@api.route('/proposals/<proposal_id>/fund', methods=['POST'])
def fund_proposal(proposal_id):
    return Funding().submit_funding(proposal_id, request.get_json())


@api.route('/agreements/<proposal_id>', methods=['GET', 'POST'])
def handle_agreements(proposal_id):
    if request.method == 'POST':
        return Agreement().create_agreement(proposal_id, request.get_json())
    else:
        return Agreement().get_agreement(proposal_id)


def create_api():
    return api
