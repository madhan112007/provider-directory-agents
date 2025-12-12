import re
from typing import Any
from .types import FieldTag

def calculate_confidence_score(*scores: float) -> float:
    """Average confidence scores with minimum 0.0, maximum 1.0"""
    if not scores:
        return 0.0
    avg = sum(scores) / len(scores)
    return max(0.0, min(1.0, avg))

def tag_from_confidence(conf: float, value: Any) -> FieldTag:
    """Map confidence to tag"""
    if value in [None, "", []]:
        return FieldTag.MISSING
    
    if conf >= 0.90:
        return FieldTag.CONFIRMED
    elif conf >= 0.70:
        return FieldTag.UPDATED
    else:
        return FieldTag.SUSPECT

def normalize_phone(phone: str) -> str:
    """Basic phone normalization"""
    import phonenumbers
    try:
        parsed = phonenumbers.parse(phone, None)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except:
        return phone.strip()

def normalize_address(address: str) -> str:
    """Basic address normalization"""
    return re.sub(r'\s+', ' ', address.strip().upper())
