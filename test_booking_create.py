import requests
import json

# Test data from the user's request
booking_data = {
    "accommodation": 1,
    "check_in": "2025-11-25T14:00:00Z",
    "check_out": "2025-11-27T10:00:00Z",
    "num_guests": 1,
    "notes": "no",
    "guests_data": [
        {
            "full_name": "re",
            "email": "re@mail.com",
            "phone": "1234567890",
            "birth_date": "2001-12-12",
            "document_type": "Carta d'Identità",
            "document_number": "ca8527dk"
        }
    ]
}

# Try to create a booking
print("Sending POST request to create booking...")
print(f"Data: {json.dumps(booking_data, indent=2)}")
print()

response = requests.post(
    'http://localhost:8000/api/bookings/',
    json=booking_data,
    headers={'Content-Type': 'application/json'}
)

print(f"Status Code: {response.status_code}")
print(f"\nResponse Headers:")
for key, value in response.headers.items():
    if 'content-type' in key.lower():
        print(f"  {key}: {value}")

print(f"\nResponse Body:")
try:
    print(json.dumps(response.json(), indent=2))
except:
    print(response.text)

