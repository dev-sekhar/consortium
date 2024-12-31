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


def create_app(port, member_address=None):
    app = Flask(__name__)

    # Generate a globally unique address for this node
    node_identifier = str(uuid4()).replace('-', '')

    main_port = network_config['main_node']['port']

    if port == main_port:
        if is_port_in_use(main_port):
            raise ValueError(f"Port {main_port} is already in use. Only one main node can run on port {main_port}.")

        blockchain = Blockchain()
        membership = Membership(blockchain)
        blockchain.set_membership(membership)
        logger.info(f"Initialized main node on port {port}")
    else:
        if network_config['authorization']['require_member_address'] and not member_address:
            raise ValueError("Member address is required for non-main nodes")

        if network_config['authorization']['verify_membership'] and not verify_member_authorization(member_address):
            raise ValueError("Unauthorized member. Only registered members can connect to the network.")

        blockchain = Blockchain()
        membership = Membership(blockchain)
        blockchain.set_membership(membership)
        logger.info(f"Connected to network as authorized member on port {port}")

    # Register the API blueprint
    api = create_api()
    app.register_blueprint(api)

    return app


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
