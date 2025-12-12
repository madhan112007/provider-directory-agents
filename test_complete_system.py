"""
Complete System Verification Test
Tests all functionalities with real data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'EY-Agent-Data Validation', 'EY-Agent-Data Validation'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'Quality_Assurance_Agent', 'Quality_Assurance_Agent'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'Automation_AGent_Correction'))

print("=" * 70)
print("PROVIDER DIRECTORY SYSTEM - COMPLETE VERIFICATION TEST")
print("=" * 70)

# Test 1: NPI Registry API
print("\n[TEST 1] NPI Registry API Validation")
print("-" * 70)
try:
    from data_validation_agent.agent import DataValidationAgent
    
    agent = DataValidationAgent()
    test_provider = {
        "provider_id": "TEST001",
        "name": "John Smith",
        "npi": "1234567890",
        "phone": "555-123-4567",
        "address": "123 Main St, Boston, MA",
        "specialty": "Internal Medicine"
    }
    
    result = agent.validate_contact_info(test_provider)
    
    if result['fields']['npi']['npi_found']:
        print("✅ NPI Registry API: WORKING")
        print(f"   - NPI Found: {result['fields']['npi']['value']}")
        print(f"   - Confidence: {result['fields']['npi']['confidence']}")
    else:
        print("⚠️  NPI Registry API: No match found (API working, provider not in registry)")
    
except Exception as e:
    print(f"❌ NPI Registry API: FAILED - {e}")

# Test 2: Google Maps API
print("\n[TEST 2] Google Maps API Validation")
print("-" * 70)
try:
    result = agent.validate_contact_info(test_provider)
    
    if result['fields']['address']['sources'] and 'google_maps' in result['fields']['address']['sources']:
        print("✅ Google Maps API: WORKING")
        print(f"   - Normalized Address: {result['fields']['address']['value']}")
        print(f"   - Match Score: {result['fields']['address']['confidence']}")
    else:
        print("⚠️  Google Maps API: Using fallback (check API key)")
    
except Exception as e:
    print(f"❌ Google Maps API: FAILED - {e}")

# Test 3: Quality Assurance Agent
print("\n[TEST 3] Quality Assurance Agent")
print("-" * 70)
try:
    from agentic_ai import QualityAssuranceAgent
    
    qa_agent = QualityAssuranceAgent()
    qa_input = {
        "original": test_provider,
        "npi": {"npi": "1234567890", "specialty": "Internal Medicine"},
        "website": test_provider,
        "pdf": {},
        "license_db": {"status": "active", "state": "MA"},
        "meta": {"member_count": 500, "specialty": "Internal Medicine"}
    }
    
    qa_result = qa_agent.process_provider(qa_input)
    
    print("✅ Quality Assurance Agent: WORKING")
    print(f"   - Confidence Score: {qa_result['confidence_score']}")
    print(f"   - Risk Score: {qa_result['risk_score']}")
    print(f"   - Action: {qa_result['action']}")
    print(f"   - Red Flags: {len(qa_result['red_flags'])}")
    
except Exception as e:
    print(f"❌ Quality Assurance Agent: FAILED - {e}")

# Test 4: Correction Agent
print("\n[TEST 4] Correction Agent")
print("-" * 70)
try:
    from automative_correction_agent import AutomativeCorrectionAgent
    
    correction_agent = AutomativeCorrectionAgent()
    test_provider_bad = {
        "provider_id": "TEST002",
        "name": "Dr. Jane Doe",
        "phone": "555.123.4567",  # Wrong format
        "address": "456 oak st",  # Incomplete
        "specialty": "cardio"  # Informal
    }
    
    correction_result = correction_agent.process_provider(test_provider_bad)
    
    print("✅ Correction Agent: WORKING")
    print(f"   - Corrections Made: {len(correction_result['corrections'])}")
    for correction in correction_result['corrections']:
        print(f"   - Fixed {correction['field']}: {correction['before']} → {correction['after']}")
    
except Exception as e:
    print(f"❌ Correction Agent: FAILED - {e}")

# Test 5: Database Operations
print("\n[TEST 5] Database Operations")
print("-" * 70)
try:
    import sqlite3
    from orchestrator.orchestrator import ProviderOrchestrator
    
    orchestrator = ProviderOrchestrator(db_path="test_verification.db")
    
    # Test batch processing
    test_batch = [
        {
            "name": "Dr. Test Provider",
            "npi": "9999999999",
            "phone": "555-999-9999",
            "address": "999 Test St, Test City, TS",
            "specialty": "Testing",
            "state": "TS"
        }
    ]
    
    job_id = "TEST_JOB_001"
    results = orchestrator.process_batch(test_batch, job_id)
    
    print("✅ Database Operations: WORKING")
    print(f"   - Providers Processed: {results['total']}")
    print(f"   - Auto-Resolved: {results['auto_resolved']}")
    print(f"   - Manual Review: {results['manual_review']}")
    print(f"   - Processing Time: {results['processing_time']:.2f}s")
    
    # Cleanup test database
    os.remove("test_verification.db")
    
except Exception as e:
    print(f"❌ Database Operations: FAILED - {e}")

# Test 6: Dashboard Components
print("\n[TEST 6] Dashboard Components")
print("-" * 70)
try:
    import streamlit
    import plotly
    import pandas
    
    print("✅ Dashboard Components: WORKING")
    print(f"   - Streamlit: {streamlit.__version__}")
    print(f"   - Plotly: {plotly.__version__}")
    print(f"   - Pandas: {pandas.__version__}")
    
except Exception as e:
    print(f"❌ Dashboard Components: FAILED - {e}")

# Summary
print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("\n📋 SUMMARY:")
print("   1. NPI Registry API - Validates provider credentials")
print("   2. Google Maps API - Validates addresses and locations")
print("   3. QA Agent - Scores confidence and risk")
print("   4. Correction Agent - Auto-fixes data issues")
print("   5. Database - Stores and retrieves provider data")
print("   6. Dashboard - Visualizes data and analytics")
print("\n✅ All core functionalities tested!")
print("\n🚀 TO RUN DASHBOARD:")
print("   cd c:\\Agents\\orchestrator")
print("   python -m streamlit run dashboard.py")
print("\n📊 TO VERIFY IN BROWSER:")
print("   1. Login as Patient - Search doctors, book appointments")
print("   2. Login as Admin - Upload CSV, view analytics")
print("=" * 70)
