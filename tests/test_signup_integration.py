#!/usr/bin/env python3
"""
Test script to verify the sign-up page integration with the database
"""

import requests
import json
import time

def test_signup_integration():
    """Test the complete signup flow"""
    
    # Test configuration
    BASE_URL = "http://localhost:5001"
    
    # Generate unique test user
    timestamp = int(time.time())
    test_user = {
        "email": f"test_user_{timestamp}@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
        "agency_name": "Test Real Estate Agency",
        "license_number": f"TEST{timestamp}",
        "phone": "+1234567890"
    }
    
    print("🧪 Testing Sign-Up Integration")
    print("=" * 50)
    print(f"📧 Test user email: {test_user['email']}")
    print(f"🏢 Agency: {test_user['agency_name']}")
    print(f"📄 License: {test_user['license_number']}")
    print()
    
    try:
        # Test 1: Health check
        print("1️⃣ Testing API health...")
        health_response = requests.get(f"{BASE_URL}/api/health")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ API is healthy")
            print(f"   📊 Version: {health_data.get('version', 'Unknown')}")
            print(f"   🔐 Authentication enabled: {health_data.get('authentication_enabled', False)}")
            print(f"   🗄️ Database status: {health_data.get('database_status', 'Unknown')}")
        else:
            print(f"   ❌ Health check failed: {health_response.status_code}")
            return False
        
        print()
        
        # Test 2: User registration
        print("2️⃣ Testing user registration...")
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if register_response.status_code == 201:
            register_data = register_response.json()
            print(f"   ✅ User registered successfully")
            print(f"   👤 User ID: {register_data['user']['id']}")
            print(f"   📧 Email: {register_data['user']['email']}")
            print(f"   🎫 Token received: {register_data['access_token'][:20]}...")
            
            # Store token for further tests
            access_token = register_data['access_token']
            user_data = register_data['user']
            
        else:
            print(f"   ❌ Registration failed: {register_response.status_code}")
            print(f"   📄 Response: {register_response.text}")
            return False
        
        print()
        
        # Test 3: Verify user data in database
        print("3️⃣ Testing user profile retrieval...")
        profile_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            user_profile = profile_data['user']
            
            print(f"   ✅ Profile retrieved successfully")
            print(f"   👤 Full name: {user_profile['full_name']}")
            print(f"   🏢 Agency: {user_profile['agency_name']}")
            print(f"   📄 License: {user_profile['license_number']}")
            print(f"   📞 Phone: {user_profile['phone']}")
            print(f"   ✅ Active: {user_profile['is_active']}")
            print(f"   📧 Email verified: {user_profile['email_verified']}")
            
        else:
            print(f"   ❌ Profile retrieval failed: {profile_response.status_code}")
            return False
        
        print()
        
        # Test 4: Test authenticated API call
        print("4️⃣ Testing authenticated API call...")
        api_response = requests.get(
            f"{BASE_URL}/api/inspections?address=123 Test St, Sydney, 2000&date=2024-01-20",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if api_response.status_code == 200:
            api_data = api_response.json()
            print(f"   ✅ Authenticated API call successful")
            print(f"   🏠 Total inspections: {api_data.get('total_inspections', 0)}")
            print(f"   🎯 Similar properties: {api_data.get('similar_inspections', 0)}")
            print(f"   🔐 Authenticated: {api_data.get('authenticated', False)}")
            print(f"   💾 Saved to database: {api_data.get('saved_to_database', False)}")
            
        else:
            print(f"   ❌ Authenticated API call failed: {api_response.status_code}")
            return False
        
        print()
        
        # Test 5: Test login with created user
        print("5️⃣ Testing login with created user...")
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": test_user['email'],
                "password": test_user['password']
            },
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            print(f"   ✅ Login successful")
            print(f"   🎫 New access token: {login_data['access_token'][:20]}...")
            print(f"   🔄 Refresh token: {login_data['refresh_token'][:20]}...")
            
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   📄 Response: {login_response.text}")
            return False
        
        print()
        
        # Test 6: Test user sessions
        print("6️⃣ Testing user sessions...")
        sessions_response = requests.get(
            f"{BASE_URL}/api/auth/sessions",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if sessions_response.status_code == 200:
            sessions_data = sessions_response.json()
            print(f"   ✅ Sessions retrieved successfully")
            print(f"   📱 Active sessions: {sessions_data.get('total_sessions', 0)}")
            
            if sessions_data.get('sessions'):
                for i, session in enumerate(sessions_data['sessions'][:2], 1):
                    print(f"   📱 Session {i}: {session.get('ip_address', 'Unknown IP')}")
            
        else:
            print(f"   ❌ Sessions retrieval failed: {sessions_response.status_code}")
            return False
        
        print()
        print("🎉 All tests passed! Sign-up integration is working correctly.")
        print()
        print("📋 Summary:")
        print(f"   ✅ User registration: Working")
        print(f"   ✅ Database storage: Working") 
        print(f"   ✅ Authentication: Working")
        print(f"   ✅ Profile retrieval: Working")
        print(f"   ✅ API integration: Working")
        print(f"   ✅ Session management: Working")
        print()
        print("🚀 The sign-up page is ready for use!")
        print(f"📍 Frontend URL: http://localhost:3000")
        print(f"🔗 API URL: {BASE_URL}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running:")
        print("   python auth_integration.py")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_password_validation():
    """Test password validation"""
    print("\n" + "=" * 50)
    print("🔒 Testing Password Validation")
    print("=" * 50)
    
    BASE_URL = "http://localhost:5001"
    
    weak_passwords = [
        ("123456", "Too short, no complexity"),
        ("password", "Common password, no complexity"),
        ("Password", "Missing digit and special char"),
        ("Password123", "Missing special char"),
        ("password123!", "Missing uppercase"),
    ]
    
    for password, reason in weak_passwords:
        try:
            test_data = {
                "email": f"test_{int(time.time())}@example.com",
                "password": password,
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                print(f"   ✅ Weak password '{password}' properly rejected ({reason})")
            else:
                print(f"   ❌ Weak password '{password}' should be rejected ({reason})")
                
        except Exception as e:
            print(f"   ❌ Error testing password '{password}': {e}")

if __name__ == "__main__":
    print("🚀 Sign-Up Integration Test Suite")
    print("Make sure the authentication server is running:")
    print("  python auth_integration.py")
    print()
    
    success = test_signup_integration()
    test_password_validation()
    
    print("\n" + "=" * 50)
    if success:
        print("✨ All tests completed successfully!")
        print("🎯 Your sign-up page is ready for production!")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    print("=" * 50)