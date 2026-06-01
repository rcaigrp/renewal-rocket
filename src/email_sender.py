import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def format_email(client, days):
    subject = f"Reminder: Your contract with {client['client_name']} renews in {days} days."
    body = f"Dear {client['client_name']},\n\nThis is a reminder that your contract renews in {days} days.\n\nBest regards,\nRenewal-Rocket"
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = 'noreply@example.com'
    msg['To'] = client['client_email']
    msg.attach(MIMEText(body, 'plain'))
    return msg

def send_email(msg, smtp_server, smtp_port, sender_email, sender_password, recipient_email):
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {e}")
        return False
