"""
This file handles membership requests and voting.
It defines the Membership class which manages membership requests and the list of members.
"""

class Membership:
    def __init__(self):
        self.members = []
        self.requests = []

    def request_membership(self, member_id, name):
        """
        Create a new membership request.
        :param member_id: <str> ID of the requesting member
        :param name: <str> Name of the requesting member
        :return: <dict> Membership request
        """
        request = {
            'id': member_id,
            'name': name,
            'status': 'Pending',
            'votes': 0,
            'rejections': 0,
            'voters': []
        }
        self.requests.append(request)
        return request

    def vote_for_member(self, request_id, voter_id, action):
        """
        Vote for a membership request.
        :param request_id: <str> ID of the membership request
        :param voter_id: <str> ID of the voter
        :param action: <str> 'approve' or 'reject'
        :return: <dict> Updated membership request
        """
        for request in self.requests:
            if request['id'] == request_id:
                if voter_id not in request['voters']:
                    request['voters'].append(voter_id)
                    if action == 'approve':
                        request['votes'] += 1
                        if request['votes'] >= (len(self.members) // 2) + 1:
                            request['status'] = 'Approved'
                            self.members.append({'id': request['id'], 'name': request['name']})
                    elif action == 'reject':
                        request['rejections'] += 1
                        if request['rejections'] >= (len(self.members) // 2) + 1:
                            request['status'] = 'Rejected'
                    return request
        return None

    def get_members(self, status=None):
        """
        Get the list of members.
        :param status: (Optional) <str> Status to filter members by
        :return: <list> List of members
        """
        if status:
            return [member for member in self.members if member.get('status') == status]
        return self.members

    def get_requests(self, status=None):
        """
        Get the list of membership requests.
        :param status: (Optional) <str> Status to filter requests by
        :return: <list> List of membership requests
        """
        if status:
            return [request for request in self.requests if request.get('status') == status]
        return self.requests

    def add_member(self, member_id, name):
        """
        Manually add a member to the list of approved members.
        :param member_id: <str> ID of the member
        :param name: <str> Name of the member
        """
        self.members.append({'id': member_id, 'name': name})