# 🚀 Quick Start Guide

## Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd C:\Users\josep\Documents\automative_correction_agent_project
pip install -r requirements.txt
```

### Step 2: Run Demo
```bash
python demo_scenarios.py
```

### Step 3: Launch Dashboard
```bash
python dashboard_ui.py
```
Then open: http://localhost:5000

---

## 📋 Quick Commands

### Process CSV File
```bash
python csv_processor.py
```
Processes `sample_data.csv` and generates:
- `corrected_providers.csv` - Corrected data
- `correction_report.txt` - Detailed report

### Test Individual Components

**Test Correction Agent:**
```bash
python automative_correction_agent.py
```

**Test Email Generator:**
```bash
python email_generator.py
```

---

## 🎯 Common Use Cases

### 1. Process Single Provider
```python
from automative_correction_agent import AutomativeCorrectionAgent

agent = AutomativeCorrectionAgent()
provider = {
    'provider_id': 'P001',
    'name': 'Dr. John Smith',
    'phone': '555.123.4567',
    'specialty': 'cardio'
}
result = agent.process_provider(provider)
print(result)
```

### 2. Process with Email Notification
```python
from automative_correction_agent import AutomativeCorrectionAgent
from email_generator import EmailGenerator, create_email_pipeline

agent = AutomativeCorrectionAgent()
email_gen = EmailGenerator()
process_and_notify = create_email_pipeline(agent, email_gen)

result = process_and_notify(provider, dry_run=True)
```

### 3. Process CSV File
```python
from csv_processor import CSVProcessor

processor = CSVProcessor('sample_data.csv')
results = processor.process_csv(dry_run=True)
processor.export_corrected_csv('output.csv')
```

---

## 🎬 Demo Scenarios

Run specific demos:

```python
from demo_scenarios import *

# Phone correction
demo_scenario_1_phone_correction()

# Specialty normalization
demo_scenario_2_specialty_normalization()

# Full workflow with email
demo_scenario_3_full_workflow_with_email()

# Manual review case
demo_scenario_4_low_confidence_manual_review()

# Batch processing
demo_scenario_5_batch_processing()
```

---

## 🌐 Dashboard Features

Access at: http://localhost:5000

**Tabs:**
1. **Process Provider** - Submit and correct provider data
2. **Correction History** - View all corrections
3. **Email Status** - Track email notifications
4. **Manual Override** - Apply manual corrections

---

## 📊 Sample Data

Use the included `sample_data.csv` with 10 test providers:
- Various phone formats
- Incomplete addresses
- Informal specialty names
- Mix of valid and invalid data

---

## ⚙️ Configuration

### Set Confidence Threshold
```python
agent = AutomativeCorrectionAgent(confidence_threshold=0.85)
```

### Add Google Maps API Key
```python
agent = AutomativeCorrectionAgent(google_maps_api_key='YOUR_KEY')
```

### Configure SMTP
```python
smtp_config = {
    'host': 'smtp.gmail.com',
    'port': 587,
    'username': 'your_email@gmail.com',
    'password': 'your_app_password'
}
email_gen = EmailGenerator(smtp_config=smtp_config)
```

---

## 🆘 Troubleshooting

**Import Error:**
```bash
pip install flask requests
```

**Port Already in Use:**
```python
# In dashboard_ui.py, change port:
app.run(debug=True, port=5001)
```

**CSV Not Found:**
```bash
# Ensure you're in the project directory
cd C:\Users\josep\Documents\automative_correction_agent_project
```

---

## 📞 Quick Reference

| File | Purpose |
|------|---------|
| `automative_correction_agent.py` | Core correction logic |
| `email_generator.py` | Email templates & sending |
| `dashboard_ui.py` | Web interface |
| `demo_scenarios.py` | Demo workflows |
| `csv_processor.py` | Batch CSV processing |
| `sample_data.csv` | Test data |

---

**Ready to go! Start with the demos and explore the dashboard.** 🎉
