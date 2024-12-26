import base64
import hashlib
from eth_utils import keccak

def convert_to_ethereum_address(public_key_pem):
    # Remove the PEM header and footer
    public_key_pem = public_key_pem.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").replace("\n", "")
    
    # Decode the base64 encoded public key
    public_key_bytes = base64.b64decode(public_key_pem)
    
    # Perform Keccak-256 hashing on the public key
    keccak_hash = keccak(public_key_bytes)
    
    # Take the last 20 bytes of the Keccak-256 hash
    address_bytes = keccak_hash[-20:]
    
    # Convert the result to a hexadecimal address
    address_hex = "0x" + address_bytes.hex()
    
    return address_hex

# Example usage
if __name__ == "__main__":
    public_key_pem = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlnOtR/uh4f2qZHPhhh5j
LBwZSWhkNJCb8n4bFNIUNdIWCORF79q0VJ6pzDU/aU6A5/sxXOT3ZVBpla4WTtQj
5lr+OCuQcRRR38Gb+ogb6XwH5pVgNZ0VrIcIjWKJocAdQDBDqtSyrlxpmrG+wTEO
hnRWXe76Lss9aof/ZFnP+NiG+FpY5ySS2yGYi1O+WQAVdIDJjMUD0qDXTD42RWo8
YcKEofLF4PcX25+MtIOv4ychrXfEyTfcA11Rp+pS0lhXQ0cUzUXZCkqr3dsSvCft
i73N/LzXFtDtGOOjILyYc7Qgz0oVFWMSVqplCs4/3ZyTeS2ET4odDzlGlEryT9qO
9wIDAQAB
-----END PUBLIC KEY-----"""

    address_ethereum = convert_to_ethereum_address(public_key_pem)
    print(f"Ethereum-like Address: {address_ethereum}")

    members = [
        {
            "address": "0x161b3fce8de0c6541120cc501e0041b5bffdd75a",
            "name": "Member One"
        },
        {
            "address": "0x56ef3606ffc60b14fa017526793a9e401f1c804e",
            "name": "Member Two"
        }
    ]

    for member in members:
        print(f"Name: {member['name']}, Address: {member['address']}")