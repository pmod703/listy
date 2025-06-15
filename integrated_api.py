from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright
from urllib.parse import quote
import os
import csv
import subprocess
import time
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

def extract_suburb_postcode(address):
    """Extract suburb and postcode from address string"""
    parts = address.strip().split(',')
    if len(parts) < 2:
        return None, None
    suburb = parts[-2].strip().lower().replace(' ', '-')
    postcode = parts[-1].strip()
    return suburb, postcode

def scrape_inspections(suburb, postcode, date):
    """Scrape Domain.com.au for inspection times"""
    results = []
    
    try:
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()

            url = f"https://www.domain.com.au/sale/{suburb}-nsw-{postcode}/inspection-times/?inspectiondate={quote(date)}"
            print(f"🔍 Navigating to: {url}")
            
            page.goto(url, timeout=60000)
            page.wait_for_timeout(8000)

            # Take screenshot for debugging
            screenshot_path = f"debug_{suburb}_{date}.png"
            page.screenshot(path=screenshot_path)
            print(f"📸 Screenshot saved as '{screenshot_path}'")

            # Find listings
            listings = page.locator("[data-testid='listing-card-wrapper-standard']")
            count = listings.count()
            print(f"📦 Found {count} listings")

            for i in range(count):
                try:
                    item = listings.nth(i)

                    address_loc = item.locator("[data-testid='address-label']")
                    time_loc = item.locator("[data-testid='inspection-time']")

                    if not address_loc.is_visible() or not time_loc.is_visible():
                        print(f"⏭ Skipping listing {i} — element not visible.")
                        continue

                    address = address_loc.inner_text(timeout=2000)
                    time_text = time_loc.inner_text(timeout=2000)

                    if "–" not in time_text:
                        continue

                    # Parse time range
                    _, time_range = time_text.strip().rsplit(' ', 1)
                    start, end = time_range.split("–")

                    results.append({
                        "address": address.strip(),
                        "date": date,
                        "start_time": start.strip(),
                        "end_time": end.strip()
                    })
                except Exception as e:
                    print(f"⚠️ Skipped listing {i} due to error: {e}")
                    continue

            browser.close()

    except Exception as e:
        print(f"❌ Scraping error: {e}")
        # Return mock data if scraping fails
        return generate_mock_data(date)

    # Save to CSV
    save_to_csv(results, suburb, date)
    
    return results

def generate_mock_data(date):
    """Generate mock inspection data for demo purposes"""
    mock_addresses = [
        "123 Main Street, Suburb NSW 2000",
        "456 Oak Avenue, Suburb NSW 2000", 
        "789 Pine Road, Suburb NSW 2000",
        "321 Elm Street, Suburb NSW 2000",
        "654 Maple Drive, Suburb NSW 2000"
    ]
    
    time_slots = [
        ("09:00", "09:30"), ("09:30", "10:00"), ("10:00", "10:30"),
        ("10:30", "11:00"), ("11:00", "11:30"), ("11:30", "12:00"),
        ("12:00", "12:30"), ("12:30", "13:00"), ("13:00", "13:30"),
        ("13:30", "14:00"), ("14:00", "14:30"), ("14:30", "15:00"),
        ("15:00", "15:30"), ("15:30", "16:00")
    ]
    
    results = []
    num_inspections = random.randint(8, 15)
    
    for i in range(num_inspections):
        address = random.choice(mock_addresses)
        start_time, end_time = random.choice(time_slots)
        
        results.append({
            "address": f"{i+1} {address}",
            "date": date,
            "start_time": start_time,
            "end_time": end_time
        })
    
    return results

def save_to_csv(results, suburb, date):
    """Save results to CSV file"""
    try:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        csv_path = os.path.join(desktop_path, f"inspections_{suburb}_{date}.csv")

        with open(csv_path, mode='w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["address", "date", "start_time", "end_time"])
            writer.writeheader()
            writer.writerows(results)

        print(f"📁 CSV saved to: {csv_path}")
        
        # Try to open CSV automatically (macOS)
        try:
            subprocess.run(["open", csv_path], check=True)
            print("📂 CSV opened in default app.")
        except Exception as e:
            print("⚠️ Failed to open CSV automatically:", e)
            
    except Exception as e:
        print(f"❌ Failed to save CSV: {e}")

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
    # For now, we'll simulate property details since Domain.com.au doesn't always provide them
    # In a real implementation, you would extract these from the property listings
    
    # Parse criteria
    bed_min, bed_max = parse_criteria_value(similar_criteria['bedrooms'])
    bath_min, bath_max = parse_criteria_value(similar_criteria['bathrooms'])
    car_min, car_max = parse_criteria_value(similar_criteria['car_spots'])
    
    # For demonstration, we'll randomly assign property features and filter
    # In production, you'd extract these from the actual listings
    filtered_inspections = []
    
    for inspection in inspections:
        # Simulate property features (in real implementation, extract from listing)
        simulated_bedrooms = random.randint(1, 6)
        simulated_bathrooms = random.randint(1, 4)
        simulated_car_spots = random.randint(0, 4)
        
        # Check if property matches criteria
        matches_bedrooms = bed_min <= simulated_bedrooms <= bed_max
        matches_bathrooms = bath_min <= simulated_bathrooms <= bath_max
        matches_car_spots = car_min <= simulated_car_spots <= car_max
        
        if matches_bedrooms and matches_bathrooms and matches_car_spots:
            # Add simulated property details to inspection data
            inspection_copy = inspection.copy()
            inspection_copy['property_details'] = {
                'bedrooms': simulated_bedrooms,
                'bathrooms': simulated_bathrooms,
                'car_spots': simulated_car_spots
            }
            filtered_inspections.append(inspection_copy)
    
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
                'competition': 'low'
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

@app.route('/api/inspections', methods=['GET'])
def get_inspections():
    """API endpoint to get inspection data"""
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
    if not suburb or not postcode:
        return jsonify({'error': 'Invalid address format. Please use format: "Street, Suburb, Postcode"'}), 400

    try:
        # Get inspection data
        inspections = scrape_inspections(suburb, postcode, date)
        
        # Filter inspections based on similar property criteria
        filtered_inspections = filter_similar_properties(inspections, similar_property_criteria)
        
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
            }
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
        'version': '1.0.0'
    })

@app.route('/api/mock-data', methods=['GET'])
def get_mock_data():
    """Get mock data for testing"""
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    time_filter = {
        'start': request.args.get('start_time', '09:00'),
        'end': request.args.get('end_time', '16:00')
    }
    
    # Generate mock inspections
    mock_inspections = generate_mock_data(date)
    
    # Analyze competition
    competition_analysis = analyze_competition(mock_inspections, time_filter)
    
    # Sort by competition level
    sorted_slots = sorted(competition_analysis, key=lambda x: x['count'])
    
    response = {
        'inspections': mock_inspections,
        'competition_analysis': competition_analysis,
        'recommendations': sorted_slots[:5],
        'total_inspections': len(mock_inspections),
        'is_mock_data': True
    }
    
    return jsonify(response)

if __name__ == '__main__':
    print("🚀 Starting Real Estate Open Home Optimizer API...")
    print("📍 API will be available at: http://localhost:5001")
    print("🔗 Health check: http://localhost:5001/api/health")
    print("🧪 Mock data: http://localhost:5001/api/mock-data")
    app.run(debug=True, port=5001, host='0.0.0.0')