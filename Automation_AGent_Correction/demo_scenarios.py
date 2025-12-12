"""
Demo Scenarios for Automative Correction Agent
Demonstrates various correction workflows with sample data.
"""

from automative_correction_agent import AutomativeCorrectionAgent
from email_generator import EmailGenerator, create_email_pipeline
import json


def demo_scenario_1_phone_correction():
    """Demo: Phone number format correction"""
    print("\n" + "="*70)
    print("DEMO SCENARIO 1: Phone Number Format Correction")
    print("="*70)
    
    agent = AutomativeCorrectionAgent()
    
    provider = {
        'provider_id': 'P001',
        'name': 'Dr. Sarah Johnson',
        'email': 'sarah.johnson@hospital.com',
        'phone': '555.123.4567',  # Incorrect format
        'address': '456 Medical Plaza, Boston, MA 02115',
        'specialty': 'Cardiology'
    }
    
    print("\n📋 Original Provider Data:")
    print(json.dumps(provider, indent=2))
    
    result = agent.process_provider(provider)
    
    print("\n✅ Corrected Provider Data:")
    print(json.dumps(result['provider_data'], indent=2))
    
    print("\n🔧 Corrections Applied:")
    for correction in result['corrections']:
        print(f"  • {correction['field'].upper()}")
        print(f"    Before: {correction['before']}")
        print(f"    After:  {correction['after']}")
        print(f"    Confidence: {correction['confidence']:.0%}")
        print(f"    Source: {correction['source']}")
    
    return result


def demo_scenario_2_specialty_normalization():
    """Demo: Specialty name normalization"""
    print("\n" + "="*70)
    print("DEMO SCENARIO 2: Specialty Name Normalization")
    print("="*70)
    
    agent = AutomativeCorrectionAgent()
    
    providers = [
        {
            'provider_id': 'P002',
            'name': 'Dr. Michael Chen',
            'email': 'mchen@clinic.com',
            'phone': '(617) 555-1234',
            'address': '789 Health Center Dr, Cambridge, MA 02139',
            'specialty': 'ortho'  # Needs normalization
        },
        {
            'provider_id': 'P003',
            'name': 'Dr. Emily Rodriguez',
            'email': 'erodriguez@medical.com',
            'phone': '617-555-5678',
            'address': '321 Care Ave, Somerville, MA 02144',
            'specialty': 'peds'  # Needs normalization
        }
    ]
    
    print("\n📋 Processing Multiple Providers:")
    results = agent.batch_process(providers)
    
    for i, result in enumerate(results):
        print(f"\n--- Provider {i+1} ---")
        print(f"Name: {result['provider_data']['name']}")
        if result['corrections']:
            for correction in result['corrections']:
                print(f"  * {correction['field']}: {correction['before']} -> {correction['after']}")
        else:
            print("  * No corrections needed")
    
    print("\n📊 Statistics:")
    stats = agent.get_statistics()
    print(json.dumps(stats, indent=2))
    
    return results


def demo_scenario_3_full_workflow_with_email():
    """Demo: Complete workflow with email notification"""
    print("\n" + "="*70)
    print("DEMO SCENARIO 3: Full Workflow with Email Notification")
    print("="*70)
    
    agent = AutomativeCorrectionAgent()
    email_gen = EmailGenerator()
    process_and_notify = create_email_pipeline(agent, email_gen)
    
    provider = {
        'provider_id': 'P004',
        'name': 'Dr. James Wilson',
        'email': 'jwilson@healthcare.com',
        'phone': '6175551234',  # Missing formatting
        'address': '555 Hospital Rd Boston MA',  # Incomplete
        'specialty': 'heart doctor'  # Informal name
    }
    
    print("\n📋 Original Provider Data:")
    print(json.dumps(provider, indent=2))
    
    # Process with email notification
    result = process_and_notify(provider, dry_run=True)
    
    print("\n✅ Processing Complete!")
    print(f"\nCorrections Applied: {len(result['corrections'])}")
    for correction in result['corrections']:
        print(f"  * {correction['field']}: {correction['before']} -> {correction['after']}")
    
    if result['email_status']:
        print(f"\n📧 Email Notification:")
        print(f"  Status: {result['email_status']['status']}")
        print(f"  To: {result['email_status']['to_email']}")
        print(f"  Subject: {result['email_status']['subject']}")
        print(f"  Email ID: {result['email_status']['email_id']}")
    
    print("\n📊 Email Statistics:")
    email_stats = email_gen.get_email_statistics()
    print(json.dumps(email_stats, indent=2))
    
    return result


