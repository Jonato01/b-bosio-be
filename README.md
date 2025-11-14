# Booking Backend - Sistema di Prenotazioni

Backend Django REST API per gestione prenotazioni di case vacanze.

## 🚀 Quick Start

### Prerequisiti
- Python 3.8+
- MySQL 8.0+
- pip

### Installazione

1. **Clona il repository**
```bash
cd "C:\Users\Renato\PycharmProjects\b&bosio"
```

2. **Crea e attiva l'ambiente virtuale**
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. **Installa le dipendenze**
```bash
pip install -r requirements.txt
```

4. **Configura il database**

Crea il database MySQL e importa lo schema fornito:
```sql
CREATE DATABASE booking_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Poi esegui lo script SQL con tutte le tabelle.

5. **Configura le variabili d'ambiente**

Copia `.env.example` in `.env` e modifica i valori:
```bash
copy .env.example .env
```

Modifica il file `.env` con le tue credenziali:
```env
DB_NAME=booking_db
DB_USER=root
DB_PASSWORD=tua_password
DB_HOST=localhost
DB_PORT=3306
```

6. **Esegui le migrazioni**
```bash
python manage.py makemigrations
python manage.py migrate --fake-initial
```

7. **Inizializza i ruoli** (già fatto automaticamente)
```bash
python test_db.py
```

Questo verifica la connessione e mostra i ruoli creati: `user`, `admin`, `manager`.

8. **Avvia il server**
```bash
python manage.py runserver
```

Oppure usa lo script automatico:
```bash
start_server.bat
```

Il server sarà disponibile su `http://localhost:8000`

### Creare un Superuser (Opzionale)

```bash
python manage.py createsuperuser
```

Accedi all'admin Django su `http://localhost:8000/admin/`

## 📚 Documentazione API

Consulta la documentazione completa in [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

### Endpoints Principali

- **Auth**: `/api/auth/login/`, `/api/auth/refresh/`, `/api/auth/verify/`
- **Users**: `/api/users/`, `/api/users/me/`, `/api/users/my_bookings/`
- **Accommodations**: `/api/accommodations/`
- **Bookings**: `/api/bookings/`
- **Statistics**: `/api/statistics/`
- **Availability Check**: `/api/check-availability/`

## 🔧 Struttura del Progetto

```
b&bosio/
├── booking_backend/          # Configurazione principale Django
│   ├── settings.py          # Impostazioni del progetto
│   ├── urls.py              # URL routing principale
│   └── wsgi.py              # WSGI configuration
├── bookings/                 # App principale
│   ├── models.py            # Modelli del database
│   ├── serializers.py       # Serializers per API
│   ├── views.py             # Views e ViewSets
│   ├── urls.py              # URL routing dell'app
│   ├── permissions.py       # Permessi personalizzati
│   └── admin.py             # Configurazione admin
├── .env                      # Variabili d'ambiente (non in git)
├── .env.example             # Template variabili d'ambiente
├── requirements.txt         # Dipendenze Python
├── init_roles.py            # Script inizializzazione ruoli
├── manage.py                # Django management script
├── API_DOCUMENTATION.md     # Documentazione completa API
└── README.md                # Questo file
```

## 🗄️ Schema Database

Il database include le seguenti tabelle:

- **users** - Utenti del sistema
- **roles** - Ruoli utente (user, admin, manager)
- **accommodations** - Alloggi disponibili
- **bookings** - Prenotazioni
- **booking_guests** - Ospiti delle prenotazioni
- **blocked_periods** - Periodi bloccati per manutenzione
- **blocked_weekdays** - Giorni della settimana bloccati
- **booking_audit** - Log delle modifiche alle prenotazioni

## 🔐 Autenticazione

Il sistema usa JWT (JSON Web Tokens) per l'autenticazione.

### Esempio Login:

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Utilizzo Token:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/users/me/
```

## 🧪 Testing

### Test Manuale con cURL

```bash
# Verifica disponibilità
curl "http://localhost:8000/api/check-availability/" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "accommodation_id": 1,
    "check_in": "2024-03-01T14:00:00Z",
    "check_out": "2024-03-05T10:00:00Z"
  }'

# Statistiche
curl http://localhost:8000/api/statistics/
```

## 🔥 Features Principali

- ✅ Autenticazione JWT con refresh token
- ✅ Gestione completa prenotazioni (CRUD)
- ✅ Sistema di stati prenotazione (pending, confirmed, cancelled, rejected)
- ✅ Verifica automatica disponibilità
- ✅ Gestione ospiti per prenotazione
- ✅ Periodi bloccati per manutenzione
- ✅ Blocco per giorni della settimana
- ✅ Audit log completo delle modifiche
- ✅ Permessi granulari (owner, admin)
- ✅ Paginazione automatica
- ✅ CORS configurato per frontend
- ✅ Admin Django completo

## 🛡️ Sicurezza

- Password hashate con algoritmo Django (PBKDF2)
- JWT con scadenza configurabile
- CORS configurato per domini specifici
- Protezione CSRF
- SQL injection prevention tramite ORM Django
- Validazione input su tutti gli endpoint

## 📦 Dipendenze Principali

- **Django 5.2.8** - Web framework
- **Django REST Framework 3.15.2** - API REST
- **djangorestframework-simplejwt 5.4.0** - JWT authentication
- **django-cors-headers 4.7.0** - CORS support
- **mysqlclient 2.2.7** - MySQL connector
- **python-dotenv 1.0.1** - Environment variables

## 🚀 Deploy in Produzione

### Checklist Pre-Deploy:

1. [ ] Cambia `DEBUG = False` in settings.py
2. [ ] Imposta `SECRET_KEY` sicura in .env
3. [ ] Configura `ALLOWED_HOSTS` in settings.py
4. [ ] Usa un database server MySQL dedicato
5. [ ] Configura HTTPS
6. [ ] Imposta CORS per il dominio di produzione
7. [ ] Configura il server web (Nginx/Apache)
8. [ ] Usa un process manager (Gunicorn/uWSGI)
9. [ ] Configura i log
10. [ ] Backup automatici del database

### Esempio configurazione Gunicorn:

```bash
pip install gunicorn
gunicorn booking_backend.wsgi:application --bind 0.0.0.0:8000
```

## 🤝 Contribuire

1. Fork del progetto
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📝 Licenza

Progetto proprietario - B&Bosio

## 👥 Team

Sviluppato per B&Bosio

## 📞 Supporto

Per problemi o domande:
- Apri un issue su GitHub
- Contatta il team di sviluppo

---

**Made with ❤️ using Django**

