import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'EY-Agent-Data Validation', 'EY-Agent-Data Validation'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'info_enrichment_agent', 'info_enrichment_agent'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Quality_Assurance_Agent', 'Quality_Assurance_Agent'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Automation_AGent_Correction'))

import sqlite3
import json
import time
from datetime import datetime
from typing import Dict, List
from enum import Enum
import pandas as pd

from data_validation_agent.agent import DataValidationAgent
from agentic_ai import QualityAssuranceAgent
from automative_correction_agent import AutomativeCorrectionAgent

class AgentState(Enum):
    PENDING = "pending"
    VALIDATION = "validation"
    ENRICHMENT = "enrichment"
    QA = "qa"
    CORRECTION = "correction"
    COMPLETED = "completed"
    FAILED = "failed"

class ProviderOrchestrator:
    def __init__(self, db_path="provider_data.db"):
        self.db_path = db_path
        self.validation_agent = DataValidationAgent()
        self.qa_agent = QualityAssuranceAgent()
        self.correction_agent = AutomativeCorrectionAgent()
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS providers
                     (id TEXT PRIMARY KEY, name TEXT, npi TEXT, phone TEXT, 
                      address TEXT, specialty TEXT, state TEXT, data JSON, 
                      status TEXT, updated_at TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS jobs
                     (job_id TEXT PRIMARY KEY, batch_size INTEGER, 
                      status TEXT, started_at TEXT, completed_at TEXT, 
                      metrics JSON)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS workflow_queue
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, provider_id TEXT, 
                      priority INTEGER, status TEXT, assigned_to TEXT, 
                      created_at TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS email_status
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, provider_id TEXT, 
                      email_type TEXT, status TEXT, sent_at TEXT, content TEXT)''')
        
        conn.commit()
        conn.close()
    
    def process_batch(self, providers: List[Dict], job_id: str) -> Dict:
        start_time = time.time()
        results = {
            "job_id": job_id,
            "total": len(providers),
            "auto_resolved": 0,
            "manual_review": 0,
            "errors": 0,
            "providers": []
        }
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?)",
                  (job_id, len(providers), "running", datetime.now().isoformat(), None, None))
        conn.commit()
        
        for provider in providers:
            try:
                result = self._process_single_provider(provider, conn)
                results["providers"].append(result)
                
                if result["action"] == "auto_resolve":
                    results["auto_resolved"] += 1
                else:
                    results["manual_review"] += 1
                    
            except Exception as e:
                results["errors"] += 1
                results["providers"].append({
                    "provider_id": provider.get("provider_id"),
                    "error": str(e),
                    "action": "failed"
                })
        
        end_time = time.time()
        results["processing_time"] = end_time - start_time
        
        c.execute("UPDATE jobs SET status=?, completed_at=?, metrics=? WHERE job_id=?",
                  ("completed", datetime.now().isoformat(), json.dumps(results), job_id))
        conn.commit()
        conn.close()
        
        return results
    
    def _process_single_provider(self, provider: Dict, conn) -> Dict:
        # Parse 'original' field if it exists (from QA Agent CSV)
        if 'original' in provider and isinstance(provider['original'], str):
            import ast
            try:
                provider = ast.literal_eval(provider['original'])
            except:
                pass
        
        # Auto-generate provider_id if missing
        if not provider.get("provider_id"):
            import hashlib
            provider["provider_id"] = f"P{hashlib.md5(str(provider).encode()).hexdigest()[:8].upper()}"
        
        provider_id = provider.get("provider_id")
        
        # 1. VALIDATION
        try:
            validation_result = self.validation_agent.validate_contact_info(provider)
        except Exception as e:
            validation_result = {"fields": {"npi": {}}, "valid": False, "error": str(e)}
        
        # 2. ENRICHMENT (simulated - would call enrichment agent)
        enriched_data = self._simulate_enrichment(provider)
        
        # 3. QA
        try:
            qa_input = {
                "original": provider,
                "npi": validation_result.get("fields", {}).get("npi", {}),
                "website": enriched_data,
                "pdf": {},
                "license_db": {"status": "active", "state": provider.get("state", "Unknown")},
                "meta": {"member_count": 500, "specialty": provider.get("specialty", "General")}
            }
            qa_result = self.qa_agent.process_provider(qa_input)
        except Exception as e:
            qa_result = {"action": "manual_review", "confidence_score": 0, "risk_score": 100, "error": str(e)}
        
        # 4. CORRECTION
        if qa_result["action"] == "auto_resolve":
            try:
                correction_result = self.correction_agent.process_provider(provider)
                provider.update(correction_result["provider_data"])
            except Exception as e:
                qa_result["action"] = "manual_review"
        
        # Save to DB
        try:
            c = conn.cursor()
            c.execute("""INSERT OR REPLACE INTO providers 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (provider_id, provider.get("name", "Unknown"), provider.get("npi", ""),
                       provider.get("phone", ""), provider.get("address", ""),
                       provider.get("specialty", "General"), provider.get("state", "Unknown"),
                       json.dumps(provider), qa_result["action"],
                       datetime.now().isoformat()))
            
            if qa_result["action"] == "manual_review":
                c.execute("INSERT INTO workflow_queue VALUES (NULL, ?, ?, ?, NULL, ?)",
                          (provider_id, qa_result.get("risk_score", 50), "pending",
                           datetime.now().isoformat()))
            
            conn.commit()
        except Exception as e:
            print(f"DB Error for {provider_id}: {e}")
        
        return {
            "provider_id": provider_id,
            "action": qa_result["action"],
            "confidence": qa_result.get("confidence_score", 0),
            "risk": qa_result.get("risk_score", 0),
            "corrections": 0
        }
    
    def _simulate_enrichment(self, provider: Dict) -> Dict:
        return {
            "name": provider.get("name"),
            "specialty": provider.get("specialty"),
            "state": provider.get("state")
        }
    
    def get_job_status(self, job_id: str) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                "job_id": row[0],
                "batch_size": row[1],
                "status": row[2],
                "started_at": row[3],
                "completed_at": row[4],
                "metrics": json.loads(row[5]) if row[5] else {}
            }
        return {}
    
    def get_workflow_queue(self, limit=50) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""SELECT * FROM workflow_queue 
                     WHERE status='pending' 
                     ORDER BY priority DESC LIMIT ?""", (limit,))
        rows = c.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "provider_id": r[1],
            "priority": r[2],
            "status": r[3],
            "created_at": r[4]
        } for r in rows]
    
    def generate_summary_report(self, job_id: str) -> Dict:
        job = self.get_job_status(job_id)
        metrics = job.get("metrics", {})
        
        return {
            "job_id": job_id,
            "total_providers": metrics.get("total", 0),
            "auto_resolved": metrics.get("auto_resolved", 0),
            "manual_review": metrics.get("manual_review", 0),
            "errors": metrics.get("errors", 0),
            "success_rate": (metrics.get("auto_resolved", 0) / metrics.get("total", 1)) * 100,
            "processing_time": metrics.get("processing_time", 0),
            "avg_time_per_provider": metrics.get("processing_time", 0) / metrics.get("total", 1)
        }

if __name__ == "__main__":
    orchestrator = ProviderOrchestrator()
    
    # Test batch
    test_providers = [
        {"provider_id": "P001", "name": "Dr. Smith", "npi": "1234567890", 
         "phone": "555-1234", "address": "123 Main St", "specialty": "Cardiology", "state": "CA"},
        {"provider_id": "P002", "name": "Dr. Jones", "npi": "9876543210",
         "phone": "555-5678", "address": "456 Oak Ave", "specialty": "Pediatrics", "state": "NY"}
    ]
    
    job_id = f"JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results = orchestrator.process_batch(test_providers, job_id)
    
    print(json.dumps(results, indent=2))
    print("\nSummary Report:")
    print(json.dumps(orchestrator.generate_summary_report(job_id), indent=2))
