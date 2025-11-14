import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_backend.settings')
django.setup()

from django.db import connection

def add_last_login_column():
    """Aggiungi la colonna last_login alla tabella users"""
    try:
        with connection.cursor() as cursor:
            # Verifica se la colonna esiste già
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'users'
                AND COLUMN_NAME = 'last_login'
            """)

            exists = cursor.fetchone()[0]

            if exists:
                print("✓ La colonna 'last_login' esiste già nella tabella 'users'")
            else:
                print("⏳ Aggiunta colonna 'last_login' alla tabella 'users'...")
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN last_login DATETIME NULL 
                    AFTER updated_at
                """)
                print("✓ Colonna 'last_login' aggiunta con successo!")

    except Exception as e:
        print(f"✗ Errore: {e}")
        sys.exit(1)

if __name__ == '__main__':
    add_last_login_column()
    print("\n✓✓✓ Database aggiornato! ✓✓✓")

