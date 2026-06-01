import argparse
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client_manager import read_clients, filter_expiring_clients
from email_sender import format_email, send_email

def log_result(message, log_path):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'a') as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")

def main():
    parser = argparse.ArgumentParser(description='Renewal-Rocket: Automate contract renewal reminders')
    parser.add_argument('--clients', required=True, help='Path to clients CSV file')
    parser.add_argument('--days', type=int, default=14, help='Number of days to look ahead')
    parser.add_argument('--send', action='store_true', help='Send emails')
    parser.add_argument('--smtp-server', default='smtp.example.com', help='SMTP server address')
    parser.add_argument('--smtp-port', type=int, default=587, help='SMTP server port')
    parser.add_argument('--sender-email', default='noreply@example.com', help='Sender email address')
    parser.add_argument('--sender-password', default='password', help='Sender email password')
    
    args = parser.parse_args()
    log_path = 'logs/renewal_log.txt'
    
    try:
        clients = read_clients(args.clients)
    except Exception as e:
        print(f"Error reading clients file: {e}")
        log_result(f"ERROR: Failed to read clients file: {e}", log_path)
        sys.exit(1)
        
    expiring = filter_expiring_clients(clients, args.days)
    
    if not expiring:
        print("No expiring contracts found.")
        log_result("INFO: No expiring contracts found.", log_path)
        return
        
    for client in expiring:
        msg = format_email(client, args.days)
        if args.send:
            success = send_email(msg, args.smtp_server, args.smtp_port, args.sender_email, args.sender_password, client['client_email'])
            if success:
                print(f"Email sent to {client['client_email']}")
                log_result(f"SUCCESS: Email sent to {client['client_email']}", log_path)
            else:
                log_result(f"FAILURE: Failed to send email to {client['client_email']}", log_path)
        else:
            print(f"[DRY RUN] Would send email to {client['client_email']}")
            log_result(f"DRY RUN: Would send email to {client['client_email']}", log_path)

if __name__ == '__main__':
    main()
