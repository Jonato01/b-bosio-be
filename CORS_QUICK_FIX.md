# ✅ PROBLEMA CORS RISOLTO!

## 🔧 Cosa è stato fatto

### 1. Configurazione CORS Aggiornata

Ho modificato `booking_backend/settings.py` per permettere richieste cross-origin dal tuo frontend:

```python
# Permetti TUTTE le origini in sviluppo
CORS_ALLOW_ALL_ORIGINS = True

# Permetti credenziali (cookies, headers di autenticazione)
CORS_ALLOW_CREDENTIALS = True

# Headers permessi
CORS_ALLOW_HEADERS = [
    'accept', 'authorization', 'content-type', 
    'origin', 'user-agent', 'x-csrftoken', ...
]

# Metodi HTTP permessi
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']

# Permetti tutti gli hosts
ALLOWED_HOSTS = ['*']
```

---

## 🚀 AZIONE RICHIESTA

### ⚠️ DEVI RIAVVIARE IL SERVER DJANGO!

Le modifiche a `settings.py` richiedono un riavvio del server.

**Ferma il server** (se è in esecuzione):
- Premi `CTRL+C` nel terminale

**Riavvia il server**:
```bash
python manage.py runserver
```

Oppure usa lo script:
```bash
start_server.bat
```

---

## 🧪 TEST CORS

### Metodo 1: File HTML di Test (Facile)

1. Apri il file `test_cors.html` nel browser:
   ```
   C:\Users\Renato\PycharmProjects\b&bosio\test_cors.html
   ```

2. Clicca su "Test /api/statistics/"

3. Se vedi "✅ SUCCESS!" con i dati, CORS funziona!

### Metodo 2: Console del Browser

1. Apri la console del browser (F12)

2. Copia e incolla:
   ```javascript
   fetch('http://localhost:8000/api/statistics/')
     .then(r => r.json())
     .then(d => console.log('✓ CORS OK:', d))
     .catch(e => console.error('✗ CORS ERROR:', e));
   ```

3. Premi INVIO

4. Se vedi `✓ CORS OK:` con i dati, funziona!

### Metodo 3: Dal Tuo Frontend

Nel tuo codice frontend, fai una richiesta normale:

```javascript
// Esempio con fetch
const response = await fetch('http://localhost:8000/api/statistics/');
const data = await response.json();
console.log(data);

// Esempio con axios
import axios from 'axios';
const response = await axios.get('http://localhost:8000/api/statistics/');
console.log(response.data);
```

---

## 🔐 Autenticazione JWT

Per le richieste autenticate, aggiungi l'header Authorization:

```javascript
const token = 'your_access_token_here';

fetch('http://localhost:8000/api/users/me/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  }
})
  .then(r => r.json())
  .then(d => console.log('User:', d))
  .catch(e => console.error('Error:', e));
```

**IMPORTANTE**: Nota lo spazio tra "Bearer" e il token!

---

## 📝 Configurazione Frontend

### React

```javascript
// src/api/client.js
const API_BASE_URL = 'http://localhost:8000/api';

export const apiClient = {
  get: async (endpoint, token = null) => {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return response.json();
  },
  
  post: async (endpoint, data, token = null) => {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return response.json();
  },
};

// Uso
import { apiClient } from './api/client';

// Senza autenticazione
const stats = await apiClient.get('/statistics/');

// Con autenticazione
const token = localStorage.getItem('access_token');
const user = await apiClient.get('/users/me/', token);
```

### Vue

```javascript
// src/services/api.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor per aggiungere token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default apiClient;

// Uso
import apiClient from '@/services/api';

// Senza autenticazione
const stats = await apiClient.get('/statistics/');

// Con autenticazione (token aggiunto automaticamente)
const user = await apiClient.get('/users/me/');
```

### Angular

```typescript
// src/app/services/api.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    let headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });
    
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    
    return headers;
  }

  get<T>(endpoint: string): Observable<T> {
    return this.http.get<T>(`${this.baseUrl}${endpoint}`, {
      headers: this.getHeaders()
    });
  }

  post<T>(endpoint: string, data: any): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}${endpoint}`, data, {
      headers: this.getHeaders()
    });
  }
}

// Uso
import { ApiService } from './services/api.service';

constructor(private api: ApiService) {}

ngOnInit() {
  // Senza autenticazione
  this.api.get('/statistics/').subscribe(
    data => console.log('Stats:', data),
    error => console.error('Error:', error)
  );

  // Con autenticazione
  this.api.get('/users/me/').subscribe(
    user => console.log('User:', user),
    error => console.error('Error:', error)
  );
}
```

---

## 🐛 Se NON Funziona Ancora

### Checklist:

1. ✅ Server Django riavviato?
   ```bash
   python manage.py runserver
   ```

2. ✅ Server risponde su http://localhost:8000?
   - Apri nel browser: http://localhost:8000/api/
   - Dovresti vedere la lista degli endpoints

3. ✅ Cache del browser pulita?
   - Chrome/Edge: CTRL+SHIFT+DEL
   - Firefox: CTRL+SHIFT+DEL
   - Safari: CMD+OPTION+E
   - Oppure usa modalità Incognito

4. ✅ Console del browser mostra errori?
   - Apri DevTools (F12)
   - Tab "Console"
   - Tab "Network"
   - Cerca errori CORS o 4xx/5xx

5. ✅ URL corretti?
   - Backend: `http://localhost:8000/api/...`
   - NON `http://127.0.0.1:8000/...` (può causare problemi CORS)
   - NON `http://localhost/...` (manca la porta)

### Debug Network Request

1. Apri DevTools (F12)
2. Tab "Network"
3. Fai una richiesta dal frontend
4. Clicca sulla richiesta
5. Tab "Headers"
6. Verifica:
   - **Request Headers**: deve avere `Origin: http://localhost:XXXX`
   - **Response Headers**: deve avere `Access-Control-Allow-Origin: *`

Se manca `Access-Control-Allow-Origin` nella risposta, il server non è stato riavviato!

---

## ⚠️ IMPORTANTE PER PRODUZIONE

Quando vai in produzione, **CAMBIA** questa configurazione!

```python
# settings.py (PRODUZIONE)
CORS_ALLOW_ALL_ORIGINS = False  # ❌ NON usare in produzione!

CORS_ALLOWED_ORIGINS = [
    "https://tuodominio.com",
    "https://www.tuodominio.com",
]

ALLOWED_HOSTS = [
    'api.tuodominio.com',
    'tuodominio.com',
]

DEBUG = False
```

---

## ✅ Checklist Finale

Prima di continuare, verifica:

- [ ] Server Django riavviato
- [ ] `test_cors.html` mostra SUCCESS
- [ ] Frontend può fare richieste GET a `/api/statistics/`
- [ ] Frontend può fare richieste autenticate con JWT

Se tutti i check sono ✅, il problema CORS è risolto!

---

## 📚 File di Riferimento

- **CORS_FIX.md** - Guida dettagliata CORS con esempi
- **test_cors.html** - Tool di test CORS interattivo
- **API_DOCUMENTATION.md** - Documentazione completa API

---

**Made with ❤️ for B&Bosio**

🎉 **CORS Risolto! Buon sviluppo!** 🎉

