import argparse
import json
import os
import requests
import sys
from core.network import Network


def load_network_config():
    """Load network configuration from JSON file"""
    config_path = os.path.join(os.path.dirname(
        __file__), 'core', 'network_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def is_main_node_running(config):
    """Check if main node is running on port 5000 and get chain info"""
    try:
        # Try to get chain info from main node
        response = requests.get(
            f"http://{config['main_node']['host']
                      }:{config['main_node']['port']}/chain",
            timeout=2
        )
        if response.status_code == 200:
            chain_data = response.json()
            print(f"Found existing blockchain network on port {
                  config['main_node']['port']}")
            print(f"Current chain length: {len(chain_data['chain'])}")
            return True
        return False
    except requests.RequestException:
        print(f"No existing blockchain network found on port {
              config['main_node']['port']}")
        return False


def get_next_available_port(config):
    """Get the next available port from the member port range"""
    min_port = config['member_nodes']['min_port']
    max_port = config['member_nodes']['max_port']

    for port in range(min_port, max_port + 1):
        try:
            requests.get(
                f"http://{config['main_node']['host']}:{port}/status", timeout=1)
        except requests.RequestException:
            return port

    raise Exception("No available ports in the configured range")


def get_member_name():
    """Prompt user for member name"""
    while True:
        name = input("Enter member name: ").strip()
        if name:
            return name
        print("Name cannot be empty. Please try again.")


def main():
    try:
        # Load network configuration
        network_config = load_network_config()

        # Check if main node exists and get chain info
        main_node_exists = is_main_node_running(network_config)

        if not main_node_exists:
            # Start as main node on port 5000
            port = network_config['main_node']['port']
            is_main_node = True
            member_name = get_member_name()
            print(
                f"Starting new blockchain network as main node on port {port}")
        else:
            # Start as member node on next available port
            port = get_next_available_port(network_config)
            is_main_node = False
            member_name = get_member_name()
            print(
                f"Connecting to existing blockchain network as member node on port {port}")

        # Start the network
        network = Network(
            port=port,
            is_main_node=is_main_node,
            main_node_port=network_config['main_node']['port'],
            member_name=member_name
        )

        network.app.run(
            host=network_config['main_node']['host'],
            port=port
        )
    except Exception as e:
        print(f"Error starting node: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
