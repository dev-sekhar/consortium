from eth_utils import to_checksum_address
from eth_account import Account
import secrets


def generate_ethereum_address():
    """Generate a new Ethereum address"""
    # Generate a random private key
    private_key = "0x" + secrets.token_hex(32)

    # Create an account from the private key
    account = Account.from_key(private_key)

    return {
        'address': account.address,
        'private_key': private_key
    }


def validate_ethereum_address(address):
    """Validate an Ethereum address"""
    try:
        # Convert to checksum address and verify format
        checksum_address = to_checksum_address(address)
        return True
    except:
        return False
