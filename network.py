"""
This file sets up the Flask web server to handle network communication.
It defines endpoints for creating new transactions, retrieving the blockchain, and managing membership.
"""

import logging
import argparse
import socket
from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain
from membership import Membership
from convert_to_ethereum_address import convert_to_ethereum_address
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import requests


def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def verify_member_authorization(address):
    """Verify if the member is authorized to connect to the network"""
    try:
        # Try to connect to the main node
        response = requests.get(f'http://localhost:5000/membership/members')
        if response.status_code == 200:
            members = response.json().get('members', [])
            return any(member['address'] == address for member in members)
    except requests.exceptions.RequestException:
        return False
    return False


def create_app(port, member_address=None):
    app = Flask(__name__)

    # Generate a globally unique address for this node
    node_identifier = str(uuid4()).replace('-', '')

    # For port 5000 (main node), initialize new blockchain
    # For other ports, connect to existing network
    if port == 5000:
        if is_port_in_use(5000):
            raise ValueError(
                "Port 5000 is already in use. Only one main node can run on port 5000.")

        blockchain = Blockchain()
        membership = Membership(blockchain)
        blockchain.set_membership(membership)
        logger.info(f"Initialized main node on port {port}")
    else:
        if not member_address:
            raise ValueError("Member address is required for non-main nodes")

        if not verify_member_authorization(member_address):
            raise ValueError(
                "Unauthorized member. Only registered members can connect to the network.")

        # Connect to existing network
        blockchain = Blockchain()
        membership = Membership(blockchain)
        blockchain.set_membership(membership)
        logger.info(
            f"Connected to network as authorized member on port {port}")

    # Initialize components properly to avoid circular dependency
    blockchain = Blockchain()
    membership = Membership(blockchain)
    blockchain.set_membership(membership)

    @app.route('/block/new', methods=['GET'])
    def new_block():
        # Create a new Block
        previous_hash = blockchain.hash(blockchain.last_block)
        block = blockchain.new_block(previous_hash)

        response = {
            'message': "New Block Created",
            'index': block['index'],
            'transactions': block['transactions'],
            'previous_hash': block['previous_hash'],
        }
        return jsonify(response), 200

    @app.route('/transactions/new', methods=['POST'])
    def new_transaction():
        values = request.get_json()

        # Debug print
        print("Received values:", values)

        # Check if we received any data
        if not values:
            return 'No data received', 400

        # Check the required fields based on transaction type
        if 'type' in values and values['type'] == 'submit_proposal':
            required = ['type', 'sender', 'proposal_details']
        else:
            required = ['sender', 'recipient', 'amount']

        # Check which required fields are missing
        missing_fields = [field for field in required if field not in values]
        if missing_fields:
            return f'Missing required fields: {", ".join(missing_fields)}', 400

        try:
            # Create a new Transaction
            transaction = blockchain.transaction_manager.create_transaction(
                sender=values['sender'],
                recipient=values.get('recipient'),  # Optional for proposals
                amount=values.get('amount'),        # Optional for proposals
                type=values.get('type'),
                proposal_details=values.get('proposal_details')
            )
        except ValueError as e:
            return str(e), 400
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return f"Server error: {str(e)}", 500

        response = {
            'message': f'Transaction will be added to Block {transaction}'}
        return jsonify(response), 201

    @app.route('/membership/add', methods=['POST'])
    def add_first_member():
        values = request.get_json()
        required = ['name', 'role']
        if not all(k in values for k in required):
            return 'Missing values', 400

        try:
            member = blockchain.membership.add_first_member(
                values['name'], values['role'])
            response = {
                'message': 'First member added',
                'member': member
            }
            return jsonify(response), 201
        except ValueError as e:
            return str(e), 400

    @app.route('/membership/request', methods=['POST'])
    def request_membership():
        values = request.get_json()
        required = ['name', 'role']
        if not all(k in values for k in required):
            return 'Missing values', 400

        try:
            membership_request = blockchain.membership.request_membership(
                values['name'],
                values['role']
            )
            response = {
                'message': 'Membership requested',
                'request': membership_request
            }
            return jsonify(response), 201
        except ValueError as e:
            return str(e), 400

    @app.route('/membership/addresses', methods=['GET'])
    def get_addresses():
        try:
            addresses = membership.get_addresses()
            response = {
                'addresses': addresses
            }
            return jsonify(response), 200
        except Exception as e:
            app.logger.error(f"Error retrieving member addresses: {e}")
            return "Internal Server Error", 500

    @app.route('/membership/vote', methods=['POST'])
    def vote_for_member():
        values = request.get_json()

        # Check that the required fields are in the POST'ed data
        required = ['request_address', 'voter_address', 'action']
        if not all(k in values for k in required):
            return 'Missing values', 400

        try:
            # Changed from vote_for_member to vote_on_request
            result = membership.vote_on_request(
                values['request_address'],
                values['voter_address'],
                values['action']
            )
            response = {'message': 'Vote recorded', 'request': result}
            return jsonify(response), 200
        except Exception as e:
            app.logger.error(f"Error voting for member: {e}")
            return "Internal Server Error", 500

    @app.route('/chain', methods=['GET'])
    def full_chain():
        response = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain),
        }
        return jsonify(response), 200

    @app.route('/membership/members', methods=['GET'])
    def get_members():
        status = request.args.get('status')
        if status:
            # Filter members/requests by status
            if status == 'pending':
                members = [req['request']
                           for req in membership.requests if req['request']['status'] == 'Pending']
            elif status == 'rejected':
                members = [req['request']
                           for req in membership.requests if req['request']['status'] == 'Rejected']
            else:
                members = membership.members
        else:
            members = membership.members

        return jsonify({'members': members}), 200

    @app.route('/block/propose', methods=['POST'])
    def propose_block():
        values = request.get_json()
        proposer = values.get('proposer')

        try:
            block = blockchain.propose_block(proposer)
            response = {
                'message': 'New block proposed',
                'block': block
            }
            return jsonify(response), 201
        except ValueError as e:
            return str(e), 400

    @app.route('/block/vote', methods=['POST'])
    def vote_block():
        values = request.get_json()

        required = ['block_index', 'voter_address']
        if not all(k in values for k in required):
            return 'Missing values', 400

        try:
            block = blockchain.vote_for_block(
                values['block_index'],
                values['voter_address']
            )

            response = {
                'message': 'Vote recorded',
                'block': block
            }
            return jsonify(response), 200
        except ValueError as e:
            return str(e), 400

    @app.route('/block/pending', methods=['GET'])
    def get_pending_blocks():
        blocks = blockchain.consensus.get_pending_blocks()
        return jsonify({'pending_blocks': blocks}), 200

    @app.route('/transactions/pending', methods=['GET'])
    def get_pending_transactions():
        """
        Get all pending transactions that haven't been added to a block yet
        """
        pending_transactions = blockchain.transaction_manager.get_pending_transactions()
        return jsonify({
            'pending_transactions': pending_transactions,
            'count': len(pending_transactions)
        }), 200

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start the blockchain node.')
    parser.add_argument('-p', '--port', type=int, default=5000,
                        help='Port to run the server on (default: 5000)')
    parser.add_argument('-a', '--address', type=str,
                        help='Member address (required for non-main nodes)')

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger(__name__)

    try:
        app = create_app(args.port, args.address)
        logger.info(f'Starting blockchain node on port {args.port}')
        app.run(host='0.0.0.0', port=args.port)
    except ValueError as e:
        logger.error(str(e))
        exit(1)
