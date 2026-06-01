import csv
from datetime import datetime, timedelta

def read_clients(file_path, days):
    clients = []
    seen_emails = set()
    
    try:
        with open(file_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            required_columns = {'client_name', 'client_email', 'renewal_date'}
            if not required_columns.issubset(set(reader.fieldnames or [])):
                raise ValueError(f"CSV missing required columns: {required_columns - set(reader.fieldnames or [])}")
            
            today = datetime.now().date()
            cutoff_date = today + timedelta(days=days)
            
            for row in reader:
                try:
                    renewal_date = datetime.strptime(row['renewal_date'], '%Y-%m-%d').date()
                except ValueError:
                    print(f"Warning: Invalid date format for {row.get('client_name', 'Unknown')}, skipping.")
                    continue
                
                if renewal_date < today:
                    print(f"Warning: Past date for {row['client_name']}, skipping.")
                    continue
                
                if renewal_date <= cutoff_date:
                    email = row['client_email']
                    if email in seen_emails:
                        print(f"Warning: Duplicate email {email} for {row['client_name']}, skipping.")
                        continue
                    
                    seen_emails.add(email)
                    clients.append({
                        'name': row['client_name'],
                        'email': email,
                        'renewal_date': renewal_date.isoformat()
                    })
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading CSV: {e}")
        
    return clients
