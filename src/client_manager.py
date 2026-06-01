import csv
from datetime import datetime, timedelta

def read_clients(csv_path):
    clients = []
    seen_emails = set()
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        if not all(col in reader.fieldnames for col in ['client_name', 'client_email', 'renewal_date']):
            raise ValueError("CSV missing required columns: client_name, client_email, renewal_date")
            
        for row in reader:
            email = row['client_email'].strip()
            if email in seen_emails:
                print(f"Warning: Duplicate email found: {email}")
                continue
            seen_emails.add(email)
            
            try:
                renewal_date = datetime.strptime(row['renewal_date'], '%Y-%m-%d')
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                if renewal_date < today:
                    print(f"Warning: Skipping past date for {row['client_name']}")
                    continue
                clients.append({
                    'client_name': row['client_name'],
                    'client_email': email,
                    'renewal_date': renewal_date
                })
            except ValueError:
                print(f"Warning: Invalid date format for {row['client_name']}")
                continue
    return clients

def filter_expiring_clients(clients, days):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    target_date = today + timedelta(days=days)
    return [c for c in clients if today <= c['renewal_date'] <= target_date]
