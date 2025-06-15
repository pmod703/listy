#!/usr/bin/env python3
"""
Test script to demonstrate the new similar property criteria functionality
"""

import requests
import json

def test_similar_property_criteria():
    """Test the new similar property criteria feature"""
    
    # Test URL
    base_url = "http://localhost:5001"
    
    # Test parameters
    test_params = {
        'address': '123 Main Street, Sydney, 2000',
        'date': '2024-01-20',
        'start_time': '09:00',
        'end_time': '16:00',
        'similar_bedrooms': '3-4',
        'similar_bathrooms': '2+',
        'similar_car_spots': '1-2'
    }
    
    print("🧪 Testing Similar Property Criteria Feature")
    print("=" * 50)
    
    try:
        # Test health endpoint first
        health_response = requests.get(f"{base_url}/api/health")
        if health_response.status_code == 200:
            print("✅ API is healthy")
        else:
            print("❌ API health check failed")
            return
        
        # Test the main endpoint with similar property criteria
        print(f"\n🔍 Testing with criteria:")
        print(f"   Bedrooms: {test_params['similar_bedrooms']}")
        print(f"   Bathrooms: {test_params['similar_bathrooms']}")
        print(f"   Car Spots: {test_params['similar_car_spots']}")
        
        response = requests.get(f"{base_url}/api/inspections", params=test_params)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📊 Results:")
            print(f"   Total inspections found: {data.get('total_inspections', 0)}")
            print(f"   Similar properties: {data.get('similar_inspections', 0)}")
            
            # Show search parameters
            search_params = data.get('search_params', {})
            criteria = search_params.get('similar_property_criteria', {})
            
            print(f"\n🎯 Applied Criteria:")
            print(f"   Bedrooms: {criteria.get('bedrooms', 'N/A')}")
            print(f"   Bathrooms: {criteria.get('bathrooms', 'N/A')}")
            print(f"   Car Spots: {criteria.get('car_spots', 'N/A')}")
            
            # Show top recommendations
            recommendations = data.get('recommendations', [])
            if recommendations:
                print(f"\n⭐ Top 3 Recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"   {i}. {rec['time']} - {rec['count']} competing properties ({rec['competition']})")
            
            print(f"\n✅ Test completed successfully!")
            
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:5001")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_different_criteria():
    """Test with different criteria combinations"""
    
    print("\n" + "=" * 50)
    print("🧪 Testing Different Criteria Combinations")
    print("=" * 50)
    
    test_cases = [
        {
            'name': 'Luxury Properties (4+ bedrooms)',
            'criteria': {'similar_bedrooms': '4+', 'similar_bathrooms': '3+', 'similar_car_spots': '2+'}
        },
        {
            'name': 'Starter Homes (1-2 bedrooms)',
            'criteria': {'similar_bedrooms': '1-2', 'similar_bathrooms': '1', 'similar_car_spots': '0-1'}
        },
        {
            'name': 'Family Homes (3-4 bedrooms)',
            'criteria': {'similar_bedrooms': '3-4', 'similar_bathrooms': '2-3', 'similar_car_spots': '1-2'}
        }
    ]
    
    base_params = {
        'address': '123 Main Street, Sydney, 2000',
        'date': '2024-01-20',
        'start_time': '09:00',
        'end_time': '16:00'
    }
    
    for test_case in test_cases:
        print(f"\n🏠 {test_case['name']}:")
        
        # Combine base params with test criteria
        params = {**base_params, **test_case['criteria']}
        
        try:
            response = requests.get("http://localhost:5001/api/inspections", params=params)
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total_inspections', 0)
                similar = data.get('similar_inspections', 0)
                
                print(f"   📊 {similar}/{total} properties match criteria")
                
                if data.get('recommendations'):
                    best_time = data['recommendations'][0]
                    print(f"   ⏰ Best time: {best_time['time']} ({best_time['count']} competing)")
                
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Similar Property Criteria Test Suite")
    print("Make sure the API server is running (python integrated_api.py)")
    print()
    
    test_similar_property_criteria()
    test_different_criteria()
    
    print("\n" + "=" * 50)
    print("✨ Test suite completed!")
    print("💡 Try the frontend at: http://localhost:3000")
    print("=" * 50)