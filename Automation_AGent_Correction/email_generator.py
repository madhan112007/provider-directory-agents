"""
Email Generator and Sender
Generates and sends notification emails to providers about auto-corrections.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailGenerator:
    def __init__(self, smtp_config: Optional[Dict] = None):
        """
        Initialize email generator with SMTP configuration
        
        Args:
            smtp_config: Dict with keys: host, port, username, password, from_email
        """
        self.smtp_config = smtp_config or {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': '<your_email>',
            'password': '<your_password>',
            'from_email': 'noreply@providerdirectory.com'
        }
        self.email_history = []
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load email templates"""
        return {
            'auto_correction': """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 20px; }}
        .correction {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
        .field-name {{ font-weight: bold; color: #4CAF50; }}
        .before {{ color: #d32f2f; text-decoration: line-through; }}
        .after {{ color: #388e3c; font-weight: bold; }}
        .footer {{ margin-top: 20px; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
        .button {{ background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; display: inline-block; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Provider Information Updated</h1>
        </div>
        <div class="content">
            <p>Dear {provider_name},</p>
            <p>Your contact information in our provider directory has been automatically updated based on verified public records and data sources.</p>
            
            <h3>Changes Made:</h3>
            {corrections_html}
            
            <p><strong>What you need to do:</strong></p>
            <ul>
                <li>Review the changes above to ensure accuracy</li>
                <li>If any information is incorrect, please contact us immediately</li>
                <li>No action needed if all information is correct</li>
            </ul>
            
            <a href="{review_link}" class="button">Review Changes</a>
            
            <p>These updates help ensure patients can reach you with accurate contact information.</p>
        </div>
        <div class="footer">
            <p>This is an automated notification from Provider Directory Management System</p>
            <p>If you have questions, contact us at support@providerdirectory.com</p>
            <p>&copy; 2024 Provider Directory. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """,
            
            'manual_review_needed': """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #ff9800; color: white; padding: 20px; text-align: center; }}
        .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 20px; }}
        .warning {{ background-color: #fff3cd; padding: 15px; margin: 10px 0; border-left: 4px solid #ff9800; }}
        .footer {{ margin-top: 20px; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
        .button {{ background-color: #ff9800; color: white; padding: 10px 20px; text-decoration: none; display: inline-block; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Action Required: Verify Your Information</h1>
        </div>
        <div class="content">
            <p>Dear {provider_name},</p>
            <div class="warning">
                <p><strong>⚠️ Manual Review Required</strong></p>
                <p>We detected potential issues with your provider information that require your attention.</p>
            </div>
            
            <h3>Issues Detected:</h3>
            {issues_html}
            
            <p><strong>Action Required:</strong></p>
            <p>Please log in to your provider portal and update your information to ensure accuracy.</p>
            
            <a href="{portal_link}" class="button">Update My Information</a>
        </div>
        <div class="footer">
            <p>This is an automated notification from Provider Directory Management System</p>
            <p>If you have questions, contact us at support@providerdirectory.com</p>
        </div>
    </div>
</body>
</html>
            """
        }
    
    def generate_correction_email(self, provider_data: Dict, corrections: List[Dict]) -> Dict:
        """Generate email content for auto-corrections"""
        provider_name = provider_data.get('name', 'Provider')
        provider_email = provider_data.get('email', '')
        provider_id = provider_data.get('provider_id', 'unknown')
        
        # Build corrections HTML
        corrections_html = ""
        for correction in corrections:
            corrections_html += f"""
            <div class="correction">
                <span class="field-name">{correction['field'].title()}:</span><br>
                <span class="before">Before: {correction['before']}</span><br>
                <span class="after">After: {correction['after']}</span><br>
                <small>Source: {correction['source']} (Confidence: {correction['confidence']:.0%})</small>
            </div>
            """
        
        # Fill template
        email_body = self.templates['auto_correction'].format(
            provider_name=provider_name,
            corrections_html=corrections_html,
            review_link=f"https://providerdirectory.com/review/{provider_id}"
        )
        
        email_data = {
            'to_email': provider_email,
            'subject': f'Provider Information Updated - {provider_name}',
            'body': email_body,
            'provider_id': provider_id,
            'type': 'auto_correction',
            'generated_at': datetime.now().isoformat()
        }
        
        return email_data
    
    def generate_manual_review_email(self, provider_data: Dict, issues: List[str]) -> Dict:
        """Generate email for manual review needed"""
        provider_name = provider_data.get('name', 'Provider')
        provider_email = provider_data.get('email', '')
        provider_id = provider_data.get('provider_id', 'unknown')
        
        # Build issues HTML
        issues_html = "<ul>"
        for issue in issues:
            issues_html += f"<li>{issue}</li>"
        issues_html += "</ul>"
        
        # Fill template
        email_body = self.templates['manual_review_needed'].format(
            provider_name=provider_name,
            issues_html=issues_html,
            portal_link=f"https://providerdirectory.com/portal/{provider_id}"
        )
        
        email_data = {
            'to_email': provider_email,
            'subject': f'Action Required: Verify Your Provider Information',
            'body': email_body,
            'provider_id': provider_id,
            'type': 'manual_review',
            'generated_at': datetime.now().isoformat()
        }
        
        return email_data
    
    def send_email(self, email_data: Dict, dry_run: bool = True) -> Dict:
        """
        Send email via SMTP
        
        Args:
            email_data: Dict with to_email, subject, body
            dry_run: If True, don't actually send (for testing)
        
        Returns:
            Dict with status and tracking info
        """
        if dry_run:
            logger.info(f"[DRY RUN] Would send email to {email_data['to_email']}")
            status = {
                'email_id': f"email_{datetime.now().timestamp()}",
                'status': 'sent_dry_run',
                'sent_at': datetime.now().isoformat(),
                'to_email': email_data['to_email'],
                'subject': email_data['subject'],
                'provider_id': email_data.get('provider_id'),
                'opened': False,
                'opened_at': None
            }
            self.email_history.append(status)
            return status
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_config['from_email']
            msg['To'] = email_data['to_email']
            msg['Subject'] = email_data['subject']
            
            # Attach HTML body
            html_part = MIMEText(email_data['body'], 'html')
            msg.attach(html_part)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            
            status = {
                'email_id': f"email_{datetime.now().timestamp()}",
                'status': 'sent',
                'sent_at': datetime.now().isoformat(),
                'to_email': email_data['to_email'],
                'subject': email_data['subject'],
                'provider_id': email_data.get('provider_id'),
                'opened': False,
                'opened_at': None
            }
            self.email_history.append(status)
            logger.info(f"Email sent successfully to {email_data['to_email']}")
            return status
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            status = {
                'email_id': f"email_{datetime.now().timestamp()}",
                'status': 'failed',
                'error': str(e),
                'sent_at': datetime.now().isoformat(),
                'to_email': email_data['to_email'],
                'provider_id': email_data.get('provider_id')
            }
            self.email_history.append(status)
            return status
    
    def track_email_open(self, email_id: str):
        """Track when an email is opened (webhook endpoint)"""
        for email in self.email_history:
            if email['email_id'] == email_id:
                email['opened'] = True
                email['opened_at'] = datetime.now().isoformat()
                logger.info(f"Email {email_id} opened")
                return True
        return False
    
    def get_email_status(self, provider_id: Optional[str] = None) -> List[Dict]:
        """Get email sending history"""
        if provider_id:
            return [e for e in self.email_history if e.get('provider_id') == provider_id]
        return self.email_history
    
    def get_email_statistics(self) -> Dict:
        """Get email statistics"""
        total_sent = len([e for e in self.email_history if e['status'] in ['sent', 'sent_dry_run']])
        total_failed = len([e for e in self.email_history if e['status'] == 'failed'])
        total_opened = len([e for e in self.email_history if e.get('opened', False)])
        
        return {
            'total_emails': len(self.email_history),
            'sent': total_sent,
            'failed': total_failed,
            'opened': total_opened,
            'open_rate': (total_opened / total_sent * 100) if total_sent > 0 else 0
        }


