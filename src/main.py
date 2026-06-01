import argparse
import os
import sys
from datetime import datetime

from src.client_manager import read_clients
from src.email_sender import send_email

def ensure_dirs():
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)

def parse_args():
    parser = argparse.ArgumentParser(description="Renewal-Rocket: Automate contract renewal reminders.")
    parser.add_argument("--clients", type=str, required=True, help="Path to the clients CSV file.")
    parser.add_argument("--days", type=int, default=14, help="Number of days before renewal to send reminders (default: 14).")
    parser.add_argument("--send", action="store_true", help="Enable email sending (default: dry run).")
    parser.add_argument("--smtp-server", type=str, default="smtp.example.com", help="SMTP server address.")
    parser.add_argument("--smtp-port", type=int, default=587, help="SMTP server port.")
    parser.add_argument("--sender-email", type=str, default="", help="Sender email address.")
    parser.add_argument("--sender-password", type=str, default="", help="Sender email password.")
    return parser.parse_args()

def log_message(message):
    ensure_dirs()
    log_path = os.path.join("logs", "renewal_log.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def main():
    args = parse_args()
    ensure_dirs()

    try:
        clients = read_clients(args.clients, args.days)
    except FileNotFoundError:
        log_message(f"ERROR: Clients file not found: {args.clients}")
        print(f"Error: Clients file not found: {args.clients}")
        sys.exit(1)
    except ValueError as e:
        log_message(f"ERROR: CSV parse error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

    if not clients:
        log_message("INFO: No clients found expiring within the specified days.")
        print("No clients found expiring within the specified days.")
        return

    smtp_config = {
        'server': args.smtp_server,
        'port': args.smtp_port,
        'sender_email': args.sender_email,
        'sender_password': args.sender_password,
        'days': args.days
    }

    for client in clients:
        if args.send:
            success = send_email(client, smtp_config)
            if success:
                log_message(f"SUCCESS: Sent renewal reminder to {client['email']}")
            else:
                log_message(f"FAILURE: Failed to send renewal reminder to {client['email']}")
        else:
            log_message(f"DRY RUN: Would send renewal reminder to {client['email']}")
            print(f"DRY RUN: Would send renewal reminder to {client['email']}")

    log_message("INFO: Process completed.")
    print("Process completed.")

if __name__ == "__main__":
    main()
