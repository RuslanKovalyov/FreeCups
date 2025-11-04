"""Utility functions for geocoding."""
import time
import requests
from typing import Optional, Tuple


class GeocodeRateLimiter:
    """Simple rate limiter for Nominatim API (1 request per second)."""
    last_request_time = 0
    min_interval = 1.0
    
    @classmethod
    def wait_if_needed(cls):
        """Wait if necessary to respect rate limit."""
        elapsed = time.time() - cls.last_request_time
        if elapsed < cls.min_interval:
            time.sleep(cls.min_interval - elapsed)
        cls.last_request_time = time.time()


def geocode_address(address: str, city: str = None, country: str = None) -> Optional[Tuple[float, float]]:
    """Convert address to coordinates using Nominatim (OpenStreetMap)."""
    query_parts = [address]
    if city:
        query_parts.append(city)
    if country:
        query_parts.append(country)
    
    query = ", ".join(query_parts)
    GeocodeRateLimiter.wait_if_needed()
    
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {'q': query, 'format': 'json', 'limit': 1}
        headers = {'User-Agent': 'FreeCups-Django-App/1.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data:
            return (float(data[0]['lat']), float(data[0]['lon']))
        
        return None
        
    except Exception as e:
        print(f"Geocoding error for '{query}': {e}")
        return None


def reverse_geocode(latitude: float, longitude: float) -> Optional[dict]:
    """Convert coordinates to address using Nominatim (OpenStreetMap)."""
    GeocodeRateLimiter.wait_if_needed()
    
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {'lat': latitude, 'lon': longitude, 'format': 'json'}
        headers = {'User-Agent': 'FreeCups-Django-App/1.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if 'address' in data:
            return {
                'full_address': data.get('display_name', ''),
                'address': data.get('address', {}),
                'city': data['address'].get('city') or data['address'].get('town') or data['address'].get('village'),
                'country': data['address'].get('country'),
            }
        
        return None
        
    except Exception as e:
        print(f"Reverse geocoding error for ({latitude}, {longitude}): {e}")
        return None
