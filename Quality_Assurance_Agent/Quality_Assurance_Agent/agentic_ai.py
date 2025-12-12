import json
import time
from typing import Dict, List, Any

class QualityAssuranceAgent:
    def __init__(self):
        self.metrics = {
            "total_processed": 0,
            "auto_resolved": 0,
            "manual_review": 0,
            "error_types": {},
            "validation_accuracy": 0
        }
        
    def process_provider(self, provider_data: Dict) -> Dict:
        """Main QA processing pipeline"""
        # Extract data sources
        original = provider_data.get("original", {})
        npi_data = provider_data.get("npi", {})
        website_data = provider_data.get("website", {})
        pdf_data = provider_data.get("pdf", {})
        license_data = provider_data.get("license_db", {})
        meta = provider_data.get("meta", {})
        
        
        element_confidence = self._compute_element_confidence(original, npi_data, website_data, pdf_data, license_data)
        
        
        cross_reference = self._cross_reference_sources(original, npi_data, website_data, pdf_data, license_data)
        
        
        red_flags = self._identify_red_flags(cross_reference, license_data, npi_data)
        
        
        conflicts = self._identify_conflicts(original, npi_data, website_data, pdf_data)
        
        
        risk_flags = self._apply_risk_heuristics(license_data, npi_data, website_data)
        
       
        confidence_score = self._compute_confidence_score(provider_data)
        risk_score = self._compute_risk_score(risk_flags, conflicts)
        impact_score = self._compute_impact_score(meta)
        
        
        action = self._determine_action(confidence_score, risk_score, impact_score)
        
        
        self._update_metrics(action, risk_flags, conflicts)
        
        return {
            "action": action,
            "confidence_score": confidence_score,
            "risk_score": risk_score,
            "impact_score": impact_score,
            "element_confidence": element_confidence,
            "cross_reference_analysis": cross_reference,
            "red_flags": red_flags,
            "conflicts": conflicts,
            "risk_flags": risk_flags
        }
    
    def _compute_element_confidence(self, original: Dict, npi: Dict, website: Dict, pdf: Dict, license: Dict) -> Dict:
        """Generate confidence score for each data element"""
        elements = {}
        
        # Name confidence
        name_sources = [d.get("name") for d in [original, npi, website, pdf] if d.get("name")]
        elements["name"] = {"score": len(name_sources) * 25, "sources": len(name_sources), "consistent": len(set(name_sources)) == 1}
        
        # Phone confidence
        phone_sources = [d.get("phone") for d in [original, npi, website, pdf] if d.get("phone")]
        elements["phone"] = {"score": len(phone_sources) * 25, "sources": len(phone_sources), "consistent": len(set(phone_sources)) == 1}
        
        # Address confidence
        addr_sources = [d.get("address") for d in [original, npi, website, pdf] if d.get("address")]
        elements["address"] = {"score": len(addr_sources) * 25, "sources": len(addr_sources), "consistent": len(set(addr_sources)) == 1}
        
        # Specialty confidence
        spec_sources = [d.get("specialty") for d in [original, npi, website, pdf] if d.get("specialty")]
        elements["specialty"] = {"score": len(spec_sources) * 25, "sources": len(spec_sources), "consistent": len(set(spec_sources)) == 1}
        
        # State confidence
        state_sources = [d.get("state") for d in [original, npi, website, license] if d.get("state")]
        elements["state"] = {"score": len(state_sources) * 25, "sources": len(state_sources), "consistent": len(set(state_sources)) == 1}
        
        # NPI confidence
        elements["npi"] = {"score": 100 if npi.get("npi") else 0, "sources": 1 if npi.get("npi") else 0, "consistent": True}
        
        # License confidence
        elements["license"] = {"score": 100 if license.get("status") == "active" else 50 if license.get("status") else 0, "sources": 1 if license.get("status") else 0, "consistent": True}
        
        return elements
    
    def _cross_reference_sources(self, original: Dict, npi: Dict, website: Dict, pdf: Dict, license: Dict) -> Dict:
        """Cross-reference information across multiple sources"""
        analysis = {}
        
        # Name cross-reference
        analysis["name"] = {
            "original": original.get("name"),
            "npi": npi.get("name"),
            "website": website.get("name"),
            "pdf": pdf.get("name"),
            "match": len(set([d.get("name") for d in [original, npi, website, pdf] if d.get("name")])) <= 1
        }
        
        
        analysis["phone"] = {
            "original": original.get("phone"),
            "npi": npi.get("phone"),
            "website": website.get("phone"),
            "pdf": pdf.get("phone"),
            "match": len(set([d.get("phone") for d in [original, npi, website, pdf] if d.get("phone")])) <= 1
        }
        
        
        analysis["address"] = {
            "original": original.get("address"),
            "npi": npi.get("address"),
            "website": website.get("address"),
            "pdf": pdf.get("address"),
            "match": len(set([d.get("address") for d in [original, npi, website, pdf] if d.get("address")])) <= 1
        }
        
        # Specialty cross-reference
        analysis["specialty"] = {
            "original": original.get("specialty"),
            "npi": npi.get("specialty"),
            "website": website.get("specialty"),
            "pdf": pdf.get("specialty"),
            "match": len(set([d.get("specialty") for d in [original, npi, website, pdf] if d.get("specialty")])) <= 1
        }
        
        # State cross-reference
        analysis["state"] = {
            "original": original.get("state"),
            "npi": npi.get("state"),
            "website": website.get("state"),
            "license": license.get("state"),
            "match": len(set([d.get("state") for d in [original, npi, website, license] if d.get("state")])) <= 1
        }
        
        return analysis
    
    def _identify_red_flags(self, cross_ref: Dict, license: Dict, npi: Dict) -> List[str]:
        """Identify red flags and inconsistencies"""
        flags = []
        
        # Inconsistent data across sources
        for field, data in cross_ref.items():
            if not data.get("match"):
                flags.append(f"INCONSISTENT_{field.upper()}: Multiple conflicting values found")
        
        # License issues
        if license.get("status") == "inactive":
            flags.append("INACTIVE_LICENSE: Provider has inactive license")
        elif not license.get("status"):
            flags.append("MISSING_LICENSE: No license information found")
        
        # NPI issues
        if not npi.get("npi"):
            flags.append("MISSING_NPI: No NPI number found")
        
        # State mismatch
        states = [cross_ref.get("state", {}).get(k) for k in ["original", "npi", "website", "license"] if cross_ref.get("state", {}).get(k)]
        if len(set(states)) > 1:
            flags.append(f"STATE_MISMATCH: Practice state differs from license state")
        
        return flags
    
    def _identify_conflicts(self, original: Dict, npi: Dict, website: Dict, pdf: Dict) -> Dict:
        """Compare values across data sources"""
        conflicts = {}
        
        # Address conflicts
        addresses = [d.get("address") for d in [original, npi, website, pdf] if d.get("address")]
        if len(set(addresses)) > 1:
            conflicts["address_mismatch"] = True
            
        # Phone conflicts
        phones = [d.get("phone") for d in [original, npi, website, pdf] if d.get("phone")]
        if len(set(phones)) > 1:
            conflicts["phone_mismatch"] = True
            
        # Specialty conflicts
        specialties = [d.get("specialty") for d in [original, npi, website, pdf] if d.get("specialty")]
        if len(set(specialties)) > 1:
            conflicts["specialty_mismatch"] = True
            
        return conflicts
    
    def _apply_risk_heuristics(self, license_data: Dict, npi_data: Dict, website_data: Dict) -> Dict:
        """Apply fraud/risk detection rules"""
        flags = {}
        
        # No active license but still in network
        flags["inactive_license_in_network"] = license_data.get("status") != "active"
        
        # Different state license than practice location
        license_state = license_data.get("state")
        practice_state = website_data.get("state") or npi_data.get("state")
        flags["license_state_mismatch"] = license_state != practice_state if license_state and practice_state else False
        
        # Missing NPI
        flags["missing_npi"] = not npi_data.get("npi")
        
        # Suspicious specialty change
        flags["specialty_change"] = bool(npi_data.get("specialty") and website_data.get("specialty") and 
                                        npi_data.get("specialty") != website_data.get("specialty"))
        
        return flags
    
    def _compute_confidence_score(self, data: Dict) -> int:
        """Compute data confidence score (0-100)"""
        score = 0
        if data.get("npi", {}).get("npi"): score += 25
        if data.get("license_db", {}).get("status") == "active": score += 25
        if data.get("website", {}).get("name"): score += 20
        if data.get("pdf", {}).get("content"): score += 15
        if data.get("original", {}).get("name"): score += 15
        return min(score, 100)
    
    def _compute_risk_score(self, risk_flags: Dict, conflicts: Dict) -> int:
        """Compute risk score (0-100)"""
        score = 0
        if risk_flags.get("inactive_license_in_network"): score += 40
        if risk_flags.get("missing_npi"): score += 30
        if risk_flags.get("license_state_mismatch"): score += 25
        if risk_flags.get("specialty_change"): score += 20
        if conflicts.get("address_mismatch"): score += 15
        if conflicts.get("phone_mismatch"): score += 10
        if conflicts.get("specialty_mismatch"): score += 15
        return min(score, 100)
    
    def _compute_impact_score(self, meta: Dict) -> int:
        """Compute member impact score"""
        score = 30  # base
        member_count = meta.get("member_count", 0)
        if member_count > 1000: score += 40
        elif member_count > 500: score += 25
        elif member_count > 100: score += 15
        
        if meta.get("specialty") in ["cardiology", "oncology", "emergency"]: score += 20
        if meta.get("region_priority") == "high": score += 10
        return min(score, 100)
    
    def _determine_action(self, confidence, risk, impact):
    

    # High risk → must review
        if risk >= 60:
            return "manual_review"

    # Medium risk + medium confidence → review
        if risk >= 30 and confidence < 50:
            return "manual_review"

    # Very low confidence → review
        if confidence <= 30:
            return "manual_review"

    # High-impact provider with some uncertainty
        if impact >= 80 and confidence < 60:
            return "manual_review"

    # Otherwise AUTO RESOLVE
        return "auto_resolve"

    
    def _update_metrics(self, action: str, risk_flags: Dict, conflicts: Dict):
        """Update run-level metrics"""
        self.metrics["total_processed"] += 1
        
        if action == "auto_resolve":
            self.metrics["auto_resolved"] += 1
        else:
            self.metrics["manual_review"] += 1
        
        # Track error types
        for flag, is_set in {**risk_flags, **conflicts}.items():
            if is_set:
                self.metrics["error_types"][flag] = self.metrics["error_types"].get(flag, 0) + 1
    
    def get_metrics(self) -> Dict:
        """Get KPI metrics"""
        total = self.metrics["total_processed"]
        if total == 0:
            return {"message": "No data processed"}
        
        manual_review_rate = (self.metrics["manual_review"] / total) * 100
        top_errors = sorted(self.metrics["error_types"].items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_processed": total,
            "manual_review_rate": round(manual_review_rate, 1),
            "auto_resolve_rate": round((self.metrics["auto_resolved"] / total) * 100, 1),
            "manual_review_count": self.metrics["manual_review"],
            "auto_resolve_count": self.metrics["auto_resolved"],
            "top_error_types": dict(top_errors),
            "target_review_rate": "10-20%",
            "within_target": 10 <= manual_review_rate <= 20
        }

# Simple usage
if __name__ == "__main__":
    agent = QualityAssuranceAgent()
    
    """# Test data
    test_provider = {
        "npi": {"npi": "1234567890", "specialty": "cardiology"},
        "license_db": {"status": "active", "state": "CA"},
        "website": {"specialty": "cardiology", "state": "CA"},
        "meta": {"member_count": 500, "priority": "normal"}
    }
    
    result = agent.process_provider(test_provider)
    print(json.dumps(result, indent=2))"""