def demo_scenario_4_low_confidence_manual_review():
    """Demo: Low confidence case requiring manual review"""
    print("\n" + "="*70)
    print("DEMO SCENARIO 4: Low Confidence - Manual Review Required")
    print("="*70)
    
    agent = AutomativeCorrectionAgent(confidence_threshold=0.9)
    email_gen = EmailGenerator()
    
    provider = {
        'provider_id': 'P005',
        'name': 'Dr. Lisa Anderson',
        'email': 'landerson@clinic.com',
        'phone': '12345',  # Invalid phone
        'address': 'Unknown',  # Incomplete address
        'specialty': 'General Medicine'  # Already correct
    }
    
    print("\n📋 Original Provider Data:")
    print(json.dumps(provider, indent=2))
    
    result = agent.process_provider(provider)
    
    print("\n⚠️  Processing Result:")
    print(f"Corrections Applied: {len(result['corrections'])}")
    print(f"Needs Manual Review: {result['needs_manual_review']}")
    
    if result['needs_manual_review']:
        print("\n🔍 Manual Review Required:")
        print("  • Phone number: Invalid format (too short)")
        print("  • Address: Incomplete or missing")
        
        # Generate manual review email
        issues = [
            "Phone number format is invalid and cannot be auto-corrected",
            "Address information is incomplete or missing"
        ]
        email_data = email_gen.generate_manual_review_email(provider, issues)
        email_status = email_gen.send_email(email_data, dry_run=True)
        
        print(f"\n📧 Manual Review Email Sent:")
        print(f"  To: {email_status['to_email']}")
        print(f"  Subject: {email_status['subject']}")
        print(f"  Type: {email_data['type']}")
    
    return result


def demo_scenario_5_batch_processing():
    """Demo: Batch processing from CSV"""
    print("\n" + "="*70)
    print("DEMO SCENARIO 5: Batch Processing from CSV")
    print("="*70)
    
    agent = AutomativeCorrectionAgent()
    email_gen = EmailGenerator()
    
    # Simulate CSV data
    providers = [
        {
            'provider_id': 'P101',
            'name': 'Dr. Robert Taylor',
            'email': 'rtaylor@hospital.com',
            'phone': '555-123-4567',
            'address': '100 Main St, Boston, MA',
            'specialty': 'Internal Medicine'
        },
        {
            'provider_id': 'P102',
            'name': 'Dr. Maria Garcia',
            'email': 'mgarcia@clinic.com',
            'phone': '(555)234-5678',
            'address': '200 Oak Ave, Cambridge, MA',
            'specialty': 'family practice'
        },
        {
            'provider_id': 'P103',
            'name': 'Dr. David Lee',
            'email': 'dlee@medical.com',
            'phone': '5553456789',
            'address': '300 Pine St, Somerville, MA',
            'specialty': 'skin doctor'
        }
    ]
    
    print(f"\n📊 Processing {len(providers)} providers...")
    
    results = agent.batch_process(providers)
    
    corrected_count = sum(1 for r in results if r['corrections'])
    total_corrections = sum(len(r['corrections']) for r in results)
    
    print(f"\n✅ Batch Processing Complete!")
    print(f"  Providers Processed: {len(providers)}")
    print(f"  Providers Corrected: {corrected_count}")
    print(f"  Total Corrections: {total_corrections}")
    
    print("\n📋 Detailed Results:")
    for result in results:
        provider = result['provider_data']
        print(f"\n  {provider['name']} ({provider['provider_id']})")
        if result['corrections']:
            for correction in result['corrections']:
                print(f"    * {correction['field']}: {correction['before']} -> {correction['after']}")
            
            # Generate and send email
            email_data = email_gen.generate_correction_email(provider, result['corrections'])
            email_status = email_gen.send_email(email_data, dry_run=True)
            print(f"    [EMAIL] {email_status['status']}")
        else:
            print(f"    * No corrections needed")
    
    print("\n📊 Final Statistics:")
    stats = agent.get_statistics()
    print(json.dumps(stats, indent=2))
    
    print("\n📧 Email Statistics:")
    email_stats = email_gen.get_email_statistics()
    print(json.dumps(email_stats, indent=2))
    
    return results


def run_all_demos():
    """Run all demo scenarios"""
    print("\n" + "="*70)
    print("🚀 AUTOMATIVE CORRECTION AGENT - DEMO SCENARIOS")
    print("="*70)
    print("\nThis demo showcases the automatic correction and notification system")
    print("for provider data quality management.\n")
    
    input("Press Enter to start Demo 1: Phone Number Correction...")
    demo_scenario_1_phone_correction()
    
    input("\n\nPress Enter to start Demo 2: Specialty Normalization...")
    demo_scenario_2_specialty_normalization()
    
    input("\n\nPress Enter to start Demo 3: Full Workflow with Email...")
    demo_scenario_3_full_workflow_with_email()
    
    input("\n\nPress Enter to start Demo 4: Manual Review Required...")
    demo_scenario_4_low_confidence_manual_review()
    
    input("\n\nPress Enter to start Demo 5: Batch Processing...")
    demo_scenario_5_batch_processing()
    
    print("\n" + "="*70)
    print("✅ ALL DEMOS COMPLETED!")
    print("="*70)
    print("\nKey Features Demonstrated:")
    print("  * Automatic phone number formatting")
    print("  * Address standardization")
    print("  * Specialty name normalization")
    print("  * Email notification generation")
    print("  * Confidence-based processing")
    print("  * Manual review workflow")
    print("  * Batch processing capabilities")
    print("  * Correction history tracking")
    print("  * Email status monitoring")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    run_all_demos()
