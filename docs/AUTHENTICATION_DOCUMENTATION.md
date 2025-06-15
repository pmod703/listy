# 🔐 Authentication System Documentation

## Overview

This document provides comprehensive information about the authentication system implemented for the Real Estate Open Home Optimizer application. The system includes user registration, login, JWT tokens, password security, session management, and protected routes.

## 🏗️ Architecture

### **Components**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Auth Routes   │    │   Auth Service  │
│   (React)       │◄──►│   (Flask)       │◄──►│   (Business)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Auth Middleware│    │   Database      │
                       │  (Protection)   │    │   (PostgreSQL)  │
                       └─────────────────┘    └─────────────────┘
```

### **Key Files**

| File | Purpose | Description |
|------|---------|-------------|
| `auth_models.py` | Data Models | Enhanced User model with authentication |
| `auth_service.py` | Business Logic | Authentication operations and security |
| `auth_middleware.py` | Route Protection | Decorators and middleware for security |
| `auth_routes.py` | API Endpoints | Flask routes for authentication |
| `auth_integration.py` | Complete API | Integrated API with authentication |
| `auth_migration.sql` | Database Schema | Authentication tables and functions |

## 🔑 Features

### **✅ User Management**
- User registration with validation
- Secure password hashing (bcrypt)
- Email verification system
- Profile management
- Account activation/deactivation

### **✅ Authentication**
- JWT token-based authentication
- Access tokens (24 hours) and refresh tokens (30 days)
- Token refresh mechanism
- Session management and tracking
- Multiple device support

### **✅ Security**
- Password strength validation
- Account lockout after failed attempts
- Rate limiting support
- Audit logging
- CORS protection
- Security headers

### **✅ Authorization**
- Protected routes with decorators
- Optional authentication
- Role-based access (admin support)
- User-specific data access

## 🗄️ Database Schema

### **Enhanced Users Table**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    agency_name VARCHAR(255),
    license_number VARCHAR(100),
    
    -- Authentication fields
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    failed_login_attempts INTEGER DEFAULT 0,
    last_failed_login TIMESTAMP,
    account_locked_until TIMESTAMP,
    
    -- Profile fields
    profile_image_url VARCHAR(500),
    bio TEXT,
    website VARCHAR(255),
    
    -- Verification tokens
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### **User Sessions Table**
```sql
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Audit Log Table**
```sql
CREATE TABLE auth_audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(255),
    additional_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 Setup Instructions

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Environment Configuration**
Create/update `.env` file:
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=realestate_optimizer
DB_USER=postgres
DB_PASSWORD=your_password

# Authentication Configuration
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# Application Settings
ENVIRONMENT=development
DEBUG=True
```

### **3. Database Migration**
```bash
# Run authentication migration
python database_migration.py --sql auth_migration.sql

# Or initialize everything
python database_migration.py init
```

### **4. Start the Server**
```bash
python auth_integration.py
```

### **5. Test the System**
```bash
python test_authentication.py
```

## 🔐 API Endpoints

### **Authentication Routes**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | User login | No |
| POST | `/api/auth/refresh` | Refresh access token | No |
| POST | `/api/auth/logout` | Logout current session | Yes |
| POST | `/api/auth/logout-all` | Logout all sessions | Yes |
| GET | `/api/auth/me` | Get user profile | Yes |
| PUT | `/api/auth/me` | Update user profile | Yes |
| POST | `/api/auth/change-password` | Change password | Yes |
| POST | `/api/auth/request-password-reset` | Request password reset | No |
| POST | `/api/auth/reset-password` | Reset password | No |
| GET | `/api/auth/verify-email/{token}` | Verify email | No |
| GET | `/api/auth/sessions` | Get active sessions | Yes |
| GET | `/api/auth/validate-token` | Validate token | Optional |

### **Protected Application Routes**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/inspections` | Get inspections | Optional |
| GET | `/api/users/{id}/properties` | Get user properties | Yes |
| GET | `/api/users/{id}/analysis-history` | Get analysis history | Yes |
| POST | `/api/properties` | Create property | Yes |
| POST | `/api/criteria` | Create criteria | Yes |

## 📝 Usage Examples

### **1. User Registration**
```python
import requests

registration_data = {
    "email": "agent@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "agency_name": "Best Real Estate",
    "license_number": "RE123456",
    "phone": "+1234567890"
}

response = requests.post(
    "http://localhost:5001/api/auth/register",
    json=registration_data
)

if response.status_code == 201:
    data = response.json()
    access_token = data['access_token']
    print(f"Registration successful! Token: {access_token}")
```

### **2. User Login**
```python
login_data = {
    "email": "agent@example.com",
    "password": "SecurePass123!"
}

response = requests.post(
    "http://localhost:5001/api/auth/login",
    json=login_data
)

if response.status_code == 200:
    data = response.json()
    access_token = data['access_token']
    refresh_token = data['refresh_token']
    print(f"Login successful!")
```

