"""
FastAPI REST API for Orchestrator
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn

from orchestrator import ProviderOrchestrator

app = FastAPI(title="Provider Directory AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = ProviderOrchestrator()

class Provider(BaseModel):
    provider_id: str
    name: str
    npi: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    specialty: Optional[str] = None
    state: Optional[str] = None

class BatchRequest(BaseModel):
    providers: List[Provider]
    job_id: Optional[str] = None

@app.get("/")
def root():
    return {
        "service": "Provider Directory AI",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/v1/process/batch")
def process_batch(request: BatchRequest, background_tasks: BackgroundTasks):
    """Process a batch of providers"""
    job_id = request.job_id or f"JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    providers = [p.dict() for p in request.providers]
    
    # Process in background
    background_tasks.add_task(orchestrator.process_batch, providers, job_id)
    
    return {
        "job_id": job_id,
        "status": "processing",
        "batch_size": len(providers),
        "message": "Batch processing started"
    }

@app.get("/api/v1/jobs/{job_id}")
def get_job_status(job_id: str):
    """Get job status and results"""
    job = orchestrator.get_job_status(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@app.get("/api/v1/jobs/{job_id}/report")
def get_job_report(job_id: str):
    """Get summary report for a job"""
    report = orchestrator.generate_summary_report(job_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return report

@app.get("/api/v1/workflow/queue")
def get_workflow_queue(limit: int = 50):
    """Get manual review queue"""
    queue = orchestrator.get_workflow_queue(limit)
    return {"queue": queue, "count": len(queue)}

@app.get("/api/v1/providers/{provider_id}")
def get_provider(provider_id: str):
    """Get provider details"""
    import sqlite3
    import json
    
    conn = sqlite3.connect(orchestrator.db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM providers WHERE id=?", (provider_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return {
        "provider_id": row[0],
        "name": row[1],
        "npi": row[2],
        "phone": row[3],
        "address": row[4],
        "specialty": row[5],
        "state": row[6],
        "data": json.loads(row[7]),
        "status": row[8],
        "updated_at": row[9]
    }

@app.get("/api/v1/stats")
def get_statistics():
    """Get system statistics"""
    import sqlite3
    import pandas as pd
    
    conn = sqlite3.connect(orchestrator.db_path)
    
    total_providers = pd.read_sql("SELECT COUNT(*) as cnt FROM providers", conn).iloc[0]['cnt']
    auto_resolved = pd.read_sql("SELECT COUNT(*) as cnt FROM providers WHERE state='auto_resolve'", conn).iloc[0]['cnt']
    manual_review = pd.read_sql("SELECT COUNT(*) as cnt FROM workflow_queue WHERE status='pending'", conn).iloc[0]['cnt']
    total_jobs = pd.read_sql("SELECT COUNT(*) as cnt FROM jobs", conn).iloc[0]['cnt']
    
    conn.close()
    
    return {
        "total_providers": total_providers,
        "auto_resolved": auto_resolved,
        "manual_review": manual_review,
        "total_jobs": total_jobs,
        "auto_resolve_rate": (auto_resolved / max(total_providers, 1)) * 100
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
