import requests

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJleHAiOjE3ODE2MjYxMzR9.gAHeSN-DPlmkMlNolPAlW4OsD5Y4qQgaSFqUBgBKFoQ'

headers = {'Authorization': f'Bearer {token}'}
data = {
    'title': 'Test Property',
    'price': '250000',
    'city': 'NewYork',
    'bedrooms': '3',
    'bathrooms': '2',
    'description': 'Beautiful property'
}

response = requests.post('http://localhost:5001/api/properties/', headers=headers, data=data)
print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')
