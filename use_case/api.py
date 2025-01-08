from flask import Blueprint, request, jsonify
from core.blockchain import Blockchain
from core.membership import Membership
from use_case.proposal import Proposal


def create_api(membership):
    """Create the API blueprint"""
    api = Blueprint('api', __name__)

    @api.route('/membership/add', methods=['POST'])
    def add_member():
        """Add a new member"""
        try:
            data = request.get_json()
            if not data or 'name' not in data or 'role' not in data:
                return jsonify({
                    'status': 'error',
                    'error': 'Name and role are required'
                }), 400

            member = membership.add_member(data['name'], data['role'])
            return jsonify({
                'status': 'success',
                'member': member
            }), 200

        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500

    @api.route('/membership/list', methods=['GET'])
    def list_members():
        """List all members"""
        try:
            members = membership.get_members()
            return jsonify(members), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500

    @api.route('/membership/approve/<address>', methods=['POST'])
    def approve_member(address):
        """Approve a pending member request"""
        try:
            data = request.get_json()
            if not data or 'approver_address' not in data:
                return jsonify({
                    'status': 'error',
                    'error': 'Approver address is required'
                }), 400

            # Add debug logging
            print(f"\nApproval request:")
            print(f"Member address: {address}")
            print(f"Approver address: {data['approver_address']}")

            result = membership.approve_member(
                address, data['approver_address'])

            # Add debug logging
            print(f"Approval result: {result}")

            return jsonify({
                'status': 'success',
                'result': result
            }), 200

        except Exception as e:
            import traceback
            print(f"\nError in approve_member:")
            print(traceback.format_exc())
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500

    @api.route('/membership/reject/<address>', methods=['POST'])
    def reject_member(address):
        """Reject a pending member request"""
        try:
            data = request.get_json()
            if not data or 'approver_address' not in data:
                return jsonify({
                    'status': 'error',
                    'error': 'Approver address is required'
                }), 400

            # Add debug logging
            print(f"\nRejection request:")
            print(f"Member address: {address}")
            print(f"Approver address: {data['approver_address']}")

            result = membership.reject_member(
                address, data['approver_address'])

            return jsonify({
                'status': 'success',
                'result': result
            }), 200

        except Exception as e:
            import traceback
            print(f"\nError in reject_member:")
            print(traceback.format_exc())
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500

    @api.route('/membership/clear', methods=['DELETE'])
    def clear_members():
        """Clear all members from the system"""
        try:
            result = membership.clear_all_members()
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500

    return api  # Return just the blueprint, not a tuple
