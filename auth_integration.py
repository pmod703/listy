#!/usr/bin/env python3
"""
Authentication Integration
Complete Flask app with authentication integrated into the clean API
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from datetime import datetime, date, time
import random
from typing import List, Dict, Any
import os

# Authentication imports
from auth_routes import auth_bp
from auth_middleware import AuthMiddleware, token_required, optional_auth, get_current_user
from auth_service import AuthService

# Database imports
from database_models import (
    User, Property, Suburb, PropertyInspection, 
    SimilarPropertyCriteria, AnalysisResult,
    PropertyService, AnalysisService
)
from database_config import get_db_session

app = Flask(__name__)
CORS(app)

# Configure Flask app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-change-in-production')

# Initialize authentication middleware
auth_middleware = AuthMiddleware(app)

# Register authentication blueprint
app.register_blueprint(auth_bp)

# =====================================================
# MOCK DATA GENERATION (Enhanced with Database)
# =====================================================

def generate_mock_data_with_db(date_str: str, suburb="sydney", postcode="2000"):
    """Generate mock data and optionally save to database"""
    
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
        # Generate realistic property details
        bedrooms = random.choices([1, 2, 3, 4, 5, 6], weights=[10, 25, 30, 25, 8, 2])[0]
        bathrooms = random.choices([1, 2, 3, 4], weights=[20, 50, 25, 5])[0]
        car_spots = random.choices([0, 1, 2, 3, 4], weights=[15, 35, 35, 12, 3])[0]
        
        # Generate address
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

def save_analysis_to_db(user_id: int, property_id: int, analysis_data: Dict[str, Any]):
    """Save analysis results to database"""
    try:
        with next(get_db_session()) as db:
            analysis = AnalysisResult(
                user_id=user_id,
                property_id=property_id,
                analysis_date=datetime.strptime(analysis_data['date'], '%Y-%m-%d').date(),
                time_window_start=datetime.strptime(analysis_data['time_filter']['start'], '%H:%M').time(),
                time_window_end=datetime.strptime(analysis_data['time_filter']['end'], '%H:%M').time(),
                search_radius_km=analysis_data.get('radius', 5.0),
                total_properties_found=analysis_data['total_inspections'],
                similar_properties_count=analysis_data['similar_inspections'],
                time_slot_analysis=analysis_data['competition_analysis'],
                recommendations=analysis_data['recommendations'],
                data_source='mock_data'
            )
            
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            
            return analysis.id
    except Exception as e:
        print(f"Error saving analysis to database: {e}")
        return None

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def parse_criteria_value(criteria_str):
    """Parse criteria string like '3-4', '2+', '1' into min/max values"""
    if '+' in criteria_str:
        min_val = int(criteria_str.replace('+', ''))
        return min_val, float('inf')
    elif '-' in criteria_str:
        parts = criteria_str.split('-')
        return int(parts[0]), int(parts[1])
    else:
        val = int(criteria_str)
        return val, val

def filter_similar_properties(inspections, similar_criteria):
    """Filter inspections based on similar property criteria"""
    bed_min, bed_max = parse_criteria_value(similar_criteria['bedrooms'])
    bath_min, bath_max = parse_criteria_value(similar_criteria['bathrooms'])
    car_min, car_max = parse_criteria_value(similar_criteria['car_spots'])
    
    filtered_inspections = []
    
    for inspection in inspections:
        property_details = inspection.get('property_details', {})
        
        bedrooms = property_details.get('bedrooms', 3)
        bathrooms = property_details.get('bathrooms', 2)
        car_spots = property_details.get('car_spots', 1)
        
        matches_bedrooms = bed_min <= bedrooms <= bed_max
        matches_bathrooms = bath_min <= bathrooms <= bath_max
        matches_car_spots = car_min <= car_spots <= car_max
        
        if matches_bedrooms and matches_bathrooms and matches_car_spots:
            filtered_inspections.append(inspection)
    
    return filtered_inspections

def analyze_competition(inspections, time_filter):
    """Analyze competition levels for different time slots"""
    time_slots = {}
    
    start_hour = int(time_filter.get('start', '09:00').split(':')[0])
    end_hour = int(time_filter.get('end', '16:00').split(':')[0])
    
    for hour in range(start_hour, end_hour + 1):
        for minute in [0, 30]:
            if hour == end_hour and minute > 0:
                break
            time_key = f"{hour:02d}:{minute:02d}"
            time_slots[time_key] = {
                'time': time_key,
                'count': 0,
                'competition': 'low',
                'properties': []
            }
    
    for inspection in inspections:
        start_time = inspection['start_time']
        hour, minute = map(int, start_time.split(':'))
        rounded_minute = 0 if minute < 30 else 30
        slot_key = f"{hour:02d}:{rounded_minute:02d}"
        
        if slot_key in time_slots:
            time_slots[slot_key]['count'] += 1
            time_slots[slot_key]['properties'].append(inspection)
    
    for slot in time_slots.values():
        count = slot['count']
        if count <= 2:
            slot['competition'] = 'low'
        elif count <= 5:
            slot['competition'] = 'medium'
        elif count <= 10:
            slot['competition'] = 'high'
        else:
            slot['competition'] = 'very-high'
    
    return list(time_slots.values())

# =====================================================
# PROTECTED API ENDPOINTS
# =====================================================

@app.route('/api/inspections', methods=['GET'])
@optional_auth
def get_inspections():
    """API endpoint to get inspection data with optional authentication"""
    address = request.args.get('address')
    date = request.args.get('date')
    time_filter = {
        'start': request.args.get('start_time', '09:00'),
        'end': request.args.get('end_time', '16:00')
    }
    similar_property_criteria = {
        'bedrooms': request.args.get('similar_bedrooms', '3-4'),
        'bathrooms': request.args.get('similar_bathrooms', '2+'),
        'car_spots': request.args.get('similar_car_spots', '1-2')
    }
    
    # Get optional parameters for database integration
    property_id = request.args.get('property_id', type=int)

    if not address or not date:
        return jsonify({'error': 'Missing address or date'}), 400

    try:
        current_user = get_current_user()
        print(f"🏠 Generating mock data for {address} on {date}")
        print(f"🎯 Similar property criteria: {similar_property_criteria}")
        if current_user:
            print(f"👤 Authenticated user: {current_user.email}")
        
        # Generate mock inspection data
        inspections = generate_mock_data_with_db(date)
        print(f"📊 Generated {len(inspections)} mock inspections")
        
        # Filter inspections based on similar property criteria
        filtered_inspections = filter_similar_properties(inspections, similar_property_criteria)
        print(f"🔍 Filtered to {len(filtered_inspections)} similar properties")
        
        # Analyze competition using filtered data
        competition_analysis = analyze_competition(filtered_inspections, time_filter)
        
        # Sort by competition level (best times first)
        sorted_slots = sorted(competition_analysis, key=lambda x: x['count'])
        
        response = {
            'inspections': inspections,
            'filtered_inspections': filtered_inspections,
            'competition_analysis': competition_analysis,
            'recommendations': sorted_slots[:5],
            'total_inspections': len(inspections),
            'similar_inspections': len(filtered_inspections),
            'search_params': {
                'address': address,
                'date': date,
                'time_filter': time_filter,
                'similar_property_criteria': similar_property_criteria
            },
            'data_source': 'mock_data',
            'authenticated': current_user is not None,
            'note': 'Using mock data while awaiting Domain API access'
        }
        
        # Save to database if user is authenticated and property_id provided
        if current_user and property_id:
            analysis_id = save_analysis_to_db(current_user.id, property_id, {
                'date': date,
                'time_filter': time_filter,
                'total_inspections': len(inspections),
                'similar_inspections': len(filtered_inspections),
                'competition_analysis': competition_analysis,
                'recommendations': sorted_slots[:5]
            })
            if analysis_id:
                response['analysis_id'] = analysis_id
                response['saved_to_database'] = True
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/properties', methods=['GET'])
@token_required
def get_user_properties(user_id):
    """Get all properties for a user (protected)"""
    try:
        current_user = get_current_user()
        
        # Users can only access their own properties (unless admin)
        if current_user.id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        with next(get_db_session()) as db:
            properties = PropertyService.get_properties_by_user(db, user_id)
            
            properties_data = []
            for prop in properties:
                properties_data.append({
                    'id': prop.id,
                    'address': prop.full_address,
                    'property_type': prop.property_type,
                    'bedrooms': prop.bedrooms,
                    'bathrooms': prop.bathrooms,
                    'car_spaces': prop.car_spaces,
                    'listing_price': float(prop.listing_price) if prop.listing_price else None,
                    'listing_status': prop.listing_status,
                    'created_at': prop.created_at.isoformat()
                })
            
            return jsonify({
                'user_id': user_id,
                'properties': properties_data,
                'total_properties': len(properties_data)
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/analysis-history', methods=['GET'])
@token_required
def get_analysis_history(user_id):
    """Get analysis history for a user (protected)"""
    try:
        current_user = get_current_user()
        
        # Users can only access their own analysis history
        if current_user.id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        limit = request.args.get('limit', 10, type=int)
        
        with next(get_db_session()) as db:
            analyses = AnalysisService.get_analysis_history(db, user_id, limit)
            
            history_data = []
            for analysis in analyses:
                history_data.append({
                    'id': analysis.id,
                    'property_id': analysis.property_id,
                    'analysis_date': analysis.analysis_date.isoformat(),
                    'total_properties': analysis.total_properties_found,
                    'similar_properties': analysis.similar_properties_count,
                    'data_source': analysis.data_source,
                    'created_at': analysis.created_at.isoformat()
                })
            
            return jsonify({
                'user_id': user_id,
                'analysis_history': history_data,
                'total_analyses': len(history_data)
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/properties', methods=['POST'])
@token_required
def create_property():
    """Create a new property (protected)"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        required_fields = ['full_address', 'property_type', 'bedrooms', 'bathrooms']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        with next(get_db_session()) as db:
            property_obj = PropertyService.create_property(db, current_user.id, {
                'full_address': data['full_address'],
                'property_type': data['property_type'],
                'bedrooms': data['bedrooms'],
                'bathrooms': data['bathrooms'],
                'car_spaces': data.get('car_spaces', 0),
                'listing_price': data.get('listing_price'),
                'listing_status': data.get('listing_status', 'active')
            })
            
            return jsonify({
                'id': property_obj.id,
                'message': 'Property created successfully',
                'property': {
                    'id': property_obj.id,
                    'address': property_obj.full_address,
                    'property_type': property_obj.property_type,
                    'bedrooms': property_obj.bedrooms,
                    'bathrooms': property_obj.bathrooms,
                    'car_spaces': property_obj.car_spaces
                }
            }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/criteria', methods=['POST'])
@token_required
def create_similar_property_criteria():
    """Create similar property criteria (protected)"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        required_fields = ['property_id', 'bedrooms_criteria', 'bathrooms_criteria', 'car_spaces_criteria']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        with next(get_db_session()) as db:
            # Verify user owns the property
            property_obj = db.query(Property).filter(
                Property.id == data['property_id'],
                Property.user_id == current_user.id
            ).first()
            
            if not property_obj:
                return jsonify({'error': 'Property not found or access denied'}), 404
            
            criteria = SimilarPropertyCriteria(
                user_id=current_user.id,
                property_id=data['property_id'],
                bedrooms_criteria=data['bedrooms_criteria'],
                bathrooms_criteria=data['bathrooms_criteria'],
                car_spaces_criteria=data['car_spaces_criteria'],
                property_types=data.get('property_types', []),
                price_range_percentage=data.get('price_range_percentage', 20.0),
                radius_km=data.get('radius_km', 5.0)
            )
            
            criteria.parse_criteria()  # Parse criteria strings
            
            db.add(criteria)
            db.commit()
            db.refresh(criteria)
            
            return jsonify({
                'id': criteria.id,
                'message': 'Similar property criteria created successfully',
                'criteria': {
                    'id': criteria.id,
                    'property_id': criteria.property_id,
                    'bedrooms_criteria': criteria.bedrooms_criteria,
                    'bathrooms_criteria': criteria.bathrooms_criteria,
                    'car_spaces_criteria': criteria.car_spaces_criteria
                }
            }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================
# PUBLIC ENDPOINTS
# =====================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with authentication status"""
    try:
        # Test database connection
        with next(get_db_session()) as db:
            db.execute("SELECT 1")
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0.0',
        'data_source': 'mock_data',
        'scraping_disabled': True,
        'database_status': db_status,
        'authentication_enabled': True,
        'features': [
            'user_authentication',
            'jwt_tokens',
            'password_security',
            'similar_property_criteria',
            'competition_analysis',
            'database_integration',
            'analysis_history',
            'protected_routes'
        ],
        'endpoints': {
            'auth': '/api/auth/*',
            'inspections': '/api/inspections (public)',
            'user_properties': '/api/users/{id}/properties (protected)',
            'analysis_history': '/api/users/{id}/analysis-history (protected)'
        },
        'note': 'Clean API with full authentication system'
    })

