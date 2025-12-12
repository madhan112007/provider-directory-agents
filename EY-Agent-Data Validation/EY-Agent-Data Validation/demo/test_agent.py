import pytest
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_validation_agent.agent import DataValidationAgent

@pytest.fixture
def agent():
    return DataValidationAgent()

@pytest.fixture
def sample_provider():
    return {
        "provider_id": "TEST_001",
        "name": "Dr. Test Provider",
        "address": "123 Test St, Test City",
        "phone": "+1-555-123-4567",
        "specialty": "Test Medicine"
    }

def test_validate_contact_info(agent, sample_provider):
    result = agent.validate_contact_info(sample_provider)
    assert result["provider_id"] == "TEST_001"
    assert 0.0 <= result["provider_confidence"] <= 1.0
    assert len(result["fields"]) >= 4  # name, npi, specialty, address, phone

def test_get_validation_summary(agent, sample_provider):
    full_result = agent.validate_contact_info(sample_provider)
    summary = agent.get_validation_summary("TEST_001")
    assert "provider_confidence" in summary
    assert summary["provider_id"] == "TEST_001"
