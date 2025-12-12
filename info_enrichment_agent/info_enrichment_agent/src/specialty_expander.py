"""
Expand specialty information from taxonomy codes
"""

from typing import Dict

class SpecialtyExpander:
    """Expand specialty information with details"""
    
    def __init__(self):
        # Map taxonomy codes to detailed specialty info
        self.specialty_details = {
            '207R00000X': {  # Internal Medicine
                'description': 'Internal Medicine',
                'subspecialties': ['Cardiology', 'Gastroenterology', 'Endocrinology', 
                                 'Nephrology', 'Pulmonology', 'Rheumatology'],
                'common_procedures': ['Physical Exam', 'Chronic Disease Management', 
                                     'Preventive Care', 'Diagnostic Testing'],
                'typical_patients': 'Adults 18+',
                'settings': ['Hospital', 'Clinic', 'Private Practice']
            },
            '208D00000X': {  # General Practice
                'description': 'General Practice',
                'subspecialties': ['Family Medicine', 'Primary Care'],
                'common_procedures': ['Annual Physicals', 'Vaccinations', 'Minor Procedures',
                                     'Chronic Disease Management'],
                'typical_patients': 'All ages',
                'settings': ['Private Practice', 'Clinic', 'Urgent Care']
            },
            '208G00000X': {  # Thoracic Surgery
                'description': 'Thoracic Surgery',
                'subspecialties': ['Cardiothoracic Surgery', 'Transplant Surgery'],
                'common_procedures': ['Heart Surgery', 'Lung Surgery', 'Transplant Surgery'],
                'typical_patients': 'Adults with cardiac/thoracic conditions',
                'settings': ['Hospital', 'Surgical Center']
            },
            '208M00000X': {  # Hospitalist
                'description': 'Hospitalist',
                'subspecialties': [],
                'common_procedures': ['Inpatient Care', 'Discharge Planning', 
                                     'Consultation Management'],
                'typical_patients': 'Hospitalized patients',
                'settings': ['Hospital']
            }
        }
    
    def expand_specialty(self, taxonomy_code: str, specialty_name: str) -> Dict:
        """Expand specialty with detailed information"""
        
        # Try to get details from taxonomy code first
        if taxonomy_code in self.specialty_details:
            details = self.specialty_details[taxonomy_code].copy()
            details['taxonomy_code'] = taxonomy_code
            details['confidence'] = 0.9
            return details
        
        # Fallback: generic expansion based on specialty name
        return self._generic_expansion(specialty_name, taxonomy_code)
    
    def _generic_expansion(self, specialty_name: str, taxonomy_code: str) -> Dict:
        """Create generic expansion for unknown specialties"""
        
        # Map common keywords to details
        keyword_mapping = {
            'cardio': {
                'subspecialties': ['Interventional Cardiology', 'Electrophysiology'],
                'common_procedures': ['Echocardiogram', 'Stress Test', 'Cardiac Cath'],
                'equipment': ['ECG Machine', 'Echo Machine', 'Stress Test Equipment']
            },
            'derm': {
                'subspecialties': ['Cosmetic Dermatology', 'Surgical Dermatology'],
                'common_procedures': ['Skin Biopsy', 'Excisions', 'Cosmetic Procedures'],
                'equipment': ['Dermatoscope', 'Laser Equipment']
            },
            'neuro': {
                'subspecialties': ['Neuromuscular', 'Stroke Neurology', 'Epilepsy'],
                'common_procedures': ['EEG', 'EMG', 'Nerve Conduction Studies'],
                'equipment': ['EEG Machine', 'EMG Machine']
            },
            'ortho': {
                'subspecialties': ['Sports Medicine', 'Joint Replacement', 'Spine'],
                'common_procedures': ['Arthroscopy', 'Fracture Repair', 'Joint Replacement'],
                'equipment': ['X-Ray', 'Surgical Instruments']
            }
        }
        
        # Find matching keywords
        specialty_lower = specialty_name.lower()
        details = {
            'subspecialties': [],
            'common_procedures': [],
            'typical_patients': 'Adults',
            'settings': ['Clinic', 'Hospital'],
            'confidence': 0.5
        }
        
        for keyword, expansion in keyword_mapping.items():
            if keyword in specialty_lower:
                details.update(expansion)
                details['confidence'] = 0.7
                break
        
        details['description'] = specialty_name
        details['taxonomy_code'] = taxonomy_code
        
        return details
    
    def create_specialty_profile(self, specialties_list: list) -> Dict:
        """Create comprehensive specialty profile for a provider"""
        
        if not specialties_list:
            return {'confidence': 0.0}
        
        all_subspecialties = []
        all_procedures = []
        
        for specialty in specialties_list:
            code = specialty.get('code', '')
            name = specialty.get('description', '')
            
            expanded = self.expand_specialty(code, name)
            
            all_subspecialties.extend(expanded.get('subspecialties', []))
            all_procedures.extend(expanded.get('common_procedures', []))
        
        # Remove duplicates
        all_subspecialties = list(set(all_subspecialties))
        all_procedures = list(set(all_procedures))
        
        # Determine provider type based on specialties
        provider_type = self._determine_provider_type(specialties_list)
        
        profile = {
            'primary_specialty': specialties_list[0]['description'] if specialties_list else '',
            'all_specialties': [s['description'] for s in specialties_list],
            'subspecialties': all_subspecialties,
            'common_procedures': all_procedures,
            'provider_type_category': provider_type,
            'specialty_confidence': self._calculate_specialty_confidence(specialties_list)
        }
        
        return profile
    
    def _determine_provider_type(self, specialties_list: list) -> str:
        """Determine provider type category"""
        if not specialties_list:
            return 'General'
        
        primary = specialties_list[0]['description'].lower()
        
        if any(word in primary for word in ['surgery', 'surgical']):
            return 'Surgical'
        elif any(word in primary for word in ['hospitalist', 'inpatient']):
            return 'Hospital-based'
        elif any(word in primary for word in ['primary', 'family', 'general']):
            return 'Primary Care'
        elif any(word in primary for word in ['specialist', 'ology']):
            return 'Specialist'
        else:
            return 'Specialized'
    
    def _calculate_specialty_confidence(self, specialties_list: list) -> float:
        """Calculate confidence in specialty information"""
        if not specialties_list:
            return 0.0
        
        # Higher confidence if we have taxonomy codes
        has_codes = any(s.get('code') for s in specialties_list)
        count = len(specialties_list)
        
        if has_codes and count >= 2:
            return 0.9
        elif has_codes:
            return 0.8
        elif count >= 2:
            return 0.7
        else:
            return 0.5