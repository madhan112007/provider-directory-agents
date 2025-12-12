"""
System Test & Verification Script
Tests all components of the Automative Correction Agent system.
"""

import sys
from datetime import datetime


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_correction_agent():
    """Test Automative Correction Agent"""
    print_header("TEST 1: Automative Correction Agent")
    
    try:
        from automative_correction_agent import AutomativeCorrectionAgent
        
        agent = AutomativeCorrectionAgent(confidence_threshold=0.9)
        
        # Test phone correction
        phone_result = agent.correct_phone_number("555.123.4567")
        assert phone_result[0] == "(555) 123-4567", "Phone correction failed"
        print("[PASS] Phone correction: PASSED")
        
        # Test specialty correction
        specialty_result = agent.correct_specialty("cardio")
        assert specialty_result[0] == "Cardiology", "Specialty correction failed"
        print("[PASS] Specialty normalization: PASSED")
        
        # Test provider processing
        test_provider = {
            'provider_id': 'TEST001',
            'name': 'Test Provider',
            'phone': '555.123.4567',
            'address': '123 Main St',
            'specialty': 'cardio'
        }
        result = agent.process_provider(test_provider)
        assert len(result['corrections']) > 0, "Provider processing failed"
        print("[PASS] Provider processing: PASSED")
        
        # Test statistics
        stats = agent.get_statistics()
        assert 'total_providers_corrected' in stats, "Statistics failed"
        print("[PASS] Statistics generation: PASSED")
        
        print("\n[PASS] Automative Correction Agent: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Automative Correction Agent: FAILED - {e}")
        return False


def test_email_generator():
    """Test Email Generator"""
    print_header("TEST 2: Email Generator")
    
    try:
        from email_generator import EmailGenerator
        
        email_gen = EmailGenerator()
        
        # Test correction email generation
        test_provider = {
            'provider_id': 'TEST001',
            'name': 'Test Provider',
            'email': 'test@example.com'
        }
        test_corrections = [
            {
                'field': 'phone',
                'before': '555.123.4567',
                'after': '(555) 123-4567',
                'confidence': 0.95,
                'source': 'Test'
            }
        ]
        
        email_data = email_gen.generate_correction_email(test_provider, test_corrections)
        assert email_data['to_email'] == 'test@example.com', "Email generation failed"
        print("[PASS] Correction email generation: PASSED")
        
        # Test email sending (dry run)
        status = email_gen.send_email(email_data, dry_run=True)
        assert status['status'] == 'sent_dry_run', "Email sending failed"
        print("[PASS] Email sending (dry run): PASSED")
        
        # Test manual review email
        issues = ["Test issue 1", "Test issue 2"]
        manual_email = email_gen.generate_manual_review_email(test_provider, issues)
        assert manual_email['type'] == 'manual_review', "Manual review email failed"
        print("[PASS] Manual review email: PASSED")
        
        # Test statistics
        stats = email_gen.get_email_statistics()
        assert 'total_emails' in stats, "Email statistics failed"
        print("[PASS] Email statistics: PASSED")
        
        print("\n[PASS] Email Generator: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Email Generator: FAILED - {e}")
        return False


def test_integration():
    """Test Integration Pipeline"""
    print_header("TEST 3: Integration Pipeline")
    
    try:
        from automative_correction_agent import AutomativeCorrectionAgent
        from email_generator import EmailGenerator, create_email_pipeline
        
        agent = AutomativeCorrectionAgent()
        email_gen = EmailGenerator()
        process_and_notify = create_email_pipeline(agent, email_gen)
        
        # Test integrated workflow
        test_provider = {
            'provider_id': 'TEST002',
            'name': 'Integration Test Provider',
            'email': 'integration@example.com',
            'phone': '555.999.8888',
            'address': '999 Test St',
            'specialty': 'ortho'
        }
        
        result = process_and_notify(test_provider, dry_run=True)
        assert 'provider_data' in result, "Integration failed"
        assert 'corrections' in result, "Integration failed"
        assert 'email_status' in result, "Integration failed"
        print("[PASS] Integrated workflow: PASSED")
        
        print("\n[PASS] Integration Pipeline: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Integration Pipeline: FAILED - {e}")
        return False


