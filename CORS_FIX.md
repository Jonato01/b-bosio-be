# 🔧 RISOLUZIONE ERRORE CORS

## ✅ Problema Risolto

**Errore**: "Il corpo della risposta non è disponibile per gli script. Motivo: CORS Missing Allow Origin"

**Causa**: Il backend Django non aveva configurato correttamente i CORS headers per permettere richieste dal frontend.

## 🛠️ Modifiche Applicate

### 1. Configurazione CORS Aggiornata (`settings.py`)

```python
# CORS settings - Permetti tutte le origini in sviluppo
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Headers permessi
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Metodi HTTP permessi
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
```

### 2. ALLOWED_HOSTS Aggiornato

```python
ALLOWED_HOSTS = ['*']  # Permetti tutti gli hosts in sviluppo
```

### 3. Middleware CORS già configurato correttamente

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # ✅ Posizione corretta
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

---

## 🚀 Riavvia il Server

**IMPORTANTE**: Devi riavviare il server Django per applicare le modifiche!

```bash
# Ferma il server (CTRL+C se è in esecuzione)

# Riavvia
python manage.py runserver
```

---

## 🧪 Test dal Frontend

### JavaScript/Fetch

```javascript
// Test semplice
fetch('http://localhost:8000/api/statistics/')
  .then(response => response.json())
  .then(data => console.log('✓ CORS funziona!', data))
  .catch(error => console.error('✗ Errore:', error));

// Con autenticazione
const token = 'your_access_token_here';

fetch('http://localhost:8000/api/users/me/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
})
  .then(response => response.json())
  .then(data => console.log('✓ User data:', data))
  .catch(error => console.error('✗ Errore:', error));
```

### Axios

```javascript
import axios from 'axios';

// Configurazione base
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Aggiungi token JWT alle richieste
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Test
api.get('/statistics/')
  .then(response => console.log('✓ CORS funziona!', response.data))
  .catch(error => console.error('✗ Errore:', error));
```

### React Example

```jsx
import { useState, useEffect } from 'react';

function App() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/statistics/')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        console.log('✓ CORS funziona!');
        setStats(data);
      })
      .catch(error => {
        console.error('✗ Errore:', error);
        setError(error.message);
      });
  }, []);

  if (error) return <div>Errore: {error}</div>;
  if (!stats) return <div>Loading...</div>;

  return (
    <div>
      <h1>Statistiche</h1>
      <p>Total Bookings: {stats.total_bookings}</p>
      <p>Pending: {stats.pending}</p>
      <p>Confirmed: {stats.confirmed}</p>
    </div>
  );
}
```

### Vue Example

```vue
<template>
  <div>
    <h1>Statistiche</h1>
    <div v-if="stats">
      <p>Total Bookings: {{ stats.total_bookings }}</p>
      <p>Pending: {{ stats.pending }}</p>
      <p>Confirmed: {{ stats.confirmed }}</p>
    </div>
    <div v-else-if="error">Errore: {{ error }}</div>
    <div v-else>Loading...</div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      stats: null,
      error: null,
    };
  },
  mounted() {
    fetch('http://localhost:8000/api/statistics/')
      .then(response => response.json())
      .then(data => {
        console.log('✓ CORS funziona!');
        this.stats = data;
      })
      .catch(error => {
        console.error('✗ Errore:', error);
        this.error = error.message;
      });
  },
};
</script>
```

---

## 🔒 Per Produzione

Quando vai in produzione, **NON usare** `CORS_ALLOW_ALL_ORIGINS = True`!

Invece, specifica solo i domini autorizzati:

```python
# settings.py (PRODUZIONE)
CORS_ALLOW_ALL_ORIGINS = False  # Disabilita in produzione!

CORS_ALLOWED_ORIGINS = [
    "https://tuodominio.com",
    "https://www.tuodominio.com",
    "https://app.tuodominio.com",
]

ALLOWED_HOSTS = [
    'tuodominio.com',
    'www.tuodominio.com',
    'api.tuodominio.com',
]

DEBUG = False
```

---

## 🐛 Troubleshooting

### Problema: Ancora errori CORS

1. **Riavvia il server Django**
   ```bash
   # CTRL+C per fermare
   python manage.py runserver
   ```

2. **Pulisci la cache del browser**
   - Chrome: CTRL+SHIFT+DEL
   - Firefox: CTRL+SHIFT+DEL
   - Oppure usa Incognito/Private mode

3. **Verifica che il server sia in ascolto su 0.0.0.0**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

4. **Controlla la console del browser**
   - Apri DevTools (F12)
   - Tab "Network"
   - Cerca richieste OPTIONS (preflight)
   - Verifica gli headers di risposta

### Problema: Token JWT non viene accettato

Verifica che il token sia inviato correttamente:

```javascript
// ✓ CORRETTO
headers: {
  'Authorization': 'Bearer ' + token,  // Nota lo spazio dopo "Bearer"
}

// ✗ SBAGLIATO
headers: {
  'Authorization': 'Token ' + token,  // Sbagliato!
  'Authorization': token,              // Sbagliato!
}
```

### Problema: 403 Forbidden

Se ricevi 403, potrebbe essere il CSRF. Per le API REST, questo non dovrebbe essere un problema perché usiamo JWT.

Se persiste, aggiungi questa decorazione alle view:

```python
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class YourViewSet(viewsets.ModelViewSet):
    # ...
```

**NOTA**: Non dovresti averne bisogno con JWT e DRF.

---

## 📝 Checklist

Prima di testare dal frontend:

- [ ] Modifiche applicate a `settings.py`
- [ ] Server Django riavviato
- [ ] Browser cache pulita (o usa Incognito)
- [ ] Backend risponde su http://localhost:8000
- [ ] Frontend fa richieste a http://localhost:8000/api/...
- [ ] Headers `Authorization` incluso nelle richieste autenticate

---

## ✅ Verifica che CORS Funzioni

### Test 1: Browser DevTools Console

Apri la console del browser e prova:

```javascript
fetch('http://localhost:8000/api/statistics/')
  .then(r => r.json())
  .then(d => console.log('✓ SUCCESS:', d))
  .catch(e => console.error('✗ ERROR:', e));
```

Se vedi `✓ SUCCESS:` con i dati, CORS funziona!

### Test 2: Network Tab

1. Apri DevTools (F12)
2. Vai su "Network"
3. Fai una richiesta dal tuo frontend
4. Cerca la richiesta OPTIONS (preflight)
5. Verifica che abbia questi headers di risposta:
   ```
   Access-Control-Allow-Origin: *
   Access-Control-Allow-Credentials: true
   Access-Control-Allow-Methods: DELETE, GET, OPTIONS, PATCH, POST, PUT
   Access-Control-Allow-Headers: accept, authorization, content-type, ...
   ```

---

## 🎉 Risolto!

Dopo aver riavviato il server Django, il tuo frontend dovrebbe essere in grado di comunicare senza problemi con il backend!

**Domande o problemi?** Controlla la sezione Troubleshooting sopra.

---

**Made with ❤️ for B&Bosio**

