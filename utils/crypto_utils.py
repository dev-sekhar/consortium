from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import json


class CryptoUtils:
    @staticmethod
    def generate_key_pair():
        """Generate a new RSA key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        # Serialize keys to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem.decode(), public_pem.decode()

    @staticmethod
    def sign_message(private_key_pem, message):
        """Sign a message using private key"""
        # Load private key from PEM
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )

        # Convert message to bytes if it's not already
        if isinstance(message, dict):
            message = json.dumps(message, sort_keys=True).encode()
        elif isinstance(message, str):
            message = message.encode()

        # Sign the message
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return signature.hex()

    @staticmethod
    def verify_signature(public_key_pem, message, signature):
        """Verify a signature using public key"""
        try:
            # Load public key from PEM
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode(),
                backend=default_backend()
            )

            # Convert message to bytes if it's not already
            if isinstance(message, dict):
                message = json.dumps(message, sort_keys=True).encode()
            elif isinstance(message, str):
                message = message.encode()

            # Verify the signature
            public_key.verify(
                bytes.fromhex(signature),
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"Signature verification failed: {str(e)}")
            return False
