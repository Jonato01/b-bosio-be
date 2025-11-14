@echo off
echo ========================================
echo    AVVIO SERVER DJANGO - B^&BOSIO
echo ========================================
echo.

echo [1/3] Verifico connessione database...
python test_db.py
if errorlevel 1 (
    echo.
    echo [ERRORE] Problema con il database!
    echo Verifica le credenziali in .env
    pause
    exit /b 1
)

echo.
echo [2/3] Verifico migrazioni...
python manage.py showmigrations --plan | find "[X]" > nul
if errorlevel 1 (
    echo.
    echo [ATTENZIONE] Alcune migrazioni non sono applicate
    echo Eseguo: python manage.py migrate
    python manage.py migrate
)

echo.
echo [3/3] Avvio server Django...
echo.
echo ========================================
echo   SERVER PRONTO!
echo ========================================
echo.
echo Accedi a: http://localhost:8000
echo Admin: http://localhost:8000/admin/
echo API: http://localhost:8000/api/
echo.
echo Premi CTRL+C per fermare il server
echo ========================================
echo.

python manage.py runserver

