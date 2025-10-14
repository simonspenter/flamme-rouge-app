# services/db.py
import os
import time
import pyodbc

# Resolve DATABASE_URL just like before
DATABASE_URL = (
    os.environ.get('SQLCONNSTR_SQLCONNSTR_DATABASE_URL') or
    os.environ.get('SQLCONNSTR_DATABASE_URL') or
    os.environ.get('ConnectionStrings:DATABASE_URL') or
    os.environ.get('DATABASE_URL')
)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

def get_db_connection(retries=3, delay=5):
    for attempt in range(1, retries + 1):
        try:
            print(f"Connecting with: {DATABASE_URL} (attempt {attempt})")
            return pyodbc.connect(DATABASE_URL)
        except pyodbc.Error as e:
            print(f"Database connection failed (attempt {attempt} of {retries}): {e}")
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All retry attempts failed.")
                raise
