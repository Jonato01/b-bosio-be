# Booking Backend API Documentation

## Panoramica
Backend Django REST API per un'applicazione di prenotazioni di case. Il sistema gestisce utenti, alloggi, prenotazioni, periodi bloccati e audit delle modifiche.

## Tecnologie Utilizzate
- Django 5.2.8
- Django REST Framework 3.15.2
- JWT Authentication (djangorestframework-simplejwt)
- MySQL Database
- CORS Headers support

## Setup e Installazione

### 1. Clona il repository e installa le dipendenze

```bash
pip install -r requirements.txt
```

### 2. Configura il database

Copia il file `.env.example` in `.env` e configura le tue credenziali del database:

```env
DB_NAME=booking_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

### 3. Importa lo schema del database

Il database deve già esistere con le tabelle create secondo lo schema fornito.

### 4. Inizializza i ruoli

```bash
python init_roles.py
```

### 5. Avvia il server

```bash
python manage.py runserver
```

Il server sarà disponibile su `http://localhost:8000`

---

## Autenticazione

Il sistema utilizza JWT (JSON Web Tokens) per l'autenticazione.

### Login

**POST** `/api/auth/login/`

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Token

**POST** `/api/auth/refresh/`

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Verify Token

**POST** `/api/auth/verify/`

