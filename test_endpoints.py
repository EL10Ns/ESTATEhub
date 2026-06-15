import requests

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJleHAiOjE3ODE2MjYxMzR9.gAHeSN-DPlmkMlNolPAlW4OsD5Y4qQgaSFqUBgBKFoQ'

# Test 1: Get all properties
print("TEST 1: Get all properties")
r = requests.get('http://localhost:5001/api/properties/')
print(f'  Status: {r.status_code}')
print(f'  Properties found: {len(r.json())}')
if r.json():
    print(f'  First property: {r.json()[0]["title"]}')
print()

# Test 2: Get specific property
print("TEST 2: Get specific property")
r = requests.get('http://localhost:5001/api/properties/1')
print(f'  Status: {r.status_code}')
print(f'  Property: {r.json()["title"]}')
print()

# Test 3: Try to create without token (should fail)
print("TEST 3: Create property WITHOUT auth token (should fail)")
r = requests.post('http://localhost:5001/api/properties/', data={'title': 'test', 'price': '100', 'city': 'test'})
print(f'  Status: {r.status_code}')
print(f'  Error: {r.json()["error"]}')
print()

# Test 4: Update property
print("TEST 4: Update property with auth")
headers = {'Authorization': f'Bearer {token}'}
data = {'bedrooms': '5', 'bathrooms': '3'}
r = requests.put('http://localhost:5001/api/properties/1', headers=headers, data=data)
print(f'  Status: {r.status_code}')
print(f'  Response: {r.json()}')
