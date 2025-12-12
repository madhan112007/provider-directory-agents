# 🏥 Provider Directory AI - Orchestration Layer

Complete multi-agent orchestration system for automated provider directory management.

## 🎯 Features

- **Multi-Agent Coordination**: Seamlessly orchestrates 4 specialized agents
- **State Machine**: LangGraph-based workflow with retry logic
- **Modern UI**: Gradient-styled Streamlit dashboard
- **REST API**: FastAPI endpoints for integration
- **Database**: SQLite for provider profiles and workflow queues
- **Real-time Monitoring**: Live job tracking and metrics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         LangGraph State Machine                  │  │
│  └──────────────────────────────────────────────────┘  │
│                         │                               │
│         ┌───────────────┼───────────────┐              │
│         ▼               ▼               ▼               │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐           │
│  │Validation│──▶│Enrichment│──▶│    QA    │           │
│  │  Agent   │   │  Agent   │   │  Agent   │           │
│  └──────────┘   └──────────┘   └──────────┘           │
│                                      │                  │
│                         ┌────────────┴────────────┐    │
│                         ▼                         ▼    │
│                  ┌──────────┐            ┌──────────┐  │
│                  │Correction│            │  Manual  │  │
│                  │  Agent   │            │  Review  │  │
│                  └──────────┘            └──────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd orchestrator
pip install -r requirements.txt
```

### 2. Launch Dashboard

```bash
# Windows
run_dashboard.bat

# Or manually
streamlit run dashboard.py
```

### 3. Start API Server (Optional)

```bash
python api_server.py
```

## 📊 Dashboard Pages

### 🎯 Dashboard
- Real-time metrics (Total Providers, Auto-Resolved, Manual Review)
- Processing pipeline funnel chart
- Resolution rate pie chart
- Recent jobs table

### ⚡ Process Batch
- Upload CSV with provider data
- Real-time progress tracking
- Instant results summary
- Download sample template

### 📋 Workflow Queue
- Manual review queue with priority sorting
- Provider details expansion
- Approve/Edit/Reject actions
- Empty state celebration

### 📊 Analytics
- Specialty distribution bar chart
- Geographic distribution by state
- Processing time trends over time
- Top 10 insights

### ⚙️ Settings
- Agent configuration (confidence threshold, batch size)
- Email settings (SMTP configuration)
- Database management (backup, clear cache, export)

## 🔌 API Endpoints

### Process Batch
```bash
POST /api/v1/process/batch
{
  "providers": [
    {
      "provider_id": "P001",
      "name": "Dr. Smith",
      "npi": "1234567890",
      "phone": "555-1234",
      "address": "123 Main St",
      "specialty": "Cardiology",
      "state": "CA"
    }
  ]
}
```

### Get Job Status
```bash
GET /api/v1/jobs/{job_id}
```

### Get Summary Report
```bash
GET /api/v1/jobs/{job_id}/report
```

### Get Workflow Queue
```bash
GET /api/v1/workflow/queue?limit=50
```

### Get Statistics
```bash
GET /api/v1/stats
```

## 📁 File Structure

```
orchestrator/
├── orchestrator.py          # Main orchestration engine
├── langgraph_orchestrator.py  # LangGraph state machine
├── dashboard.py             # Streamlit UI
├── api_server.py            # FastAPI REST API
├── requirements.txt         # Dependencies
├── run_dashboard.bat        # Launch script
├── provider_data.db         # SQLite database
└── README.md               # This file
```

## 🗄️ Database Schema

### providers
- id (TEXT PRIMARY KEY)
- name, npi, phone, address, specialty, state
- data (JSON)
- state (TEXT)
- updated_at (TEXT)

### jobs
- job_id (TEXT PRIMARY KEY)
- batch_size, status
- started_at, completed_at
- metrics (JSON)

### workflow_queue
- id (INTEGER PRIMARY KEY)
- provider_id, priority, status
- assigned_to, created_at

### email_status
- id (INTEGER PRIMARY KEY)
- provider_id, email_type, status
- sent_at, content

## 🎨 UI Features

- **Gradient Background**: Purple-blue gradient theme
- **Glass Morphism**: Frosted glass effect cards
- **Hover Effects**: Smooth button animations
- **Responsive**: Works on all screen sizes
- **Dark Mode**: Built-in dark theme support

## 📈 KPIs Tracked

- Total providers processed
- Auto-resolve rate (target: 80-90%)
- Manual review rate (target: 10-20%)
- Processing time per provider
- Error rate by type
- Success rate per batch
- SLA compliance

## 🔄 Workflow States

1. **PENDING** → Initial state
2. **VALIDATION** → Data validation agent
3. **ENRICHMENT** → Information enrichment agent
4. **QA** → Quality assurance agent
5. **CORRECTION** → Automative correction agent
6. **COMPLETED** → Final state
7. **FAILED** → Error state (with retry logic)

## 🛠️ Configuration

Edit `orchestrator.py` to customize:

```python
confidence_threshold = 0.9  # Auto-correction threshold
batch_size = 200           # Default batch size
max_retries = 3            # Max retry attempts
```

## 📧 Email Notifications

Configure SMTP in Settings page:
- SMTP Server: smtp.gmail.com
- SMTP Port: 587
- Sender Email: noreply@provider.ai

## 🧪 Testing

```python
from orchestrator import ProviderOrchestrator

orchestrator = ProviderOrchestrator()

test_providers = [
    {
        "provider_id": "P001",
        "name": "Dr. Smith",
        "npi": "1234567890",
        "phone": "555-1234",
        "address": "123 Main St",
        "specialty": "Cardiology",
        "state": "CA"
    }
]

job_id = "TEST_JOB_001"
results = orchestrator.process_batch(test_providers, job_id)
print(results)
```

## 🎯 Demo Scenarios

### Flow 1: Batch Update (200 Providers)
```bash
# Upload providers_200.csv in dashboard
# Click "Start Processing"
# View real-time progress
# Check summary report
```

### Flow 2: New Provider Onboarding
```bash
# Add single provider via API
# Monitor workflow queue
# Review flagged providers
# Approve/reject changes
```

## 🚨 Error Handling

- **Retry Logic**: 3 attempts with exponential backoff
- **Graceful Degradation**: Falls back to manual review
- **Error Logging**: All errors logged to database
- **Rollback Support**: Transaction-based updates

## 📊 Performance

- **Throughput**: 200 providers in ~5 minutes
- **Latency**: <2 seconds per provider
- **Accuracy**: 95%+ validation accuracy
- **Auto-Resolve**: 80-90% of providers

## 🔐 Security

- Input validation on all endpoints
- SQL injection prevention
- Rate limiting (API)
- Audit trail for all changes

## 🎓 Team Roles

- **Person 1 (madhan)**: Orchestrator + Directory Management Agent
- **Person 2 (mahaa)**: Data Validation Agent
- **Person 3 (jaswan)**: Information Enrichment Agent
- **Person 4 (kanika)**: Quality Assurance Agent
- **Person 5 (joe)**: Automative Correction Agent + Notifications

## 📞 Support

For issues or questions, contact the orchestration team.

---

**Built with ❤️ by Team Orchestrator**
