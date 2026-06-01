import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile
import csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.main import main
from io import StringIO

class TestRenewalRocket(unittest.TestCase):

    def setUp(self):
        self.temp_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        writer = csv.writer(self.temp_csv)
        writer.writerow(['client_name', 'client_email', 'renewal_date'])
        writer.writerow(['Acme Corp', 'acme@example.com', '2030-01-01'])
        self.temp_csv.close()
        self.temp_log_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_log_dir)

    def tearDown(self):
        os.remove(self.temp_csv.name)
        os.rmdir(self.temp_log_dir)
        os.chdir(self.original_cwd)

    @patch('src.email_sender.smtplib')
    @patch('src.main.client_manager')
    def test_criterion_1_2_3(self, mock_client_manager, mock_smtplib):
        mock_client_manager.read_clients.return_value = [{
            'client_name': 'Acme Corp',
            'client_email': 'acme@example.com',
            'renewal_date': '2030-01-01',
            'days_until': 14
        }]

        mock_server = MagicMock()
        mock_smtplib.SMTP.return_value.__enter__.return_value = mock_server

        sys.argv = ['main.py', '--clients', self.temp_csv.name, '--days', '14', '--send', 
                    '--smtp-server', 'smtp.test.com', '--smtp-port', '587',
                    '--sender-email', 'test@test.com', '--sender-password', 'pass']
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            self.assertIn('Acme Corp', output)
            self.assertIn('SENT', output)

    @patch('src.email_sender.smtplib')
    @patch('src.main.client_manager')
    def test_criterion_4(self, mock_client_manager, mock_smtplib):
        mock_client_manager.read_clients.return_value = [{
            'client_name': 'Acme Corp',
            'client_email': 'acme@example.com',
            'renewal_date': '2030-01-01',
            'days_until': 14
        }]

        mock_server = MagicMock()
        mock_smtplib.SMTP.return_value.__enter__.return_value = mock_server

        sys.argv = ['main.py', '--clients', self.temp_csv.name, '--days', '14', '--send', 
                    '--smtp-server', 'smtp.test.com', '--smtp-port', '587',
                    '--sender-email', 'test@test.com', '--sender-password', 'pass']
        
        main()
        mock_server.sendmail.assert_called_once()
        call_args = mock_server.sendmail.call_args
        self.assertEqual(call_args[0][1], 'acme@example.com')

    @patch('src.email_sender.smtplib')
    @patch('src.main.client_manager')
    def test_criterion_5(self, mock_client_manager, mock_smtplib):
        mock_client_manager.read_clients.return_value = [{
            'client_name': 'Acme Corp',
            'client_email': 'acme@example.com',
            'renewal_date': '2030-01-01',
            'days_until': 14
        }]

        mock_server = MagicMock()
        mock_smtplib.SMTP.return_value.__enter__.return_value = mock_server

        sys.argv = ['main.py', '--clients', self.temp_csv.name, '--days', '14', '--send', 
                    '--smtp-server', 'smtp.test.com', '--smtp-port', '587',
                    '--sender-email', 'test@test.com', '--sender-password', 'pass']
        
        main()
        
        log_file = os.path.join(self.temp_log_dir, 'logs', 'renewal_log.txt')
        self.assertTrue(os.path.exists(log_file))
        with open(log_file, 'r') as f:
            content = f.read()
            self.assertIn('Acme Corp', content)
            self.assertIn('SENT', content)

if __name__ == '__main__':
    unittest.main()