### **3. Accessing Protected Routes**
```python
headers = {
    "Authorization": f"Bearer {access_token}"
}

# Get user profile
response = requests.get(
    "http://localhost:5001/api/auth/me",
    headers=headers
)

# Create property
property_data = {
    "full_address": "123 Main St, Sydney NSW 2000",
    "property_type": "house",
    "bedrooms": 3,
    "bathrooms": 2,
    "car_spaces": 1,
    "listing_price": 800000
}

response = requests.post(
    "http://localhost:5001/api/properties",
    json=property_data,
    headers=headers
)
```

### **4. Token Refresh**
```python
refresh_data = {
    "refresh_token": refresh_token
}

response = requests.post(
    "http://localhost:5001/api/auth/refresh",
    json=refresh_data
)

if response.status_code == 200:
    data = response.json()
    new_access_token = data['access_token']
```

## 🛡️ Security Features

### **Password Security**
- **Minimum 8 characters**
- **Must contain**: uppercase, lowercase, digit, special character
- **bcrypt hashing** with salt
- **Common password rejection**

```python
# Password validation example
def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True
```

### **Account Lockout**
- **5 failed attempts** → Account locked for 30 minutes
- **Automatic unlock** after lockout period
- **Failed attempt tracking** with timestamps

### **JWT Token Security**
- **Access tokens**: 24 hours expiry
- **Refresh tokens**: 30 days expiry
- **Secure signing** with secret key
- **Token validation** on every request

### **Session Management**
- **Multiple device support**
- **Session tracking** with IP and user agent
- **Automatic cleanup** of expired sessions
- **Manual logout** from specific or all sessions

## 🔧 Middleware and Decorators

### **@token_required**
Requires valid JWT token for route access.

```python
@app.route('/api/protected')
@token_required
def protected_route():
    current_user = get_current_user()
    return jsonify({'user': current_user.to_dict()})
```

### **@optional_auth**
Optional authentication - user can be None.

```python
@app.route('/api/public')
@optional_auth
def public_route():
    current_user = get_current_user()  # May be None
    authenticated = current_user is not None
    return jsonify({'authenticated': authenticated})
```

### **@verified_user_required**
Requires verified user (email verified).

```python
@app.route('/api/verified-only')
@verified_user_required
def verified_route():
    current_user = get_current_user()
    return jsonify({'verified_user': current_user.email})
```

## 📊 Monitoring and Logging

### **Audit Logging**
All authentication events are logged:
- User registration
- Login attempts (success/failure)
- Password changes
- Account lockouts
- Token refresh
- Logout events

### **Security Views**
```sql
-- Active sessions
SELECT * FROM active_user_sessions;

-- Authentication statistics
SELECT * FROM auth_statistics;

-- User security summary
SELECT * FROM user_security_summary;
```

### **Maintenance Functions**
```sql
-- Clean up expired sessions
SELECT cleanup_expired_sessions();

-- Log authentication event
SELECT log_auth_event(user_id, 'login', ip_address, user_agent, true);
```

## 🧪 Testing

### **Automated Test Suite**
```bash
python test_authentication.py
```

**Tests Include:**
- ✅ Health check
- ✅ Password validation
- ✅ User registration
- ✅ User login
- ✅ Protected routes
- ✅ Token refresh
- ✅ Profile updates
- ✅ Password changes
- ✅ Session management
- ✅ API integration

### **Manual Testing**
```bash
# Test registration
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'

# Test login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'

# Test protected route
curl -X GET http://localhost:5001/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🚀 Production Deployment

### **Environment Variables**
```bash
# Production settings
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-super-secure-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Database (use connection pooling)
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Security
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_ENABLED=True
```

### **Security Checklist**
- ✅ Use HTTPS in production
- ✅ Set secure secret keys
- ✅ Enable rate limiting
- ✅ Configure CORS properly
- ✅ Set up database backups
- ✅ Monitor authentication logs
- ✅ Regular security updates

### **Performance Optimization**
- **Connection pooling** for database
- **Redis caching** for sessions (optional)
- **Rate limiting** with Redis
- **CDN** for static assets
- **Load balancing** for high traffic

## 🔄 Integration with Frontend

### **React Integration Example**
```javascript
// Authentication context
const AuthContext = createContext();

// Login function
const login = async (email, password) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    setUser(data.user);
  }
};

// Protected API calls
const apiCall = async (url, options = {}) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.status === 401) {
    // Token expired, try refresh
    await refreshToken();
    // Retry original request
  }
  
  return response;
};
```

## 🔮 Future Enhancements

### **Planned Features**
- **OAuth integration** (Google, Facebook)
- **Two-factor authentication** (2FA)
- **Advanced role management**
- **API key authentication**
- **Single sign-on (SSO)**
- **Advanced rate limiting**
- **Geolocation-based security**

### **Scalability Improvements**
- **Redis session storage**
- **Distributed rate limiting**
- **Microservices architecture**
- **Event-driven authentication**
- **Advanced monitoring**

This authentication system provides enterprise-grade security for your Real Estate Open Home Optimizer application while maintaining ease of use and integration! 🔐