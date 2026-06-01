import csv
from datetime import datetime, timedelta
from pathlib import Path


def read_clients(csv_path: str) -> list[dict]:
    """Read clients from CSV file. Returns list of client dicts."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    clients = []
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        
        # Validate required columns
        required_cols = {'name', 'email', 'contract_end_date'}
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or has no headers")
        
        missing = required_cols - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        for row in reader:
            # Skip rows with missing critical fields
            if not row.get('name') or not row.get('email') or not row.get('contract_end_date'):
                continue
            clients.append(row)
    
    return clients


def filter_expiring_clients(clients: list[dict], days: int) -> list[dict]:
    """Filter clients whose contracts expire within the given days."""
    now = datetime.now()
    threshold = now + timedelta(days=days)
    
    expiring = []
    for client in clients:
        try:
            end_date = datetime.strptime(client['contract_end_date'], '%Y-%m-%d')
            # Skip past dates
            if end_date < now:
                continue
            # Include if expiring within threshold
            if end_date <= threshold:
                expiring.append({
                    'name': client['name'],
                    'email': client['email'],
                    'contract_end_date': client['contract_end_date'],
                    'days_until_expiry': (end_date - now).days
                })
        except (ValueError, KeyError):
            continue
    
    return expiring
