# Consortium Blockchain with Proof of Vote

This project implements a consortium blockchain with a Proof of Vote (PoV) consensus mechanism. Members can join through voting, conduct transactions, and participate in block validation through voting.

## Prerequisites

- Python 3.x
- Flask
- cryptography
- eth-utils

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/your-repo/consortium.git
   cd consortium
   ```

2. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the Flask server:
   ```sh
   python network.py
   ```

## Complete Process Flow

### 1. Member Management

#### Add First Member

```bash
# Add the first member manually (no voting required)
curl -X POST -H "Content-Type: application/json" -d '{
    "name": "Member One"
}' http://localhost:5000/membership/add

# Response will include the member's address
# Save this address as MEMBER_ONE_ADDRESS
```

#### Add Additional Members

```bash
# Request membership for a new member
curl -X POST -H "Content-Type: application/json" -d '{
    "name": "Member Two"
}' http://localhost:5000/membership/request

# Response will include the request address
# Save this as MEMBER_TWO_REQUEST_ADDRESS

# Approve membership request
curl -X POST -H "Content-Type: application/json" -d '{
    "request_address": "MEMBER_TWO_REQUEST_ADDRESS",
    "voter_address": "MEMBER_ONE_ADDRESS",
    "action": "approve"
}' http://localhost:5000/membership/vote

# Or reject membership request
curl -X POST -H "Content-Type: application/json" -d '{
    "request_address": "MEMBER_TWO_REQUEST_ADDRESS",
    "voter_address": "MEMBER_ONE_ADDRESS",
    "action": "reject"
}' http://localhost:5000/membership/vote
```

### 2. Transaction Management

#### Create Transactions

```bash
# Create transaction between registered members
curl -X POST -H "Content-Type: application/json" -d '{
    "sender": "MEMBER_ONE_ADDRESS",
    "recipient": "MEMBER_TWO_ADDRESS",
    "amount": 10
}' http://localhost:5000/transactions/new
```

### 3. Block Creation and Consensus (PoV)

#### Propose and Vote on Blocks

```bash
# Propose a new block containing pending transactions
curl -X POST -H "Content-Type: application/json" -d '{
    "proposer": "MEMBER_ONE_ADDRESS"
}' http://localhost:5000/block/propose

# First member votes on the block
curl -X POST -H "Content-Type: application/json" -d '{
    "block_index": 2,
    "voter_address": "MEMBER_ONE_ADDRESS"
}' http://localhost:5000/block/vote

# Second member votes on the block
curl -X POST -H "Content-Type: application/json" -d '{
    "block_index": 2,
    "voter_address": "MEMBER_TWO_ADDRESS"
}' http://localhost:5000/block/vote
```

### 4. View Status and Information

```bash
# Get all members
curl http://localhost:5000/membership/members

# Get pending membership requests
curl http://localhost:5000/membership/members?status=pending

# Get rejected members
curl http://localhost:5000/membership/members?status=rejected

# Get pending blocks awaiting votes
curl http://localhost:5000/block/pending

# Get the complete blockchain
curl http://localhost:5000/chain

# Get all member addresses
curl http://localhost:5000/membership/addresses
```

## Example Complete Flow

1. Start by adding the first member:

   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"name": "Member One"}' http://localhost:5000/membership/add
   # Save the returned address as MEMBER_ONE_ADDRESS
   ```

2. Request and approve second member:

   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"name": "Member Two"}' http://localhost:5000/membership/request
   # Save the returned request address as MEMBER_TWO_REQUEST_ADDRESS

   curl -X POST -H "Content-Type: application/json" -d '{
       "request_address": "MEMBER_TWO_REQUEST_ADDRESS",
       "voter_address": "MEMBER_ONE_ADDRESS",
       "action": "approve"
   }' http://localhost:5000/membership/vote
   ```

3. Create transactions:

   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{
       "sender": "MEMBER_ONE_ADDRESS",
       "recipient": "MEMBER_TWO_ADDRESS",
       "amount": 10
   }' http://localhost:5000/transactions/new
   ```

4. Create and approve block:

   ```bash
   # Propose block
   curl -X POST -H "Content-Type: application/json" -d '{
       "proposer": "MEMBER_ONE_ADDRESS"
   }' http://localhost:5000/block/propose

   # Get votes from members
   curl -X POST -H "Content-Type: application/json" -d '{
       "block_index": 2,
       "voter_address": "MEMBER_ONE_ADDRESS"
   }' http://localhost:5000/block/vote

   curl -X POST -H "Content-Type: application/json" -d '{
       "block_index": 2,
       "voter_address": "MEMBER_TWO_ADDRESS"
   }' http://localhost:5000/block/vote
   ```

## Important Notes

- First member is added manually without voting
- Additional members require approval from existing members
- A member request can be rejected by existing members
- Transactions require both sender and recipient to be registered members
- Blocks require a minimum of 2 votes to be approved
- Members can only vote once per block
- Transactions remain pending until included in an approved block
- The system uses a Proof of Vote (PoV) consensus mechanism
- All addresses are in Ethereum format
