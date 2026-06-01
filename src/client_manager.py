import csv
from datetime import datetime, timedelta

def read_clients(csv_path, days):
    clients = []
    with open(csv_path, mode='r') as f:
        reader = csv.DictReader(f)
        required_cols = {'client_name', 'client_email', 'renewal_date'}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            raise ValueError("Missing required columns in CSV")
        
        today = datetime.now().date()
        cutoff = today + timedelta(days=days)
        
        for row in reader:
            try:
                renewal_date = datetime.strptime(row['renewal_date'], '%Y-%m-%d').date()
                if today <= renewal_date <= cutoff:
                    clients.append({
                        'name': row['client_name'],
                        'email': row['client_email'],
                        'renewal_date': renewal_date
                    })
            except ValueError:
                continue
    return clients
