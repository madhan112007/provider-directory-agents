# 🏗️ System Architecture

## Overview

The Provider Directory AI system uses a multi-agent architecture orchestrated by a central coordinator that manages workflow, state transitions, and data persistence.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────┐         ┌──────────────────┐                 │
│  │   Streamlit UI   │         │   REST API       │                 │
│  │   (Dashboard)    │         │   (FastAPI)      │                 │
│  │   Port: 8501     │         │   Port: 8000     │                 │
│  └────────┬─────────┘         └────────┬─────────┘                 │
│           │                             │                            │
└───────────┼─────────────────────────────┼────────────────────────────┘
            │                             │
            └──────────────┬──────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              LangGraph State Machine                        │   │
│  │  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐    │   │
│  │  │Entry │──▶│Validate──▶│Enrich│──▶│  QA  │──▶│Route │    │   │
│  │  └──────┘   └──────┘   └──────┘   └──────┘   └──┬───┘    │   │
│  │                                                   │         │   │
│  │                                    ┌──────────────┴────┐   │   │
│  │                                    ▼                   ▼   │   │
│  │                              ┌──────────┐      ┌──────────┐│   │
│  │                              │ Correct  │      │  Manual  ││   │
│  │                              │          │      │  Review  ││   │
│  │                              └────┬─────┘      └────┬─────┘│   │
│  │                                   │                 │      │   │
│  │                                   └────────┬────────┘      │   │
│  │                                            ▼               │   │
│  │                                      ┌──────────┐          │   │
│  │                                      │ Complete │          │   │
│  │                                      └──────────┘          │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              Provider Orchestrator                          │   │
│  │  • Batch Processing                                         │   │
│  │  • Job Management                                           │   │
│  │  • Workflow Queue                                           │   │
│  │  • Retry Logic                                              │   │
│  │  • Error Handling                                           │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                         AGENT LAYER                                   │
├───────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │   Validation    │  │   Enrichment    │  │       QA        │     │
│  │     Agent       │  │     Agent       │  │     Agent       │     │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤     │
│  │ • NPI Lookup    │  │ • VLM/OCR PDF   │  │ • Discrepancy   │     │
│  │ • Maps API      │  │ • Web Scraping  │  │   Detection     │     │
│  │ • Phone Valid   │  │ • Education     │  │ • Risk Scoring  │     │
│  │ • Address Valid │  │ • License Check │  │ • Prioritization│     │
│  │ • Confidence    │  │ • Fuzzy Match   │  │ • Fraud Check   │     │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘     │
│           │                    │                     │               │
│           └────────────────────┼─────────────────────┘               │
│                                │                                      │
│                    ┌───────────▼───────────┐                         │
│                    │    Correction Agent   │                         │
│                    ├───────────────────────┤                         │
│                    │ • Auto-Correction     │                         │
│                    │ • Phone Format        │                         │
│                    │ • Address Complete    │                         │
│                    │ • Specialty Normalize │                         │
│                    │ • Email Generation    │                         │
│                    └───────────────────────┘                         │
│                                                                        │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
┌────────────────────────────────▼───────────────────────────────────────┐
│                         DATA LAYER                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                    SQLite Database                                │ │
│  ├──────────────────────────────────────────────────────────────────┤ │
│  │                                                                   │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │ │
│  │  │  providers  │  │    jobs     │  │workflow_queue│             │ │
│  │  ├─────────────┤  ├─────────────┤  ├─────────────┤             │ │
│  │  │ • id        │  │ • job_id    │  │ • id        │             │ │
│  │  │ • name      │  │ • batch_size│  │ • provider_id│            │ │
│  │  │ • npi       │  │ • status    │  │ • priority  │             │ │
│  │  │ • phone     │  │ • started_at│  │ • status    │             │ │
│  │  │ • address   │  │ • completed │  │ • created_at│             │ │
│  │  │ • specialty │  │ • metrics   │  │             │             │ │
│  │  │ • state     │  │             │  │             │             │ │
│  │  │ • data      │  │             │  │             │             │ │
│  │  │ • updated_at│  │             │  │             │             │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │ │
│  │                                                                   │ │
│  │  ┌─────────────┐                                                 │ │
│  │  │email_status │                                                 │ │
│  │  ├─────────────┤                                                 │ │
│  │  │ • id        │                                                 │ │
│  │  │ • provider_id│                                                │ │
│  │  │ • email_type│                                                 │ │
│  │  │ • status    │                                                 │ │
│  │  │ • sent_at   │                                                 │ │
│  │  │ • content   │                                                 │ │
│  │  └─────────────┘                                                 │ │
│  │                                                                   │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼───────────────────────────────────────┐
│                      EXTERNAL SERVICES                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ NPI Registry │  │ Google Maps  │  │ Email Server │                 │
│  │     API      │  │     API      │  │    (SMTP)    │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interfaces

#### Streamlit Dashboard
- **Port**: 8501
- **Features**:
  - Real-time metrics dashboard
  - Batch upload and processing
  - Workflow queue management
  - Analytics and reporting
  - Settings configuration

#### REST API
- **Port**: 8000
- **Framework**: FastAPI
- **Endpoints**:
  - `POST /api/v1/process/batch` - Process provider batch
  - `GET /api/v1/jobs/{job_id}` - Get job status
  - `GET /api/v1/jobs/{job_id}/report` - Get summary report
  - `GET /api/v1/workflow/queue` - Get manual review queue
  - `GET /api/v1/providers/{provider_id}` - Get provider details
  - `GET /api/v1/stats` - Get system statistics

### 2. Orchestration Layer

