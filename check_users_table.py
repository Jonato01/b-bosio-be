import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_backend.settings')
django.setup()

from django.db import connection

def check_users_columns():
    """Verifica le colonne nella tabella users"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'users'
            ORDER BY ORDINAL_POSITION
        """)

        columns = cursor.fetchall()

        print("📋 Colonne nella tabella 'users':\n")
        for col in columns:
            print(f"  - {col[0]:20} | {col[1]:15} | NULL: {col[2]:3} | Default: {col[3]}")

        print(f"\n✓ Totale: {len(columns)} colonne")

        # Colonne richieste da Django
        required = ['id', 'email', 'password_hash', 'is_active', 'is_staff', 'is_superuser', 'last_login']
        existing = [col[0] for col in columns]

        print("\n🔍 Verifica colonne richieste:")
        for req in required:
            if req in existing:
                print(f"  ✓ {req}")
            else:
                print(f"  ✗ {req} - MANCANTE!")

        missing = [r for r in required if r not in existing]
        if missing:
            print(f"\n⚠️  Colonne mancanti: {', '.join(missing)}")
            print("\nSQL per aggiungere le colonne mancanti:")

            if 'is_superuser' in missing:
                print("ALTER TABLE users ADD COLUMN is_superuser TINYINT(1) DEFAULT 0 NOT NULL;")
            if 'last_login' in missing:
                print("ALTER TABLE users ADD COLUMN last_login DATETIME NULL;")

if __name__ == '__main__':
    check_users_columns()

