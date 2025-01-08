"""
This file sets up the Flask web server to handle network communication.
It defines endpoints for creating new transactions, retrieving the blockchain, and managing membership.
"""

import logging
import argparse
import socket
import json
import requests
from flask import Flask, jsonify, request
from uuid import uuid4
from core.blockchain import Blockchain
from core.membership import Membership
from use_case.api import create_api
from utilities.convert_to_ethereum_address import generate_ethereum_address, validate_ethereum_address
import os
import threading
import time as timestamp

# Configure logging
logger = logging.getLogger(__name__)

# Load network configuration
with open('core/network_config.json', 'r') as config_file:
    network_config = json.load(config_file)


def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def verify_member_authorization(address):
    """Verify if the member is authorized to connect to the network"""
    if not validate_ethereum_address(address):
        return False
    try:
        main_port = network_config['main_node']['port']
        endpoint = network_config['endpoints']['membership']
        response = requests.get(f'http://localhost:{main_port}{endpoint}')
        if response.status_code == 200:
            members = response.json().get('members', [])
            return any(member['address'] == address for member in members)
    except requests.exceptions.RequestException:
        return False
    return False


def create_app(blockchain=None, membership=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Import api creation here to avoid circular import
    from use_case.api import create_api

    # Create and register the API blueprint
    api = create_api(membership)
    app.register_blueprint(api)

    return app


class Network:
    def __init__(self):
        self.app = Flask(__name__)
        self.load_config()
        self.blockchain = Blockchain(self.config)
        self.membership = Membership(self.blockchain)

        # Register routes
        self.register_routes()

        # Start block creation thread
        self.start_block_creation_thread()

    def convert_to_seconds(self, value, unit):
        """Convert time units to seconds"""
        units = {
            'seconds': 1,
            'minutes': 60,
            'hours': 3600,
            'days': 86400
        }
        return value * units.get(unit.lower(), 1)

    def start_monitoring(self):
        """Start the monitoring thread for pending requests"""
        monitor_thread = threading.Thread(
            target=self.membership.monitor_pending_requests,
            daemon=True  # Make thread daemon so it exits when main thread exits
        )
        monitor_thread.start()
        print("Started monitoring thread for pending requests")

    def register_routes(self):
        """Register all API endpoints"""

        # Chain endpoint
        @self.app.route('/chain', methods=['GET'])
        def get_chain():
            try:
                chain_data = {
                    'chain': self.blockchain.chain,
                    'length': len(self.blockchain.chain)
                }
                return jsonify(chain_data)
            except Exception as e:
                print(f"Error getting chain: {str(e)}")
                return jsonify({'error': str(e)}), 500

        # Member management endpoints
        @self.app.route('/membership/add', methods=['POST'])
        def add_member():
            try:
                data = request.get_json()
                if not data or 'name' not in data or 'role' not in data:
                    return jsonify({'error': 'Missing name or role'}), 400

                member = self.membership.add_member(data['name'], data['role'])

                # Add transaction to pending pool
                self.blockchain.add_transaction({
                    'type': 'member_added',
                    'member': member,
                    'timestamp': int(timestamp.time())
                })

                return jsonify(member)
            except Exception as e:
                print(f"Error in add_member route: {str(e)}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/membership/list', methods=['GET'])
        def get_members():
            try:
                return jsonify(self.blockchain.members)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/membership/approve/<address>', methods=['POST'])
        def approve_member(address):
            try:
                data = request.get_json()
                approver_address = data.get('approver_address')
                if not approver_address:
                    return jsonify({'error': 'Missing approver_address'}), 400

                result = self.membership.vote_for_member(
                    address, approver_address, 'approve')
                return jsonify({'success': result})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/membership/reject/<address>', methods=['POST'])
        def reject_member(address):
            try:
                data = request.get_json()
                rejecter_address = data.get('approver_address')
                if not rejecter_address:
                    return jsonify({'error': 'Missing approver_address'}), 400

                result = self.membership.vote_for_member(
                    address, rejecter_address, 'reject')
                return jsonify({'success': result})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        # Proposal endpoints
        @self.app.route('/proposals/submit', methods=['POST'])
        def submit_proposal():
            try:
                data = request.get_json()
                if not data or 'proposer_address' not in data or 'proposal_data' not in data:
                    return jsonify({'error': 'Missing proposer_address or proposal_data'}), 400

                proposal = self.blockchain.consensus.submit_proposal(
                    data['proposer_address'],
                    data['proposal_data']
                )

                # Add transaction to pending pool
                self.blockchain.add_transaction({
                    'type': 'proposal_submitted',
                    'proposal': proposal,
                    'timestamp': int(timestamp.time())
                })

                return jsonify(proposal)
            except Exception as e:
                print(f"Error submitting proposal: {str(e)}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/proposals/approve', methods=['POST'])
        def approve_proposal():
            try:
                data = request.get_json()
                if not data or 'voter_address' not in data:
                    return jsonify({'error': 'Missing voter_address'}), 400

                result = self.blockchain.consensus.vote_proposal(
                    data['voter_address'], 'approve')

                if result:
                    # Add transaction to pending pool
                    self.blockchain.add_transaction({
                        'type': 'proposal_approved',
                        'voter': data['voter_address'],
                        'timestamp': int(timestamp.time())
                    })

                return jsonify({'success': result})
            except Exception as e:
                print(f"Error approving proposal: {str(e)}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/proposals/reject', methods=['POST'])
        def reject_proposal():
            try:
                data = request.get_json()
                if not data or 'voter_address' not in data:
                    return jsonify({'error': 'Missing voter_address'}), 400

                result = self.blockchain.consensus.vote_proposal(
                    data['voter_address'], 'reject')

                if result:
                    # Add transaction to pending pool
                    self.blockchain.add_transaction({
                        'type': 'proposal_rejected',
                        'voter': data['voter_address'],
                        'timestamp': int(timestamp.time())
                    })

                return jsonify({'success': result})
            except Exception as e:
                print(f"Error rejecting proposal: {str(e)}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/proposals/list', methods=['GET'])
        def get_proposals():
            try:
                return jsonify({
                    'current_proposal': self.blockchain.consensus.current_proposal,
                    'votes': self.blockchain.consensus.votes
                })
            except Exception as e:
                print(f"Error getting proposals: {str(e)}")
                return jsonify({'error': str(e)}), 500

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            config_path = os.path.join('core', 'network_config.json')
            with open(config_path, 'r') as f:
                self.config = json.load(f)
                print("Loaded network configuration successfully")
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            raise

    def start_block_creation_thread(self):
        """Start thread for periodic block creation"""
        def create_blocks():
            check_freq_value = self.config['blockchain']['block_creation']['check_frequency']['value']
            check_freq_unit = self.config['blockchain']['block_creation']['check_frequency']['unit']
            check_interval = self.convert_to_seconds(
                check_freq_value, check_freq_unit)

            while True:
                try:
                    block = self.blockchain.create_block()
                    if block:
                        self.blockchain.add_block(block)
                        print(f"\nNew block created with {
                              len(block['transactions'])} transactions")
                        print(f"Block: {block}")
                    # Use timestamp instead of time
                    timestamp.sleep(check_interval)
                except Exception as e:
                    print(f"Error in block creation: {str(e)}")
                    timestamp.sleep(5)  # Wait 5 seconds on error

        block_thread = threading.Thread(target=create_blocks, daemon=True)
        block_thread.start()
        print(f"\nStarted block creation thread with interval: {self.config['blockchain']['block_creation']['interval']['value']} {
              self.config['blockchain']['block_creation']['interval']['unit']}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start the blockchain node.')
    parser.add_argument('-p', '--port', type=int,
                        default=network_config['main_node']['port'],
                        help=f'Port to run the server on (default: {network_config["main_node"]["port"]})')
    parser.add_argument('-a', '--address', type=str,
                        help='Member address (required for non-main nodes)')

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, network_config['logging']['level']),
        format=network_config['logging']['format'],
        datefmt=network_config['logging']['date_format']
    )

    logger = logging.getLogger(__name__)

    try:
        app = create_app(args.port, args.address)
        logger.info(f'Starting blockchain node on port {args.port}')
        app.run(
            host=network_config['main_node']['host'],
            port=args.port
        )
    except ValueError as e:
        logger.error(str(e))
        exit(1)
