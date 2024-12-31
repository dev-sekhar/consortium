from core.blockchain import Blockchain
from core.membership import Membership
from utilities.convert_to_ethereum_address import generate_ethereum_address


def test_add_first_member():
    print("\n=== Testing First Member Addition ===\n")

    # Initialize blockchain and membership
    blockchain = Blockchain()
    membership = Membership(blockchain)
    blockchain.set_membership(membership)

    # Generate test address for lender
    print("Generating lender address...")
    lender = generate_ethereum_address()
    print(f"Lender Address: {lender['address']}")

    try:
        # Add first member (lender)
        print("\nAdding first member (Lender One)...")
        lender_data = {
            "name": "Lender One",
            "role": "lender",
            "address": lender['address']
        }

        result = membership.add_member(lender_data)
        print("\nMember added successfully!")
        print("Member details:")
        print(f"ID: {result['member_id']}")
        print(f"Name: {result['name']}")
        print(f"Role: {result['role']}")
        print(f"Address: {result['address']}")
        print(f"Status: {result['status']}")
        print(f"Joined Date: {result['joined_date']}")

        # Verify member was added
        print("\nVerifying membership...")
        is_member = membership.is_member(lender['address'])
        print(f"Is member verified? {is_member}")

        # Get all members
        print("\nCurrent members list:")
        all_members = membership.get_members()
        print(f"Total members: {len(all_members)}")
        for member in all_members:
            print(f"- {member['name']} ({member['role']})")

    except Exception as e:
        print(f"\nError: {str(e)}")
        raise e

    print("\n=== Test Completed Successfully ===")


if __name__ == "__main__":
    test_add_first_member()
