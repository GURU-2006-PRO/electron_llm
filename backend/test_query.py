"""
Test actual query processing
"""
import requests
import time

API_URL = 'http://localhost:5000'

print("=" * 70)
print("TESTING QUERY PROCESSING")
print("=" * 70)
print()

# Wait for server to be ready
print("[1/3] Checking if backend is running...")
try:
    response = requests.get(f'{API_URL}/health', timeout=5)
    if response.status_code == 200:
        print("  ✓ Backend is running")
        print(f"  ✓ Dataset loaded: {response.json()['dataset_loaded']}")
        print(f"  ✓ Rows: {response.json()['rows']:,}")
    else:
        print("  ✗ Backend returned error")
        exit(1)
except Exception as e:
    print(f"  ✗ Backend not running: {e}")
    print()
    print("SOLUTION: Start backend first:")
    print("  cd insightx-app/backend")
    print("  python api_server.py")
    exit(1)

print()
print("[2/3] Testing simple query...")
try:
    response = requests.post(
        f'{API_URL}/query',
        json={'query': 'hello', 'use_ai': False},
        timeout=10
    )
    
    if response.status_code == 200:
        print("  ✓ Simple query works")
        print(f"  Response: {response.json()['answer'][:100]}...")
    else:
        print(f"  ✗ Simple query failed: {response.status_code}")
        print(f"  Error: {response.text}")
except Exception as e:
    print(f"  ✗ Simple query error: {e}")

print()
print("[3/3] Testing advanced query with Gemini...")
try:
    response = requests.post(
        f'{API_URL}/advanced-query',
        json={'query': 'show total rows', 'model': 'gemini-flash'},
        timeout=30
    )
    
    print(f"  Status code: {response.status_code}")
    print(f"  Response: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'error':
            print(f"  ✗ Advanced query returned error:")
            print(f"     {data.get('error')}")
        else:
            print("  ✓ Advanced query works!")
            if data.get('insight'):
                print(f"  Answer: {data['insight'].get('direct_answer', 'N/A')[:100]}...")
    else:
        print(f"  ✗ Advanced query failed: {response.status_code}")
        print(f"  Error: {response.text[:200]}")
except Exception as e:
    print(f"  ✗ Advanced query error: {e}")

print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
