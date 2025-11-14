import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_backend.settings')
django.setup()

from django.db import connection

def add_missing_columns():
    """Aggiungi le colonne mancanti alla tabella users"""
    try:
        with connection.cursor() as cursor:
            # Verifica e aggiungi is_active
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'users'
                AND COLUMN_NAME = 'is_active'
            """)

            if cursor.fetchone()[0] == 0:
                print("⏳ Aggiunta colonna 'is_active'...")
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN is_active TINYINT(1) DEFAULT 1 NOT NULL
                    AFTER last_login
                """)
                print("✓ Colonna 'is_active' aggiunta!")
            else:
                print("✓ Colonna 'is_active' già presente")

            # Verifica e aggiungi is_staff
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'users'
                AND COLUMN_NAME = 'is_staff'
            """)

            if cursor.fetchone()[0] == 0:
                print("⏳ Aggiunta colonna 'is_staff'...")
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN is_staff TINYINT(1) DEFAULT 0 NOT NULL
                    AFTER is_active
                """)
                print("✓ Colonna 'is_staff' aggiunta!")
            else:
                print("✓ Colonna 'is_staff' già presente")

            # Verifica e aggiungi is_superuser
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'users'
                AND COLUMN_NAME = 'is_superuser'
            """)

            if cursor.fetchone()[0] == 0:
                print("⏳ Aggiunta colonna 'is_superuser'...")
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN is_superuser TINYINT(1) DEFAULT 0 NOT NULL
                    AFTER is_staff
                """)
                print("✓ Colonna 'is_superuser' aggiunta!")
            else:
                print("✓ Colonna 'is_superuser' già presente")

    except Exception as e:
        print(f"✗ Errore: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    add_missing_columns()
    print("\n✓✓✓ Database aggiornato con successo! ✓✓✓")
    print("\nPuoi ora riavviare il server Django.")

