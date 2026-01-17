"""
Test script for authentication system
Run this after starting the server to test auth endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/auth"

def test_authentication():
    print("=" * 60)
    print("Testing Ruman Authentication System")
    print("=" * 60)
    print()
    
    # Test 1: Health check
    print("1. Testing API health check...")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"   ✅ Status: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   Make sure the server is running: python app.py")
        return
    
    print()
    
    # Test 2: Register new user
    print("2. Testing user registration...")
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123",
        "role": "student"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        if response.status_code == 201:
            print(f"   ✅ User registered: {response.json()['username']}")
        elif response.status_code == 400:
            print(f"   ⚠️  User already exists (expected if run before)")
        else:
            print(f"   ❌ Error: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 3: Login with default admin
    print("3. Testing login (admin)...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            data=login_data  # OAuth2PasswordRequestForm uses form data, not JSON
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"   ✅ Login successful!")
            print(f"   Token: {access_token[:30]}...")
            
            # Test 4: Get current user info
            print()
            print("4. Testing /me endpoint with token...")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{BASE_URL}/me", headers=headers)
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"   ✅ Current user: {user_info['username']} (role: {user_info['role']})")
            else:
                print(f"   ❌ Error: {response.json()}")
        else:
            print(f"   ❌ Login failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 5: Test invalid credentials
    print("5. Testing invalid credentials...")
    invalid_login = {
        "username": "admin",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", data=invalid_login)
        if response.status_code == 401:
            print(f"   ✅ Correctly rejected invalid credentials")
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("=" * 60)
    print("Authentication Tests Complete!")
    print("=" * 60)
    print()
    print("Try these next:")
    print("1. Visit http://localhost:8000/docs for interactive API docs")
    print("2. Test registration with different roles (teacher, student)")
    print("3. Test protected endpoints with token authentication")


if __name__ == "__main__":
    test_authentication()
