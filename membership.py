"""
This file handles membership requests and voting.
It defines the Membership class which manages membership requests and the list of members.
"""

from blockchain import Blockchain
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from convert_to_ethereum_address import convert_to_ethereum_address


class Membership:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.members = []
        self.requests = []

    def generate_key_pair(self):
        """
        Generate a public-private key pair.
        :return: <tuple> (public_key, private_key)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return public_key, private_key

    def serialize_public_key(self, public_key):
        """
        Serialize the public key to PEM format.
        :param public_key: <RSAPublicKey> Public key
        :return: <str> Serialized public key
        """
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    def add_member(self, name):
        """
        Manually add a member to the list of approved members.
        :param name: <str> Name of the member
        :return: <dict> Member object
        """
        public_key, private_key = self.generate_key_pair()
        public_key_pem = self.serialize_public_key(public_key)
        address = convert_to_ethereum_address(public_key_pem)
        member = {'address': address, 'name': name}
        self.members.append(member)
        # Register the member in the blockchain
        self.blockchain.register_member(address)
        return member

    def request_membership(self, name):
        """
        Create a new membership request.
        :param name: <str> Name of the requesting member
        :return: <dict> Membership request
        """
        public_key, private_key = self.generate_key_pair()
        public_key_pem = self.serialize_public_key(public_key)
        address = convert_to_ethereum_address(public_key_pem)
        request = {
            'address': address,
            'name': name,
            'status': 'Pending',
            'votes': 0,
            'rejections': 0,
            'voters': []
        }
        self.requests.append({'request': request, 'private_key': private_key})
        return request

    def vote_for_member(self, request_address, voter_address, action):
        """
        Vote for a membership request.
        :param request_address: <str> Address of the membership request
        :param voter_address: <str> Address of the voter
        :param action: <str> 'approve' or 'reject'
        :return: <dict> Updated membership request
        """
        for request in self.requests:
            if request['request']['address'] == request_address:
                if voter_address not in request['request']['voters']:
                    request['request']['voters'].append(voter_address)
                    if action == 'approve':
                        request['request']['votes'] += 1
                        if request['request']['votes'] >= (len(self.members) // 2) + 1:
                            request['request']['status'] = 'Approved'
                            self.members.append(
                                {'address': request['request']['address'], 'name': request['request']['name']})
                            self.blockchain.register_member(
                                request['request']['address'])
                    elif action == 'reject':
                        request['request']['rejections'] += 1
                        if request['request']['rejections'] >= (len(self.members) // 2) + 1:
                            request['request']['status'] = 'Rejected'
                    return request['request']
        return None

    def get_addresses(self):
        """
        Get the list of member addresses.
        :return: <list> List of addresses
        """
        return [member['address'] for member in self.members]
