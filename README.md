"""
This file provides an overview of the project and instructions for setup and usage.
"""

# My Blockchain App

This is a simple consortium blockchain application with membership management.

## Setup

1. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

2. Run the application:
   ```sh
   python network.py
   ```

## Endpoints

- `/transactions/new`: Creates a new transaction.
- `/chain`: Returns the full blockchain.
- `/membership/request`: Requests membership.
- `/membership/vote`: Votes for a membership request.
- `/membership/members`: Returns the list of members or membership requests based on status.
- `/membership/add`: Manually adds a member.

### Example Usage

1. **Create a New Transaction**:

   ```sh
   curl -X POST -H "Content-Type: application/json" -d '{"sender": "address1", "recipient": "address2", "amount": 10}' http://192.168.3.106:5000/transactions/new
   ```

2. **Retrieve the Full Blockchain**:

   ```sh
   curl http://192.168.3.106:5000/chain
   ```

3. **Request Membership**:

   ```sh
   curl -X POST -H "Content-Type: application/json" -d '{"id": "member1", "name": "Member One"}' http://192.168.3.106:5000/membership/request
   ```

4. **Vote for a Membership Request**:

   ```sh
   curl -X POST -H "Content-Type: application/json" -d '{"request_id": "member1", "voter_id": "voter1", "action": "approve"}' http://192.168.3.106:5000/membership/vote
   ```

5. **Get the List of Members**:

   ```sh
   curl http://192.168.3.106:5000/membership/members
   ```

6. **Get the List of Pending Membership Requests**:

   ```sh
   curl http://192.168.3.106:5000/membership/members?status=pending
   ```

7. **Get the List of Rejected Membership Requests**:

   ```sh
   curl http://192.168.3.106:5000/membership/members?status=rejected
   ```

8. **Manually Add a Member**:
   ```sh
   curl -X POST -H "Content-Type: application/json" -d '{"id": "member1", "name": "Member One"}' http://192.168.3.106:5000/membership/add
   ```

### Test Script

You can use the following test script to automate the process of adding the first member, requesting membership for two additional members, approving one member, rejecting another, and querying for pending requests, all members, and rejected members.

Create a file named [test_script.sh](http://_vscodecontentref_/2) with the following content:

```bash
#!/bin/bash

# Base URL
BASE_URL="http://192.168.3.106:5000"

# Function to print and execute curl commands
execute_curl() {
    echo "Request: $1"
    eval $1
    echo -e "\n"
}

# Add the first member manually
echo "Adding the first member..."
execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"id\": \"member1\", \"name\": \"Member One\"}' $BASE_URL/membership/add"

# Request membership for two additional members
echo "Requesting membership for member2..."
execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"id\": \"member2\", \"name\": \"Member Two\"}' $BASE_URL/membership/request"

echo "Requesting membership for member3..."
execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"id\": \"member3\", \"name\": \"Member Three\"}' $BASE_URL/membership/request"

# Approve the membership request for member2
echo "Approving membership request for member2..."
execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"request_id\": \"member2\", \"voter_id\": \"member1\", \"action\": \"approve\"}' $BASE_URL/membership/vote"

# Reject the membership request for member3
echo "Rejecting membership request for member3..."
execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"request_id\": \"member3\", \"voter_id\": \"member1\", \"action\": \"reject\"}' $BASE_URL/membership/vote"

# Query for pending requests
echo "Querying for pending requests..."
execute_curl "curl $BASE_URL/membership/members?status=pending"

# Query for all members
echo "Querying for all members..."
execute_curl "curl $BASE_URL/membership/members"

# Query for rejected members
echo "Querying for rejected members..."
execute_curl "curl $BASE_URL/membership/members?status=rejected"
```
