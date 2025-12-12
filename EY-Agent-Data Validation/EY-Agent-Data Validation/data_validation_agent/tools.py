import requests
import time
from typing import Dict, Any
from .utils import normalize_phone, normalize_address

def npi_lookup(provider: Dict[str, Any]) -> Dict[str, Any]:
    """
    Real NPI Registry API lookup
    API Docs: https://npiregistry.cms.hhs.gov/api-page
    """
    npi_from_input = provider.get("npi", "").strip()
    name = provider.get("name", "").strip()
    
    # Build query parameters
    params = {"version": "2.1"}
    
    if npi_from_input:
        params["number"] = npi_from_input
    elif name:
        # Search by name if NPI not provided
        name_parts = name.split()
        if len(name_parts) >= 2:
            params["first_name"] = name_parts[0]
            params["last_name"] = name_parts[-1]
    
    try:
        response = requests.get(
            "https://npiregistry.cms.hhs.gov/api/",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("result_count", 0) > 0:
            result = data["results"][0]
            basic = result.get("basic", {})
            addresses = result.get("addresses", [])
            taxonomies = result.get("taxonomies", [])
            
            # Get practice address
            practice_addr = next(
                (a for a in addresses if a.get("address_purpose") == "LOCATION"),
                addresses[0] if addresses else {}
            )
            
            # Get primary taxonomy
            primary_tax = next(
                (t for t in taxonomies if t.get("primary")),
                taxonomies[0] if taxonomies else {}
            )
            
            return {
                "npi_found": True,
                "npi": result.get("number", npi_from_input),
                "name": f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip(),
                "primary_taxonomy": primary_tax.get("desc", ""),
                "practice_address": f"{practice_addr.get('address_1', '')} {practice_addr.get('city', '')} {practice_addr.get('state', '')}".strip(),
                "license_state": practice_addr.get("state", ""),
                "source": "npi_registry",
                "timestamp": time.time()
            }
    except Exception as e:
        print(f"NPI lookup error: {e}")
    
    # Fallback if API fails or no results
    return {
        "npi_found": False,
        "npi": npi_from_input,
        "name": name,
        "primary_taxonomy": provider.get("specialty", ""),
        "practice_address": provider.get("address", ""),
        "license_state": provider.get("state", ""),
        "source": "input_only",
        "timestamp": time.time()
    }

def maps_lookup(provider: Dict[str, Any]) -> Dict[str, Any]:
    """
    Google Maps Geocoding API for address validation
    Get API key: https://console.cloud.google.com/apis/credentials
    """
    input_addr = provider.get("address", "").strip()
    input_phone = provider.get("phone", "").strip()
    
    # Set your Google Maps API key here or use environment variable
    GOOGLE_MAPS_API_KEY = "AIzaSyD_DdM1LuuHk-jo8NV4A5W6nKf5c-_Wmng"
    
    normalized_addr = normalize_address(input_addr)
    normalized_phone = normalize_phone(input_phone)
    
    if not GOOGLE_MAPS_API_KEY:
        # Fallback to basic normalization if no API key
        return {
            "normalized_address": normalized_addr,
            "normalized_phone": normalized_phone,
            "address_match_score": 0.7,
            "phone_match_score": 0.7,
            "geo_confirmed": False,
            "source": "basic_normalization",
            "timestamp": time.time()
        }
    
    try:
        # Geocoding API call
        response = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={
                "address": input_addr,
                "key": GOOGLE_MAPS_API_KEY
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "OK" and data.get("results"):
            result = data["results"][0]
            formatted_addr = result.get("formatted_address", normalized_addr)
            
            # Calculate match score based on location type
            location_type = result.get("geometry", {}).get("location_type", "")
            match_score = {
                "ROOFTOP": 1.0,
                "RANGE_INTERPOLATED": 0.9,
                "GEOMETRIC_CENTER": 0.7,
                "APPROXIMATE": 0.5
            }.get(location_type, 0.6)
            
            return {
                "normalized_address": formatted_addr,
                "normalized_phone": normalized_phone,
                "address_match_score": match_score,
                "phone_match_score": 0.8 if normalized_phone else 0.5,
                "geo_confirmed": True,
                "source": "google_maps",
                "timestamp": time.time()
            }
    except Exception as e:
        print(f"Maps lookup error: {e}")
    
    # Fallback
    return {
        "normalized_address": normalized_addr,
        "normalized_phone": normalized_phone,
        "address_match_score": 0.6,
        "phone_match_score": 0.6,
        "geo_confirmed": False,
        "source": "fallback",
        "timestamp": time.time()
    }

def validate_email_format(email: str) -> float:
    """Simple email format validation"""
    if not email or "@" not in email:
        return 0.0
    domain = email.split("@")[-1]
    return 0.9 if "." in domain else 0.4
