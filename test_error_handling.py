#!/usr/bin/env python3
"""
Test script to demonstrate the improved error handling in the FastAPI application.
This script tests various error scenarios including duplicate usernames and emails.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001"


def test_user_creation():
    """Test user creation with proper error handling"""

    print("=== Testing User Registration Error Handling ===\n")

    # Test 1: Create a user successfully
    print("1. Creating a new user...")
    user_data = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpassword123",
        "role": "user",
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

    # Test 2: Try to create user with same username
    print("2. Attempting to create user with duplicate username...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

    # Test 3: Try to create user with same email but different username
    print("3. Attempting to create user with duplicate email...")
    user_data_different_username = user_data.copy()
    user_data_different_username["username"] = "differentuser123"

    try:
        response = requests.post(
            f"{BASE_URL}/auth/register", json=user_data_different_username
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

    # Test 4: Try to create user with missing required field
    print("4. Attempting to create user with missing email...")
    incomplete_user_data = {
        "username": "incompleteuser",
        "first_name": "Incomplete",
        "last_name": "User",
        "password": "testpassword123",
        "role": "user",
        # Missing email field
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=incomplete_user_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()


def test_authentication():
    """Test authentication with proper error handling"""

    print("=== Testing Authentication Error Handling ===\n")

    # Test 1: Valid login
    print("1. Testing valid login...")
    login_data = {"username": "testuser123", "password": "testpassword123"}

    try:
        response = requests.post(f"{BASE_URL}/token", data=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

    # Test 2: Invalid username
    print("2. Testing invalid username...")
    invalid_login_data = {"username": "nonexistentuser", "password": "testpassword123"}

    try:
        response = requests.post(f"{BASE_URL}/token", data=invalid_login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

    # Test 3: Invalid password
    print("3. Testing invalid password...")
    wrong_password_data = {"username": "testuser123", "password": "wrongpassword"}

    try:
        response = requests.post(f"{BASE_URL}/token", data=wrong_password_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()


if __name__ == "__main__":
    print("Testing FastAPI Error Handling\n")
    print("Make sure the FastAPI server is running on http://127.0.0.1:8001\n")

    try:
        # Test if server is reachable
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Server is running and reachable\n")
            test_user_creation()
            test_authentication()
        else:
            print("❌ Server is not responding correctly")
    except requests.exceptions.ConnectionError:
        print(
            "❌ Cannot connect to server. Make sure it's running on http://127.0.0.1:8001"
        )
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
