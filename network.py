"""
This file sets up the Flask web server to handle network communication.
It defines endpoints for creating new transactions, retrieving the blockchain, and managing membership.
"""

import logging
from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain
from membership import Membership

app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain and Membership
blockchain = Blockchain()
membership = Membership()

# Configure logging
logging.basicConfig(level=logging.DEBUG)


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    Endpoint to create a new transaction.
    """
    try:
        values = request.get_json()
        required = ['sender', 'recipient', 'amount']
        if not all(k in values for k in required):
            return 'Missing values', 400

        # Check if sender and recipient are registered members
        registered_members = [member['id']
                              for member in membership.get_members()]
        if values['sender'] not in registered_members or values['recipient'] not in registered_members:
            return jsonify({'message': 'Unauthorized: Sender or recipient is not a registered member'}), 403

        index = blockchain.new_transaction(
            values['sender'], values['recipient'], values['amount'])
        response = {'message': f'Transaction will be added to Block {index}'}
        return jsonify(response), 201
    except Exception as e:
        app.logger.error(f"Error during new transaction: {e}")
        return "Internal Server Error", 500


@app.route('/chain', methods=['GET'])
def full_chain():
    """
    Endpoint to return the full blockchain.
    """
    try:
        response = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain),
        }
        return jsonify(response), 200
    except Exception as e:
        app.logger.error(f"Error retrieving full chain: {e}")
        return "Internal Server Error", 500


@app.route('/membership/request', methods=['POST'])
def request_membership():
    """
    Endpoint to request membership.
    """
    try:
        values = request.get_json()
        required = ['id', 'name']
        if not all(k in values for k in required):
            return 'Missing values', 400
        membership_request = membership.request_membership(
            values['id'], values['name'])
        response = {'message': 'Membership request submitted',
                    'request': membership_request}
        return jsonify(response), 201
    except Exception as e:
        app.logger.error(f"Error during membership request: {e}")
        return "Internal Server Error", 500


@app.route('/membership/vote', methods=['POST'])
def vote_for_member():
    """
    Endpoint to vote for a membership request.
    """
    try:
        values = request.get_json()
        required = ['request_id', 'voter_id', 'action']
        if not all(k in values for k in required):
            return 'Missing values', 400
        app.logger.debug(f"Received vote request for: {values['request_id']} from voter: {
                         values['voter_id']} with action: {values['action']}")
        membership_request = membership.vote_for_member(
            values['request_id'], values['voter_id'], values['action'])
        if membership_request:
            response = {'message': 'Vote submitted',
                        'request': membership_request}
        else:
            response = {'message': 'Request not found'}
        return jsonify(response), 200
    except Exception as e:
        app.logger.error(f"Error during voting: {e}")
        return "Internal Server Error", 500


@app.route('/membership/members', methods=['GET'])
def get_members():
    """
    Endpoint to get the list of members.
    """
    try:
        status = request.args.get('status')
        if status == 'pending':
            response = {'requests': membership.get_requests(status='Pending')}
        elif status == 'rejected':
            response = {'requests': membership.get_requests(status='Rejected')}
        else:
            response = {'members': membership.get_members(status=status)}
        return jsonify(response), 200
    except Exception as e:
        app.logger.error(f"Error retrieving members: {e}")
        return "Internal Server Error", 500


@app.route('/membership/add', methods=['POST'])
def add_member():
    """
    Endpoint to manually add a member.
    """
    try:
        if len(membership.get_members()) > 0:
            return jsonify({'message': 'Manual addition of members is restricted to the first member only.'}), 403
        values = request.get_json()
        required = ['id', 'name']
        if not all(k in values for k in required):
            return 'Missing values', 400
        membership.add_member(values['id'], values['name'])
        response = {'message': 'Member added', 'member': {
            'id': values['id'], 'name': values['name']}}
        return jsonify(response), 201
    except Exception as e:
        app.logger.error(f"Error adding member: {e}")
        return "Internal Server Error", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
