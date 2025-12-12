# 🚀 Quick Start Guide

Get the Provider Directory AI system running in 5 minutes!

## ⚡ Installation

### Step 1: Install Dependencies

```bash
cd c:\Agents\orchestrator
pip install -r requirements.txt
```

### Step 2: Install Additional Requirements

```bash
# For LangGraph support (optional)
pip install langgraph langchain

# For API server (optional)
pip install fastapi uvicorn
```

## 🎯 Launch Dashboard

### Windows
```bash
run_dashboard.bat
```

### Manual Launch
```bash
streamlit run dashboard.py
```

The dashboard will open at: **http://localhost:8501**

## 📊 Using the Dashboard

### 1️⃣ View Dashboard
- See real-time metrics
- Monitor processing pipeline
- Check resolution rates

### 2️⃣ Process a Batch

1. Click **"Process Batch"** in sidebar
2. Upload CSV file with provider data
3. Click **"Start Processing"**
4. Watch real-time progress
5. View results summary

### Sample CSV Format:
```csv
provider_id,name,npi,phone,address,specialty,state
P001,Dr. Smith,1234567890,555-1234,123 Main St,Cardiology,CA
P002,Dr. Jones,9876543210,555-5678,456 Oak Ave,Pediatrics,NY
```

### 3️⃣ Review Workflow Queue

1. Click **"Workflow Queue"** in sidebar
2. Expand providers needing review
3. Click **Approve**, **Edit**, or **Reject**

### 4️⃣ View Analytics

1. Click **"Analytics"** in sidebar
2. Explore specialty distribution
3. Check geographic coverage
4. Monitor processing trends

## 🔌 Using the API

### Start API Server
```bash
python api_server.py
```

API will be available at: **http://localhost:8000**

### API Documentation
Visit: **http://localhost:8000/docs**

### Example API Call

```bash
curl -X POST "http://localhost:8000/api/v1/process/batch" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## 🧪 Run Tests

```bash
python test_orchestrator.py
```

This will run 5 test scenarios:
1. Single provider processing
2. Batch processing (10 providers)
3. Workflow queue management
4. Job status retrieval
5. Error handling

## 📁 Sample Data

Create a file `sample_providers.csv`:

```csv
provider_id,name,npi,phone,address,specialty,state
P001,Dr. John Smith,1234567890,555-123-4567,123 Main St Boston MA,Cardiology,MA
P002,Dr. Jane Doe,9876543210,555-987-6543,456 Oak Ave New York NY,Pediatrics,NY
P003,Dr. Bob Johnson,4567891230,555-456-7891,789 Pine Rd Chicago IL,Orthopedics,IL
P004,Dr. Alice Williams,3216549870,555-321-6549,321 Elm St Miami FL,Dermatology,FL
P005,Dr. Charlie Brown,7891234560,555-789-1234,654 Maple Dr Dallas TX,Neurology,TX
```

Upload this in the dashboard to test!

## 🎨 Dashboard Features

### Metrics Cards
- **Total Providers**: All providers in system
- **Auto-Resolved**: Automatically processed
- **Manual Review**: Awaiting human review
- **Total Jobs**: Batch jobs completed

### Charts
- **Processing Pipeline**: Funnel chart showing flow
- **Resolution Rate**: Pie chart of outcomes
- **Specialty Distribution**: Bar chart by specialty
- **Geographic Distribution**: Bar chart by state
- **Processing Time Trends**: Line chart over time

### Actions
- **Upload CSV**: Drag & drop or browse
- **Start Processing**: Begin batch job
- **Download Template**: Get sample CSV
- **Approve/Edit/Reject**: Review queue actions
- **Export Data**: Download results

## 🔧 Configuration

### Database Location
Default: `provider_data.db` in orchestrator folder

### Change Port
```bash
streamlit run dashboard.py --server.port 8502
```

### API Port
Edit `api_server.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Check if port 8501 is in use
netstat -ano | findstr :8501

# Kill process if needed
taskkill /PID <PID> /F
```

### Import errors
```bash
# Ensure all paths are correct
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database locked
```bash
# Close all connections
# Delete provider_data.db
# Restart orchestrator
```

## 📞 Next Steps

1. ✅ Launch dashboard
2. ✅ Upload sample data
3. ✅ Process first batch
4. ✅ Review workflow queue
5. ✅ Explore analytics
6. ✅ Try API endpoints
7. ✅ Run test suite

## 🎓 Learn More

- Read full [README.md](README.md)
- Check [API documentation](http://localhost:8000/docs)
- Review agent implementations in parent folders

## 💡 Tips

- Start with small batches (10-20 providers)
- Monitor the workflow queue regularly
- Use analytics to identify patterns
- Export data for external reporting
- Configure email notifications in Settings

---

**Ready to go! 🚀**

Questions? Check the main README or contact the team.
