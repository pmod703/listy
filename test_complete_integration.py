#!/usr/bin/env python3
"""
Complete Integration Test
Tests the full sign-up page integration with authentication and database
"""

import requests
import time
import subprocess
import os
import signal

def start_backend():
    """Start the authentication backend"""
    try:
        print("🚀 Starting authentication backend...")
        process = subprocess.Popen(
            ['python', 'auth_integration.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Test if server is running
        response = requests.get('http://localhost:5001/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend started successfully")
            return process
        else:
            print("❌ Backend failed to start properly")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def test_complete_flow():
    """Test the complete user flow"""
    print("\n🧪 Testing Complete User Flow")
    print("=" * 50)
    
    # Test data
    timestamp = int(time.time())
    test_user = {
        "email": f"integration_test_{timestamp}@example.com",
        "password": "TestPass123!",
        "first_name": "Integration",
        "last_name": "Test",
        "agency_name": "Test Real Estate",
        "license_number": f"INT{timestamp}",
        "phone": "+1234567890"
    }
    
    try:
        # Step 1: Test API health
        print("1️⃣ Testing API health...")
        health_response = requests.get('http://localhost:5001/api/health')
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ API healthy - Version: {health_data.get('version')}")
            print(f"   🔐 Authentication: {health_data.get('authentication_enabled')}")
            print(f"   🗄️ Database: {health_data.get('database_status')}")
        else:
            print(f"   ❌ Health check failed: {health_response.status_code}")
            return False
        
        # Step 2: Test user registration (sign-up page functionality)
        print("\n2️⃣ Testing user registration...")
        register_response = requests.post(
            'http://localhost:5001/api/auth/register',
            json=test_user,
            headers={'Content-Type': 'application/json'}
        )
        
        if register_response.status_code == 201:
            register_data = register_response.json()
            access_token = register_data['access_token']
            user_data = register_data['user']
            
            print(f"   ✅ Registration successful")
            print(f"   👤 User ID: {user_data['id']}")
            print(f"   📧 Email: {user_data['email']}")
            print(f"   🏢 Agency: {user_data['agency_name']}")
            print(f"   🎫 Token: {access_token[:20]}...")
        else:
            print(f"   ❌ Registration failed: {register_response.status_code}")
            print(f"   📄 Response: {register_response.text}")
            return False
        
        # Step 3: Test authenticated profile access
        print("\n3️⃣ Testing authenticated profile access...")
        profile_response = requests.get(
            'http://localhost:5001/api/auth/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            user_profile = profile_data['user']
            
            print(f"   ✅ Profile access successful")
            print(f"   👤 Full name: {user_profile['full_name']}")
            print(f"   📧 Email verified: {user_profile['email_verified']}")
            print(f"   ✅ Account active: {user_profile['is_active']}")
        else:
            print(f"   ❌ Profile access failed: {profile_response.status_code}")
            return False
        
        # Step 4: Test main application API with authentication
        print("\n4️⃣ Testing main application API...")
        api_response = requests.get(
            'http://localhost:5001/api/inspections?address=123 Test St, Sydney, 2000&date=2024-01-20&similar_bedrooms=3-4&similar_bathrooms=2%2B&similar_car_spots=1-2',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if api_response.status_code == 200:
            api_data = api_response.json()
            
            print(f"   ✅ API call successful")
            print(f"   🏠 Total inspections: {api_data.get('total_inspections', 0)}")
            print(f"   🎯 Similar properties: {api_data.get('similar_inspections', 0)}")
            print(f"   🔐 Authenticated: {api_data.get('authenticated', False)}")
            print(f"   💾 Saved to DB: {api_data.get('saved_to_database', False)}")
            
            # Check recommendations
            recommendations = api_data.get('recommendations', [])
            if recommendations:
                print(f"   📊 Top recommendation: {recommendations[0]['time']} ({recommendations[0]['competition']})")
        else:
            print(f"   ❌ API call failed: {api_response.status_code}")
            return False
        
        # Step 5: Test login with created user
        print("\n5️⃣ Testing login functionality...")
        login_response = requests.post(
            'http://localhost:5001/api/auth/login',
            json={
                'email': test_user['email'],
                'password': test_user['password']
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            
            print(f"   ✅ Login successful")
            print(f"   🎫 New access token: {login_data['access_token'][:20]}...")
            print(f"   🔄 Refresh token: {login_data['refresh_token'][:20]}...")
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            return False
        
        # Step 6: Test session management
        print("\n6️⃣ Testing session management...")
        sessions_response = requests.get(
            'http://localhost:5001/api/auth/sessions',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if sessions_response.status_code == 200:
            sessions_data = sessions_response.json()
            
            print(f"   ✅ Session management working")
            print(f"   📱 Active sessions: {sessions_data.get('total_sessions', 0)}")
        else:
            print(f"   ❌ Session management failed: {sessions_response.status_code}")
            return False
        
        print("\n🎉 All integration tests passed!")
        print("\n📋 Summary:")
        print("   ✅ API health check: Working")
        print("   ✅ User registration: Working")
        print("   ✅ Database storage: Working")
        print("   ✅ Authentication: Working")
        print("   ✅ Profile access: Working")
        print("   ✅ Main app API: Working")
        print("   ✅ Login functionality: Working")
        print("   ✅ Session management: Working")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Backend may not be running.")
        return False
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print("\n🌐 Testing Frontend Accessibility")
    print("=" * 50)
    
    try:
        # Test if React app is running
        response = requests.get('http://localhost:3000', timeout=5)
        
        if response.status_code == 200:
            print("✅ Frontend is accessible at http://localhost:3000")
            
            # Check if it contains our app content
            content = response.text
            if 'Open Home Optimizer' in content or 'react' in content.lower():
                print("✅ Frontend contains expected content")
                return True
            else:
                print("⚠️ Frontend accessible but content may not be loaded")
                return True
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Frontend not running on http://localhost:3000")
        print("💡 Start with: cd my-real-estate-app && npm start")
        return False
    except Exception as e:
        print(f"❌ Error testing frontend: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Complete Integration Test Suite")
    print("Real Estate Open Home Optimizer - Sign-Up Page Integration")
    print("=" * 70)
    
    backend_process = None
    
    try:
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            print("❌ Could not start backend. Exiting.")
            return False
        
        # Test complete flow
        flow_success = test_complete_flow()
        
        # Test frontend
        frontend_success = test_frontend_accessibility()
        
        # Final summary
        print("\n" + "=" * 70)
        print("📊 FINAL TEST RESULTS")
        print("=" * 70)
        
        if flow_success:
            print("✅ Backend Integration: PASSED")
        else:
            print("❌ Backend Integration: FAILED")
        
        if frontend_success:
            print("✅ Frontend Accessibility: PASSED")
        else:
            print("❌ Frontend Accessibility: FAILED")
        
        if flow_success and frontend_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("🚀 Your sign-up page is ready for use!")
            print("\n📍 Access your application:")
            print("   🌐 Frontend: http://localhost:3000")
            print("   🔗 Backend API: http://localhost:5001")
            print("   📊 Health Check: http://localhost:5001/api/health")
            print("\n💡 Next steps:")
            print("   1. Visit http://localhost:3000")
            print("   2. Click 'Create one here' to test sign-up")
            print("   3. Fill out the form and register")
            print("   4. You'll be logged in automatically!")
        else:
            print("\n⚠️ Some tests failed. Please check the implementation.")
        
        return flow_success and frontend_success
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        return False
    finally:
        # Clean up backend process
        if backend_process:
            try:
                print("\n🧹 Cleaning up backend process...")
                os.killpg(os.getpgid(backend_process.pid), signal.SIGTERM)
                backend_process.wait(timeout=5)
                print("✅ Backend process terminated")
            except Exception as e:
                print(f"⚠️ Error terminating backend: {e}")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)