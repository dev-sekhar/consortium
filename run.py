from core.network import Network
from utilities.convert_to_ethereum_address import generate_ethereum_address
import threading
import time


def setup_first_lender(network):
    """Create the first lender based on user input"""
    try:
        print("\nNo members found. Setting up the first lender...")
        name = input("Enter the name for the first lender: ")

        # Create first lender with active status directly
        first_lender = {
            'address': generate_ethereum_address(),
            'name': name,
            'role': "lender",
            'status': 'active',
            'timestamp': int(time.time())
        }

        # Add to blockchain members directly
        network.blockchain.members = [first_lender]
        print(f"First lender created successfully: {first_lender}")

        # Add transaction to pending pool
        network.blockchain.add_transaction({
            'type': 'member_added',
            'member': first_lender,
            'timestamp': first_lender['timestamp']
        })

        return first_lender

    except Exception as e:
        print(f"Error setting up first lender: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise


def main():
    try:
        # Create network instance
        network = Network()

        # Check if any members exist
        if not network.blockchain.members:
            setup_first_lender(network)
        else:
            print(f"\nFound existing members: {
                  len(network.blockchain.members)}")

        # Start Flask app
        network.app.run(debug=False, use_reloader=False)

    except Exception as e:
        print(f"Error in main: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
