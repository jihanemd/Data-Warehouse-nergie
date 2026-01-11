# 🎨 Guide d'intégration Dashboard + API PostgreSQL

## 📋 Vue d'ensemble

```
┌─────────────────┐
│  Dashboard      │  (HTML/CSS/JS)
│  (localhost:8000)│──┐
└─────────────────┘  │
                     │ HTTP Requests
┌─────────────────┐  │
│  Backend API    │◄─┘
│  (localhost:5000)│  (Flask Python)
└─────────────────┘
        │
        │ SQL Queries
        ▼
┌─────────────────┐
│  PostgreSQL     │
│  dw_energie_fr  │
└─────────────────┘
```

---

## 🚀 Setup Complet (5 minutes)

### 1️⃣ Préparation

```bash
# Vérifier PostgreSQL est lancé
# Windows: Ouvrir Services → PostgreSQL
# Linux: sudo systemctl start postgresql

# Vérifier la BD existe
psql -U postgres -d dw_energie_france -c "SELECT COUNT(*) FROM gold.dim_plant;"
# Résultat attendu: 9744
```

### 2️⃣ Installer dépendances API

```bash
# Windows PowerShell
cd c:\Users\dell\Documents\DataSPACE\Data-Warehouse-nergie

# Créer .env
Copy-Item .env.example .env

# Installer Flask
.\.venv\Scripts\pip.exe install flask flask-cors python-dotenv
```

### 3️⃣ Lancer l'API

```bash
# Terminal 1: Backend API
.\.venv\Scripts\python.exe backend_api.py

# Résultat:
# ✅ Connexion PostgreSQL: localhost:5432/dw_energie_france
# 🚀 Serveur démarré sur http://localhost:5000
```

### 4️⃣ Lancer le Dashboard

```bash
# Terminal 2: Dashboard (Python SimpleServer)
cd dashboard
.\.venv\Scripts\python.exe -m http.server 8000

# Résultat:
# Serving HTTP on 0.0.0.0 port 8000...
```

### 5️⃣ Ouvrir le Dashboard

```bash
# Terminal 3: Ouvrir navigateur
start http://localhost:8000/index.html
```

---

## 📡 Endpoints API

### Health Check
```bash
GET http://localhost:5000/health
# Réponse: {"status": "healthy", "database": "connected"}
```

### KPIs
```bash
GET http://localhost:5000/api/kpis
# Réponse JSON:
# {
#   "totalProduction": 1234,
#   "byType": {"Solaire": 342, "Éolien": 567, ...},
#   "installedCapacity": 28.5,
#   "timestamp": "2026-01-11T..."
# }
```

### Production par type
```bash
GET http://localhost:5000/api/production/by-type
# Réponse:
# {"labels": ["Solaire", "Éolien", ...], "values": [342, 567, ...]}
```

### Production horaire
```bash
GET http://localhost:5000/api/production/hourly
# Réponse:
# {"hours": ["00h", "01h", ...], "production": [850, 820, ...]}
```

### Capacité par région
```bash
GET http://localhost:5000/api/capacity/by-region
# Réponse:
# {"regions": ["Hauts-de-France", ...], "capacity": [4.5, 3.8, ...]}
```

### Top installations
```bash
GET http://localhost:5000/api/installations
# Réponse: [{"id": 1, "name": "...", "capacity": 125.5, ...}, ...]
```

### Mix énergétique
```bash
GET http://localhost:5000/api/energy-mix
# Réponse:
# {"sources": ["Éolien", "Solaire", ...], "percentages": [36, 28, ...]}
```

### Régions
```bash
GET http://localhost:5000/api/regions
# Réponse:
# [{"name": "Hauts-de-France", "installations": 756, "capacity": 4.5}, ...]
```

### Statistiques
```bash
GET http://localhost:5000/api/statistics
# Réponse:
# {
#   "daysRecorded": 4383,
#   "energyTypes": 5,
#   "peakProduction": 1400,
#   "minProduction": 640,
#   "avgProduction": 1050
# }
```

---

## 🔧 Intégration dans le Dashboard

### Option A: Remplacer données mock (Recommandé)

#### Étape 1: Éditer `dashboard/js/charts.js`

**AVANT:**
```javascript
new Chart(productionCtx, {
  type: 'bar',
  data: {
    labels: ['Solaire', 'Éolien', 'Hydro', 'Thermique', 'Autres'],
    datasets: [{
      data: [342, 567, 298, 145, 82],  // ← Données statiques
      ...
    }]
  }
});
```

