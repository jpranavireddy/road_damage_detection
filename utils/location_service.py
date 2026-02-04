"""
Location service for geocoding area names and managing map coordinates
"""

import requests
import json
import time
from typing import Tuple, Optional, Dict

class LocationService:
    """Service for converting area names to GPS coordinates and managing locations"""
    
    def __init__(self):
        # Default locations for common area types
        self.default_locations = {
            # Major cities
            'new york': (40.7128, -74.0060),
            'los angeles': (34.0522, -118.2437),
            'chicago': (41.8781, -87.6298),
            'houston': (29.7604, -95.3698),
            'phoenix': (33.4484, -112.0740),
            'philadelphia': (39.9526, -75.1652),
            'san antonio': (29.4241, -98.4936),
            'san diego': (32.7157, -117.1611),
            'dallas': (32.7767, -96.7970),
            'san jose': (37.3382, -121.8863),
            
            # Highway examples
            'highway a1': (40.7589, -73.9851),
            'interstate 95': (39.0458, -76.6413),
            'route 66': (35.2271, -101.8313),
            'highway 101': (37.7749, -122.4194),
            
            # Generic locations
            'downtown': (40.7589, -73.9851),
            'main street': (40.7589, -73.9851),
            'city center': (40.7589, -73.9851),
        }
    
    def geocode_area_name(self, area_name: str) -> Optional[Tuple[float, float]]:
        """
        Convert area name to GPS coordinates using multiple methods
        
        Args:
            area_name (str): Name of the area/location
            
        Returns:
            Tuple[float, float]: (latitude, longitude) or None if not found
        """
        if not area_name:
            return None
        
        area_lower = area_name.lower().strip()
        
        # First, check our default locations
        for key, coords in self.default_locations.items():
            if key in area_lower:
                return coords
        
        # Try to extract coordinates from area name if it contains them
        coords = self.extract_coordinates_from_text(area_name)
        if coords:
            return coords
        
        # Try free geocoding service (Nominatim - OpenStreetMap)
        coords = self.geocode_with_nominatim(area_name)
        if coords:
            return coords
        
        # If all else fails, return a reasonable default
        return self.get_default_location()
    
    def extract_coordinates_from_text(self, text: str) -> Optional[Tuple[float, float]]:
        """
        Extract GPS coordinates from text if present
        Formats: "lat40.7128_lon-74.0060", "40.7128,-74.0060", etc.
        """
        import re
        
        # Pattern for lat/lon format
        lat_lon_pattern = r'lat([-+]?\d+\.?\d*).*?lon([-+]?\d+\.?\d*)'
        match = re.search(lat_lon_pattern, text.lower())
        if match:
            try:
                lat = float(match.group(1))
                lon = float(match.group(2))
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return (lat, lon)
            except ValueError:
                pass
        
        # Pattern for decimal coordinates
        coord_pattern = r'([-+]?\d+\.?\d+)\s*,\s*([-+]?\d+\.?\d+)'
        match = re.search(coord_pattern, text)
        if match:
            try:
                lat = float(match.group(1))
                lon = float(match.group(2))
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return (lat, lon)
            except ValueError:
                pass
        
        return None
    
    def geocode_with_nominatim(self, area_name: str) -> Optional[Tuple[float, float]]:
        """
        Use Nominatim (OpenStreetMap) geocoding service
        """
        try:
            # Clean up the area name
            query = area_name.strip()
            
            # Nominatim API endpoint
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'RoadDamageDetectionSystem/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    result = data[0]
                    lat = float(result['lat'])
                    lon = float(result['lon'])
                    return (lat, lon)
            
        except Exception as e:
            print(f"Geocoding error for '{area_name}': {e}")
        
        return None
    
    def get_default_location(self) -> Tuple[float, float]:
        """Get default location (New York City)"""
        return (40.7128, -74.0060)
    
    def get_area_bounds(self, center_lat: float, center_lon: float, 
                       radius_km: float = 5.0) -> Dict[str, float]:
        """
        Calculate bounding box around a center point
        
        Args:
            center_lat (float): Center latitude
            center_lon (float): Center longitude
            radius_km (float): Radius in kilometers
            
        Returns:
            Dict with north, south, east, west bounds
        """
        # Rough conversion: 1 degree ≈ 111 km
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * abs(center_lat / 90.0))  # Adjust for latitude
        
        return {
            'north': center_lat + lat_delta,
            'south': center_lat - lat_delta,
            'east': center_lon + lon_delta,
            'west': center_lon - lon_delta
        }
    
    def find_center_of_damages(self, damaged_images: list) -> Optional[Tuple[float, float]]:
        """
        Find the center point of all damaged locations
        
        Args:
            damaged_images (list): List of damage reports with GPS coordinates
            
        Returns:
            Tuple[float, float]: Center coordinates or None
        """
        valid_coords = []
        
        for img_data in damaged_images:
            lat = img_data.get('latitude')
            lon = img_data.get('longitude')
            
            if lat is not None and lon is not None:
                valid_coords.append((lat, lon))
        
        if not valid_coords:
            return None
        
        # Calculate center point
        avg_lat = sum(coord[0] for coord in valid_coords) / len(valid_coords)
        avg_lon = sum(coord[1] for coord in valid_coords) / len(valid_coords)
        
        return (avg_lat, avg_lon)
    
    def get_map_center_for_area(self, area_name: str, damaged_images: list = None) -> Tuple[float, float]:
        """
        Get the best map center for an area, considering area name and damage locations
        
        Args:
            area_name (str): Name of the area
            damaged_images (list): List of damage reports (optional)
            
        Returns:
            Tuple[float, float]: Best center coordinates for the map
        """
        # First priority: Center of actual damage locations
        if damaged_images:
            damage_center = self.find_center_of_damages(damaged_images)
            if damage_center:
                return damage_center
        
        # Second priority: Geocoded area name
        area_coords = self.geocode_area_name(area_name)
        if area_coords:
            return area_coords
        
        # Fallback: Default location
        return self.get_default_location()
    
    def suggest_area_names(self, partial_name: str) -> list:
        """
        Suggest area names based on partial input
        
        Args:
            partial_name (str): Partial area name
            
        Returns:
            list: List of suggested area names
        """
        if not partial_name or len(partial_name) < 2:
            return []
        
        partial_lower = partial_name.lower()
        suggestions = []
        
        # Check default locations
        for location in self.default_locations.keys():
            if partial_lower in location:
                suggestions.append(location.title())
        
        # Add common area types
        common_areas = [
            f"{partial_name} Highway",
            f"{partial_name} Street",
            f"{partial_name} Avenue",
            f"{partial_name} Road",
            f"Downtown {partial_name}",
            f"{partial_name} District"
        ]
        
        suggestions.extend(common_areas[:3])  # Limit suggestions
        
        return suggestions[:5]  # Return top 5 suggestions