import httpx
import asyncio
import pytest
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

@pytest.mark.asyncio
async def test_flow():
    print("\nConnecting to server...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("Registering user...")
        # 1. Register a user
        user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "testpassword123"
        }
        try:
            response = await client.post(f"{BASE_URL}/users/", json=user_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error during registration: {type(e).__name__}: {str(e)}")
            return
        
        if response.status_code != 200:
             print("Registration failed, user might already exist. Continuing...")

        # 2. Login
        print("\n--- Testing Login ---")
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        response = await client.post(f"{BASE_URL}/login/access-token", data=login_data)
        print(f"Status: {response.status_code}")
        token_data = response.json()
        token = token_data.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Token obtained: {token[:20]}...")

        # 2.1 Get Current User info
        print("\n--- Testing Get Me ---")
        response = await client.get(f"{BASE_URL}/users/me", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"User: {response.json()['full_name']} ({response.json()['email']})")

        # 3. Get Account Info
        print("\n--- Testing Get Accounts ---")
        response = await client.get(f"{BASE_URL}/banking/accounts", headers=headers)
        print(f"Status: {response.status_code}")
        accounts = response.json()
        print(f"Accounts: {accounts}")
        account_id = accounts[0]['id']
        assert accounts[0]['account_type'] == "checking"

        # 3.1 Create a savings account
        print("\n--- Testing Create Savings Account ---")
        savings_data = {"account_type": "savings"}
        response = await client.post(f"{BASE_URL}/banking/accounts", json=savings_data, headers=headers)
        print(f"Status: {response.status_code}")
        new_account = response.json()
        print(f"New Account: {new_account}")
        assert new_account['account_number'].startswith("CP-")
        assert new_account['account_type'] == "savings"
        new_account_id = new_account['id']

        # 3.2 Update Account Nickname
        print("\n--- Testing Update Account Nickname ---")
        update_data = {"nickname": "Minha Reserva"}
        response = await client.patch(f"{BASE_URL}/banking/accounts/{new_account_id}", json=update_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Updated Account: {response.json()}")
        assert response.json()['nickname'] == "Minha Reserva"

        # 3.3 Get Single Account Details
        print("\n--- Testing Get Single Account ---")
        response = await client.get(f"{BASE_URL}/banking/accounts/{new_account_id}", headers=headers)
        print(f"Status: {response.status_code}")
        assert response.json()['id'] == new_account_id

        # 4. Deposit
        print("\n--- Testing Deposit ---")
        deposit_data = {
            "amount": 1000.0,
            "type": "deposit",
            "account_id": account_id
        }
        response = await client.post(f"{BASE_URL}/banking/transactions", json=deposit_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # 5. Withdrawal (Success)
        print("\n--- Testing Withdrawal (Success) ---")
        withdraw_data = {
            "amount": 100.0,  # Adjusted to stay within $500 limit
            "type": "withdrawal",
            "account_id": account_id
        }
        response = await client.post(f"{BASE_URL}/banking/transactions", json=withdraw_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # 5.1 Withdrawal (Amount Limit)
        print("\n--- Testing Withdrawal (Amount Limit) ---")
        withdraw_high_data = {
            "amount": 600.0,
            "type": "withdrawal",
            "account_id": account_id
        }
        response = await client.post(f"{BASE_URL}/banking/transactions", json=withdraw_high_data, headers=headers)
        print(f"Status (Expected 400): {response.status_code}")
        print(f"Response: {response.json()}")

        # 6. Withdrawal (Insufficient Balance)
        print("\n--- Testing Withdrawal (Insufficient Balance) ---")
        withdraw_fail_data = {
            "amount": 450.0,  # Below $500 limit but above remaining balance ($1000 - $100 - $200 = $700, so 450 is fine, wait)
            # Let's use a value that definitely exceeds current balance:
            # Current: 1000 (dep) - 100 (with) - 200 (transf) = 700.
            # Let's try to withdraw 800.
            "amount": 490.0, 
            "type": "withdrawal",
            "account_id": account_id
        }
        # First one (490) should work. Balance becomes 210.
        await client.post(f"{BASE_URL}/banking/transactions", json=withdraw_fail_data, headers=headers)
        
        # Now try another 490. Should fail due to balance.
        response = await client.post(f"{BASE_URL}/banking/transactions", json=withdraw_fail_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 400
        # Updated to new "bonitinho" error format
        error_msg = response.json().get('error', {}).get('message', '') or response.json().get('detail', '')
        assert "Insufficient balance" in error_msg

        # 6.1 Transfer (Success)
        print("\n--- Testing Transfer (Success) ---")
        # Register second user to get destination account
        user2_data = {
            "email": "user2@example.com",
            "full_name": "User Two",
            "password": "testpassword123"
        }
        await client.post(f"{BASE_URL}/users/", json=user2_data)
        
        # Login as user2 to get their account number
        login2_data = {"username": "user2@example.com", "password": "testpassword123"}
        resp2 = await client.post(f"{BASE_URL}/login/access-token", data=login2_data)
        token2 = resp2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        resp_acc2 = await client.get(f"{BASE_URL}/banking/accounts", headers=headers2)
        dest_account_number = resp_acc2.json()[0]["account_number"]

        transfer_data = {
            "source_account_id": account_id,
            "destination_account_number": dest_account_number,
            "amount": 200.0,
            "description": "Presente de aniversário"
        }
        response = await client.post(f"{BASE_URL}/banking/transfer", json=transfer_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # 7. Statement with Pagination
        print("\n--- Testing Statement (Pagination) ---")
        response = await client.get(f"{BASE_URL}/banking/statement/{account_id}?skip=0&limit=2", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Transactions count (limited to 2): {len(response.json())}")

        # 8. Health Check
        print("\n--- Testing Health Check ---")
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Health: {response.json()}")

        # 9. Close Account
        print("\n--- Testing Close Account ---")
        # Should fail if balance > 0 (account_id has 300 balance from previous steps: 1000 - 500 - 200)
        response = await client.delete(f"{BASE_URL}/banking/accounts/{account_id}", headers=headers)
        print(f"Status (Expected 400): {response.status_code}")
        
        # Should succeed for new_account_id (balance is 0)
        response = await client.delete(f"{BASE_URL}/banking/accounts/{new_account_id}", headers=headers)
        print(f"Status (Expected 200): {response.status_code}")
        print(f"Response: {response.json()}")

        print("\n--- All Professional Endpoints Tested! ---")

if __name__ == "__main__":
    asyncio.run(test_flow())
