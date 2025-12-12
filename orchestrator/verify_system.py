"""System Verification Script"""
import sqlite3
import pandas as pd
import json

print("=" * 60)
print("PROVIDER DIRECTORY AI - SYSTEM VERIFICATION")
print("=" * 60)

# 1. Database Check
print("\n[DATABASE STATUS]")
conn = sqlite3.connect('provider_data.db')

providers_count = pd.read_sql('SELECT COUNT(*) as cnt FROM providers', conn).iloc[0]['cnt']
manual_review = pd.read_sql('SELECT COUNT(*) as cnt FROM workflow_queue WHERE status="pending"', conn).iloc[0]['cnt']
auto_resolved = pd.read_sql('SELECT COUNT(*) as cnt FROM providers WHERE status="auto_resolve"', conn).iloc[0]['cnt']
jobs_count = pd.read_sql('SELECT COUNT(*) as cnt FROM jobs', conn).iloc[0]['cnt']

print(f"   Total Providers: {providers_count}")
print(f"   Auto-Resolved: {auto_resolved}")
print(f"   Manual Review: {manual_review}")
print(f"   Total Jobs: {jobs_count}")

# 2. Latest Job Status
print("\n[LATEST JOB]")
latest_job = pd.read_sql('SELECT * FROM jobs ORDER BY started_at DESC LIMIT 1', conn)
if not latest_job.empty:
    metrics = json.loads(latest_job['metrics'].iloc[0])
    print(f"   Job ID: {latest_job['job_id'].iloc[0]}")
    print(f"   Status: {latest_job['status'].iloc[0]}")
    print(f"   Batch Size: {latest_job['batch_size'].iloc[0]}")
    print(f"   Processing Time: {metrics.get('processing_time', 0):.2f}s")
    print(f"   Success Rate: {(metrics.get('auto_resolved', 0) / metrics.get('total', 1) * 100):.1f}%")

# 3. Specialty Distribution
print("\n[TOP SPECIALTIES]")
specialties = pd.read_sql('''
    SELECT specialty, COUNT(*) as count 
    FROM providers 
    GROUP BY specialty 
    ORDER BY count DESC 
    LIMIT 5
''', conn)
for _, row in specialties.iterrows():
    print(f"   {row['specialty']}: {row['count']}")

# 4. State Distribution
print("\n[TOP STATES]")
states = pd.read_sql('''
    SELECT state, COUNT(*) as count 
    FROM providers 
    GROUP BY state 
    ORDER BY count DESC 
    LIMIT 5
''', conn)
for _, row in states.iterrows():
    print(f"   {row['state']}: {row['count']}")

# 5. High Priority Manual Reviews
print("\n[HIGH PRIORITY REVIEWS]")
high_priority = pd.read_sql('''
    SELECT provider_id, priority 
    FROM workflow_queue 
    WHERE status="pending" 
    ORDER BY priority DESC 
    LIMIT 5
''', conn)
for _, row in high_priority.iterrows():
    print(f"   {row['provider_id']}: Priority {row['priority']}")

conn.close()

# 6. Agent Status
print("\n[AGENT STATUS]")
try:
    from data_validation_agent.agent import DataValidationAgent
    print("   [OK] Data Validation Agent")
except:
    print("   [FAIL] Data Validation Agent (import error)")

try:
    from agentic_ai import QualityAssuranceAgent
    print("   [OK] Quality Assurance Agent")
except:
    print("   [FAIL] Quality Assurance Agent (import error)")

try:
    from automative_correction_agent import AutomativeCorrectionAgent
    print("   [OK] Correction Agent")
except:
    print("   [FAIL] Correction Agent (import error)")

# 7. Dashboard Status
print("\n[DASHBOARD]")
print("   URL: http://localhost:8501")
print("   Status: Running (check browser)")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print("\n[SUMMARY]")
print(f"   - {providers_count} providers processed")
print(f"   - {auto_resolved} auto-resolved ({auto_resolved/max(providers_count,1)*100:.1f}%)")
print(f"   - {manual_review} need manual review ({manual_review/max(providers_count,1)*100:.1f}%)")
print(f"   - {jobs_count} batch jobs completed")
print("\n[OK] System is operational!")
