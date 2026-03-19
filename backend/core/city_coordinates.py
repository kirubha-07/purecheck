"""
City coordinates for India heatmap visualization.
Latitude and longitude for major Indian cities.
Used by /api/heatmap/ endpoint.
"""

CITY_COORDINATES = {
    "trichy": {"lat": 10.7905, "lng": 78.7047, "state": "Tamil Nadu"},
    "tiruchirapalli": {"lat": 10.7905, "lng": 78.7047, "state": "Tamil Nadu"},
    "coimbatore": {"lat": 11.0089, "lng": 76.9411, "state": "Tamil Nadu"},
    "chennai": {"lat": 13.0827, "lng": 80.2707, "state": "Tamil Nadu"},
    "madurai": {"lat": 9.9252, "lng": 78.1198, "state": "Tamil Nadu"},
    "salem": {"lat": 11.6643, "lng": 78.1460, "state": "Tamil Nadu"},
    "vellore": {"lat": 12.9716, "lng": 79.1304, "state": "Tamil Nadu"},
    "kannur": {"lat": 12.2181, "lng": 75.3736, "state": "Kerala"},
    "kochi": {"lat": 9.9312, "lng": 76.2673, "state": "Kerala"},
    "bangalore": {"lat": 12.9716, "lng": 77.5946, "state": "Karnataka"},
    "bengaluru": {"lat": 12.9716, "lng": 77.5946, "state": "Karnataka"},
    "hyderabad": {"lat": 17.3850, "lng": 78.4867, "state": "Telangana"},
    "pune": {"lat": 18.5204, "lng": 73.8567, "state": "Maharashtra"},
    "mumbai": {"lat": 19.0760, "lng": 72.8777, "state": "Maharashtra"},
    "delhi": {"lat": 28.7041, "lng": 77.1025, "state": "Delhi"},
    "new delhi": {"lat": 28.7041, "lng": 77.1025, "state": "Delhi"},
    "kolkata": {"lat": 22.5726, "lng": 88.3639, "state": "West Bengal"},
    "ahmedabad": {"lat": 23.0225, "lng": 72.5714, "state": "Gujarat"},
    "jaipur": {"lat": 26.9124, "lng": 75.7873, "state": "Rajasthan"},
    "lucknow": {"lat": 26.8467, "lng": 80.9462, "state": "Uttar Pradesh"},
    "bhopal": {"lat": 23.1815, "lng": 77.4104, "state": "Madhya Pradesh"},
    "indore": {"lat": 22.7196, "lng": 75.8577, "state": "Madhya Pradesh"},
    "nagpur": {"lat": 21.1458, "lng": 79.0882, "state": "Maharashtra"},
    "patna": {"lat": 25.5941, "lng": 85.1376, "state": "Bihar"},
    "bhubaneswar": {"lat": 20.2961, "lng": 85.8245, "state": "Odisha"},
    "chandigarh": {"lat": 30.7333, "lng": 76.7794, "state": "Chandigarh"},
    "surat": {"lat": 21.1702, "lng": 72.8311, "state": "Gujarat"},
    "vadodara": {"lat": 22.3072, "lng": 73.1812, "state": "Gujarat"},
    "nashik": {"lat": 19.9975, "lng": 73.7898, "state": "Maharashtra"},
    "aurangabad": {"lat": 19.8762, "lng": 75.3433, "state": "Maharashtra"},
}


def get_coordinates(city_name: str):
    """
    Get latitude and longitude for a city.
    
    Args:
        city_name: City name (case-insensitive)
    
    Returns:
        {'lat': float, 'lng': float, 'state': str} or None if not found
    """
    city_lower = city_name.lower().strip()
    return CITY_COORDINATES.get(city_lower)


def get_all_coordinates():
    """Get all city coordinates."""
    return CITY_COORDINATES
