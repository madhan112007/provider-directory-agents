# Quality Assurance Agent

Healthcare provider data quality assurance system with automated discrepancy detection, risk scoring, and prioritization.

## Files Structure

```
Quality_Assurance_Agent/
├── agentic_ai.py          # Core QA Agent logic
├── test_agentic.py        # Test runner
├── api_server.py          # Metrics API server
├── providers_200.csv      # Input data (200 providers)
├── qa_results.csv         # Output: Processed results
├── qa_metrics.json        # Output: Summary metrics
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### 1. Run QA Analysis
```bash
python test_agentic.py
```
**Output:**
- `qa_results.csv` - Provider results with scores and flags
- `qa_metrics.json` - Summary metrics

### 2. Start API Server
```bash
python api_server.py
```
**Server:** http://localhost:5003

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info |
| `GET /api/metrics` | Overall metrics |
| `GET /api/dashboard/summary` | Dashboard summary |
| `GET /api/dashboard/error-distribution` | Error types |
| `GET /api/dashboard/risk-breakdown` | Risk distribution |
| `GET /api/dashboard/confidence-breakdown` | Confidence distribution |
| `GET /api/dashboard/action-split` | Action distribution |
| `GET /api/providers/high-risk` | High risk providers |
| `GET /api/providers/manual-review` | Manual review list |

## Features

### Data Sources Compared
- Original dataset
- NPI API data
- Website scrape
- PDF-enriched data
- License database

### Scoring System
- **Confidence Score** (0-100): Data quality across sources
- **Risk Score** (0-100): Fraud/compliance risk level
- **Impact Score** (0-100): Member impact (volume, specialty, region)

### Red Flags Detected
- Inconsistent data across sources
- Inactive license
- Missing NPI
- State mismatches
- Specialty changes

### Actions
- **Auto-resolve**: Low risk, high confidence
- **Manual review**: High risk or high impact (target: 10-20%)

## Key Metrics

- Total processed
- Manual review rate
- Auto-resolve rate
- Top error types
- Target compliance
