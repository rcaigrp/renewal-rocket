#!/usr/bin/env python3
"""Renewal-Rocket: CLI tool for automated contract renewal reminders."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from client_manager import read_clients, filter_expiring_clients
from email_sender import send_email


def parse_args(argv=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Automate contract renewal reminders')
    parser.add_argument('--clients', required=True, help='Path to clients CSV file')
    parser.add_argument('--days', type=int, default=14, help='Days before expiry to trigger reminder')
    parser.add_argument('--send', action='store_true', help='Actually send emails (default: dry run)')
    parser.add_argument('--log', default='logs/renewal_log.txt', help='Path to log file')
    return parser.parse_args(argv)


def write_log(log_path: str, message: str):
    """Append message to log file."""
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(path, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")


def main(argv=None):
    """Main entry point."""
    args = parse_args(argv)
    
    try:
        clients = read_clients(args.clients)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading clients: {e}")
        sys.exit(1)
    
    expiring = filter_expiring_clients(clients, args.days)
    
    if not expiring:
        print("No contracts expiring within the specified timeframe.")
        return
    
    print(f"Found {len(expiring)} contract(s) expiring within {args.days} days.")
    
    for client in expiring:
        if args.send:
            success = send_email(client, args.days)
            status = "SENT" if success else "FAILED"
            print(f"  [{status}] {client['name']} ({client['email']})")
            write_log(args.log, f"{status}: Email to {client['email']} for {client['name']}")
        else:
            print(f"  [DRY RUN] Would send to: {client['name']} ({client['email']})")
            write_log(args.log, f"DRY RUN: Would send to {client['email']} for {client['name']}")


if __name__ == '__main__':
    main()
