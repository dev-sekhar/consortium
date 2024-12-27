"""
This file sets up the Flask web server to handle network communication.
It defines endpoints for creating new transactions, retrieving the blockchain, and managing membership.
"""

import logging
from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain
from membership import Membership
from convert_to_ethereum_address import convert_to_ethereum_address
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# Instantiate the Membership with the same blockchain instance
membership = Membership(blockchain)


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

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    try:
        # Create a new Transaction
        index = blockchain.new_transaction(
            values['sender'], values['recipient'], values['amount'])
        response = {'message': f'Transaction will be added to Block {index}'}
        return jsonify(response), 201
    except ValueError as e:
        response = {'message': str(e)}
        return jsonify(response), 400


@app.route('/membership/add', methods=['POST'])
def add_member():
    values = request.get_json()

    # Check that the required field is in the POST'ed data
    required = ['name']
    if not all(k in values for k in required):
        return 'Missing name', 400

    # Add the new member
    member = membership.add_member(values['name'])

    response = {
        'message': 'Member added',
        'member': member
    }
    return jsonify(response), 201


@app.route('/membership/request', methods=['POST'])
def request_membership():
    values = request.get_json()

    # Check that the required field is in the POST'ed data
    required = ['name']
    if not all(k in values for k in required):
        return 'Missing name', 400

    # Create a new membership request
    membership_request = membership.request_membership(values['name'])

    response = {
        'message': 'Membership request created',
        'request': membership_request
    }
    return jsonify(response), 201


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
        # Vote for the membership request
        result = membership.vote_for_member(
            values['request_address'], values['voter_address'], values['action'])
        if result:
            response = {'message': 'Vote recorded', 'request': result}
            return jsonify(response), 200
        else:
            response = {'message': 'Invalid vote or request not found'}
            return jsonify(response), 400
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


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port=5000)
