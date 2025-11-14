import os
import sys
from pathlib import Path
# Ensure project root is on sys.path so `booking_backend` can be imported
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_backend.settings')
django.setup()
from django.db import connection

def print_columns(table):
    print('\n--- Columns for', table, '---')
    with connection.cursor() as cursor:
        cursor.execute("SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, EXTRA FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s", [table])
        rows = cursor.fetchall()
        if not rows:
            print('Table not found or no columns')
            return
        for r in rows:
            print(r)

def show_create(table):
    print('\n--- SHOW CREATE TABLE', table, '---')
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"SHOW CREATE TABLE `{table}`")
            row = cursor.fetchone()
            if row:
                print(row[1])
        except Exception as e:
            print('Error:', e)

if __name__ == '__main__':
    for t in ['users', 'django_admin_log']:
        print_columns(t)
        show_create(t)
