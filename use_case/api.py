from flask import Blueprint, jsonify, request
from core.blockchain import Blockchain
from core.membership import Membership
from .proposal import Proposal
from .review_process import ReviewProcess
from .voting import Voting
from .funding import Funding
from .agreement import Agreement
from utilities.convert_to_ethereum_address import generate_ethereum_address
from use_case.smart_contracts.member_auto_reject import MemberAutoRejectContract

api = Blueprint('api', __name__)
blockchain = Blockchain()
membership = Membership(blockchain)
blockchain.set_membership(membership)

# Initialize auto-reject contract
auto_reject_contract = MemberAutoRejectContract(membership)

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
def vote_on_request():
    """Vote on a membership request"""
    data = request.get_json()

    # Validate required fields
    required_fields = ['request_id', 'voter_address', 'action']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields',
            'required_fields': required_fields
        }), 400

    try:
        result = membership.vote_on_request(
            request_id=data['request_id'],
            voter_address=data['voter_address'],
            action=data['action']
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api.route('/membership/request/<request_id>/status', methods=['GET'])
def get_request_status(request_id):
    """Get the status of a specific membership request"""
    try:
        # Check in pending requests first
        request = next(
            (req for req in membership.get_pending_requests()
             if req['request_id'] == request_id),
            None
        )

        # If not in pending, check in rejected requests
        if not request:
            request = next(
                (req for req in membership.get_rejected_requests()
                 if req['request_id'] == request_id),
                None
            )

        if not request:
            return jsonify({
                'error': 'Request not found',
                'request_id': request_id
            }), 404

        # Get auto-reject status
        status = auto_reject_contract.get_request_status(request_id)

        # Combine request data with auto-reject status
        response = {
            'request_id': request_id,
            'status': request['status'],
            'name': request['name'],
            'role': request['role'],
            'address': request['address'],
            'timestamp': request['timestamp'],
            'reminder_sent': request.get('reminder_sent', False),
            'reminder_time': request.get('reminder_time'),
            'auto_reject_info': status
        }

        if 'update_time' in request:
            response['update_time'] = request['update_time']
        if 'update_reason' in request:
            response['update_reason'] = request['update_reason']

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/membership/debug/requests', methods=['GET'])
def debug_requests():
    """Debug endpoint to see all requests in the system"""
    return jsonify({
        'pending': membership.get_pending_requests(),
        'active': membership.get_members(),
        'rejected': membership.get_rejected_requests(),
        'total_count': {
            'pending': len(membership.get_pending_requests()),
            'active': len(membership.get_members()),
            'rejected': len(membership.get_rejected_requests())
        }
    }), 200

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