#### LangGraph State Machine
- **States**: Entry → Validate → Enrich → QA → Route → (Correct | Manual Review) → Complete
- **Features**:
  - State transitions with validation
  - Retry logic (max 3 attempts)
  - Error handling and recovery
  - Conditional routing based on QA results

#### Provider Orchestrator
- **Responsibilities**:
  - Batch job management
  - Agent coordination
  - Database operations
  - Workflow queue management
  - Metrics collection

### 3. Agent Layer

#### Data Validation Agent (Person 2 - mahaa)
- **Input**: Provider record (name, address, phone, specialty, NPI)
- **Processing**:
  - NPI Registry API lookup
  - Google Maps/Places API validation
  - Phone number formatting
  - Address normalization
  - Email validation
- **Output**: Field-level confidence scores and tags

#### Information Enrichment Agent (Person 3 - jaswan)
- **Input**: Base provider data + PDFs
- **Processing**:
  - VLM/OCR extraction from PDFs
  - Web scraping for additional data
  - Education inference
  - License verification
  - Fuzzy matching across sources
- **Output**: Enriched provider profile

#### Quality Assurance Agent (Person 4 - kanika)
- **Input**: Original + validated + enriched data
- **Processing**:
  - Cross-reference validation
  - Discrepancy detection
  - Risk scoring (fraud heuristics)
  - Impact assessment
  - Prioritization logic
- **Output**: Action (auto_resolve | manual_review) + scores

#### Automative Correction Agent (Person 5 - joe)
- **Input**: Provider data flagged for correction
- **Processing**:
  - Phone number standardization
  - Address completion (Google Maps)
  - Specialty normalization
  - High-confidence auto-correction
- **Output**: Corrected data + email notifications

### 4. Data Layer

#### SQLite Database
- **Tables**:
  - `providers`: Unified provider profile store
  - `jobs`: Batch job tracking
  - `workflow_queue`: Manual review queue
  - `email_status`: Email notification tracking

#### Data Flow
1. Provider data ingested via UI/API
2. Stored in `providers` table
3. Job created in `jobs` table
4. Agents process and update provider data
5. Manual review items added to `workflow_queue`
6. Email notifications logged in `email_status`

### 5. External Services

#### NPI Registry API
- **Purpose**: Validate provider NPI and retrieve official data
- **Data**: Name, taxonomy, practice location, license info

#### Google Maps API
- **Purpose**: Validate and complete addresses, verify phone numbers
- **Data**: Formatted address, coordinates, phone, business info

#### Email Server (SMTP)
- **Purpose**: Send notifications to providers and admins
- **Types**: Correction notifications, review requests, status updates

## Data Flow

### Flow 1: Batch Update (200 Providers)

```
1. Upload CSV → Dashboard
2. Create Job → Orchestrator
3. For each provider:
   a. Validate → Validation Agent
   b. Enrich → Enrichment Agent
   c. QA Check → QA Agent
   d. Route:
      - High confidence → Correction Agent → Complete
      - Low confidence → Manual Review Queue
4. Generate Summary Report
5. Display Results
```

### Flow 2: New Provider Onboarding

```
1. Submit Provider → API/Dashboard
2. Create Job → Orchestrator
3. Validate → Validation Agent
4. Enrich → Enrichment Agent
5. QA Check → QA Agent
6. If auto_resolve:
   - Correct → Correction Agent
   - Send Email → Email Server
   - Complete
7. If manual_review:
   - Add to Queue → workflow_queue
   - Notify Admin
   - Wait for Human Review
```

## State Transitions

```
PENDING
  ↓
VALIDATION (Validation Agent)
  ↓
ENRICHMENT (Enrichment Agent)
  ↓
QA (QA Agent)
  ↓
ROUTING (Orchestrator Decision)
  ├─→ CORRECTION (Auto-Resolve) → COMPLETED
  └─→ MANUAL_REVIEW (Human Review) → COMPLETED
```

## Error Handling

### Retry Logic
- Max retries: 3
- Exponential backoff: 1s, 2s, 4s
- After 3 failures → Manual Review

### Graceful Degradation
- API failures → Use cached data
- Validation errors → Flag for review
- Enrichment failures → Continue with partial data

### Rollback Support
- Transaction-based database updates
- Snapshot before corrections
- Audit trail for all changes

## Performance Optimization

### Batch Processing
- Process 200 providers in parallel
- Async API calls
- Connection pooling

### Caching
- NPI lookup results cached
- Maps API responses cached
- Specialty vocabulary cached

### Database Indexing
- Index on provider_id
- Index on job_id
- Index on priority (workflow_queue)

## Security

### Input Validation
- Pydantic models for API
- SQL injection prevention
- XSS protection in UI

### Authentication (Future)
- JWT tokens for API
- Role-based access control
- Audit logging

### Data Privacy
- PII encryption at rest
- Secure API communication (HTTPS)
- HIPAA compliance considerations

## Monitoring & Observability

### Metrics Tracked
- Processing time per provider
- Auto-resolve rate
- Manual review rate
- Error rate by type
- API latency
- Database query performance

### Logging
- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized log aggregation

### Alerting (Future)
- High error rate alerts
- SLA breach notifications
- System health checks

## Scalability

### Horizontal Scaling
- Stateless API servers
- Load balancer for API
- Distributed task queue (Celery)

### Vertical Scaling
- Database optimization
- Caching layer (Redis)
- Async processing

### Future Enhancements
- Kubernetes deployment
- Microservices architecture
- Event-driven architecture (Kafka)

---

**Architecture Version**: 1.0  
**Last Updated**: 2024  
**Maintained By**: Team Orchestrator
