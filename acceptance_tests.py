import os
import sys
import tempfile
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import importlib.util

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MAIN_MODULE = os.path.join(PROJECT_ROOT, 'src', 'main.py')

def test_criterion_1_cli_parses_args():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, dir=PROJECT_ROOT) as f:
        f.write("client_name,client_email,renewal_date\n")
        future_date = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        f.write(f"Client A,clientA@example.com,{future_date}\n")
        csv_path = f.name
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, MAIN_MODULE, '--clients', csv_path, '--days', '10', '--send',
             '--smtp-server', 'smtp.test.com', '--smtp-port', '587',
             '--sender-email', 'sender@test.com', '--sender-password', 'secret'],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        assert result.returncode == 0
    finally:
        os.unlink(csv_path)

def test_criterion_2_read_csv_and_filter():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, dir=PROJECT_ROOT) as f:
        f.write("client_name,client_email,renewal_date\n")
        future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        past_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        f.write(f"Client A,clientA@example.com,{future_date}\n")
        f.write(f"Client B,clientB@example.com,{past_date}\n")
        csv_path = f.name
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, MAIN_MODULE, '--clients', csv_path, '--days', '10',
             '--sender-email', 'sender@test.com', '--sender-password', 'secret'],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        assert '[DRY RUN] Would send to clientA@example.com' in result.stdout
        assert 'Client B' not in result.stdout
    finally:
        os.unlink(csv_path)

def test_criterion_3_email_formatting():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, dir=PROJECT_ROOT) as f:
        f.write("client_name,client_email,renewal_date\n")
        future_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        f.write(f"Acme Corp,acme@example.com,{future_date}\n")
        csv_path = f.name
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, MAIN_MODULE, '--clients', csv_path, '--days', '14',
             '--sender-email', 'sender@test.com', '--sender-password', 'secret'],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        assert 'Reminder: Your contract with Acme Corp renews in 14 days.' in result.stdout
    finally:
        os.unlink(csv_path)

def test_criterion_4_sends_email():
    spec = importlib.util.spec_from_file_location("main", MAIN_MODULE)
    main_mod = importlib.util.module_from_spec(spec)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, dir=PROJECT_ROOT) as f:
        f.write("client_name,client_email,renewal_date\n")
        future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        f.write(f"Client A,clientA@example.com,{future_date}\n")
        csv_path = f.name

    try:
        with patch('smtplib.SMTP') as mock_smtp:
            mock_instance = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_instance
            sys.argv = ['main.py', '--clients', csv_path, '--days', '5', '--send',
                        '--smtp-server', 'smtp.test.com', '--smtp-port', '587',
                        '--sender-email', 'sender@test.com', '--sender-password', 'secret']
            spec.loader.exec_module(main_mod)
            main_mod.main()
            mock_smtp.assert_called_once()
            mock_instance.sendmail.assert_called_once()
    finally:
        os.unlink(csv_path)

def test_criterion_5_logs_success_failure():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, dir=PROJECT_ROOT) as f:
        f.write("client_name,client_email,renewal_date\n")
        future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        f.write(f"Client A,clientA@example.com,{future_date}\n")
        csv_path = f.name
    
    log_path = os.path.join(PROJECT_ROOT, 'logs', 'renewal_log.txt')
    if os.path.exists(log_path):
        os.remove(log_path)
        
    import subprocess
    result = subprocess.run(
        [sys.executable, MAIN_MODULE, '--clients', csv_path, '--days', '10',
         '--sender-email', 'sender@test.com', '--sender-password', 'secret'],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    
    assert os.path.exists(log_path)
    with open(log_path, 'r') as lf:
        log_content = lf.read()
    assert '[DRY RUN]' in log_content or '[SUCCESS]' in log_content or '[FAIL]' in log_content
    
    os.unlink(csv_path)
    if os.path.exists(log_path):
        os.remove(log_path)
