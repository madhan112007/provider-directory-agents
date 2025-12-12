"""
Test suite for orchestrator
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'EY-Agent-Data Validation', 'EY-Agent-Data Validation'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Quality_Assurance_Agent', 'Quality_Assurance_Agent'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Automation_AGent_Correction'))

from orchestrator import ProviderOrchestrator
from datetime import datetime
import json

def test_single_provider():
    print("=" * 60)
    print("TEST 1: Single Provider Processing")
    print("=" * 60)
    
    orchestrator = ProviderOrchestrator()
    
    test_provider = {
        "provider_id": "TEST_P001",
        "name": "Dr. John Smith",
        "npi": "1234567890",
        "phone": "555-123-4567",
        "address": "123 Main Street, Boston, MA 02101",
        "specialty": "Cardiology",
        "state": "MA"
    }
    
    job_id = f"TEST_JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\n📋 Processing provider: {test_provider['name']}")
    print(f"🆔 Job ID: {job_id}")
    
    results = orchestrator.process_batch([test_provider], job_id)
    
    print(f"\n✅ Results:")
    print(f"   Total: {results['total']}")
    print(f"   Auto-Resolved: {results['auto_resolved']}")
    print(f"   Manual Review: {results['manual_review']}")
    print(f"   Errors: {results['errors']}")
    print(f"   Processing Time: {results['processing_time']:.2f}s")
    
    print(f"\n📊 Summary Report:")
    report = orchestrator.generate_summary_report(job_id)
    print(json.dumps(report, indent=2))
    
    return results

def test_batch_processing():
    print("\n" + "=" * 60)
    print("TEST 2: Batch Processing (10 Providers)")
    print("=" * 60)
    
    orchestrator = ProviderOrchestrator()
    
    test_providers = [
        {
            "provider_id": f"TEST_P{str(i).zfill(3)}",
            "name": f"Dr. Test Provider {i}",
            "npi": f"123456789{i}",
            "phone": f"555-{str(i).zfill(3)}-0000",
            "address": f"{i*100} Test St, Boston, MA 02101",
            "specialty": ["Cardiology", "Pediatrics", "Orthopedics"][i % 3],
            "state": ["MA", "CA", "NY"][i % 3]
        }
        for i in range(10)
    ]
    
    job_id = f"TEST_BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\n📋 Processing {len(test_providers)} providers")
    print(f"🆔 Job ID: {job_id}")
    
    results = orchestrator.process_batch(test_providers, job_id)
    
    print(f"\n✅ Results:")
    print(f"   Total: {results['total']}")
    print(f"   Auto-Resolved: {results['auto_resolved']} ({results['auto_resolved']/results['total']*100:.1f}%)")
    print(f"   Manual Review: {results['manual_review']} ({results['manual_review']/results['total']*100:.1f}%)")
    print(f"   Errors: {results['errors']}")
    print(f"   Processing Time: {results['processing_time']:.2f}s")
    print(f"   Avg Time/Provider: {results['processing_time']/results['total']:.2f}s")
    
    return results

def test_workflow_queue():
    print("\n" + "=" * 60)
    print("TEST 3: Workflow Queue")
    print("=" * 60)
    
    orchestrator = ProviderOrchestrator()
    
    queue = orchestrator.get_workflow_queue(10)
    
    print(f"\n📋 Workflow Queue: {len(queue)} items")
    
    for item in queue[:5]:
        print(f"\n   Provider: {item['provider_id']}")
        print(f"   Priority: {item['priority']}")
        print(f"   Status: {item['status']}")
        print(f"   Created: {item['created_at']}")
    
    return queue

def test_job_retrieval():
    print("\n" + "=" * 60)
    print("TEST 4: Job Status Retrieval")
    print("=" * 60)
    
    orchestrator = ProviderOrchestrator()
    
    # Create a test job first
    test_provider = {
        "provider_id": "TEST_RETRIEVE_001",
        "name": "Dr. Retrieve Test",
        "npi": "9999999999",
        "phone": "555-999-9999",
        "address": "999 Test Ave, Boston, MA",
        "specialty": "Testing",
        "state": "MA"
    }
    
    job_id = f"TEST_RETRIEVE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    orchestrator.process_batch([test_provider], job_id)
    
    # Retrieve job status
    job_status = orchestrator.get_job_status(job_id)
    
    print(f"\n📊 Job Status:")
    print(json.dumps(job_status, indent=2))
    
    return job_status

def test_error_handling():
    print("\n" + "=" * 60)
    print("TEST 5: Error Handling")
    print("=" * 60)
    
    orchestrator = ProviderOrchestrator()
    
    # Provider with missing required fields
    bad_provider = {
        "provider_id": "TEST_BAD_001",
        "name": "",  # Empty name
        "npi": "invalid",  # Invalid NPI
        "phone": "",
        "address": "",
        "specialty": "",
        "state": ""
    }
    
    job_id = f"TEST_ERROR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\n📋 Processing provider with errors")
    
    try:
        results = orchestrator.process_batch([bad_provider], job_id)
        print(f"\n✅ Error handling successful")
        print(f"   Errors caught: {results['errors']}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    
    return results

def run_all_tests():
    print("\n" + "=" * 60)
    print("🧪 ORCHESTRATOR TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Single Provider", test_single_provider),
        ("Batch Processing", test_batch_processing),
        ("Workflow Queue", test_workflow_queue),
        ("Job Retrieval", test_job_retrieval),
        ("Error Handling", test_error_handling)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔬 Running: {test_name}")
            result = test_func()
            results[test_name] = "✅ PASSED"
        except Exception as e:
            results[test_name] = f"❌ FAILED: {str(e)}"
            print(f"\n❌ Test failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, status in results.items():
        print(f"   {test_name}: {status}")
    
    passed = sum(1 for s in results.values() if "PASSED" in s)
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    return results

if __name__ == "__main__":
    run_all_tests()
