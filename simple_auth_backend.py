#!/usr/bin/env python3
"""
Simple Authentication Backend
A minimal Flask app with authentication that doesn't require database setup
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
import random

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'demo-secret-key-change-in-production'
app.config['JWT_SECRET_KEY'] = 'demo-jwt-secret-key-change-in-production'

# In-memory user storage for demo
DEMO_USERS = {
    'demo@realestate.com': {
        'id': 1,
        'email': 'demo@realestate.com',
        'password_hash': bcrypt.hashpw('DemoPass123!'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        'first_name': 'Demo',
        'last_name': 'User',
        'agency_name': 'Demo Real Estate',
        'license_number': 'DEMO123',
        'created_at': datetime.now().isoformat()
    },
    'agent@realestate.com': {
        'id': 2,
        'email': 'agent@realestate.com',
        'password_hash': bcrypt.hashpw('AgentPass123!'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        'first_name': 'Real Estate',
        'last_name': 'Agent',
        'agency_name': 'Premium Properties',
        'license_number': 'AGENT456',
        'created_at': datetime.now().isoformat()
    }
}

# In-memory token storage for demo
ACTIVE_TOKENS = set()

def generate_token(user_data):
    """Generate JWT token"""
    payload = {
        'user_id': user_data['id'],
        'email': user_data['email'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        if token not in ACTIVE_TOKENS:
            return None
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# =====================================================
# AUTHENTICATION ROUTES
# =====================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check if user exists
        user = DEMO_USERS.get(email)
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate tokens
        access_token = generate_token(user)
        refresh_token = generate_token(user)  # In real app, this would be different
        
        # Store tokens
        ACTIVE_TOKENS.add(access_token)
        ACTIVE_TOKENS.add(refresh_token)
        
        # Return user data (without password)
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return jsonify({
            'message': 'Login successful',
            'user': user_data,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer'
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check if user already exists
        if email in DEMO_USERS:
            return jsonify({'error': 'User already exists'}), 400
        
        # Create new user
        user_id = len(DEMO_USERS) + 1
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        new_user = {
            'id': user_id,
            'email': email,
            'password_hash': password_hash,
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
            'agency_name': data.get('agency_name', ''),
            'license_number': data.get('license_number', ''),
            'created_at': datetime.now().isoformat()
        }
        
        DEMO_USERS[email] = new_user
        
        # Generate token
        access_token = generate_token(new_user)
        ACTIVE_TOKENS.add(access_token)
        
        # Return user data (without password)
        user_data = {k: v for k, v in new_user.items() if k != 'password_hash'}
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user_data,
            'access_token': access_token,
            'token_type': 'Bearer'
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/validate-token', methods=['GET'])
def validate_token():
    """Validate token endpoint"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'valid': False, 'message': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'valid': False, 'message': 'Invalid or expired token'}), 401
        
        # Get user data
        user_email = payload['email']
        user = DEMO_USERS.get(user_email)
        
        if not user:
            return jsonify({'valid': False, 'message': 'User not found'}), 401
        
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return jsonify({
            'valid': True,
            'user': user_data
        }), 200
        
    except Exception as e:
        print(f"Token validation error: {e}")
        return jsonify({'valid': False, 'error': 'Token validation failed'}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get user data
        user_email = payload['email']
        user = DEMO_USERS.get(user_email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return jsonify({'user': user_data}), 200
        
    except Exception as e:
        print(f"Get user error: {e}")
        return jsonify({'error': 'Failed to get user information'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            ACTIVE_TOKENS.discard(token)
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@app.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    """Refresh token endpoint"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'error': 'Refresh token is required'}), 400
        
        payload = verify_token(refresh_token)
        if not payload:
            return jsonify({'error': 'Invalid or expired refresh token'}), 401
        
        # Get user data
        user_email = payload['email']
        user = DEMO_USERS.get(user_email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        # Generate new access token
        new_access_token = generate_token(user)
        ACTIVE_TOKENS.add(new_access_token)
        
        return jsonify({
            'access_token': new_access_token,
            'token_type': 'Bearer'
        }), 200
        
    except Exception as e:
        print(f"Token refresh error: {e}")
        return jsonify({'error': 'Token refresh failed'}), 500

# =====================================================
# MOCK DATA GENERATION
# =====================================================

def generate_mock_data(date_str: str, suburb="sydney", postcode="2000"):
    """Generate mock inspection data"""
    suburbs = [
        "Bondi", "Surry Hills", "Paddington", "Newtown", "Glebe", 
        "Manly", "Chatswood", "Parramatta", "Hornsby", "Cronulla",
        "Balmain", "Leichhardt", "Rozelle", "Annandale", "Dulwich Hill"
    ]
    
    street_names = [
        "George Street", "King Street", "Queen Street", "Park Avenue", "High Street",
        "Church Street", "Victoria Road", "Oxford Street", "Crown Street", "Bay Street",
        "Hill Road", "Beach Road", "Forest Way", "Garden Street", "River Road"
    ]
    
    property_types = ["House", "Apartment", "Townhouse", "Villa", "Studio"]
    
    time_slots = [
        ("09:00", "09:30"), ("09:30", "10:00"), ("10:00", "10:30"),
        ("10:30", "11:00"), ("11:00", "11:30"), ("11:30", "12:00"),
        ("12:00", "12:30"), ("12:30", "13:00"), ("13:00", "13:30"),
        ("13:30", "14:00"), ("14:00", "14:30"), ("14:30", "15:00"),
        ("15:00", "15:30"), ("15:30", "16:00")
    ]
    
    results = []
    num_inspections = random.randint(12, 25)
    
    for i in range(num_inspections):
        bedrooms = random.choices([1, 2, 3, 4, 5, 6], weights=[10, 25, 30, 25, 8, 2])[0]
        bathrooms = random.choices([1, 2, 3, 4], weights=[20, 50, 25, 5])[0]
        car_spots = random.choices([0, 1, 2, 3, 4], weights=[15, 35, 35, 12, 3])[0]
        
        street_number = random.randint(1, 999)
        street = random.choice(street_names)
        suburb_name = random.choice(suburbs)
        property_type = random.choice(property_types)
        
        start_time, end_time = random.choice(time_slots)
        
        results.append({
            "address": f"{street_number} {street}, {suburb_name} NSW {postcode}",
            "date": date_str,
            "start_time": start_time,
            "end_time": end_time,
            "property_details": {
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "car_spots": car_spots,
                "property_type": property_type
            }
        })
    
    return results

# =====================================================
# API ENDPOINTS
# =====================================================

@app.route('/api/inspections', methods=['GET'])
def get_inspections():
    """Get inspection data"""
    address = request.args.get('address')
    date = request.args.get('date')
    
    if not address or not date:
        return jsonify({'error': 'Missing address or date'}), 400

    try:
        # Generate mock inspection data
        inspections = generate_mock_data(date)
        
        response = {
            'inspections': inspections,
            'total_inspections': len(inspections),
            'search_params': {
                'address': address,
                'date': date
            },
            'data_source': 'mock_data',
            'note': 'Using mock data for demonstration'
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'authentication': 'enabled',
        'demo_users': list(DEMO_USERS.keys()),
        'features': ['authentication', 'mock_data']
    })

if __name__ == '__main__':
    print("🚀 Starting Simple Authentication Backend...")
    print("📍 API will be available at: http://localhost:5001")
    print("🔗 Health check: http://localhost:5001/api/health")
    print("🔐 Authentication endpoints: /api/auth/*")
    print("👤 Demo users:")
    for email in DEMO_USERS.keys():
        print(f"   - {email}")
    print("🔑 Demo password: DemoPass123! or AgentPass123!")
    print("")
    
    app.run(debug=True, port=5001, host='0.0.0.0')