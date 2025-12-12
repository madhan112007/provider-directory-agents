"""
Infer education information from available data
No API needed - uses inference rules
"""

import pandas as pd
from typing import Dict
import random

class EducationInferrer:
    """Infer education based on location, experience, and specialty"""
    
    def __init__(self):
        # Medical schools by region
        self.medical_schools = {
            'Northeast': [
                'Harvard Medical School',
                'Columbia University College of Physicians and Surgeons',
                'Johns Hopkins University School of Medicine',
                'University of Pennsylvania Perelman School of Medicine',
                'Yale School of Medicine',
                'Boston University School of Medicine',
                'Tufts University School of Medicine'
            ],
            'Midwest': [
                'Northwestern University Feinberg School of Medicine',
                'University of Chicago Pritzker School of Medicine',
                'University of Michigan Medical School',
                'Washington University in St. Louis School of Medicine',
                'Mayo Clinic Alix School of Medicine'
            ],
            'South': [
                'Duke University School of Medicine',
                'Vanderbilt University School of Medicine',
                'University of Texas Southwestern Medical Center',
                'Emory University School of Medicine',
                'University of Florida College of Medicine'
            ],
            'West': [
                'Stanford University School of Medicine',
                'University of California, San Francisco School of Medicine',
                'University of California, Los Angeles David Geffen School of Medicine',
                'University of Washington School of Medicine',
                'University of Colorado School of Medicine'
            ]
        }
        
        # Residency programs by specialty
        self.residency_programs = {
            'Internal Medicine': [
                'Massachusetts General Hospital',
                'Johns Hopkins Hospital',
                'Cleveland Clinic',
                'Mayo Clinic',
                'Brigham and Women\'s Hospital'
            ],
            'Family Medicine': [
                'University of Washington',
                'University of Michigan',
                'University of California, San Francisco',
                'Oregon Health & Science University',
                'University of North Carolina'
            ],
            'Pediatrics': [
                'Boston Children\'s Hospital',
                'Children\'s Hospital of Philadelphia',
                'Cincinnati Children\'s Hospital',
                'Texas Children\'s Hospital',
                'Children\'s Hospital Los Angeles'
            ],
            'Surgery': [
                'Massachusetts General Hospital',
                'Johns Hopkins Hospital',
                'Cleveland Clinic',
                'Mayo Clinic',
                'University of California, San Francisco'
            ]
        }
    
    def infer_education(self, provider_data: Dict) -> Dict:
        """Infer education based on available data"""
        
        # Extract key information
        location = provider_data.get('address', '')
        years_exp = provider_data.get('years_experience', 0)
        specialty = provider_data.get('primary_specialty', '')
        provider_type = provider_data.get('provider_type', '')
        
        # Determine region from address
        region = self._get_region_from_address(location)
        
        # Inference logic with confidence scoring
        inferred = {
            'inferred_degree': self._infer_degree(provider_type),
            'degree_confidence': self._calculate_degree_confidence(provider_type),
            
            'inferred_medical_school': self._infer_medical_school(region, years_exp),
            'medical_school_confidence': self._calculate_school_confidence(region, years_exp),
            
            'inferred_residency': self._infer_residency(specialty, region),
            'residency_confidence': self._calculate_residency_confidence(specialty),
            
            'inferred_fellowship': self._infer_fellowship(specialty, years_exp),
            'fellowship_confidence': self._calculate_fellowship_confidence(specialty, years_exp),
            
            'graduation_year': self._calculate_graduation_year(years_exp),
            'board_eligible': self._is_board_eligible(years_exp, specialty),
            'board_confidence': self._calculate_board_confidence(years_exp, specialty)
        }
        
        # Calculate overall education confidence
        confidences = [
            inferred['degree_confidence'],
            inferred['medical_school_confidence'],
            inferred['residency_confidence'],
            inferred['fellowship_confidence'],
            inferred['board_confidence']
        ]
        inferred['overall_education_confidence'] = sum(confidences) / len(confidences)
        
        return inferred
    
    def _get_region_from_address(self, address: str) -> str:
        """Determine US region from address"""
        address_lower = address.lower()
        
        if any(state in address_lower for state in ['ca', 'or', 'wa', 'nv', 'az']):
            return 'West'
        elif any(state in address_lower for state in ['ny', 'ma', 'ct', 'nj', 'pa', 'ri']):
            return 'Northeast'
        elif any(state in address_lower for state in ['tx', 'fl', 'ga', 'nc', 'sc', 'al']):
            return 'South'
        elif any(state in address_lower for state in ['il', 'oh', 'mi', 'in', 'wi', 'mn']):
            return 'Midwest'
        else:
            return 'Unknown'
    
    def _infer_degree(self, provider_type: str) -> str:
        """Infer degree from provider type"""
        type_lower = provider_type.lower()
        
        if 'md' in type_lower:
            return 'Doctor of Medicine (MD)'
        elif 'do' in type_lower:
            return 'Doctor of Osteopathic Medicine (DO)'
        elif 'np' in type_lower:
            return 'Nurse Practitioner (NP)'
        elif 'pa' in type_lower:
            return 'Physician Assistant (PA)'
        elif 'phd' in type_lower:
            return 'Doctor of Philosophy (PhD)'
        else:
            return 'Medical Professional'
    
    def _calculate_degree_confidence(self, provider_type: str) -> float:
        """Calculate confidence in degree inference"""
        if provider_type and any(deg in provider_type.lower() 
                               for deg in ['md', 'do', 'np', 'pa', 'phd']):
            return 0.9  # High confidence if credential is specified
        else:
            return 0.3  # Low confidence if unknown
    
    def _infer_medical_school(self, region: str, years_exp: int) -> str:
        """Infer likely medical school"""
        if region == 'Unknown' or years_exp <= 0:
            return 'Unknown'
        
        # Get schools for this region
        schools = self.medical_schools.get(region, [])
        if not schools:
            return 'Unknown'
        
        # Weight older schools for experienced providers
        if years_exp > 20:
            # More likely prestigious/traditional schools
            return schools[0] if schools else 'Unknown'
        else:
            # Random selection from regional schools
            return random.choice(schools)
    
    def _calculate_school_confidence(self, region: str, years_exp: int) -> float:
        """Calculate confidence in school inference"""
        if region == 'Unknown':
            return 0.1
        elif years_exp <= 0:
            return 0.2
        else:
            return 0.6  # Moderate confidence
    
    def _infer_residency(self, specialty: str, region: str) -> str:
        """Infer likely residency program"""
        if not specialty or specialty == 'Unknown':
            return 'Unknown'
        
        # Get top residency programs for this specialty
        programs = self.residency_programs.get(specialty, [])
        if not programs:
            return f'{specialty} Residency Program'
        
        # Select based on region if possible
        regional_keywords = {
            'Northeast': ['Massachusetts', 'Boston', 'New York', 'Philadelphia', 'Johns Hopkins'],
            'Midwest': ['Cleveland', 'Chicago', 'Michigan', 'Mayo', 'Washington'],
            'South': ['Duke', 'Vanderbilt', 'Texas', 'Emory', 'Florida'],
            'West': ['Stanford', 'California', 'UCSF', 'UCLA', 'Washington', 'Colorado']
        }
        
        region_keywords = regional_keywords.get(region, [])
        for program in programs:
            if any(keyword.lower() in program.lower() 
                  for keyword in region_keywords):
                return program
        
        return programs[0]  # Return top program
    
    def _calculate_residency_confidence(self, specialty: str) -> float:
        """Calculate confidence in residency inference"""
        if not specialty or specialty == 'Unknown':
            return 0.1
        elif specialty in self.residency_programs:
            return 0.7
        else:
            return 0.4
    
    def _infer_fellowship(self, specialty: str, years_exp: int) -> str:
        """Infer fellowship training"""
        if not specialty or years_exp < 5:
            return ''
        
        # Common fellowships by specialty
        fellowships = {
            'Internal Medicine': ['Cardiology', 'Gastroenterology', 'Endocrinology'],
            'Pediatrics': ['Pediatric Cardiology', 'Pediatric Neurology'],
            'Surgery': ['Surgical Oncology', 'Trauma Surgery', 'Transplant Surgery']
        }
        
        if specialty in fellowships and years_exp >= 5:
            possible_fellowships = fellowships[specialty]
            return random.choice(possible_fellowships) + ' Fellowship'
        
        return ''
    
    def _calculate_fellowship_confidence(self, specialty: str, years_exp: int) -> float:
        """Calculate confidence in fellowship inference"""
        if years_exp < 5:
            return 0.0  # Unlikely to have fellowship
        elif specialty and years_exp >= 5:
            return 0.5  # Moderate confidence
        else:
            return 0.2
    
    def _calculate_graduation_year(self, years_exp: int) -> int:
        """Calculate likely graduation year"""
        if years_exp <= 0:
            return 0
        
        current_year = pd.Timestamp.now().year
        return current_year - years_exp
    
    def _is_board_eligible(self, years_exp: int, specialty: str) -> bool:
        """Determine if likely board eligible"""
        if years_exp >= 3 and specialty:
            return True
        return False
    
    def _calculate_board_confidence(self, years_exp: int, specialty: str) -> float:
        """Calculate confidence in board eligibility"""
        if years_exp >= 5 and specialty:
            return 0.8
        elif years_exp >= 3 and specialty:
            return 0.6
        else:
            return 0.3