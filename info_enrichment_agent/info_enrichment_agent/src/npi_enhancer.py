"""
Enhance provider data using NPI Registry API
FREE - no API key needed
"""

import requests
import pandas as pd
import time
from typing import Dict, List
import json
import os
from datetime import datetime

class NPIEnhancer:
    """Enhance provider data using NPI Registry"""
    
    def __init__(self, cache_enabled=True):
        self.api_url = "https://npiregistry.cms.hhs.gov/api/"
        self.cache_enabled = cache_enabled
        os.makedirs("data/cache/npi", exist_ok=True)
    
    def enhance_provider(self, npi_number: str) -> Dict:
        """Get enhanced data for a single NPI"""
        
        # Check cache first
        cache_file = f"data/cache/npi/{npi_number}.json"
        if self.cache_enabled and os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # Call NPI API
        try:
            response = requests.get(
                f"{self.api_url}?version=2.1&number={npi_number}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                enhanced = self._parse_npi_response(data, npi_number)
                
                # Save to cache
                if self.cache_enabled:
                    with open(cache_file, 'w') as f:
                        json.dump(enhanced, f, indent=2)
                
                return enhanced
            else:
                print(f"❌ NPI API error for {npi_number}: {response.status_code}")
                return self._create_empty_enhancement(npi_number)
                
        except Exception as e:
            print(f"❌ Error enhancing NPI {npi_number}: {e}")
            return self._create_empty_enhancement(npi_number)
    
    def _parse_npi_response(self, npi_data: Dict, npi_number: str) -> Dict:
        """Parse NPI API response into structured format"""
        
        if npi_data.get('result_count', 0) == 0:
            return self._create_empty_enhancement(npi_number)
        
        result = npi_data['results'][0]
        
        # Extract basic info
        basic_info = result.get('basic', {})
        taxonomies = result.get('taxonomies', [])
        addresses = result.get('addresses', [])
        
        # Process taxonomies (specialties)
        specialty_list = []
        primary_specialty = ""
        for tax in taxonomies:
            desc = tax.get('desc', '')
            code = tax.get('code', '')
            if desc:
                specialty_list.append({
                    'code': code,
                    'description': desc,
                    'primary': tax.get('primary', False),
                    'state': tax.get('state', ''),
                    'license': tax.get('license', '')
                })
                if tax.get('primary', False):
                    primary_specialty = desc
        
        # Process addresses
        practice_locations = []
        for addr in addresses:
            if addr.get('country_code') == 'US':
                practice_locations.append({
                    'address': f"{addr.get('address_1', '')} {addr.get('address_2', '')}",
                    'city': addr.get('city', ''),
                    'state': addr.get('state', ''),
                    'zip': addr.get('postal_code', ''),
                    'phone': addr.get('telephone_number', ''),
                    'type': addr.get('address_purpose', '')
                })
        
        # Calculate years of experience
        enumeration_date = basic_info.get('enumeration_date', '')
        years_experience = self._calculate_experience(enumeration_date)
        
        # Build enhanced data
        enhanced = {
            'npi': npi_number,
            'provider_type': basic_info.get('credential', ''),
            'enumeration_date': enumeration_date,
            'years_experience': years_experience,
            'career_stage': self._categorize_career_stage(years_experience),
            'primary_specialty': primary_specialty,
            'all_specialties': specialty_list,
            'practice_locations': practice_locations,
            'organization_name': result.get('organization_name', ''),
            'gender': basic_info.get('gender', ''),
            'status': basic_info.get('status', ''),
            'last_updated': basic_info.get('last_updated', ''),
            'npi_confidence': 0.95,  # NPI data is highly reliable
            'sources': ['npi_registry']
        }
        
        return enhanced
    
    def _calculate_experience(self, enumeration_date: str) -> int:
        """Calculate years of experience from enumeration date"""
        if not enumeration_date:
            return 0
        
        try:
            enum_year = int(enumeration_date.split('-')[0])
            current_year = datetime.now().year
            return max(0, current_year - enum_year)
        except:
            return 0
    
    def _categorize_career_stage(self, years: int) -> str:
        """Categorize provider by career stage"""
        if years >= 20:
            return "Senior (20+ years)"
        elif years >= 10:
            return "Experienced (10-19 years)"
        elif years >= 5:
            return "Mid-Career (5-9 years)"
        elif years > 0:
            return "Early Career (1-4 years)"
        else:
            return "New (0-1 years)"
    
    def _create_empty_enhancement(self, npi_number: str) -> Dict:
        """Create empty enhancement for failed API calls"""
        return {
            'npi': npi_number,
            'provider_type': '',
            'enumeration_date': '',
            'years_experience': 0,
            'career_stage': 'Unknown',
            'primary_specialty': '',
            'all_specialties': [],
            'practice_locations': [],
            'organization_name': '',
            'npi_confidence': 0.0,
            'sources': []
        }
    
    def batch_enhance(self, npi_list: List[str]) -> pd.DataFrame:
        """Enhance multiple NPIs efficiently"""
        
        print(f"\n🔍 Enhancing {len(npi_list)} providers via NPI Registry...")
        
        enhanced_data = []
        for i, npi in enumerate(npi_list, 1):
            if pd.isna(npi) or npi == '':
                continue
                
            print(f"  [{i}/{len(npi_list)}] Processing NPI: {npi}")
            enhanced = self.enhance_provider(str(npi).strip())
            enhanced_data.append(enhanced)
            
            # Rate limiting (be nice to free API)
            time.sleep(0.1)  # 10 requests per second
        
        # Convert to DataFrame
        df = pd.DataFrame(enhanced_data)
        
        print(f"✅ NPI enhancement complete: {len(df)} providers enhanced")
        print(f"   Average experience: {df['years_experience'].mean():.1f} years")
        
        return df