```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Utilizzo del Token

Includi il token di accesso nell'header di ogni richiesta protetta:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## API Endpoints

### Users

#### Registrazione Utente
**POST** `/api/users/`

```json
{
  "email": "nuovo@example.com",
  "password": "password123",
  "password_confirm": "password123",
  "display_name": "Mario Rossi"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "nuovo@example.com",
  "display_name": "Mario Rossi",
  "role": 1,
  "role_name": "user",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Profilo Utente Corrente
**GET** `/api/users/me/`

Richiede autenticazione.

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "display_name": "Mario Rossi",
  "role": 1,
  "role_name": "user",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Aggiorna Profilo
**PUT/PATCH** `/api/users/update_profile/`

```json
{
  "display_name": "Mario Rossi Aggiornato",
  "password": "nuova_password123"
}
```

#### Le Mie Prenotazioni
**GET** `/api/users/my_bookings/`

Ritorna tutte le prenotazioni dell'utente corrente.

#### Lista Utenti
**GET** `/api/users/`

Richiede autenticazione. Gli utenti normali vedono solo se stessi, gli admin vedono tutti.

---

### Roles

#### Lista Ruoli
**GET** `/api/roles/`

```json
[
  {
    "id": 1,
    "name": "user"
  },
  {
    "id": 2,
    "name": "admin"
  },
  {
    "id": 3,
    "name": "manager"
  }
]
```

---

### Accommodations (Alloggi)

#### Lista Alloggi
**GET** `/api/accommodations/`

```json
[
  {
    "id": 1,
    "slug": "villa-mare",
    "title": "Villa al Mare",
    "description": "Bellissima villa con vista mare",
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  }
]
```

#### Dettaglio Alloggio
**GET** `/api/accommodations/{slug}/`

**Esempio:** `/api/accommodations/villa-mare/`

#### Crea Alloggio
**POST** `/api/accommodations/`

Richiede permessi admin.

```json
{
  "slug": "appartamento-centro",
  "title": "Appartamento in Centro",
  "description": "Moderno appartamento nel cuore della città"
}
```

#### Aggiorna Alloggio
**PUT/PATCH** `/api/accommodations/{slug}/`

Richiede permessi admin.

#### Elimina Alloggio
**DELETE** `/api/accommodations/{slug}/`

Richiede permessi admin.

#### Verifica Disponibilità Alloggio
**GET** `/api/accommodations/{slug}/availability/?check_in=2024-03-01T14:00:00Z&check_out=2024-03-05T10:00:00Z`

```json
{
  "available": true,
  "accommodation": {
    "id": 1,
    "slug": "villa-mare",
    "title": "Villa al Mare",
    "description": "Bellissima villa con vista mare"
  },
  "conflicting_bookings": [],
  "blocked_periods": []
}
```

#### Prenotazioni dell'Alloggio
**GET** `/api/accommodations/{slug}/bookings/?status=confirmed`

Ritorna tutte le prenotazioni per l'alloggio specificato.

#### Periodi Bloccati dell'Alloggio
**GET** `/api/accommodations/{slug}/blocked_periods/`

Ritorna tutti i periodi bloccati per l'alloggio specificato.

---

### Bookings (Prenotazioni)

#### Lista Prenotazioni
**GET** `/api/bookings/`

**Query Parameters:**
- `status` - filtra per stato (pending, confirmed, cancelled, rejected)
- `accommodation` - filtra per ID alloggio
- `start_date` - filtra per data inizio
- `end_date` - filtra per data fine

**Esempio:** `/api/bookings/?status=confirmed&accommodation=1`

```json
{
  "count": 10,
  "next": "http://localhost:8000/api/bookings/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "accommodation": 1,
      "accommodation_title": "Villa al Mare",
      "user": 2,
      "user_email": "cliente@example.com",
      "check_in": "2024-03-01T14:00:00Z",
      "check_out": "2024-03-05T10:00:00Z",
      "num_guests": 4,
      "status": "confirmed",
      "notes": "Arrivo previsto per le 16:00",
      "created_at": "2024-02-15T10:00:00Z",
      "updated_at": "2024-02-16T12:00:00Z",
      "guests_details": [
        {
          "id": 1,
          "booking": 1,
          "full_name": "Giovanni Bianchi",
          "email": "giovanni@example.com",
          "phone": "+39 123 456 7890",
          "birth_date": "1985-05-15",
          "document_type": "Passaporto",
          "document_number": "AB123456",
          "notes": null
        }
      ]
    }
  ]
}
```

#### Crea Prenotazione
**POST** `/api/bookings/`

```json
{
  "accommodation": 1,
  "user": 2,
  "check_in": "2024-03-01T14:00:00Z",
  "check_out": "2024-03-05T10:00:00Z",
  "num_guests": 2,
  "notes": "Richiesta camera al primo piano",
  "guests_data": [
    {
      "full_name": "Mario Rossi",
      "email": "mario@example.com",
      "phone": "+39 123 456 7890",
      "birth_date": "1980-01-01",
      "document_type": "Carta d'Identità",
      "document_number": "AB1234567"
    },
    {
      "full_name": "Laura Rossi",
      "email": "laura@example.com",
      "phone": "+39 123 456 7891",
      "birth_date": "1982-05-15",
      "document_type": "Carta d'Identità",
      "document_number": "CD7654321"
    }
  ]
}
```

**Validazioni:**
- `check_out` deve essere dopo `check_in`
- Non devono esserci prenotazioni sovrapposte
- Il periodo non deve essere bloccato

#### Dettaglio Prenotazione
**GET** `/api/bookings/{id}/`

#### Aggiorna Prenotazione
**PUT/PATCH** `/api/bookings/{id}/`

#### Elimina Prenotazione
**DELETE** `/api/bookings/{id}/`

#### Conferma Prenotazione
**POST** `/api/bookings/{id}/confirm/`

Cambia lo stato da "pending" a "confirmed". Crea un log di audit.

```json
{
  "id": 1,
  "status": "confirmed",
  ...
}
```

#### Annulla Prenotazione
**POST** `/api/bookings/{id}/cancel/`

Cambia lo stato a "cancelled". Crea un log di audit.

#### Rifiuta Prenotazione
**POST** `/api/bookings/{id}/reject/`

Cambia lo stato da "pending" a "rejected". Crea un log di audit.

#### Ospiti della Prenotazione
**GET** `/api/bookings/{id}/guests/`

Ritorna tutti gli ospiti associati alla prenotazione.

#### Aggiungi Ospite
**POST** `/api/bookings/{id}/add_guest/`

```json
{
  "full_name": "Giuseppe Verdi",
  "email": "giuseppe@example.com",
  "phone": "+39 123 456 7892",
  "birth_date": "1990-08-20",
  "document_type": "Passaporto",
  "document_number": "XY987654"
}
```

#### Log di Audit della Prenotazione
**GET** `/api/bookings/{id}/audit_log/`

Ritorna la cronologia delle modifiche della prenotazione.

```json
[
  {
    "id": 3,
    "booking": 1,
    "action": "confirmed",
    "actor_user": 1,
    "actor_user_email": "admin@example.com",
    "data_json": {
      "previous_status": "pending",
      "new_status": "confirmed"
    },
    "created_at": "2024-02-16T12:00:00Z"
  },
  {
    "id": 1,
    "booking": 1,
    "action": "created",
    "actor_user": 2,
    "actor_user_email": "cliente@example.com",
    "data_json": {
      "status": "pending",
      "accommodation_id": 1
    },
    "created_at": "2024-02-15T10:00:00Z"
  }
]
```

---

### Booking Guests (Ospiti)

#### Lista Ospiti
**GET** `/api/booking-guests/?booking=1`

#### Crea Ospite
**POST** `/api/booking-guests/`

```json
{
  "booking": 1,
  "full_name": "Anna Verdi",
  "email": "anna@example.com",
  "phone": "+39 123 456 7893",
  "birth_date": "1995-03-10",
  "document_type": "Carta d'Identità",
  "document_number": "EF1122334",
  "notes": "Vegetariana"
}
```

#### Dettaglio Ospite
**GET** `/api/booking-guests/{id}/`

#### Aggiorna Ospite
**PUT/PATCH** `/api/booking-guests/{id}/`

#### Elimina Ospite
**DELETE** `/api/booking-guests/{id}/`

---

### Blocked Periods (Periodi Bloccati)

#### Lista Periodi Bloccati
**GET** `/api/blocked-periods/?accommodation=1`

```json
[
  {
    "id": 1,
    "accommodation": 1,
    "accommodation_title": "Villa al Mare",
    "start_date": "2024-04-01T00:00:00Z",
    "end_date": "2024-04-15T23:59:59Z",
    "reason": "Manutenzione ordinaria",
    "created_by": 1,
    "created_by_email": "admin@example.com",
    "created_at": "2024-03-01T10:00:00Z"
  }
]
```

#### Crea Periodo Bloccato
**POST** `/api/blocked-periods/`

```json
{
  "accommodation": 1,
  "start_date": "2024-04-01T00:00:00Z",
  "end_date": "2024-04-15T23:59:59Z",
  "reason": "Manutenzione straordinaria"
}
```

Il campo `created_by` viene automaticamente impostato all'utente corrente.

#### Aggiorna Periodo Bloccato
**PUT/PATCH** `/api/blocked-periods/{id}/`

#### Elimina Periodo Bloccato
**DELETE** `/api/blocked-periods/{id}/`

---

### Blocked Weekdays (Giorni della Settimana Bloccati)

Permette di bloccare specifici giorni della settimana (es. tutti i lunedì).

#### Lista Giorni Bloccati
**GET** `/api/blocked-weekdays/?accommodation=1`

```json
[
  {
    "id": 1,
    "accommodation": 1,
    "accommodation_title": "Villa al Mare",
    "weekday": 0,
    "start_time": null,
    "end_time": null,
    "reason": "Chiuso il lunedì",
    "created_by": 1,
    "created_by_email": "admin@example.com",
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

**Valori weekday:**
- 0 = Lunedì
- 1 = Martedì
- 2 = Mercoledì
- 3 = Giovedì
- 4 = Venerdì
- 5 = Sabato
- 6 = Domenica

#### Crea Giorno Bloccato
**POST** `/api/blocked-weekdays/`

```json
{
  "accommodation": 1,
  "weekday": 0,
  "start_time": "00:00:00",
  "end_time": "23:59:59",
  "reason": "Chiuso ogni lunedì"
}
```

#### Aggiorna Giorno Bloccato
**PUT/PATCH** `/api/blocked-weekdays/{id}/`

#### Elimina Giorno Bloccato
**DELETE** `/api/blocked-weekdays/{id}/`

---

### Booking Audit (Log di Audit)

#### Lista Audit Log
**GET** `/api/booking-audit/?booking=1`

Questo endpoint è in sola lettura.

```json
[
  {
    "id": 1,
    "booking": 1,
    "action": "created",
    "actor_user": 2,
    "actor_user_email": "cliente@example.com",
    "data_json": {
      "status": "pending"
    },
    "created_at": "2024-02-15T10:00:00Z"
  }
]
```

---

### Utility Endpoints

#### Verifica Disponibilità Generica
**POST** `/api/check-availability/`

```json
{
  "accommodation_id": 1,
  "check_in": "2024-03-01T14:00:00Z",
  "check_out": "2024-03-05T10:00:00Z"
}
```

**Response:**
```json
{
  "available": true,
  "accommodation": {
    "id": 1,
    "slug": "villa-mare",
    "title": "Villa al Mare",
    "description": "Bellissima villa con vista mare"
  },
  "check_in": "2024-03-01T14:00:00Z",
  "check_out": "2024-03-05T10:00:00Z",
  "conflicting_bookings_count": 0,
  "blocked_periods_count": 0
}
```

#### Statistiche Prenotazioni
**GET** `/api/statistics/`

Non richiede autenticazione.

```json
{
  "total_bookings": 156,
  "pending": 12,
  "confirmed": 98,
  "cancelled": 32,
  "rejected": 14,
  "total_accommodations": 8,
  "total_users": 245
}
```

---

## Esempi di Utilizzo con cURL

### Registrazione e Login

```bash
# Registrazione
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "display_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Creare una Prenotazione

```bash
# Salva il token in una variabile
TOKEN="your_access_token_here"

# Crea prenotazione
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accommodation": 1,
    "check_in": "2024-03-01T14:00:00Z",
    "check_out": "2024-03-05T10:00:00Z",
    "num_guests": 2,
    "notes": "Test booking",
    "guests_data": [
      {
        "full_name": "Mario Rossi",
        "email": "mario@example.com",
        "phone": "+39 123 456 7890"
      }
    ]
  }'
```

### Confermare una Prenotazione

```bash
curl -X POST http://localhost:8000/api/bookings/1/confirm/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Verificare Disponibilità

```bash
curl -X GET "http://localhost:8000/api/accommodations/villa-mare/availability/?check_in=2024-03-01T14:00:00Z&check_out=2024-03-05T10:00:00Z"
```

---

## Esempi con JavaScript/Fetch

### Login e Salvataggio Token

```javascript
// Login
async function login(email, password) {
  const response = await fetch('http://localhost:8000/api/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  const data = await response.json();
  
  // Salva i token
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  
  return data;
}

// Uso
login('test@example.com', 'password123');
```

### Richiesta con Autenticazione

```javascript
async function getMyBookings() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/users/my_bookings/', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  
  return await response.json();
}
```

### Creare una Prenotazione

```javascript
async function createBooking(bookingData) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/bookings/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(bookingData),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(JSON.stringify(error));
  }
  
  return await response.json();
}

