#!/usr/bin/env python3
"""
Test script for the clean API (no scraping)
"""

import requests
import json

def test_clean_api():
    """Test the clean API functionality"""
    
    # Test URL
    base_url = "http://localhost:5001"
    
    # Test parameters
    test_params = {
        'address': '123 George Street, Sydney, 2000',
        'date': '2024-01-20',
        'start_time': '09:00',
        'end_time': '16:00',
        'similar_bedrooms': '3-4',
        'similar_bathrooms': '2+',
        'similar_car_spots': '1-2'
    }
    
    print("🧪 Testing Clean API (No Scraping)")
    print("=" * 50)
    
    try:
        # Test health endpoint first
        print("🔍 Testing health endpoint...")
        health_response = requests.get(f"{base_url}/api/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ API is healthy")
            print(f"   Version: {health_data.get('version', 'Unknown')}")
            print(f"   Data Source: {health_data.get('data_source', 'Unknown')}")
            print(f"   Scraping Disabled: {health_data.get('scraping_disabled', 'Unknown')}")
        else:
            print("❌ API health check failed")
            return
        
        # Test the main endpoint with similar property criteria
        print(f"\n🔍 Testing inspections endpoint with criteria:")
        print(f"   Address: {test_params['address']}")
        print(f"   Bedrooms: {test_params['similar_bedrooms']}")
        print(f"   Bathrooms: {test_params['similar_bathrooms']}")
        print(f"   Car Spots: {test_params['similar_car_spots']}")
        
        response = requests.get(f"{base_url}/api/inspections", params=test_params)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📊 Results:")
            print(f"   Total mock inspections: {data.get('total_inspections', 0)}")
            print(f"   Similar properties: {data.get('similar_inspections', 0)}")
            print(f"   Data source: {data.get('data_source', 'Unknown')}")
            
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
                print(f"\n⭐ Top 5 Recommendations:")
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"   {i}. {rec['time']} - {rec['count']} competing properties ({rec['competition']})")
            
            # Show some sample properties
            filtered_inspections = data.get('filtered_inspections', [])
            if filtered_inspections:
                print(f"\n🏠 Sample Similar Properties:")
                for i, prop in enumerate(filtered_inspections[:3], 1):
                    details = prop.get('property_details', {})
                    print(f"   {i}. {prop['address']}")
                    print(f"      {details.get('bedrooms', 'N/A')} bed, {details.get('bathrooms', 'N/A')} bath, {details.get('car_spots', 'N/A')} car")
                    print(f"      Open: {prop['start_time']}-{prop['end_time']}")
            
            print(f"\n✅ Test completed successfully!")
            
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running:")
        print("   Run: python clean_api.py")
        print("   Or:  ./start_clean_backend.sh")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_mock_endpoint():
    """Test the dedicated mock data endpoint"""
    
    print("\n" + "=" * 50)
    print("🧪 Testing Mock Data Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5001/api/mock-data", params={
            'similar_bedrooms': '2-3',
            'similar_bathrooms': '1+',
            'similar_car_spots': '0-2'
        })
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"📊 Mock Data Results:")
            print(f"   Total properties: {data.get('total_inspections', 0)}")
            print(f"   Matching criteria: {data.get('similar_inspections', 0)}")
            print(f"   Is mock data: {data.get('is_mock_data', False)}")
            
            recommendations = data.get('recommendations', [])
            if recommendations:
                print(f"\n⭐ Best Times:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"   {i}. {rec['time']} ({rec['competition']} competition)")
            
        else:
            print(f"❌ Mock endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Mock endpoint test failed: {e}")

if __name__ == "__main__":
    print("🚀 Clean API Test Suite")
    print("Make sure the clean API server is running:")
    print("  python clean_api.py")
    print("  OR")
    print("  ./start_clean_backend.sh")
    print()
    
    test_clean_api()
    test_mock_endpoint()
    
    print("\n" + "=" * 50)
    print("✨ Test suite completed!")
    print("💡 Frontend available at: http://localhost:3000")
    print("🔗 API docs at: http://localhost:5001/api/health")
    print("=" * 50)