**APRÈS:**
```javascript
// Créer fonction pour charger les données
async function loadProductionChart() {
  try {
    const response = await fetch('http://localhost:5000/api/production/by-type');
    const data = await response.json();
    
    new Chart(productionCtx, {
      type: 'bar',
      data: {
        labels: data.labels,  // ← Données réelles
        datasets: [{
          data: data.values,   // ← Données réelles
          ...
        }]
      }
    });
  } catch (error) {
    console.error('Erreur chargement API:', error);
    // Fallback sur données mock
  }
}

// Lancer au démarrage
document.addEventListener('DOMContentLoaded', loadProductionChart);
```

#### Étape 2: Mettre à jour tous les graphiques

Appliquer le même pattern pour:
- `hourlyChart`
- `capacityChart`
- `pieChart`

### Option B: Créer couche abstraction (Avancé)

Créer fichier `dashboard/js/api-client.js`:

```javascript
class EnergyAPIClient {
  constructor(baseURL = 'http://localhost:5000') {
    this.baseURL = baseURL;
  }

  async getKPIs() {
    return this.fetch('/api/kpis');
  }

  async getProductionByType() {
    return this.fetch('/api/production/by-type');
  }

  async getProductionHourly() {
    return this.fetch('/api/production/hourly');
  }

  async getCapacityByRegion() {
    return this.fetch('/api/capacity/by-region');
  }

  async getEnergyMix() {
    return this.fetch('/api/energy-mix');
  }

  async getInstallations() {
    return this.fetch('/api/installations');
  }

  async fetch(endpoint) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`Erreur API: ${endpoint}`, error);
      throw error;
    }
  }
}

// Utilisation
const api = new EnergyAPIClient();
const data = await api.getProductionByType();
console.log(data);
```

---

## 🌐 Déploiement Production

### Serveur Linux/Cloud

#### 1️⃣ Installer PostgreSQL et Python

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib python3-pip

# Créer base de données
sudo -u postgres createdb dw_energie_france
```

#### 2️⃣ Déployer application

```bash
git clone https://github.com/jihanemd/Data-Warehouse-nergie.git
cd Data-Warehouse-nergie

# Créer env virtuel
python3 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt
pip install flask flask-cors python-dotenv
```

#### 3️⃣ Configurer Gunicorn + Nginx

```bash
# Installer Gunicorn
pip install gunicorn

# Créer service systemd
sudo nano /etc/systemd/system/energy-api.service
```

```ini
[Unit]
Description=Energy DW API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/Data-Warehouse-nergie
ExecStart=/var/www/Data-Warehouse-nergie/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:5000 \
    backend_api:app

Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Lancer service
sudo systemctl start energy-api
sudo systemctl enable energy-api
```

#### 4️⃣ Configurer Nginx

```nginx
server {
    listen 80;
    server_name energy-dw.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        add_header 'Access-Control-Allow-Origin' '*';
    }
}
```

---

## 🔒 Sécurité

### Checklist Production

- [ ] Modifier `DB_PASSWORD` dans `.env`
- [ ] Générer `SECRET_KEY` aléatoire (50 caractères)
- [ ] `FLASK_DEBUG=False` en production
- [ ] Configurer CORS pour domaines spécifiques
- [ ] Ajouter authentification API (JWT token)
- [ ] Chiffrer connexion BD (SSL)
- [ ] Mettre en place rate limiting
- [ ] Configurer HTTPS/TLS
- [ ] Surveiller logs erreurs
- [ ] Backups réguliers PostgreSQL

### Ajout JWT (Optionnel)

```python
from flask_jwt_extended import JWTManager, create_access_token

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
jwt = JWTManager(app)

@app.route('/login', methods=['POST'])
def login():
    # Validation utilisateur
    access_token = create_access_token(identity='user')
    return jsonify(access_token=access_token)

@app.route('/api/kpis', methods=['GET'])
@jwt_required()
def get_kpis():
    # Route protégée
    ...
```

---

## 📊 Monitoring

### Logs

```bash
# Voir logs temps réel
tail -f logs/api.log

# Analyser erreurs
grep "ERROR" logs/api.log
```

### Métriques

```bash
# Chargement BD
SELECT COUNT(*) FROM gold.dim_plant;
SELECT COUNT(*) FROM gold.fact_energy_production;

# Performance requêtes
EXPLAIN ANALYZE SELECT * FROM gold.fact_energy_production LIMIT 1;
```

---

## 🐛 Troubleshooting

| Problème | Solution |
|----------|----------|
| API Connection Refused | Vérifier `FLASK_HOST` et port 5000 |
| CORS Error | Ajouter origin dans Flask CORS config |
| PostgreSQL Error | Vérifier credentials `.env` |
| Données nulles | Vérifier pipeline ETL exécuté |
| Performances lentes | Ajouter indexes PostgreSQL |

---

## 📚 Ressources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)
- [PostgreSQL JSON API](https://www.postgresql.org/docs/current/functions-json.html)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)

---

**Version**: 1.0.0  
**Dernière mise à jour**: 11 Janvier 2026  
**Auteur**: Data Warehouse Énergie France 🔋
