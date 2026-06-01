import os
import sys
import unittest
import io
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import tempfile
import csv

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.main import main, parse_args, log_message, ensure_dirs
from src.client_manager import read_clients
from src.email_sender import format_renewal_email, send_email

class TestRenewalRocket(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.temp_dir, "test_clients.csv")
        with open(self.csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["client_name", "client_email", "renewal_date"])
            today = datetime.now().date()
            writer.writerow(["Test Client", "test@example.com", (today + timedelta(days=10)).isoformat()])
            writer.writerow(["Future Client", "future@example.com", (today + timedelta(days=30)).isoformat()])
        
        self.smtp_config = {
            "server": "smtp.test.com",
            "port": 587,
            "sender_email": "sender@test.com",
            "sender_password": "password",
            "days": 14
        }

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if os.path.exists("logs/renewal_log.txt"):
            os.remove("logs/renewal_log.txt")

    def test_criterion_1_cli_args(self):
        with patch("sys.argv", ["main.py", "--clients", self.csv_path, "--days", "14", "--send", "--smtp-server", "smtp.test.com", "--sender-email", "sender@test.com", "--sender-password", "password"]):
            args = parse_args()
            self.assertEqual(args.clients, self.csv_path)
            self.assertEqual(args.days, 14)
            self.assertTrue(args.send)

    def test_criterion_2_read_and_filter_clients(self):
        clients = read_clients(self.csv_path, 14)
        self.assertEqual(len(clients), 1)
        self.assertEqual(clients[0]['name'], "Test Client")

    def test_criterion_3_format_email(self):
        client = {"name": "Test Client", "email": "test@example.com", "renewal_date": "2023-12-31"}
        subject, body = format_renewal_email(client, 14)
        self.assertIn("Test Client", subject)
        self.assertIn("14 days", subject)
        self.assertIn("Test Client", body)

    def test_criterion_4_send_email_mock(self):
        client = {"name": "Test Client", "email": "test@example.com", "renewal_date": "2023-12-31"}
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            result = send_email(client, self.smtp_config)
            self.assertTrue(result)
            mock_server.sendmail.assert_called_once()

    def test_criterion_5_logging(self):
        log_message("Test log message")
        self.assertTrue(os.path.exists("logs/renewal_log.txt"))
        with open("logs/renewal_log.txt", "r") as f:
            content = f.read()
            self.assertIn("Test log message", content)

    def test_edge_case_duplicate_emails(self):
        with open(self.csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["client_name", "client_email", "renewal_date"])
            today = datetime.now().date()
            writer.writerow(["Client 1", "dup@example.com", (today + timedelta(days=10)).isoformat()])
            writer.writerow(["Client 2", "dup@example.com", (today + timedelta(days=12)).isoformat()])
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            clients = read_clients(self.csv_path, 14)
            self.assertEqual(len(clients), 1)
            self.assertIn("Duplicate email", mock_stdout.getvalue())

    def test_edge_case_past_dates(self):
        with open(self.csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["client_name", "client_email", "renewal_date"])
            today = datetime.now().date()
            writer.writerow(["Past Client", "past@example.com", (today - timedelta(days=5)).isoformat()])
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            clients = read_clients(self.csv_path, 14)
            self.assertEqual(len(clients), 0)
            self.assertIn("Past date", mock_stdout.getvalue())

    def test_edge_case_csv_error(self):
        bad_csv = os.path.join(self.temp_dir, "bad.csv")
        with open(bad_csv, "w", newline="") as f:
            f.write("name,email\n")
        with self.assertRaises(ValueError):
            read_clients(bad_csv, 14)

if __name__ == '__main__':
    unittest.main()
