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