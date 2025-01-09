import hashlib
import json


def hash_block(block):
    """Create a SHA-256 hash of a block"""
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()
