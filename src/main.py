import argparse
import os
import sys
from datetime import datetime

# Add src to path if running as script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import client_manager
import email_sender

def main():
    parser = argparse.ArgumentParser(description='Renewal-Rocket: Automate contract renewal reminders.')
    parser.add_argument('--clients', required=True, help='Path to the CSV file.')
    parser.add_argument('--days', type=int, default=14, help='Number of days before renewal to send reminders.')
    parser.add_argument('--send', action='store_true', help='Enable email sending.')
    parser.add_argument('--smtp-server', default='smtp.example.com', help='SMTP server address.')
    parser.add_argument('--smtp-port', type=int, default=587, help='SMTP server port.')
    parser.add_argument('--sender-email', required=False, help='Sender email address.')
    parser.add_argument('--sender-password', required=False, help='Sender email password.')

    args = parser.parse_args()

    if args.send:
        if not args.sender_email or not args.sender_password:
            print("Error: --sender-email and --sender-password are required when using --send.")
            sys.exit(1)

    try:
        clients = client_manager.read_clients(args.clients, args.days)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not clients:
        print("No clients found for renewal in the specified timeframe.")
        return

    log_dir = 'logs'
    log_file = os.path.join(log_dir, 'renewal_log.txt')
    os.makedirs(log_dir, exist_ok=True)

    with open(log_file, 'a') as f:
        for client in clients:
            subject = f"Reminder: Your contract with {client['client_name']} renews in {client['days_until']} days."
            body = f"Reminder: Your contract with {client['client_name']} renews in {client['days_until']} days."
            
            if args.send:
                success = email_sender.send_email(
                    client['client_email'],
                    subject,
                    body,
                    args.smtp_server,
                    args.smtp_port,
                    args.sender_email,
                    args.sender_password
                )
                status = "SENT" if success else "FAILED"
            else:
                status = "DRY RUN"

            f.write(f"{datetime.now().isoformat()} | {client['client_name']} | {client['client_email']} | {status}\n")
            print(f"Processed {client['client_name']}: {status}")

if __name__ == '__main__':
    main()
