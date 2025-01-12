import os

# Get absolute path to the db directory
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db')
DB_PATH = os.path.join(DB_DIR, 'trans.sqlite3')

# Ensure db directory exists
os.makedirs(DB_DIR, exist_ok=True)