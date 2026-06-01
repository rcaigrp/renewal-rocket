import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def format_email(client: dict, days: int) -> tuple[str, str]:
    """Format email subject and body. Returns (subject, body)."""
    subject = f"Reminder: Your contract with {client['name']} renews in {days} days."
    body = f"""Dear {client['name']},

This is a reminder that your contract with us is set to renew on {client['contract_end_date']} ({days} days from now).

Please review your contract details and let us know if you have any questions.

Best regards,
Your Team
"""
    return subject, body


def send_email(client: dict, days: int, smtp_host: str = 'localhost', smtp_port: int = 25,
               sender_email: str = 'noreply@example.com', sender_password: str = '') -> bool:
    """Send renewal reminder email. Returns True on success, False on failure."""
    try:
        subject, body = format_email(client, days)
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = client['email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        if sender_password:
            server.login(sender_email, sender_password)
        server.sendmail(sender_email, client['email'], msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        print(f"Failed to send email to {client['email']}: {e}")
        return False
