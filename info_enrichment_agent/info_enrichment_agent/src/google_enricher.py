"""
Enrich practice information using Google Places API
Requires: Google API Key (free tier available)
"""

import requests
import pandas as pd
from typing import Dict, Optional, List
import json
import os
from src.config import GOOGLE_API_KEY

class GoogleEnricher:
    """Get practice information from Google Places"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or GOOGLE_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        os.makedirs("data/cache/google", exist_ok=True)
    
    def enrich_practice(self, practice_name: str, address: str) -> Dict:
        """Get practice details from Google Places"""

        if not self.api_key or self.api_key == "YOUR_GOOGLE_API_KEY_HERE":
            print("⚠️  Google API key not configured. Using mock data.")
            return self._get_mock_practice_data()

        # Check cache
        cache_key = f"{practice_name}_{address}".replace(' ', '_').replace(',', '')
        cache_file = f"data/cache/google/{cache_key}.json"
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)

        try:
            # Step 1: Find place ID
            place_id = self._find_place_id(practice_name, address)
            if not place_id:
                return self._get_empty_practice_data()

            # Step 2: Get place details
            practice_info = self._get_place_details(place_id)

            # Save to cache
            with open(cache_file, 'w') as f:
                json.dump(practice_info, f, indent=2)

            return practice_info

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error for {practice_name}: {e}")
            return self._get_empty_practice_data()
        except Exception as e:
            print(f"❌ Google Places error for {practice_name}: {e}")
            return self._get_empty_practice_data()
    
    def _find_place_id(self, name: str, address: str) -> Optional[str]:
        """Find Google Place ID for a practice"""
        
        url = f"{self.base_url}/findplacefromtext/json"
        params = {
            'key': self.api_key,
            'input': f"{name} {address}",
            'inputtype': 'textquery',
            'fields': 'place_id,name'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('candidates'):
            return data['candidates'][0]['place_id']
        
        return None
    
    def _get_place_details(self, place_id: str) -> Dict:
        """Get detailed information about a place"""
        
        url = f"{self.base_url}/details/json"
        params = {
            'key': self.api_key,
            'place_id': place_id,
            'fields': 'name,formatted_address,formatted_phone_number,website,opening_hours,types,rating,user_ratings_total,business_status'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('result'):
            result = data['result']
            
            # Determine if telehealth is available
            types = result.get('types', [])
            telehealth = self._check_telehealth(types, result.get('website', ''))
            
            # Parse business hours
            hours = self._parse_business_hours(result.get('opening_hours', {}))
            
            practice_info = {
                'practice_name': result.get('name', ''),
                'google_address': result.get('formatted_address', ''),
                'phone': result.get('formatted_phone_number', ''),
                'website': result.get('website', ''),
                'business_hours': hours,
                'google_rating': result.get('rating', 0),
                'total_reviews': result.get('user_ratings_total', 0),
                'business_status': result.get('business_status', ''),
                'place_types': types,
                'telehealth_available': telehealth,
                'practice_type': self._categorize_practice(types),
                'google_confidence': 0.9,
                'sources': ['google_places']
            }
            
            return practice_info
        
        return self._get_empty_practice_data()
    
    def _check_telehealth(self, types: List[str], website: str) -> bool:
        """Check if practice offers telehealth"""
        telehealth_indicators = [
            'telehealth', 'telemedicine', 'virtual visit', 'online appointment',
            'video consultation', 'remote care'
        ]
        
        # Check website (would need to scrape, but we'll infer)
        website_lower = website.lower() if website else ''
        
        # Check if any telehealth indicators in practice types
        type_check = any(indicator in ' '.join(types).lower() 
                        for indicator in telehealth_indicators)
        
        # Or in website (simplified check)
        website_check = any(indicator in website_lower 
                           for indicator in telehealth_indicators[:3])
        
        return type_check or website_check
    
    def _parse_business_hours(self, opening_hours: Dict) -> List[str]:
        """Parse Google's opening hours format"""
        if not opening_hours or 'weekday_text' not in opening_hours:
            return []
        
        return opening_hours['weekday_text']
    
    def _categorize_practice(self, types: List[str]) -> str:
        """Categorize practice type"""
        type_str = ' '.join(types).lower()
        
        if 'hospital' in type_str:
            return 'Hospital'
        elif 'clinic' in type_str:
            return 'Clinic'
        elif 'health' in type_str and 'center' in type_str:
            return 'Health Center'
        elif 'doctor' in type_str or 'physician' in type_str:
            return 'Private Practice'
        elif 'medical' in type_str:
            return 'Medical Office'
        else:
            return 'Healthcare Facility'
    
    def _get_empty_practice_data(self) -> Dict:
        return {
            'practice_name': '',
            'google_address': '',
            'phone': '',
            'website': '',
            'business_hours': [],
            'google_rating': 0,
            'total_reviews': 0,
            'business_status': '',
            'place_types': [],
            'telehealth_available': False,
            'practice_type': '',
            'google_confidence': 0.0,
            'sources': []
        }
    
    def _get_mock_practice_data(self) -> Dict:
        """Return mock data for demo when no API key"""
        return {
            'practice_name': 'Mock Practice',
            'google_address': 'Mock Address',
            'phone': '(555) 123-4567',
            'website': 'www.mockpractice.com',
            'business_hours': ['Mon-Fri: 9am-5pm', 'Sat: 10am-2pm'],
            'google_rating': 4.2,
            'total_reviews': 42,
            'business_status': 'OPERATIONAL',
            'place_types': ['doctor', 'health', 'point_of_interest'],
            'telehealth_available': True,
            'practice_type': 'Private Practice',
            'google_confidence': 0.5,  # Lower confidence for mock data
            'sources': ['mock_data']
        }