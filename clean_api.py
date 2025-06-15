#!/usr/bin/env python3
"""
Clean Real Estate Open Home Optimizer API
No scraping - uses mock data only while waiting for legitimate Domain API access
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

def generate_mock_data(date, suburb="suburb", postcode="2000"):
    """Generate realistic mock inspection data for demo purposes"""
    
    # Realistic suburb names for Sydney
    suburbs = [
        "Bondi", "Surry Hills", "Paddington", "Newtown", "Glebe", 
        "Manly", "Chatswood", "Parramatta", "Hornsby", "Cronulla",
        "Balmain", "Leichhardt", "Rozelle", "Annandale", "Dulwich Hill"
    ]
    
    # Street names
    street_names = [
        "George Street", "King Street", "Queen Street", "Park Avenue", "High Street",
        "Church Street", "Victoria Road", "Oxford Street", "Crown Street", "Bay Street",
        "Hill Road", "Beach Road", "Forest Way", "Garden Street", "River Road"
    ]
    
    # Property types for variety
    property_types = ["House", "Apartment", "Townhouse", "Villa", "Studio"]
    
    time_slots = [
        ("09:00", "09:30"), ("09:30", "10:00"), ("10:00", "10:30"),
        ("10:30", "11:00"), ("11:00", "11:30"), ("11:30", "12:00"),
        ("12:00", "12:30"), ("12:30", "13:00"), ("13:00", "13:30"),
        ("13:30", "14:00"), ("14:00", "14:30"), ("14:30", "15:00"),
        ("15:00", "15:30"), ("15:30", "16:00")
    ]
    
    results = []
    num_inspections = random.randint(12, 25)  # More realistic number
    
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
            "date": date,
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

def parse_criteria_value(criteria_str):
    """Parse criteria string like '3-4', '2+', '1' into min/max values"""
    if '+' in criteria_str:
        # Handle cases like '2+', '3+'
        min_val = int(criteria_str.replace('+', ''))
        return min_val, float('inf')
    elif '-' in criteria_str:
        # Handle cases like '3-4', '1-2'
        parts = criteria_str.split('-')
        return int(parts[0]), int(parts[1])
    else:
        # Handle exact values like '3', '2'
        val = int(criteria_str)
        return val, val

def filter_similar_properties(inspections, similar_criteria):
    """Filter inspections based on similar property criteria"""
    
    # Parse criteria
    bed_min, bed_max = parse_criteria_value(similar_criteria['bedrooms'])
    bath_min, bath_max = parse_criteria_value(similar_criteria['bathrooms'])
    car_min, car_max = parse_criteria_value(similar_criteria['car_spots'])
    
    filtered_inspections = []
    
    for inspection in inspections:
        property_details = inspection.get('property_details', {})
        
        # Get property features
        bedrooms = property_details.get('bedrooms', 3)
        bathrooms = property_details.get('bathrooms', 2)
        car_spots = property_details.get('car_spots', 1)
        
        # Check if property matches criteria
        matches_bedrooms = bed_min <= bedrooms <= bed_max
        matches_bathrooms = bath_min <= bathrooms <= bath_max
        matches_car_spots = car_min <= car_spots <= car_max
        
        if matches_bedrooms and matches_bathrooms and matches_car_spots:
            filtered_inspections.append(inspection)
    
    return filtered_inspections

def analyze_competition(inspections, time_filter):
    """Analyze competition levels for different time slots"""
    time_slots = {}
    
    # Initialize 30-minute time slots
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
    
    # Count inspections per time slot
    for inspection in inspections:
        start_time = inspection['start_time']
        # Round to nearest 30-minute slot
        hour, minute = map(int, start_time.split(':'))
        rounded_minute = 0 if minute < 30 else 30
        slot_key = f"{hour:02d}:{rounded_minute:02d}"
        
        if slot_key in time_slots:
            time_slots[slot_key]['count'] += 1
            time_slots[slot_key]['properties'].append(inspection)
    
    # Determine competition levels
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

def extract_suburb_postcode(address):
    """Extract suburb and postcode from address string"""
    parts = address.strip().split(',')
    if len(parts) < 2:
        return "sydney", "2000"  # Default values
    suburb = parts[-2].strip().lower().replace(' ', '-')
    postcode = parts[-1].strip()
    return suburb, postcode

@app.route('/api/inspections', methods=['GET'])
def get_inspections():
    """API endpoint to get inspection data - uses mock data only"""
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

    if not address or not date:
        return jsonify({'error': 'Missing address or date'}), 400

    suburb, postcode = extract_suburb_postcode(address)

    try:
        print(f"🏠 Generating mock data for {address} on {date}")
        print(f"🎯 Similar property criteria: {similar_property_criteria}")
        
        # Generate mock inspection data
        inspections = generate_mock_data(date, suburb, postcode)
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
            'recommendations': sorted_slots[:5],  # Top 5 recommendations
            'total_inspections': len(inspections),
            'similar_inspections': len(filtered_inspections),
            'search_params': {
                'address': address,
                'suburb': suburb,
                'postcode': postcode,
                'date': date,
                'time_filter': time_filter,
                'similar_property_criteria': similar_property_criteria
            },
            'data_source': 'mock_data',
            'note': 'Using mock data while awaiting Domain API access'
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'data_source': 'mock_data',
        'scraping_disabled': True,
        'note': 'Scraping functionality removed - using mock data only'
    })

@app.route('/api/mock-data', methods=['GET'])
def get_mock_data():
    """Get mock data for testing"""
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
    mock_inspections = generate_mock_data(date)
    
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

if __name__ == '__main__':
    print("🚀 Starting Clean Real Estate Open Home Optimizer API...")
    print("📍 API will be available at: http://localhost:5001")
    print("🔗 Health check: http://localhost:5001/api/health")
    print("🧪 Mock data: http://localhost:5001/api/mock-data")
    print("⚠️  SCRAPING DISABLED - Using mock data only")
    print("🤝 Ready for Domain API integration when available")
    app.run(debug=True, port=5001, host='0.0.0.0')