import sys
import os
import csv
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from main import parse_args, main
from client_manager import read_clients, filter_expiring_clients
from email_sender import format_email, send_email


# Acceptance Criterion 1: CLI parses arguments correctly
def test_criterion_1_cli_parses_args():
    """User runs: python main.py --clients data/clients.csv --days 14 --send"""
    args = parse_args(['--clients', 'data/clients.csv', '--days', '14', '--send'])
    assert args.clients == 'data/clients.csv'
    assert args.days == 14
    assert args.send is True


# Acceptance Criterion 2: Reads CSV and filters contracts expiring within N days
def test_criterion_2_read_csv_and_filter():
    """Tool reads clients.csv, identifies contracts expiring in 14 days."""
    # Create temp CSV
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'email', 'contract_end_date'])
        writer.writerow(['Acme Corp', 'contact@acme.com', '2025-01-15'])
        writer.writerow(['Beta Inc', 'info@beta.com', '2025-06-01'])
        writer.writerow(['Gamma LLC', 'admin@gamma.com', '2023-01-01'])  # Past date
        temp_path = f.name
    
    try:
        clients = read_clients(temp_path)
        assert len(clients) == 3  # All rows read (past dates filtered later)
        
        # Filter for 30 days (Acme should be included, Beta and Gamma excluded)
        expiring = filter_expiring_clients(clients, 30)
        assert len(expiring) == 1
        assert expiring[0]['name'] == 'Acme Corp'
        assert expiring[0]['email'] == 'contact@acme.com'
    finally:
        os.unlink(temp_path)


# Acceptance Criterion 3: Formats email correctly
def test_criterion_3_email_format():
    """Tool formats email: 'Reminder: Your contract with [Client] renews in 14 days.'"""
    client = {
        'name': 'Acme Corp',
        'email': 'contact@acme.com',
        'contract_end_date': '2025-01-15',
        'days_until_expiry': 14
    }
    subject, body = format_email(client, 14)
    assert 'Reminder: Your contract with Acme Corp renews in 14 days.' == subject
    assert 'Acme Corp' in body
    assert '2025-01-15' in body


# Acceptance Criterion 4: Sends email via SMTP
def test_criterion_4_sends_email():
    """Tool sends email to client.email."""
    client = {
        'name': 'Acme Corp',
        'email': 'contact@acme.com',
        'contract_end_date': '2025-01-15',
        'days_until_expiry': 14
    }
    
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        result = send_email(client, 14, smtp_host='localhost', smtp_port=25)
        
        assert result is True
        mock_smtp.assert_called_once_with('localhost', 25)
        mock_server.sendmail.assert_called_once()


# Acceptance Criterion 5: Writes to log file
def test_criterion_5_writes_log():
    """Tool writes success/failure to logs/renewal_log.txt."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        log_path = f.name
    
    try:
        main(['--clients', 'data/clients.csv', '--days', '14', '--log', log_path])
        
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        assert len(log_content) > 0
        assert '[DRY RUN]' in log_content
    finally:
        os.unlink(log_path)
