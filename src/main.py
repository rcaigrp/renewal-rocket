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
    parser.add_argument('--send', action='store_true', help='Enable email sending. Default is dry run.')
    parser.add_argument('--smtp-server', default='smtp.example.com', help='SMTP server address.')
    parser.add_argument('--smtp-port', type=int, default=587, help='SMTP server port.')
    parser.add_argument('--sender-email', required=True, help='Sender email address.')
    parser.add_argument('--sender-password', required=True, help='Sender email password.')
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'renewal_log.txt')

    try:
        clients = []
        with open(args.clients, mode='r') as f:
            reader = csv.DictReader(f)
            required_cols = {'client_name', 'client_email', 'renewal_date'}
            if not required_cols.issubset(set(reader.fieldnames or [])):
                raise ValueError("Missing required columns in CSV")
            
            today = datetime.now().date()
            cutoff = today + timedelta(days=args.days)
            
            seen_emails = set()
            for row in reader:
                try:
                    renewal_date = datetime.strptime(row['renewal_date'], '%Y-%m-%d').date()
                except ValueError:
                    continue
                    
                if renewal_date < today:
                    continue
                    
                if renewal_date <= cutoff:
                    email = row['client_email']
                    if email in seen_emails:
                        print(f"Warning: Duplicate email for {row['client_name']} ({email}). Skipping.")
                        with open(log_file, 'a') as lf:
                            lf.write(f"[WARN] Duplicate email: {email}\n")
                        continue
                    seen_emails.add(email)
                    clients.append(row)
    except FileNotFoundError:
        print(f"Error: Clients file not found: {args.clients}")
        with open(log_file, 'a') as lf:
            lf.write(f"[FAIL] File not found: {args.clients}\n")
        return
    except ValueError as e:
        print(f"Error reading CSV: {e}")
        with open(log_file, 'a') as lf:
            lf.write(f"[FAIL] CSV Error: {e}\n")
        return

    if not clients:
        print("No upcoming renewals found within the specified timeframe.")
        with open(log_file, 'a') as lf:
            lf.write("[INFO] No upcoming renewals.\n")
        return

    for client in clients:
        subject = f"Reminder: Your contract with {client['client_name']} renews in {args.days} days."
        body = f"Reminder: Your contract with {client['client_name']} renews in {args.days} days."
        
        if args.send:
            try:
                with smtplib.SMTP(args.smtp_server, args.smtp_port) as server:
                    server.starttls()
                    server.login(args.sender_email, args.sender_password)
                    msg = MIMEMultipart()
                    msg['From'] = args.sender_email
                    msg['To'] = client['client_email']
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body, 'plain'))
                    server.sendmail(args.sender_email, client['client_email'], msg.as_string())
                print(f"[SUCCESS] Sent email to {client['client_email']}")
                with open(log_file, 'a') as lf:
                    lf.write(f"[SUCCESS] Sent email to {client['client_email']}\n")
            except Exception as e:
                print(f"[FAIL] Failed to send email to {client['client_email']}: {e}")
                with open(log_file, 'a') as lf:
                    lf.write(f"[FAIL] Email send failed for {client['client_email']}: {e}\n")
        else:
            print(f"[DRY RUN] Would send to {client['client_email']}: {subject}")
            with open(log_file, 'a') as lf:
                lf.write(f"[DRY RUN] Would send to {client['client_email']}: {subject}\n")

if __name__ == "__main__":
    main()
