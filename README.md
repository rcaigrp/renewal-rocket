# Renewal-Rocket

A CLI tool that automates contract renewal reminders to prevent revenue loss.

## Installation

No external dependencies are required. Python 3.11+ is needed.

## Usage

1. Prepare your `clients.csv` in the `data/` directory:
   ```csv
   client_name,client_email,renewal_date
   Acme Corp,acme@example.com,2030-01-01
   ```

2. Run the tool:
   ```bash
   python main.py --clients data/clients.csv --days 14 --send
   ```

### Flags

- `--clients`: Path to the CSV file.
- `--days`: Number of days before renewal to send reminders (default: 14).
- `--send`: Enable email sending (default: dry run).
- `--smtp-server`: SMTP server address (default: smtp.example.com).
- `--smtp-port`: SMTP server port (default: 587).
- `--sender-email`: Sender email address.
- `--sender-password`: Sender email password.

## Configuration

- Ensure `data/clients.csv` exists with columns: `client_name`, `client_email`, `renewal_date`.
- Logs are written to `logs/renewal_log.txt`.
