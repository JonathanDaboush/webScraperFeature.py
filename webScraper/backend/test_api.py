"""
Quick API test script
Run this to verify the backend API is working correctly
"""

import requests
import json

API_URL = "http://localhost:5000/api"

def test_api():
    print("Testing WebScraper API...")
    print("=" * 50)
    
    # Test 1: Stats endpoint
    print("\n1. Testing /api/stats...")
    try:
        response = requests.get(f"{API_URL}/stats")
        if response.status_code == 200:
            print("✓ Stats endpoint working")
            print(f"   Data: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"✗ Stats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Products endpoint
    print("\n2. Testing /api/products...")
    try:
        response = requests.get(f"{API_URL}/products")
        if response.status_code == 200:
            print("✓ Products endpoint working")
            products = response.json()
            print(f"   Found {len(products)} products")
        else:
            print(f"✗ Products endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Deals endpoint
    print("\n3. Testing /api/deals...")
    try:
        response = requests.get(f"{API_URL}/deals")
        if response.status_code == 200:
            print("✓ Deals endpoint working")
            deals = response.json()
            print(f"   Found {len(deals)} deals")
        else:
            print(f"✗ Deals endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Sources endpoint
    print("\n4. Testing /api/sources...")
    try:
        response = requests.get(f"{API_URL}/sources")
        if response.status_code == 200:
            print("✓ Sources endpoint working")
            sources = response.json()
            print(f"   Found {len(sources)} sources")
        else:
            print(f"✗ Sources endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: Settings endpoint
    print("\n5. Testing /api/settings...")
    try:
        response = requests.get(f"{API_URL}/settings")
        if response.status_code == 200:
            print("✓ Settings endpoint working")
            print(f"   Settings: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"✗ Settings endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("API test complete!")
    print("\nIf all tests passed, your backend is ready!")
    print("If any failed, make sure:")
    print("  1. Backend is running (python api.py)")
    print("  2. PostgreSQL is running")
    print("  3. Database 'webscraper' exists")

if __name__ == "__main__":
    try:
        test_api()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
