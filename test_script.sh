#!/bin/bash

# Base URL
BASE_URL="http://192.168.3.106:5000"

# Function to print and execute curl commands
execute_curl() {
    echo "Request: $1"
    RESPONSE=$(eval $1)
    echo "Response: $RESPONSE"
    echo -e "\n"
    echo $RESPONSE
}

# Add the first member manually
echo "Adding the first member..."
MEMBER1_RESPONSE=$(execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"name\": \"Member One\"}' $BASE_URL/membership/add")
echo "Raw Member 1 Response: $MEMBER1_RESPONSE"
MEMBER1_ADDRESS=$(echo "$MEMBER1_RESPONSE" | jq -r '.member.address' | tr -d '\n')
echo "Member 1 Address: $MEMBER1_ADDRESS"

# Request membership for member2
echo "Requesting membership for member2..."
MEMBER2_RESPONSE=$(execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"name\": \"Member Two\"}' $BASE_URL/membership/request")
echo "Raw Member 2 Response: $MEMBER2_RESPONSE"
MEMBER2_ADDRESS=$(echo "$MEMBER2_RESPONSE" | jq -r '.request.address' | tr -d '\n')
echo "Member 2 Address: $MEMBER2_ADDRESS"

# Request membership for member3
echo "Requesting membership for member3..."
MEMBER3_RESPONSE=$(execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"name\": \"Member Three\"}' $BASE_URL/membership/request")
echo "Raw Member 3 Response: $MEMBER3_RESPONSE"
MEMBER3_ADDRESS=$(echo "$MEMBER3_RESPONSE" | jq -r '.request.address' | tr -d '\n')
echo "Member 3 Address: $MEMBER3_ADDRESS"

# Approve the membership request for member2 by member1
echo "Approving membership request for member2 by member1..."
execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"request_address\": \"$MEMBER2_ADDRESS\", \"voter_address\": \"$MEMBER1_ADDRESS\", \"action\": \"approve\"}' $BASE_URL/membership/vote"

# Reject the membership request for member3 by member1
echo "Rejecting membership request for member3 by member1..."
execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"request_address\": \"$MEMBER3_ADDRESS\", \"voter_address\": \"$MEMBER1_ADDRESS\", \"action\": \"reject\"}' $BASE_URL/membership/vote"

# Reject the membership request for member3 by member2
echo "Rejecting membership request for member3 by member2..."
execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"request_address\": \"$MEMBER3_ADDRESS\", \"voter_address\": \"$MEMBER2_ADDRESS\", \"action\": \"reject\"}' $BASE_URL/membership/vote"

# Query for pending requests
echo "Querying for pending requests..."
execute_curl "curl $BASE_URL/membership/members?status=pending"

# Query for all members
echo "Querying for all members..."
execute_curl "curl $BASE_URL/membership/members"

# Query for rejected members
echo "Querying for rejected members..."
execute_curl "curl $BASE_URL/membership/members?status=rejected"

# Add transactions from registered members
echo "Adding transactions from registered members..."
execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"sender\": \"$MEMBER1_ADDRESS\", \"recipient\": \"$MEMBER2_ADDRESS\", \"amount\": 10}' $BASE_URL/transactions/new"
execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"sender\": \"$MEMBER2_ADDRESS\", \"recipient\": \"$MEMBER1_ADDRESS\", \"amount\": 5}' $BASE_URL/transactions/new"

# Add transactions from unregistered members
echo "Adding transactions from unregistered members..."
execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"sender\": \"unregistered1\", \"recipient\": \"$MEMBER1_ADDRESS\", \"amount\": 15}' $BASE_URL/transactions/new"
execute_curl "curl -X POST -H \"Content-Type: application/json\" -d '{\"sender\": \"$MEMBER1_ADDRESS\", \"recipient\": \"unregistered2\", \"amount\": 20}' $BASE_URL/transactions/new"

# Retrieve the full blockchain
echo "Retrieving the full blockchain..."
execute_curl "curl $BASE_URL/chain"

# Print all member addresses
echo "Printing all member addresses..."
execute_curl "curl $BASE_URL/membership/addresses"