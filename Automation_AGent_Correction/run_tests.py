"""
Quick test script to verify all components work correctly
"""

print("="*70)
print("TESTING AUTOMATIVE CORRECTION AGENT SYSTEM")
print("="*70)

# Test 1: Import all modules
print("\n[TEST 1] Importing modules...")
try:
    from automative_correction_agent import AutomativeCorrectionAgent
    from email_generator import EmailGenerator, create_email_pipeline
    import dashboard_ui
    print("  [PASS] All modules imported successfully")
except Exception as e:
    print(f"  [FAIL] Import error: {e}")
    exit(1)

# Test 2: Create agent instance
print("\n[TEST 2] Creating correction agent...")
try:
    agent = AutomativeCorrectionAgent(confidence_threshold=0.9)
    print("  [PASS] Agent created successfully")
except Exception as e:
    print(f"  [FAIL] Agent creation error: {e}")
    exit(1)

# Test 3: Process provider data
print("\n[TEST 3] Processing provider data...")
try:
    test_provider = {
        'provider_id': 'TEST001',
        'name': 'Dr. Test Provider',
        'email': 'test@example.com',
        'phone': '555.123.4567',
        'address': '123 Test St Boston MA',
        'specialty': 'cardio'
    }
    result = agent.process_provider(test_provider)
    print(f"  [PASS] Processed provider with {len(result['corrections'])} corrections")
    for correction in result['corrections']:
        print(f"    - {correction['field']}: {correction['before']} -> {correction['after']}")
except Exception as e:
    print(f"  [FAIL] Processing error: {e}")
    exit(1)

# Test 4: Email generator
print("\n[TEST 4] Testing email generator...")
try:
    email_gen = EmailGenerator()
    if result['corrections']:
        email_data = email_gen.generate_correction_email(
            result['provider_data'],
            result['corrections']
        )
        email_status = email_gen.send_email(email_data, dry_run=True)
        print(f"  [PASS] Email generated and sent (dry run)")
        print(f"    - To: {email_status['to_email']}")
        print(f"    - Status: {email_status['status']}")
except Exception as e:
    print(f"  [FAIL] Email error: {e}")
    exit(1)

# Test 5: Statistics
print("\n[TEST 5] Getting statistics...")
try:
    stats = agent.get_statistics()
    email_stats = email_gen.get_email_statistics()
    print(f"  [PASS] Statistics retrieved")
    print(f"    - Providers corrected: {stats['total_providers_corrected']}")
    print(f"    - Fields corrected: {stats['total_fields_corrected']}")
    print(f"    - Emails sent: {email_stats['sent']}")
except Exception as e:
    print(f"  [FAIL] Statistics error: {e}")
    exit(1)

# Test 6: Batch processing
print("\n[TEST 6] Testing batch processing...")
try:
    providers = [
        {
            'provider_id': 'BATCH001',
            'name': 'Dr. Batch Test 1',
            'email': 'batch1@example.com',
            'phone': '617-555-1234',
            'specialty': 'peds'
        },
        {
            'provider_id': 'BATCH002',
            'name': 'Dr. Batch Test 2',
            'email': 'batch2@example.com',
            'phone': '(617)555-5678',
            'specialty': 'ortho'
        }
    ]
    results = agent.batch_process(providers)
    total_corrections = sum(len(r['corrections']) for r in results)
    print(f"  [PASS] Batch processed {len(providers)} providers")
    print(f"    - Total corrections: {total_corrections}")
except Exception as e:
    print(f"  [FAIL] Batch processing error: {e}")
    exit(1)

# Test 7: Pipeline integration
print("\n[TEST 7] Testing integrated pipeline...")
try:
    pipeline = create_email_pipeline(agent, email_gen)
    test_provider = {
        'provider_id': 'PIPELINE001',
        'name': 'Dr. Pipeline Test',
        'email': 'pipeline@example.com',
        'phone': '5551234567',
        'specialty': 'family practice'
    }
    result = pipeline(test_provider, dry_run=True)
    print(f"  [PASS] Pipeline executed successfully")
    print(f"    - Corrections: {len(result['corrections'])}")
    if result['email_status']:
        print(f"    - Email status: {result['email_status']['status']}")
except Exception as e:
    print(f"  [FAIL] Pipeline error: {e}")
    exit(1)

print("\n" + "="*70)
print("ALL TESTS PASSED!")
print("="*70)
print("\nSystem is ready to use!")
print("\nTo run the application:")
print("  1. Dashboard UI:    python dashboard_ui.py")
print("  2. Demo scenarios:  python demo_scenarios.py")
print("  3. Quick test:      python automative_correction_agent.py")
print("\n" + "="*70)