# Integration function
def create_email_pipeline(correction_agent, email_generator):
    """Create integrated pipeline: corrections → email generation → sending"""
    
    def process_and_notify(provider_data: Dict, dry_run: bool = True) -> Dict:
        """Process provider corrections and send notification email"""
        # Step 1: Apply corrections
        result = correction_agent.process_provider(provider_data)
        
        # Step 2: Generate email if corrections were made
        email_status = None
        if result['corrections']:
            email_data = email_generator.generate_correction_email(
                result['provider_data'],
                result['corrections']
            )
            # Step 3: Send email
            email_status = email_generator.send_email(email_data, dry_run=dry_run)
        
        return {
            'provider_data': result['provider_data'],
            'corrections': result['corrections'],
            'email_status': email_status,
            'needs_manual_review': result['needs_manual_review']
        }
    
    return process_and_notify


if __name__ == "__main__":
    # Demo usage
    email_gen = EmailGenerator()
    
    # Test correction email
    test_provider = {
        'provider_id': 'P001',
        'name': 'Dr. John Smith',
        'email': 'dr.smith@example.com',
        'phone': '(555) 123-4567',
        'address': '123 Main St, Boston, MA 02101',
        'specialty': 'Cardiology'
    }
    
    test_corrections = [
        {
            'field': 'phone',
            'before': '555.123.4567',
            'after': '(555) 123-4567',
            'confidence': 0.95,
            'source': 'Standardized US format'
        },
        {
            'field': 'specialty',
            'before': 'cardio',
            'after': 'Cardiology',
            'confidence': 0.98,
            'source': 'Controlled vocabulary'
        }
    ]
    
    print("Generating correction notification email...")
    email_data = email_gen.generate_correction_email(test_provider, test_corrections)
    print(f"\nTo: {email_data['to_email']}")
    print(f"Subject: {email_data['subject']}")
    print(f"\nEmail preview saved to file")
    
    # Send email (dry run)
    status = email_gen.send_email(email_data, dry_run=True)
    print(f"\nEmail Status: {status['status']}")
    print(f"Email ID: {status['email_id']}")
    
    # Statistics
    print("\n" + "="*50)
    print("Email Statistics:")
    print(email_gen.get_email_statistics())
