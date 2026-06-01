import argparse
import csv
import os
import sys
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def main():
    parser = argparse.ArgumentParser(description="Renewal-Rocket: Automate contract renewal reminders.")
    parser.add_argument('--clients', required=True, help='Path to the CSV file.')
    parser.add_argument('--days', type=int, default=14, help='Number of days before renewal to send reminders.')
    parser.add_argument('--send', action='store_true', help='Enable email sending (default: dry run).')
    parser.add_argument('--smtp-server', default='smtp.example.com', help='SMTP server address.')
    parser.add_argument('--smtp-port', type=int, default=587, help='SMTP server port.')
    parser.add_argument('--sender-email', default='', help='Sender email address.')
    parser.add_argument('--sender-password', default='', help='Sender email password.')
    
    args = parser.parse_args()

    # Resolve absolute path for log file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'renewal_log.txt')

    # Read and filter clients
    clients = []
    try:
        with open(args.clients, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    renewal_date = datetime.strptime(row['renewal_date'], '%Y-%m-%d')
                    if (renewal_date - datetime.now()).days <= args.days:
                        clients.append(row)
                except (KeyError, ValueError):
                    continue
    except FileNotFoundError:
        print(f"Error: Client file '{args.clients}' not found.")
        sys.exit(1)

    # Send emails or dry run
    with open(log_path, 'a') as log:
        for client in clients:
            subject = f"Reminder: Your contract with {client['client_name']} renews in {args.days} days."
            body = f"Dear {client['client_name']},\n\nReminder: Your contract with {client['client_name']} renews in {args.days} days.\n\nBest regards,\nRenewal-Rocket"
            
            if args.send:
                if not args.sender_email or not args.sender_password:
                    msg = f"Skipping {client['client_name']}: SMTP credentials not provided for sending.\n"
                    log.write(msg)
                    print(f"WARNING: {msg.strip()}")
                    continue
                
                try:
                    msg = MIMEMultipart()
                    msg['From'] = args.sender_email
                    msg['To'] = client['client_email']
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body, 'plain'))
                    
                    with smtplib.SMTP(args.smtp_server, args.smtp_port) as server:
                        server.starttls()
                        server.login(args.sender_email, args.sender_password)
                        server.sendmail(args.sender_email, client['client_email'], msg.as_string())
                    log.write(f"SUCCESS: Sent reminder to {client['client_email']}\n")
                    print(f"SUCCESS: Sent reminder to {client['client_email']}")
                except Exception as e:
                    log.write(f"FAILURE: Failed to send to {client['client_email']}: {str(e)}\n")
                    print(f"FAILURE: Failed to send to {client['client_email']}: {str(e)}")
            else:
                log.write(f"DRY RUN: Would send reminder to {client['client_email']}\n")
                print(f"DRY RUN: Would send reminder to {client['client_email']}")

if __name__ == '__main__':
    main()