def test_csv_processor():
    """Test CSV Processor"""
    print_header("TEST 4: CSV Processor")
    
    try:
        import os
        from csv_processor import CSVProcessor
        
        csv_file = 'sample_data.csv'
        
        if not os.path.exists(csv_file):
            print(f"[WARN] Warning: {csv_file} not found, skipping CSV tests")
            return True
        
        processor = CSVProcessor(csv_file)
        
        # Test CSV reading
        providers = processor.read_csv()
        assert len(providers) > 0, "CSV reading failed"
        print(f"[PASS] CSV reading: PASSED ({len(providers)} providers)")
        
        # Test processing (first 2 providers only for speed)
        test_providers = providers[:2]
        processor.agent.batch_process(test_providers)
        print("[PASS] CSV processing: PASSED")
        
        print("\n[PASS] CSV Processor: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] CSV Processor: FAILED - {e}")
        return False


def test_api_endpoints():
    """Test API structure"""
    print_header("TEST 5: API Endpoints")
    
    try:
        from automative_correction_agent import create_correction_api
        
        api = create_correction_api()
        
        # Test API structure
        assert 'correct_provider' in api, "API structure failed"
        assert 'correct_batch' in api, "API structure failed"
        assert 'get_history' in api, "API structure failed"
        assert 'get_stats' in api, "API structure failed"
        print("[PASS] API structure: PASSED")
        
        # Test API functions
        test_provider = {
            'provider_id': 'API001',
            'name': 'API Test',
            'phone': '555.111.2222',
            'specialty': 'peds'
        }
        
        result = api['correct_provider'](test_provider)
        assert 'provider_data' in result, "API function failed"
        print("[PASS] API functions: PASSED")
        
        stats = api['get_stats']()
        assert 'total_providers_corrected' in stats, "API stats failed"
        print("[PASS] API statistics: PASSED")
        
        print("\n[PASS] API Endpoints: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] API Endpoints: FAILED - {e}")
        return False


def verify_files():
    """Verify all required files exist"""
    print_header("FILE VERIFICATION")
    
    required_files = [
        'automative_correction_agent.py',
        'email_generator.py',
        'dashboard_ui.py',
        'demo_scenarios.py',
        'csv_processor.py',
        'requirements.txt',
        'README.md',
        'QUICKSTART.md',
        'PROJECT_SUMMARY.md',
        'sample_data.csv'
    ]
    
    all_exist = True
    for file in required_files:
        import os
        if os.path.exists(file):
            print(f"[OK] {file}")
        else:
            print(f"[MISSING] {file}")
            all_exist = False
    
    if all_exist:
        print("\n[OK] All required files present")
    else:
        print("\n[ERROR] Some files are missing")
    
    return all_exist


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("  AUTOMATIVE CORRECTION AGENT - SYSTEM TEST")
    print("="*70)
    print(f"\n  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # File verification
    results.append(("File Verification", verify_files()))
    
    # Component tests
    results.append(("Correction Agent", test_correction_agent()))
    results.append(("Email Generator", test_email_generator()))
    results.append(("Integration Pipeline", test_integration()))
    results.append(("CSV Processor", test_csv_processor()))
    results.append(("API Endpoints", test_api_endpoints()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name:.<50} {status}")
    
    print("\n" + "="*70)
    print(f"  TOTAL: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n*** ALL TESTS PASSED - System is ready for demo!")
        print("\nNext Steps:")
        print("  1. Run demos: python demo_scenarios.py")
        print("  2. Launch dashboard: python dashboard_ui.py")
        print("  3. Process CSV: python csv_processor.py")
    else:
        print("\n*** Some tests failed - please review errors above")
    
    print(f"\n  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
