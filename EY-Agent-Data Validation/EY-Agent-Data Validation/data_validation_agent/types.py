from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class FieldTag(str, Enum):
    CONFIRMED = "confirmed"
    UPDATED = "updated"
    SUSPECT = "suspect"
    MISSING = "missing"

@dataclass
class FieldResult:
    value: Any
    confidence: float
    tag: FieldTag
    sources: List[str]
    last_verified: Optional[str] = None

@dataclass
class ValidationResult:
    provider_id: str
    fields: Dict[str, FieldResult]
    provider_confidence: float
