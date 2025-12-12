"""
Automative Correction Agent
Automatically identifies and corrects common provider data errors with high confidence.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutomativeCorrectionAgent:
    def __init__(self, confidence_threshold: float = 0.9, google_maps_api_key: Optional[str] = None):
        self.confidence_threshold = confidence_threshold
        self.google_maps_api_key = google_maps_api_key
        self.correction_history = []
        self.specialty_vocabulary = self._load_specialty_vocabulary()
        
    def _load_specialty_vocabulary(self) -> Dict[str, str]:
        """Load controlled vocabulary for specialty normalization"""
        return {
            'cardio': 'Cardiology',
            'cardiologist': 'Cardiology',
            'heart doctor': 'Cardiology',
            'ortho': 'Orthopedics',
            'orthopedic': 'Orthopedics',
            'bone doctor': 'Orthopedics',
            'pediatrics': 'Pediatrics',
            'peds': 'Pediatrics',
            'child doctor': 'Pediatrics',
            'internal medicine': 'Internal Medicine',
            'family practice': 'Family Medicine',
            'family medicine': 'Family Medicine',
            'general practice': 'Family Medicine',
            'dermatology': 'Dermatology',
            'skin doctor': 'Dermatology',
            'neurology': 'Neurology',
            'neurologist': 'Neurology',
            'psychiatry': 'Psychiatry',
            'mental health': 'Psychiatry',
        }
    
    def correct_phone_number(self, phone: str) -> Tuple[Optional[str], float, str]:
        """Standardize phone number to US format (XXX) XXX-XXXX"""
        if not phone:
            return None, 0.0, "Empty phone number"
        
        # Extract digits only
        digits = re.sub(r'\D', '', phone)
        
        # US phone number validation
        if len(digits) == 10:
            formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            confidence = 0.95
            source = "Standardized US format"
            return formatted, confidence, source
        elif len(digits) == 11 and digits[0] == '1':
            formatted = f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            confidence = 0.95
            source = "Standardized US format (removed country code)"
            return formatted, confidence, source
        else:
            return None, 0.0, "Invalid phone number length"
    
    def correct_address(self, address: str) -> Tuple[Optional[str], float, str]:
        """Complete and standardize address using Google Maps API"""
        if not address or len(address.strip()) < 5:
            return None, 0.0, "Address too short"
        
        # If no API key, do basic standardization
        if not self.google_maps_api_key:
            cleaned = ' '.join(address.split())
            return cleaned, 0.7, "Basic standardization (no API)"
        
        try:
            # Google Maps Geocoding API
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': address,
                'key': self.google_maps_api_key
            }
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'OK' and data['results']:
                    formatted_address = data['results'][0]['formatted_address']
                    confidence = 0.92
                    source = "Google Maps API"
                    return formatted_address, confidence, source
        except Exception as e:
            logger.warning(f"Google Maps API error: {e}")
        
        # Fallback to basic cleaning
        cleaned = ' '.join(address.split())
        return cleaned, 0.7, "Basic standardization"
    
    def correct_specialty(self, specialty: str) -> Tuple[Optional[str], float, str]:
        """Normalize specialty name against controlled vocabulary"""
        if not specialty:
            return None, 0.0, "Empty specialty"
        
        specialty_lower = specialty.lower().strip()
        
        # Exact match
        if specialty_lower in self.specialty_vocabulary:
            normalized = self.specialty_vocabulary[specialty_lower]
            return normalized, 0.98, "Controlled vocabulary"
        
        # Partial match
        for key, value in self.specialty_vocabulary.items():
            if key in specialty_lower or specialty_lower in key:
                return value, 0.85, "Partial match in vocabulary"
        
        # No match - return cleaned version
        cleaned = specialty.strip().title()
        return cleaned, 0.6, "Basic cleaning"
    
    def process_provider(self, provider_data: Dict) -> Dict:
        """Process a single provider record and apply corrections"""
        provider_id = provider_data.get('provider_id', 'unknown')
        corrections = []
        
        # Phone correction
        if 'phone' in provider_data:
            corrected_phone, confidence, source = self.correct_phone_number(provider_data['phone'])
            if corrected_phone and confidence >= self.confidence_threshold and corrected_phone != provider_data['phone']:
                corrections.append({
                    'field': 'phone',
                    'before': provider_data['phone'],
                    'after': corrected_phone,
                    'confidence': confidence,
                    'source': source,
                    'timestamp': datetime.now().isoformat()
                })
                provider_data['phone'] = corrected_phone
        
        # Address correction
        if 'address' in provider_data:
            corrected_address, confidence, source = self.correct_address(provider_data['address'])
            if corrected_address and confidence >= self.confidence_threshold and corrected_address != provider_data['address']:
                corrections.append({
                    'field': 'address',
                    'before': provider_data['address'],
                    'after': corrected_address,
                    'confidence': confidence,
                    'source': source,
                    'timestamp': datetime.now().isoformat()
                })
                provider_data['address'] = corrected_address
        
        # Specialty correction
        if 'specialty' in provider_data:
            corrected_specialty, confidence, source = self.correct_specialty(provider_data['specialty'])
            if corrected_specialty and confidence >= self.confidence_threshold and corrected_specialty != provider_data['specialty']:
                corrections.append({
                    'field': 'specialty',
                    'before': provider_data['specialty'],
                    'after': corrected_specialty,
                    'confidence': confidence,
                    'source': source,
                    'timestamp': datetime.now().isoformat()
                })
                provider_data['specialty'] = corrected_specialty
        
        # Log corrections
        if corrections:
            correction_record = {
                'provider_id': provider_id,
                'corrections': corrections,
                'timestamp': datetime.now().isoformat(),
                'status': 'auto_corrected'
            }
            self.correction_history.append(correction_record)
            logger.info(f"Auto-corrected {len(corrections)} fields for provider {provider_id}")
        
        return {
            'provider_data': provider_data,
            'corrections': corrections,
            'needs_manual_review': any(c['confidence'] < self.confidence_threshold for c in corrections)
        }
    
    def batch_process(self, providers: List[Dict]) -> List[Dict]:
        """Process multiple provider records"""
        results = []
        for provider in providers:
            result = self.process_provider(provider)
            results.append(result)
        return results
    
    def get_correction_history(self, provider_id: Optional[str] = None) -> List[Dict]:
        """Retrieve correction history, optionally filtered by provider"""
        if provider_id:
            return [h for h in self.correction_history if h['provider_id'] == provider_id]
        return self.correction_history
    
    def get_statistics(self) -> Dict:
        """Get correction statistics"""
        total_corrections = len(self.correction_history)
        total_fields = sum(len(h['corrections']) for h in self.correction_history)
        
        field_counts = {}
        for record in self.correction_history:
            for correction in record['corrections']:
                field = correction['field']
                field_counts[field] = field_counts.get(field, 0) + 1
        
        return {
            'total_providers_corrected': total_corrections,
            'total_fields_corrected': total_fields,
            'corrections_by_field': field_counts,
            'average_corrections_per_provider': total_fields / total_corrections if total_corrections > 0 else 0
        }


# API endpoints for integration
def create_correction_api():
    """Factory function to create API endpoints"""
    agent = AutomativeCorrectionAgent()
    
    def correct_provider(provider_data: Dict) -> Dict:
        """API endpoint: Correct a single provider"""
        return agent.process_provider(provider_data)
    
    def correct_batch(providers: List[Dict]) -> List[Dict]:
        """API endpoint: Correct multiple providers"""
        return agent.batch_process(providers)
    
    def get_history(provider_id: Optional[str] = None) -> List[Dict]:
        """API endpoint: Get correction history"""
        return agent.get_correction_history(provider_id)
    
    def get_stats() -> Dict:
        """API endpoint: Get statistics"""
        return agent.get_statistics()
    
    return {
        'correct_provider': correct_provider,
        'correct_batch': correct_batch,
        'get_history': get_history,
        'get_stats': get_stats
    }


if __name__ == "__main__":
    # Demo usage
    agent = AutomativeCorrectionAgent()
    
    # Test data
    test_provider = {
        'provider_id': 'P001',
        'name': 'Dr. John Smith',
        'phone': '555.123.4567',
        'address': '123 Main St Boston MA',
        'specialty': 'cardio'
    }
    
    print("Original Provider Data:")
    print(test_provider)
    print("\n" + "="*50 + "\n")
    
    result = agent.process_provider(test_provider)
    
    print("Corrected Provider Data:")
    print(result['provider_data'])
    print("\nCorrections Applied:")
    for correction in result['corrections']:
        print(f"  {correction['field']}: {correction['before']} -> {correction['after']}")
        print(f"    Confidence: {correction['confidence']:.2%}, Source: {correction['source']}")
    
    print("\n" + "="*50 + "\n")
    print("Statistics:")
    print(agent.get_statistics())
