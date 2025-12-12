"""
Interactive Demo Script for Provider Directory AI
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'EY-Agent-Data Validation', 'EY-Agent-Data Validation'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Quality_Assurance_Agent', 'Quality_Assurance_Agent'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Automation_AGent_Correction'))

from orchestrator import ProviderOrchestrator
from datetime import datetime
import json
import time
import pandas as pd

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_section(text):
    print(f"\n{'─' * 70}")
    print(f"  {text}")
    print(f"{'─' * 70}")

def demo_flow_1_batch_update():
    """Flow 1: Batch Update of 200 Providers"""
    print_header("🎯 DEMO FLOW 1: Batch Update (200 Providers)")
    
    orchestrator = ProviderOrchestrator()
    
    # Generate 200 test providers
    print("\n📋 Generating 200 test providers...")
    providers = []
    
    specialties = ["Cardiology", "Pediatrics", "Orthopedics", "Dermatology", 
                   "Neurology", "Oncology", "Emergency Medicine", "Radiology"]
    states = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
    
    for i in range(200):
        providers.append({
            "provider_id": f"P{str(i+1).zfill(4)}",
            "name": f"Dr. Provider {i+1}",
            "npi": f"12345{str(i+1).zfill(5)}",
            "phone": f"555-{str(i+1).zfill(3)}-0000",
            "address": f"{(i+1)*100} Medical Plaza, City {i+1}, {states[i % len(states)]} {10000+i}",
            "specialty": specialties[i % len(specialties)],
            "state": states[i % len(states)]
        })
    
    print(f"✅ Generated {len(providers)} providers")
    
    # Show sample
    print("\n📊 Sample Providers:")
    for p in providers[:3]:
        print(f"   • {p['name']} - {p['specialty']} - {p['state']}")
    print(f"   ... and {len(providers)-3} more")
    
    # Process batch
    job_id = f"FLOW1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\n🚀 Starting batch processing...")
    print(f"   Job ID: {job_id}")
    print(f"   Batch Size: {len(providers)}")
    
    start_time = time.time()
    
    # Simulate progress
    print("\n⏳ Processing:")
    for i in range(0, 101, 20):
        print(f"   [{i}%] {'█' * (i//5)}{' ' * (20-i//5)}", end='\r')
        time.sleep(0.3)
    
    results = orchestrator.process_batch(providers, job_id)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"\n\n✅ Batch processing completed!")
    
    # Display results
    print_section("📊 RESULTS SUMMARY")
    
    print(f"\n   Total Providers: {results['total']}")
    print(f"   Auto-Resolved: {results['auto_resolved']} ({results['auto_resolved']/results['total']*100:.1f}%)")
    print(f"   Manual Review: {results['manual_review']} ({results['manual_review']/results['total']*100:.1f}%)")
    print(f"   Errors: {results['errors']}")
    print(f"   Processing Time: {processing_time:.2f}s")
    print(f"   Avg Time/Provider: {processing_time/results['total']:.3f}s")
    
    # KPIs
    print_section("🎯 KEY PERFORMANCE INDICATORS")
    
    report = orchestrator.generate_summary_report(job_id)
    
    print(f"\n   ✓ Success Rate: {report['success_rate']:.1f}%")
    print(f"   ✓ Auto-Resolve Rate: {results['auto_resolved']/results['total']*100:.1f}%")
    print(f"   ✓ Manual Review Rate: {results['manual_review']/results['total']*100:.1f}%")
    print(f"   ✓ Throughput: {results['total']/processing_time:.1f} providers/sec")
    
    # Target comparison
    print("\n   📈 Target Comparison:")
    auto_rate = results['auto_resolved']/results['total']*100
    manual_rate = results['manual_review']/results['total']*100
    
    print(f"      Auto-Resolve: {auto_rate:.1f}% (Target: 80-90%) {'✅' if 80 <= auto_rate <= 90 else '⚠️'}")
    print(f"      Manual Review: {manual_rate:.1f}% (Target: 10-20%) {'✅' if 10 <= manual_rate <= 20 else '⚠️'}")
    
    return results

def demo_flow_2_new_onboarding():
    """Flow 2: New Provider Onboarding"""
    print_header("🎯 DEMO FLOW 2: New Provider Onboarding")
    
    orchestrator = ProviderOrchestrator()
    
    # New providers to onboard
    new_providers = [
        {
            "provider_id": "NEW_001",
            "name": "Dr. Sarah Johnson",
            "npi": "9999999991",
            "phone": "555-NEW-0001",
            "address": "100 New Medical Center, Boston, MA 02101",
            "specialty": "Cardiology",
            "state": "MA"
        },
        {
            "provider_id": "NEW_002",
            "name": "Dr. Michael Chen",
            "npi": "9999999992",
            "phone": "555-NEW-0002",
            "address": "200 Innovation Drive, San Francisco, CA 94105",
            "specialty": "Neurology",
            "state": "CA"
        },
        {
            "provider_id": "NEW_003",
            "name": "Dr. Emily Rodriguez",
            "npi": "9999999993",
            "phone": "555-NEW-0003",
            "address": "300 Healthcare Plaza, New York, NY 10001",
            "specialty": "Pediatrics",
            "state": "NY"
        }
    ]
    
    print(f"\n📋 Onboarding {len(new_providers)} new providers:")
    for p in new_providers:
        print(f"   • {p['name']} - {p['specialty']} - {p['state']}")
    
    job_id = f"FLOW2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\n🚀 Starting onboarding process...")
    print(f"   Job ID: {job_id}")
    
    results = orchestrator.process_batch(new_providers, job_id)
    
    print(f"\n✅ Onboarding completed!")
    
    # Show individual results
    print_section("📊 INDIVIDUAL RESULTS")
    
    for provider_result in results['providers']:
        print(f"\n   Provider: {provider_result['provider_id']}")
        print(f"   Action: {provider_result['action']}")
        print(f"   Confidence: {provider_result['confidence']}/100")
        print(f"   Risk Score: {provider_result['risk']}/100")
        print(f"   Corrections: {provider_result['corrections']}")
    
    # Workflow queue
    print_section("📋 WORKFLOW QUEUE")
    
    queue = orchestrator.get_workflow_queue(10)
    
    if queue:
        print(f"\n   {len(queue)} providers in manual review queue:")
        for item in queue[:5]:
            print(f"   • {item['provider_id']} - Priority: {item['priority']} - Status: {item['status']}")
    else:
        print("\n   ✅ No providers in queue - all auto-resolved!")
    
    return results

def demo_analytics():
    """Show analytics and insights"""
    print_header("📊 ANALYTICS & INSIGHTS")
    
    orchestrator = ProviderOrchestrator()
    
    import sqlite3
    conn = sqlite3.connect(orchestrator.db_path)
    
    # Provider statistics
    print_section("🏥 PROVIDER STATISTICS")
    
    total_providers = pd.read_sql("SELECT COUNT(*) as cnt FROM providers", conn).iloc[0]['cnt']
    auto_resolved = pd.read_sql("SELECT COUNT(*) as cnt FROM providers WHERE state='auto_resolve'", conn).iloc[0]['cnt']
    manual_review = pd.read_sql("SELECT COUNT(*) as cnt FROM workflow_queue WHERE status='pending'", conn).iloc[0]['cnt']
    
    print(f"\n   Total Providers: {total_providers:,}")
    print(f"   Auto-Resolved: {auto_resolved:,}")
    print(f"   Manual Review: {manual_review:,}")
    
    # Specialty distribution
    print_section("🏥 TOP SPECIALTIES")
    
    specialty_df = pd.read_sql("""
        SELECT specialty, COUNT(*) as count 
        FROM providers 
        GROUP BY specialty 
        ORDER BY count DESC 
        LIMIT 5
    """, conn)
    
    if not specialty_df.empty:
        print()
        for _, row in specialty_df.iterrows():
            print(f"   • {row['specialty']}: {row['count']} providers")
    
    # Geographic distribution
    print_section("🗺️ TOP STATES")
    
    state_df = pd.read_sql("""
        SELECT state, COUNT(*) as count 
        FROM providers 
        GROUP BY state 
        ORDER BY count DESC 
        LIMIT 5
    """, conn)
    
    if not state_df.empty:
        print()
        for _, row in state_df.iterrows():
            print(f"   • {row['state']}: {row['count']} providers")
    
    # Job statistics
    print_section("📈 JOB STATISTICS")
    
    jobs_df = pd.read_sql("SELECT * FROM jobs ORDER BY started_at DESC LIMIT 5", conn)
    
    if not jobs_df.empty:
        print()
        for _, job in jobs_df.iterrows():
            print(f"   • {job['job_id']}: {job['batch_size']} providers - {job['status']}")
    
    conn.close()

def main():
    """Run complete demo"""
    print_header("🏥 PROVIDER DIRECTORY AI - COMPLETE DEMO")
    
    print("\n🎬 This demo will showcase:")
    print("   1. Flow 1: Batch Update (200 providers)")
    print("   2. Flow 2: New Provider Onboarding")
    print("   3. Analytics & Insights")
    
    input("\n👉 Press Enter to start Flow 1...")
    
    # Flow 1
    flow1_results = demo_flow_1_batch_update()
    
    input("\n👉 Press Enter to start Flow 2...")
    
    # Flow 2
    flow2_results = demo_flow_2_new_onboarding()
    
    input("\n👉 Press Enter to view analytics...")
    
    # Analytics
    demo_analytics()
    
    # Final summary
    print_header("🎉 DEMO COMPLETE!")
    
    print("\n✅ Successfully demonstrated:")
    print("   ✓ Batch processing of 200 providers")
    print("   ✓ New provider onboarding workflow")
    print("   ✓ Manual review queue management")
    print("   ✓ Analytics and reporting")
    
    print("\n📊 Overall Statistics:")
    print(f"   • Flow 1: {flow1_results['total']} providers processed")
    print(f"   • Flow 2: {flow2_results['total']} providers onboarded")
    print(f"   • Total: {flow1_results['total'] + flow2_results['total']} providers")
    
    print("\n🚀 Next Steps:")
    print("   1. Launch dashboard: run_dashboard.bat")
    print("   2. Start API server: python api_server.py")
    print("   3. Run tests: python test_orchestrator.py")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
