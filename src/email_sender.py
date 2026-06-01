import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def format_renewal_email(client, days):
    subject = f"Reminder: Your contract with {client['name']} renews in {days} days."
    body = f"Dear {client['name']},\n\nThis is a reminder that your contract renews in {days} days.\n\nBest regards,\nRenewal-Rocket"
    return subject, body

def send_email(client, smtp_config):
    subject, body = format_renewal_email(client, smtp_config.get('days', 14))
    
    msg = MIMEMultipart()
    msg['From'] = smtp_config['sender_email']
    msg['To'] = client['email']
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        server.starttls()
        server.login(smtp_config['sender_email'], smtp_config['sender_password'])
        server.sendmail(smtp_config['sender_email'], client['email'], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email to {client['email']}: {e}")
        return False