@app.route('/api/mock-data', methods=['GET'])
def get_mock_data():
    """Get mock data for testing (public)"""
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    time_filter = {
        'start': request.args.get('start_time', '09:00'),
        'end': request.args.get('end_time', '16:00')
    }
    similar_property_criteria = {
        'bedrooms': request.args.get('similar_bedrooms', '3-4'),
        'bathrooms': request.args.get('similar_bathrooms', '2+'),
        'car_spots': request.args.get('similar_car_spots', '1-2')
    }
    
    # Generate mock inspections
    mock_inspections = generate_mock_data_with_db(date)
    
    # Filter based on criteria
    filtered_inspections = filter_similar_properties(mock_inspections, similar_property_criteria)
    
    # Analyze competition
    competition_analysis = analyze_competition(filtered_inspections, time_filter)
    
    # Sort by competition level
    sorted_slots = sorted(competition_analysis, key=lambda x: x['count'])
    
    response = {
        'inspections': mock_inspections,
        'filtered_inspections': filtered_inspections,
        'competition_analysis': competition_analysis,
        'recommendations': sorted_slots[:5],
        'total_inspections': len(mock_inspections),
        'similar_inspections': len(filtered_inspections),
        'is_mock_data': True,
        'search_params': {
            'similar_property_criteria': similar_property_criteria,
            'time_filter': time_filter
        }
    }
    
    return jsonify(response)

# =====================================================
# ERROR HANDLERS
# =====================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Real Estate API with Full Authentication...")
    print("📍 API will be available at: http://localhost:5001")
    print("🔗 Health check: http://localhost:5001/api/health")
    print("🔐 Authentication: http://localhost:5001/api/auth/*")
    print("🧪 Mock data: http://localhost:5001/api/mock-data")
    print("🗄️  Database integration: Full support")
    print("🔒 Protected routes: Require authentication")
    print("⚠️  SCRAPING DISABLED - Using mock data only")
    print("🤝 Ready for Domain API integration when available")
    
    app.run(debug=True, port=5001, host='0.0.0.0')