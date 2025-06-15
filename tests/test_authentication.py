#!/usr/bin/env python3
"""
Authentication System Test Suite
Comprehensive tests for the authentication functionality
"""

import requests
import json
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5001"
AUTH_URL = f"{BASE_URL}/api/auth"

class AuthenticationTester:
    """Test class for authentication system"""
    
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.test_user_email = f"test_{int(time.time())}@example.com"
        self.test_password = "TestPass123!"
        
    def print_test_header(self, test_name):
        """Print formatted test header"""
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print(f"{'='*60}")
    
    def print_result(self, success, message):
        """Print test result"""
        status = "✅" if success else "❌"
        print(f"{status} {message}")
    
    def test_health_check(self):
        """Test API health check"""
        self.print_test_header("Health Check")
        
        try:
            response = requests.get(f"{BASE_URL}/api/health")
            
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, f"API is healthy - Version: {data.get('version')}")
                self.print_result(True, f"Authentication enabled: {data.get('authentication_enabled')}")
                self.print_result(True, f"Database status: {data.get('database_status')}")
                return True
            else:
                self.print_result(False, f"Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Health check error: {e}")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        self.print_test_header("User Registration")
        
        try:
            # Test successful registration
            registration_data = {
                "email": self.test_user_email,
                "password": self.test_password,
                "first_name": "Test",
                "last_name": "User",
                "agency_name": "Test Real Estate",
                "license_number": "TEST123456",
                "phone": "+1234567890"
            }
            
            response = requests.post(f"{AUTH_URL}/register", json=registration_data)
            
            if response.status_code == 201:
                data = response.json()
                self.access_token = data.get('access_token')
                
                self.print_result(True, f"User registered successfully: {data['user']['email']}")
                self.print_result(True, f"Access token received: {self.access_token[:20]}...")
                
                # Test duplicate email registration
                response2 = requests.post(f"{AUTH_URL}/register", json=registration_data)
                if response2.status_code == 400:
                    self.print_result(True, "Duplicate email registration properly rejected")
                else:
                    self.print_result(False, "Duplicate email registration should be rejected")
                
                return True
            else:
                self.print_result(False, f"Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Registration error: {e}")
            return False
    
    def test_password_validation(self):
        """Test password validation"""
        self.print_test_header("Password Validation")
        
        weak_passwords = [
            "123456",           # Too short, no complexity
            "password",         # Common password
            "Password",         # Missing digit and special char
            "Password123",      # Missing special char
            "password123!",     # Missing uppercase
        ]
        
        success_count = 0
        
        for weak_password in weak_passwords:
            try:
                registration_data = {
                    "email": f"weak_{int(time.time())}@example.com",
                    "password": weak_password,
                    "first_name": "Test",
                    "last_name": "User"
                }
                
                response = requests.post(f"{AUTH_URL}/register", json=registration_data)
                
                if response.status_code == 400:
                    self.print_result(True, f"Weak password '{weak_password}' properly rejected")
                    success_count += 1
                else:
                    self.print_result(False, f"Weak password '{weak_password}' should be rejected")
                    
            except Exception as e:
                self.print_result(False, f"Password validation error: {e}")
        
        return success_count == len(weak_passwords)
    
    def test_user_login(self):
        """Test user login"""
        self.print_test_header("User Login")
        
        try:
            # Test successful login
            login_data = {
                "email": self.test_user_email,
                "password": self.test_password
            }
            
            response = requests.post(f"{AUTH_URL}/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.refresh_token = data.get('refresh_token')
                
                self.print_result(True, f"Login successful for: {data['user']['email']}")
                self.print_result(True, f"Access token: {self.access_token[:20]}...")
                self.print_result(True, f"Refresh token: {self.refresh_token[:20]}...")
                
                # Test invalid login
                invalid_login = {
                    "email": self.test_user_email,
                    "password": "wrongpassword"
                }
                
                response2 = requests.post(f"{AUTH_URL}/login", json=invalid_login)
                if response2.status_code == 401:
                    self.print_result(True, "Invalid password properly rejected")
                else:
                    self.print_result(False, "Invalid password should be rejected")
                
                return True
            else:
                self.print_result(False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Login error: {e}")
            return False
    
    def test_protected_routes(self):
        """Test protected routes"""
        self.print_test_header("Protected Routes")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Test accessing user info
            response = requests.get(f"{AUTH_URL}/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, f"Protected route accessible: {data['user']['email']}")
                
                # Test without token
                response2 = requests.get(f"{AUTH_URL}/me")
                if response2.status_code == 401:
                    self.print_result(True, "Protected route properly secured without token")
                else:
                    self.print_result(False, "Protected route should require authentication")
                
                # Test with invalid token
                invalid_headers = {"Authorization": "Bearer invalid_token"}
                response3 = requests.get(f"{AUTH_URL}/me", headers=invalid_headers)
                if response3.status_code == 401:
                    self.print_result(True, "Invalid token properly rejected")
                else:
                    self.print_result(False, "Invalid token should be rejected")
                
                return True
            else:
                self.print_result(False, f"Protected route access failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Protected route error: {e}")
            return False
    
    def test_token_refresh(self):
        """Test token refresh"""
        self.print_test_header("Token Refresh")
        
        try:
            refresh_data = {"refresh_token": self.refresh_token}
            
            response = requests.post(f"{AUTH_URL}/refresh", json=refresh_data)
            
            if response.status_code == 200:
                data = response.json()
                new_access_token = data.get('access_token')
                
                self.print_result(True, f"Token refreshed successfully: {new_access_token[:20]}...")
                
                # Test with invalid refresh token
                invalid_refresh = {"refresh_token": "invalid_refresh_token"}
                response2 = requests.post(f"{AUTH_URL}/refresh", json=invalid_refresh)
                
                if response2.status_code == 401:
                    self.print_result(True, "Invalid refresh token properly rejected")
                else:
                    self.print_result(False, "Invalid refresh token should be rejected")
                
                # Update access token for further tests
                self.access_token = new_access_token
                return True
            else:
                self.print_result(False, f"Token refresh failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Token refresh error: {e}")
            return False
    
    def test_profile_update(self):
        """Test profile update"""
        self.print_test_header("Profile Update")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            update_data = {
                "first_name": "Updated",
                "last_name": "Name",
                "bio": "This is my updated bio",
                "website": "https://example.com"
            }
            
            response = requests.put(f"{AUTH_URL}/me", json=update_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                user = data['user']
                
                self.print_result(True, f"Profile updated: {user['first_name']} {user['last_name']}")
                self.print_result(True, f"Bio updated: {user.get('bio', 'N/A')}")
                self.print_result(True, f"Website updated: {user.get('website', 'N/A')}")
                return True
            else:
                self.print_result(False, f"Profile update failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Profile update error: {e}")
            return False
    
    def test_password_change(self):
        """Test password change"""
        self.print_test_header("Password Change")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            new_password = "NewTestPass123!"
            
            change_data = {
                "current_password": self.test_password,
                "new_password": new_password
            }
            
            response = requests.post(f"{AUTH_URL}/change-password", json=change_data, headers=headers)
            
            if response.status_code == 200:
                self.print_result(True, "Password changed successfully")
                
                # Test login with new password
                login_data = {
                    "email": self.test_user_email,
                    "password": new_password
                }
                
                response2 = requests.post(f"{AUTH_URL}/login", json=login_data)
                if response2.status_code == 200:
                    self.print_result(True, "Login successful with new password")
                    # Update tokens
                    data = response2.json()
                    self.access_token = data.get('access_token')
                    self.refresh_token = data.get('refresh_token')
                else:
                    self.print_result(False, "Login failed with new password")
                
                # Update password for cleanup
                self.test_password = new_password
                return True
            else:
                self.print_result(False, f"Password change failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Password change error: {e}")
            return False
    
    def test_session_management(self):
        """Test session management"""
        self.print_test_header("Session Management")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Get user sessions
            response = requests.get(f"{AUTH_URL}/sessions", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                sessions = data.get('sessions', [])
                
                self.print_result(True, f"Retrieved {len(sessions)} active sessions")
                
                # Test logout from current session
                response2 = requests.post(f"{AUTH_URL}/logout", headers=headers)
                if response2.status_code == 200:
                    self.print_result(True, "Logout successful")
                    
                    # Test accessing protected route after logout
                    response3 = requests.get(f"{AUTH_URL}/me", headers=headers)
                    if response3.status_code == 401:
                        self.print_result(True, "Access denied after logout")
                    else:
                        self.print_result(False, "Should be denied access after logout")
                else:
                    self.print_result(False, "Logout failed")
                
                return True
            else:
                self.print_result(False, f"Session retrieval failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Session management error: {e}")
            return False
    
    def test_api_integration(self):
        """Test API integration with authentication"""
        self.print_test_header("API Integration")
        
        try:
            # Login again for this test
            login_data = {
                "email": self.test_user_email,
                "password": self.test_password
            }
            
            response = requests.post(f"{AUTH_URL}/login", json=login_data)
            if response.status_code != 200:
                self.print_result(False, "Could not login for integration test")
                return False
            
            data = response.json()
            token = data.get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test public endpoint (no auth required)
            response1 = requests.get(f"{BASE_URL}/api/mock-data")
            if response1.status_code == 200:
                self.print_result(True, "Public endpoint accessible without auth")
            else:
                self.print_result(False, "Public endpoint should be accessible")
            
            # Test semi-protected endpoint (optional auth)
            response2 = requests.get(f"{BASE_URL}/api/inspections?address=123 Test St, Sydney, 2000&date=2024-01-20")
            if response2.status_code == 200:
                data2 = response2.json()
                self.print_result(True, f"Inspections endpoint accessible: authenticated={data2.get('authenticated', False)}")
            else:
                self.print_result(False, "Inspections endpoint should be accessible")
            
            # Test with authentication
            response3 = requests.get(
                f"{BASE_URL}/api/inspections?address=123 Test St, Sydney, 2000&date=2024-01-20",
                headers=headers
            )
            if response3.status_code == 200:
                data3 = response3.json()
                self.print_result(True, f"Inspections with auth: authenticated={data3.get('authenticated', False)}")
            else:
                self.print_result(False, "Inspections with auth should work")
            
            return True
            
        except Exception as e:
            self.print_result(False, f"API integration error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting Authentication Test Suite")
        print(f"📍 Testing API at: {BASE_URL}")
        print(f"🔐 Auth endpoints: {AUTH_URL}")
        print(f"📧 Test user email: {self.test_user_email}")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Password Validation", self.test_password_validation),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Protected Routes", self.test_protected_routes),
            ("Token Refresh", self.test_token_refresh),
            ("Profile Update", self.test_profile_update),
            ("Password Change", self.test_password_change),
            ("Session Management", self.test_session_management),
            ("API Integration", self.test_api_integration),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Print summary
        self.print_test_header("Test Summary")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n📊 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Authentication system is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the implementation.")
        
        return passed == total

def main():
    """Main test function"""
    tester = AuthenticationTester()
    
    try:
        success = tester.run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        exit(1)

if __name__ == "__main__":
    main()