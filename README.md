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
- `/membership/members`: Returns the list of members.

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
    curl -X POST -H "Content-Type: application/json" -d '{"request_id": "member1"}' http://192.168.3.106:5000/membership/vote
    ```

5. **Get the List of Members**:
    ```sh
    curl http://192.168.3.106:5000/membership/members
    ```

