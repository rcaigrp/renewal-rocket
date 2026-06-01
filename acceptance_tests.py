import unittest
import os
import sys
import csv
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from client_manager import read_clients, filter_expiring_clients
from email_sender import format_email, send_email

class TestClientManager(unittest.TestCase):
    def test_read_clients_success(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['client_name', 'client_email', 'renewal_date'])
            writer.writerow(['Alice', 'alice@example.com', (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')])
            temp_path = f.name
        clients = read_clients(temp_path)
        self.assertEqual(len(clients), 1)
        self.assertEqual(clients[0]['client_name'], 'Alice')
        os.unlink(temp_path)

    def test_read_clients_duplicate_email(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['client_name', 'client_email', 'renewal_date'])
            writer.writerow(['Alice', 'alice@example.com', (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')])
            writer.writerow(['Bob', 'alice@example.com', (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')])
            temp_path = f.name
        clients = read_clients(temp_path)
        self.assertEqual(len(clients), 1)
        os.unlink(temp_path)

    def test_read_clients_missing_columns(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name, email, date\n")
            f.write("Alice, alice@example.com, 2023-01-01\n")
            temp_path = f.name
        with self.assertRaises(ValueError):
            read_clients(temp_path)
        os.unlink(temp_path)

    def test_filter_expiring_clients(self):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        clients = [
            {'client_name': 'Alice', 'client_email': 'alice@example.com', 'renewal_date': today + timedelta(days=10)},
            {'client_name': 'Bob', 'client_email': 'bob@example.com', 'renewal_date': today + timedelta(days=20)},
            {'client_name': 'Charlie', 'client_email': 'charlie@example.com', 'renewal_date': today - timedelta(days=5)},
        ]
        expiring = filter_expiring_clients(clients, 14)
        self.assertEqual(len(expiring), 1)
        self.assertEqual(expiring[0]['client_name'], 'Alice')

class TestEmailSender(unittest.TestCase):
    def test_format_email(self):
        client = {'client_name': 'Alice', 'client_email': 'alice@example.com'}
        msg = format_email(client, 14)
        self.assertIn('Alice', str(msg['Subject']))
        self.assertIn('alice@example.com', str(msg['To']))

    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        client = {'client_name': 'Alice', 'client_email': 'alice@example.com'}
        msg = format_email(client, 14)
        result = send_email(msg, 'smtp.example.com', 587, 'sender@example.com', 'password', 'alice@example.com')
        self.assertTrue(result)
        mock_server.send_message.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp):
        mock_smtp.side_effect = Exception("Connection failed")
        client = {'client_name': 'Alice', 'client_email': 'alice@example.com'}
        msg = format_email(client, 14)
        result = send_email(msg, 'smtp.example.com', 587, 'sender@example.com', 'password', 'alice@example.com')
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
