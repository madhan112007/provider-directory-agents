"""
Utility functions for the enrichment agent
"""

import pandas as pd
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any

def save_to_cache(data: Any, provider_id: str, source: str):
    """Save API responses to cache"""
    cache_dir = f"data/cache/{source}"
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_file = f"{cache_dir}/{provider_id}.json"
    with open(cache_file, 'w') as f:
        json.dump(data, f, indent=2)

def load_from_cache(provider_id: str, source: str) -> Any:
    """Load API response from cache"""
    cache_file = f"data/cache/{source}/{provider_id}.json"
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return None

def clean_phone_number(phone: str) -> str:
    """Clean and format phone number"""
    if pd.isna(phone):
        return ""
    
    # Remove all non-digits
    digits = re.sub(r'\D', '', str(phone))
    
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    
    return str(phone).strip()

def extract_state_from_address(address: str) -> str:
    """Extract state abbreviation from address"""
    if pd.isna(address):
        return ""
    
    # Common state patterns
    states = {
        'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
        'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT',
        'delaware': 'DE', 'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI',
        'idaho': 'ID', 'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA',
        'kansas': 'KS', 'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME',
        'maryland': 'MD', 'massachusetts': 'MA', 'michigan': 'MI',
        'minnesota': 'MN', 'mississippi': 'MS', 'missouri': 'MO',
        'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
        'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM',
        'new york': 'NY', 'north carolina': 'NC', 'north dakota': 'ND',
        'ohio': 'OH', 'oklahoma': 'OK', 'oregon': 'OR', 'pennsylvania': 'PA',
        'rhode island': 'RI', 'south carolina': 'SC', 'south dakota': 'SD',
        'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT', 'vermont': 'VT',
        'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
        'wisconsin': 'WI', 'wyoming': 'WY'
    }
    
    address_lower = str(address).lower()
    
    # Look for state abbreviations (CA, NY, etc.)
    for word in address_lower.split():
        word = word.strip(',.')
        if word.upper() in states.values():
            return word.upper()
    
    # Look for full state names
    for state_name, state_abbr in states.items():
        if state_name in address_lower:
            return state_abbr
    
    return ""

def calculate_confidence_score(sources_count: int, data_quality: float) -> float:
    """Calculate overall confidence score"""
    if sources_count == 0:
        return 0.0
    
    source_score = min(sources_count / 3, 1.0)  # Max 3 sources
    quality_score = data_quality
    
    return round((source_score * 0.6 + quality_score * 0.4), 2)

def generate_provider_id(name: str, npi: str = "") -> str:
    """Generate unique provider ID"""
    if npi and str(npi).strip():
        return f"PROV_{str(npi).strip()}"
    
    # Use name if no NPI
    name_clean = re.sub(r'\W+', '', str(name).lower().replace(' ', '_'))
    return f"PROV_{name_clean[:20]}"

def format_timestamp() -> str:
    """Get current timestamp for filenames"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def print_progress(current: int, total: int, message: str = ""):
    """Print progress bar"""
    percentage = (current / total) * 100
    bar_length = 40
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    print(f'\r{message} |{bar}| {percentage:.1f}% ({current}/{total})', end='')
    if current == total:
        print()