// Uso
const bookingData = {
  accommodation: 1,
  check_in: '2024-03-01T14:00:00Z',
  check_out: '2024-03-05T10:00:00Z',
  num_guests: 2,
  notes: 'Arrivo previsto alle 16:00',
  guests_data: [
    {
      full_name: 'Mario Rossi',
      email: 'mario@example.com',
      phone: '+39 123 456 7890',
      birth_date: '1980-01-01',
      document_type: 'Carta d\'Identità',
      document_number: 'AB1234567'
    }
  ]
};

createBooking(bookingData)
  .then(data => console.log('Prenotazione creata:', data))
  .catch(error => console.error('Errore:', error));
```

### Refresh del Token

```javascript
async function refreshToken() {
  const refresh = localStorage.getItem('refresh_token');
  
  const response = await fetch('http://localhost:8000/api/auth/refresh/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh }),
  });
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  
  return data;
}
```

---

## Codici di Stato HTTP

- `200 OK` - Richiesta riuscita
- `201 Created` - Risorsa creata con successo
- `204 No Content` - Richiesta riuscita senza contenuto di risposta
- `400 Bad Request` - Dati non validi
- `401 Unauthorized` - Autenticazione richiesta o fallita
- `403 Forbidden` - Non hai i permessi necessari
- `404 Not Found` - Risorsa non trovata
- `500 Internal Server Error` - Errore del server

---

## Permessi

- **AllowAny**: Accessibile senza autenticazione
- **IsAuthenticated**: Richiede autenticazione
- **IsAdminOrReadOnly**: Lettura per tutti, scrittura solo per admin
- **IsOwnerOrAdmin**: Solo il proprietario o un admin può modificare

---

## Paginazione

Le liste di risorse sono paginate con 20 elementi per pagina. La risposta include:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/bookings/?page=2",
  "previous": null,
  "results": [...]
}
```

Per navigare: `/api/bookings/?page=2`

---

## Note Importanti

1. **Timezone**: Il server usa il fuso orario `Europe/Rome`
2. **Date Format**: Usa il formato ISO 8601 (es. `2024-03-01T14:00:00Z`)
3. **Validazioni**: Le prenotazioni sovrapposte vengono automaticamente rifiutate
4. **Audit Log**: Tutte le modifiche alle prenotazioni vengono registrate
5. **CORS**: Configurato per accettare richieste da localhost:3000 e localhost:8080

---

## Sviluppo Futuro

Possibili miglioramenti:
- Sistema di notifiche email
- Upload di immagini per gli alloggi
- Sistema di recensioni
- Pagamenti integrati
- API per calendario iCal
- Esportazione report in PDF
- Sistema di messaggistica tra host e guest

---

## Supporto

Per problemi o domande, contatta il team di sviluppo.

## Licenza

Proprietario: B&Bosio

