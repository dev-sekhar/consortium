from eth_utils import to_checksum_address
from eth_account import Account


def generate_ethereum_address() -> str:
    """Generate a valid Ethereum address"""
    # Generate a new Ethereum account
    account = Account.create()
    address = account.address

    # Convert to checksum address
    checksum_address = to_checksum_address(address)

    return checksum_address


def validate_ethereum_address(address: str) -> bool:
    """Validate an Ethereum address"""
    try:
        # Convert to checksum address and verify format
        to_checksum_address(address)
        return True
    except ValueError:
        return False
