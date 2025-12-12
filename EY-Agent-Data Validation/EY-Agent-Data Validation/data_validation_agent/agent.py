import time
from typing import Dict, Any
from datetime import datetime
from .types import FieldResult, FieldTag, ValidationResult
from .tools import npi_lookup, maps_lookup, validate_email_format
from .utils import calculate_confidence_score, tag_from_confidence, normalize_phone, normalize_address

class DataValidationAgent:
    def __init__(self):
        self.results_cache: Dict[str, ValidationResult] = {}
    
    def validate_contact_info(self, provider: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation function. Returns structured result.
        """
        provider_id = provider.get("provider_id")
        if not provider_id:
            raise ValueError("provider_id is required")
        
        start_time = time.time()
        
        # 1. Call external tools
        npi_data = npi_lookup(provider)
        maps_data = maps_lookup(provider)
        
        # 2. Field-by-field validation
        fields = {}
        
        # NAME
        input_name = provider.get("name", "")
        npi_name = npi_data.get("name", "")
        name_conf = 1.0 if input_name.lower() == npi_name.lower() else 0.75
        fields["name"] = FieldResult(
            value=input_name,
            confidence=name_conf,
            tag=tag_from_confidence(name_conf, input_name),
            sources=["input", "npi_registry"]
        )
        
        # NPI
        npi_conf = 0.95 if npi_data["npi_found"] else 0.3
        fields["npi"] = FieldResult(
            value=npi_data["npi"],
            confidence=npi_conf,
            tag=FieldTag.CONFIRMED if npi_data["npi_found"] else FieldTag.SUSPECT,
            sources=["npi_registry"]
        )
        
        # SPECIALTY
        input_spec = provider.get("specialty", "")
        npi_spec = npi_data.get("primary_taxonomy", "")
        spec_conf = 1.0 if input_spec.lower() == npi_spec.lower() else 0.8
        fields["specialty"] = FieldResult(
            value=input_spec,
            confidence=spec_conf,
            tag=tag_from_confidence(spec_conf, input_spec),
            sources=["input", "npi_registry"]
        )
        
        # ADDRESS
        input_addr = provider.get("address", "")
        maps_addr = maps_data["normalized_address"]
        addr_conf = maps_data["address_match_score"]
        fields["address"] = FieldResult(
            value=maps_addr if addr_conf >= 0.8 else input_addr,
            confidence=addr_conf,
            tag=tag_from_confidence(addr_conf, input_addr),
            sources=["input", "google_maps"]
        )
        
        # PHONE
        input_phone = provider.get("phone", "")
        maps_phone = maps_data["normalized_phone"]
        phone_format_conf = 0.9 if input_phone.startswith(("+1-", "+1")) else 0.5
        phone_match_conf = maps_data["phone_match_score"]
        phone_conf = calculate_confidence_score(phone_format_conf, phone_match_conf)
        fields["phone"] = FieldResult(
            value=maps_phone if phone_conf >= 0.8 else input_phone,
            confidence=phone_conf,
            tag=tag_from_confidence(phone_conf, input_phone),
            sources=["input", "google_maps"]
        )
        
        # EMAIL (optional)
        email = provider.get("email")
        if email:
            email_conf = validate_email_format(email)
            fields["email"] = FieldResult(
                value=email,
                confidence=email_conf,
                tag=tag_from_confidence(email_conf, email),
                sources=["input"]
            )
        
        # 3. Provider-level confidence
        confidences = [f.confidence for f in fields.values()]
        provider_confidence = sum(confidences) / len(confidences)
        
        # 4. Cache result
        result = ValidationResult(
            provider_id=provider_id,
            fields=fields,
            provider_confidence=provider_confidence
        )
        self.results_cache[provider_id] = result
        
        processing_time = time.time() - start_time
        print(f"Validated {provider_id} in {processing_time:.2f}s (confidence: {provider_confidence:.2f})")
        
        return self._result_to_dict(result)
    
    def get_validation_summary(self, provider_id: str) -> Dict[str, Any]:
        """Compact summary for other agents"""
        result = self.results_cache.get(provider_id)
        if not result:
            raise ValueError(f"No validation result for {provider_id}")
        
        return {
            "provider_id": provider_id,
            "provider_confidence": result.provider_confidence,
            "field_status": {k: v.tag.value for k, v in result.fields.items()},
            "critical_issues": sum(1 for v in result.fields.values() if v.tag == FieldTag.SUSPECT)
        }
    
    def _result_to_dict(self, result: ValidationResult) -> Dict[str, Any]:
        """Convert dataclass to dict for JSON serialization"""
        now = datetime.utcnow().isoformat()
        fields_dict = {
            k: {
                **vars(v),
                "last_verified": now
            }
            for k, v in result.fields.items()
        }
        return {
            "provider_id": result.provider_id,
            "fields": fields_dict,
            "provider_confidence": result.provider_confidence,
            "validation_time": now
        }
