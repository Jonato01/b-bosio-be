import requests
import json

# Test l'endpoint blocked-periods
response = requests.get('http://localhost:8000/api/blocked-periods/')

print(f"Status Code: {response.status_code}")
print(f"\nResponse Headers:")
for key, value in response.headers.items():
    if 'access-control' in key.lower() or 'content-type' in key.lower():
        print(f"  {key}: {value}")

print(f"\nResponse Body:")
print(json.dumps(response.json(), indent=2))

