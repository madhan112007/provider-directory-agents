"""
Dashboard UI for Automative Correction Agent
Web-based interface for reviewing corrections, managing emails, and manual overrides.
"""

from flask import Flask, render_template_string, request, jsonify
from automative_correction_agent import AutomativeCorrectionAgent
from email_generator import EmailGenerator, create_email_pipeline
from datetime import datetime
import json

app = Flask(__name__)

# Initialize agents
correction_agent = AutomativeCorrectionAgent(confidence_threshold=0.9)
email_generator = EmailGenerator()
process_and_notify = create_email_pipeline(correction_agent, email_generator)

# Dashboard HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Automative Correction Agent Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header h1 { font-size: 28px; }
        .header p { opacity: 0.9; margin-top: 5px; }
        .container { max-width: 1400px; margin: 20px auto; padding: 0 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-card h3 { color: #666; font-size: 14px; margin-bottom: 10px; }
        .stat-card .value { font-size: 32px; font-weight: bold; color: #667eea; }
        .section { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .section h2 { color: #333; margin-bottom: 20px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; color: #555; }
        .form-group input, .form-group textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        .form-group textarea { min-height: 80px; font-family: monospace; }
        .btn { padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.3s; }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #5568d3; }
        .btn-success { background: #48bb78; color: white; }
        .btn-success:hover { background: #38a169; }
        .btn-warning { background: #ed8936; color: white; }
        .btn-warning:hover { background: #dd6b20; }
        .correction-item { background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #48bb78; border-radius: 4px; }
        .correction-item.manual-review { border-left-color: #ed8936; }
        .correction-field { margin: 8px 0; }
        .correction-field strong { color: #667eea; }
        .before { color: #e53e3e; text-decoration: line-through; }
        .after { color: #48bb78; font-weight: bold; }
        .email-item { background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #667eea; }
        .email-item.failed { border-left-color: #e53e3e; }
        .email-item.opened { border-left-color: #48bb78; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
        .badge-success { background: #c6f6d5; color: #22543d; }
        .badge-warning { background: #feebc8; color: #7c2d12; }
        .badge-danger { background: #fed7d7; color: #742a2a; }
        .badge-info { background: #bee3f8; color: #2c5282; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #e2e8f0; }
        .tab { padding: 12px 24px; cursor: pointer; border: none; background: none; font-size: 14px; font-weight: 600; color: #666; transition: all 0.3s; }
        .tab.active { color: #667eea; border-bottom: 2px solid #667eea; margin-bottom: -2px; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        #result { margin-top: 20px; padding: 15px; border-radius: 4px; display: none; }
        #result.success { background: #c6f6d5; color: #22543d; }
        #result.error { background: #fed7d7; color: #742a2a; }
        .json-display { background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 4px; overflow-x: auto; font-family: 'Courier New', monospace; font-size: 13px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Automative Correction Agent Dashboard</h1>
        <p>Automated provider data correction and notification system</p>
    </div>
    
    <div class="container">
        <!-- Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Corrections</h3>
                <div class="value" id="stat-corrections">0</div>
            </div>
            <div class="stat-card">
                <h3>Providers Corrected</h3>
                <div class="value" id="stat-providers">0</div>
            </div>
            <div class="stat-card">
                <h3>Emails Sent</h3>
                <div class="value" id="stat-emails">0</div>
            </div>
            <div class="stat-card">
                <h3>Email Open Rate</h3>
                <div class="value" id="stat-open-rate">0%</div>
            </div>
        </div>
        
        <!-- Main Tabs -->
        <div class="section">
            <div class="tabs">
                <button class="tab active" onclick="switchTab('process')">Process Provider</button>
                <button class="tab" onclick="switchTab('history')">Correction History</button>
                <button class="tab" onclick="switchTab('emails')">Email Status</button>
                <button class="tab" onclick="switchTab('manual')">Manual Override</button>
            </div>
            
            <!-- Process Provider Tab -->
            <div id="tab-process" class="tab-content active">
                <h2>Process Provider Data</h2>
                <form id="processForm">
                    <div class="form-group">
                        <label>Provider ID</label>
                        <input type="text" id="provider_id" value="P001" required>
                    </div>
                    <div class="form-group">
                        <label>Provider Name</label>
                        <input type="text" id="provider_name" value="Dr. John Smith" required>
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="provider_email" value="dr.smith@example.com" required>
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="text" id="provider_phone" value="555.123.4567" required>
                    </div>
                    <div class="form-group">
                        <label>Address</label>
                        <input type="text" id="provider_address" value="123 Main St Boston MA" required>
                    </div>
                    <div class="form-group">
                        <label>Specialty</label>
                        <input type="text" id="provider_specialty" value="cardio" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Process & Send Notification</button>
                </form>
                <div id="result"></div>
            </div>
            
            <!-- Correction History Tab -->
            <div id="tab-history" class="tab-content">
                <h2>Correction History</h2>
                <button class="btn btn-success" onclick="loadHistory()">Refresh History</button>
                <div id="history-list"></div>
            </div>
            
            <!-- Email Status Tab -->
            <div id="tab-emails" class="tab-content">
                <h2>Email Status & Tracking</h2>
                <button class="btn btn-success" onclick="loadEmails()">Refresh Emails</button>
                <div id="email-list"></div>
            </div>
            
            <!-- Manual Override Tab -->
            <div id="tab-manual" class="tab-content">
                <h2>Manual Override</h2>
                <p style="color: #666; margin-bottom: 20px;">Manually correct provider data when automatic correction confidence is low.</p>
                <form id="manualForm">
                    <div class="form-group">
                        <label>Provider ID</label>
                        <input type="text" id="manual_provider_id" required>
                    </div>
                    <div class="form-group">
                        <label>Field to Correct</label>
                        <select id="manual_field" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
                            <option value="phone">Phone</option>
                            <option value="address">Address</option>
                            <option value="specialty">Specialty</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>New Value</label>
                        <input type="text" id="manual_value" required>
                    </div>
                    <div class="form-group">
                        <label>Reason</label>
                        <textarea id="manual_reason" placeholder="Explain why this manual correction is needed"></textarea>
                    </div>
                    <button type="submit" class="btn btn-warning">Apply Manual Correction</button>
                </form>
                <div id="manual-result"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Tab switching
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('tab-' + tabName).classList.add('active');
        }
        
        // Load statistics
        function loadStats() {
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('stat-corrections').textContent = data.correction_stats.total_fields_corrected;
                    document.getElementById('stat-providers').textContent = data.correction_stats.total_providers_corrected;
                    document.getElementById('stat-emails').textContent = data.email_stats.sent;
                    document.getElementById('stat-open-rate').textContent = data.email_stats.open_rate.toFixed(1) + '%';
                });
        }
        
        // Process provider form
        document.getElementById('processForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const data = {
                provider_id: document.getElementById('provider_id').value,
                name: document.getElementById('provider_name').value,
                email: document.getElementById('provider_email').value,
                phone: document.getElementById('provider_phone').value,
                address: document.getElementById('provider_address').value,
                specialty: document.getElementById('provider_specialty').value
            };
            
            fetch('/api/process', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(r => r.json())
            .then(result => {
                const resultDiv = document.getElementById('result');
                resultDiv.style.display = 'block';
                resultDiv.className = 'success';
                
                let html = '<h3>Processing Complete</h3>';
                if (result.corrections.length > 0) {
                    html += '<div class="correction-item"><strong>Corrections Applied:</strong>';
                    result.corrections.forEach(c => {
                        html += `<div class="correction-field">
                            <strong>${c.field}:</strong> 
                            <span class="before">${c.before}</span> → 
                            <span class="after">${c.after}</span>
                            <br><small>Confidence: ${(c.confidence * 100).toFixed(0)}% | Source: ${c.source}</small>
                        </div>`;
                    });
                    html += '</div>';
                    
                    if (result.email_status) {
                        html += `<div class="correction-item">
                            <strong>Email Notification:</strong> ${result.email_status.status}
                            <br><small>Sent to: ${result.email_status.to_email}</small>
                        </div>`;
                    }
                } else {
                    html += '<p>No corrections needed - all data is already accurate!</p>';
                }
                
                resultDiv.innerHTML = html;
                loadStats();
            })
            .catch(err => {
                const resultDiv = document.getElementById('result');
                resultDiv.style.display = 'block';
                resultDiv.className = 'error';
                resultDiv.innerHTML = '<h3>Error</h3><p>' + err.message + '</p>';
            });
        });
        
        // Load correction history
        function loadHistory() {
            fetch('/api/history')
                .then(r => r.json())
                .then(data => {
                    const list = document.getElementById('history-list');
                    if (data.length === 0) {
                        list.innerHTML = '<p style="color: #666; margin-top: 20px;">No corrections yet.</p>';
                        return;
                    }
                    
                    let html = '';
                    data.forEach(record => {
                        html += `<div class="correction-item">
                            <strong>Provider ID:</strong> ${record.provider_id} 
                            <span class="badge badge-success">${record.status}</span>
                            <br><small>${record.timestamp}</small>
                            <div style="margin-top: 10px;">`;
                        
                        record.corrections.forEach(c => {
                            html += `<div class="correction-field">
                                <strong>${c.field}:</strong> 
                                <span class="before">${c.before}</span> → 
                                <span class="after">${c.after}</span>
                                <br><small>Confidence: ${(c.confidence * 100).toFixed(0)}%</small>
                            </div>`;
                        });
                        
                        html += '</div></div>';
                    });
                    list.innerHTML = html;
                });
        }
        
        // Load email status
        function loadEmails() {
            fetch('/api/emails')
                .then(r => r.json())
                .then(data => {
                    const list = document.getElementById('email-list');
                    if (data.length === 0) {
                        list.innerHTML = '<p style="color: #666; margin-top: 20px;">No emails sent yet.</p>';
                        return;
                    }
                    
                    let html = '';
                    data.forEach(email => {
                        const statusClass = email.status === 'failed' ? 'failed' : (email.opened ? 'opened' : '');
                        const badge = email.status === 'failed' ? 'badge-danger' : 
                                     (email.opened ? 'badge-success' : 'badge-info');
                        const statusText = email.status === 'failed' ? 'Failed' :
                                          (email.opened ? 'Opened' : 'Sent');
                        
                        html += `<div class="email-item ${statusClass}">
                            <strong>To:</strong> ${email.to_email} 
                            <span class="badge ${badge}">${statusText}</span>
                            <br><strong>Subject:</strong> ${email.subject}
                            <br><strong>Provider ID:</strong> ${email.provider_id}
                            <br><small>Sent: ${email.sent_at}</small>
                            ${email.opened_at ? '<br><small>Opened: ' + email.opened_at + '</small>' : ''}
                        </div>`;
                    });
                    list.innerHTML = html;
                });
        }
        
        // Manual override form
        document.getElementById('manualForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const data = {
                provider_id: document.getElementById('manual_provider_id').value,
                field: document.getElementById('manual_field').value,
                value: document.getElementById('manual_value').value,
                reason: document.getElementById('manual_reason').value
            };
            
            fetch('/api/manual-override', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(r => r.json())
            .then(result => {
                const resultDiv = document.getElementById('manual-result');
                resultDiv.style.display = 'block';
                resultDiv.className = 'success';
                resultDiv.innerHTML = '<h3>Manual Override Applied</h3><pre class="json-display">' + 
                                     JSON.stringify(result, null, 2) + '</pre>';
            });
        });
        
        // Load initial stats
        loadStats();
    </script>
</body>
</html>
"""

# API Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/process', methods=['POST'])
def process_provider():
    """Process provider and send notification"""
    provider_data = request.json
    result = process_and_notify(provider_data, dry_run=True)
    return jsonify(result)

@app.route('/api/history')
def get_history():
    """Get correction history"""
    history = correction_agent.get_correction_history()
    return jsonify(history)

@app.route('/api/emails')
def get_emails():
    """Get email status"""
    emails = email_generator.get_email_status()
    return jsonify(emails)

@app.route('/api/stats')
def get_stats():
    """Get statistics"""
    correction_stats = correction_agent.get_statistics()
    email_stats = email_generator.get_email_statistics()
    return jsonify({
        'correction_stats': correction_stats,
        'email_stats': email_stats
    })

@app.route('/api/manual-override', methods=['POST'])
def manual_override():
    """Apply manual correction override"""
    data = request.json
    
    # Log manual override
    override_record = {
        'provider_id': data['provider_id'],
        'field': data['field'],
        'value': data['value'],
        'reason': data['reason'],
        'timestamp': datetime.now().isoformat(),
        'type': 'manual_override'
    }
    
    return jsonify({
        'status': 'success',
        'override': override_record,
        'message': f"Manual override applied for {data['field']}"
    })

@app.route('/api/email-preview/<provider_id>')
def email_preview(provider_id):
    """Preview email content"""
    # This would fetch provider data and generate preview
    return jsonify({'preview': 'Email preview HTML here'})


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Automative Correction Agent Dashboard Starting...")
    print("="*60)
    print("\nDashboard URL: http://localhost:5000")
    print("\nFeatures:")
    print("   - Process provider data with auto-corrections")
    print("   - View correction history")
    print("   - Track email notifications")
    print("   - Manual override interface")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, port=5000)
