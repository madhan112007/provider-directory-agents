# Automative Correction Agent + Notification Owner

## 🎯 Overview

The **Automative Correction Agent** is an intelligent system that automatically identifies and corrects common provider data errors, then generates and sends notification emails about the changes. This reduces manual workload and ensures data quality in provider directories.

## 👤 Owner: Person 5 (Joe)

## 🚀 Core Features

### 1. **Automatic Error Correction**
- **Phone Number Standardization**: Converts various formats to standard US format `(XXX) XXX-XXXX`
- **Address Completion**: Uses Google Maps API to complete and standardize addresses
- **Specialty Normalization**: Maps informal specialty names to controlled vocabulary

### 2. **Confidence-Based Processing**
- Only auto-corrects when confidence > 90% threshold
- Low-confidence cases routed to manual review queue
- Complete before/after snapshot logging

### 3. **Email Notification System**
- Auto-generates provider-facing emails summarizing corrections
- Includes source of corrected data (NPI registry, hospital website, etc.)
- Tracks email sends and opens for audit
- Customizable email templates

### 4. **Dashboard UI**
- Review auto-corrections in real-time
- Email preview and send status
- Manual override interface
- Correction history with full audit trail

## 📁 Project Structure

```
automative_correction_agent_project/
│
├── automative_correction_agent.py   # Core correction logic and APIs
├── email_generator.py               # Email templating and sending
├── dashboard_ui.py                  # Flask web dashboard
├── demo_scenarios.py                # Demo workflows
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup Steps

1. **Navigate to project directory**
```bash
cd C:\Users\josep\Documents\automative_correction_agent_project
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Optional: Configure Google Maps API**
   - Get API key from [Google Cloud Console](https://console.cloud.google.com/)
   - Set in `automative_correction_agent.py` initialization

4. **Optional: Configure SMTP for email sending**
   - Update SMTP settings in `email_generator.py`
   - Default uses Gmail SMTP (requires app password)

## 🎮 Usage

### 1. Run Demo Scenarios

```bash
python demo_scenarios.py
```

This runs 5 comprehensive demo scenarios:
- Phone number correction
- Specialty normalization
- Full workflow with email
- Manual review cases
- Batch processing

### 2. Launch Dashboard UI

```bash
python dashboard_ui.py
```

Then open browser to: `http://localhost:5000`

Dashboard features:
- **Process Provider**: Submit provider data for auto-correction
- **Correction History**: View all corrections with timestamps
- **Email Status**: Track sent emails and open rates
- **Manual Override**: Apply manual corrections when needed

### 3. Use as Python Library

```python
from automative_correction_agent import AutomativeCorrectionAgent
from email_generator import EmailGenerator, create_email_pipeline

# Initialize
agent = AutomativeCorrectionAgent(confidence_threshold=0.9)
email_gen = EmailGenerator()
process_and_notify = create_email_pipeline(agent, email_gen)

# Process provider
provider_data = {
    'provider_id': 'P001',
    'name': 'Dr. John Smith',
    'email': 'dr.smith@example.com',
    'phone': '555.123.4567',
    'address': '123 Main St Boston MA',
    'specialty': 'cardio'
}

result = process_and_notify(provider_data, dry_run=True)
print(result)
```

## 📊 Example Correction Workflow

### Input (from Data Validation Agent)
```json
{
  "provider_id": "P001",
  "name": "Dr. Smith",
  "phone": "555.123.4567",
  "address": "123 Main St Boston",
  "specialty": "cardio"
}
```

### Processing
1. **Phone Correction**: `555.123.4567` → `(555) 123-4567` (95% confidence)
2. **Address Completion**: `123 Main St Boston` → `123 Main St, Boston, MA 02101` (92% confidence)
3. **Specialty Normalization**: `cardio` → `Cardiology` (98% confidence)

### Output
```json
{
  "provider_data": {
    "provider_id": "P001",
    "name": "Dr. Smith",
    "phone": "(555) 123-4567",
    "address": "123 Main St, Boston, MA 02101",
    "specialty": "Cardiology"
  },
  "corrections": [
    {
      "field": "phone",
      "before": "555.123.4567",
      "after": "(555) 123-4567",
      "confidence": 0.95,
      "source": "Standardized US format"
    }
  ],
  "email_status": {
    "status": "sent",
    "to_email": "dr.smith@example.com",
    "email_id": "email_1234567890"
  }
}
```

### Email Sent to Provider
```
Subject: Provider Information Updated - Dr. Smith

Dear Dr. Smith,

Your contact information was updated automatically based on public records:

✓ Phone: 555.123.4567 → (555) 123-4567
✓ Specialty: cardio → Cardiology

Please review the changes or contact us if incorrect.
```

## 🔧 API Endpoints

### Correction Agent APIs

```python
# Correct single provider
result = agent.process_provider(provider_data)

# Batch process multiple providers
results = agent.batch_process(providers_list)

# Get correction history
history = agent.get_correction_history(provider_id='P001')

# Get statistics
stats = agent.get_statistics()
```

### Email Generator APIs

```python
# Generate correction email
email_data = email_gen.generate_correction_email(provider_data, corrections)

# Send email
status = email_gen.send_email(email_data, dry_run=False)

# Track email opens
email_gen.track_email_open(email_id)

# Get email statistics
stats = email_gen.get_email_statistics()
```

### Dashboard REST APIs

- `POST /api/process` - Process provider and send notification
- `GET /api/history` - Get correction history
- `GET /api/emails` - Get email status
- `GET /api/stats` - Get statistics
- `POST /api/manual-override` - Apply manual correction

## 📈 Statistics & Monitoring

The system tracks:
- Total providers corrected
- Total fields corrected
- Corrections by field type (phone, address, specialty)
- Email send/open rates
- Manual override frequency
- Confidence score distributions

## 🔐 Security & Privacy

- All corrections logged with timestamps
- Before/after snapshots for audit trail
- Email content sanitized
- No PII exposed in logs
- SMTP credentials stored securely

## 🎯 Integration Points

### Input Sources
- Data Validation Agent output
- CSV file imports
- REST API submissions
- Manual dashboard entries

### Output Destinations
- Provider directory database
- Email notification system
- Manual review queue
- Audit log storage

## 🧪 Testing

Run individual demos:
```bash
python -c "from demo_scenarios import demo_scenario_1_phone_correction; demo_scenario_1_phone_correction()"
```

Test with custom data:
```bash
python automative_correction_agent.py
```

## 📝 Configuration

### Confidence Threshold
```python
agent = AutomativeCorrectionAgent(confidence_threshold=0.9)
```

### Google Maps API
```python
agent = AutomativeCorrectionAgent(google_maps_api_key='YOUR_API_KEY')
```

### SMTP Settings
```python
smtp_config = {
    'host': 'smtp.gmail.com',
    'port': 587,
    'username': 'your_email@gmail.com',
    'password': 'your_app_password',
    'from_email': 'noreply@providerdirectory.com'
}
email_gen = EmailGenerator(smtp_config=smtp_config)
```

## 📦 Deliverables

✅ **automative_correction_agent.py** - Correction logic and APIs  
✅ **email_generator.py** - Email templating and sending  
✅ **dashboard_ui.py** - Web UI for review and management  
✅ **demo_scenarios.py** - Demo workflows  
✅ **requirements.txt** - Dependencies  
✅ **README.md** - Complete documentation  

## 🎬 Demo Ready

The system is fully demo-ready with:
- 5 comprehensive demo scenarios
- Interactive web dashboard
- Sample provider data
- Email preview functionality
- Real-time statistics

## 🤝 Support

For questions or issues:
- Review demo scenarios in `demo_scenarios.py`
- Check API documentation in source files
- Test with dashboard UI at `http://localhost:5000`

## 📄 License

Internal use only - Provider Directory Management System

---

**Built by Person 5 (Joe) - Automative Correction Agent Owner**
