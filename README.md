# 🚀 Data Warehouse Énergie 

**Pipeline ETL: CSV → PostgreSQL → Dashboard Interactif**

Pipeline d'ingestion et d'analyse des données énergétiques avec ETL 3-étapes (Bronze/Silver/Gold), PostgreSQL Star Schema (20,488 lignes), et dashboard temps réel avec 15+ graphes interactifs + API REST.

---

## 📊 En résumé

- ✅ **61,554 lignes** ingérées en Bronze
- ✅ **100% qualité** (0 rejets en Silver)
- ✅ **20,488 lignes** chargées PostgreSQL
- ✅ **15+ graphes** interactifs (Chart.js + Leaflet)
- ✅ **9 graphes avancés** (production/consommation multi-années)
- ✅ **API REST** Flask avec 9 endpoints
- ✅ **Carte SIG** interactive avec 5 installations

---

## 🏗️ Architecture

```
CSV Sources (61,554 lignes)
    ↓
BRONZE (raw Parquet)
    ↓
SILVER (nettoyé)
    ↓
GOLD (Star Schema 7 tables)
    ↓
PostgreSQL (20,488 lignes)
    ↓
Backend Flask API (9 endpoints)
    ↓
Dashboard HTML/JS (15+ graphes)
```

**Star Schema PostgreSQL:**
- 4 Dimensions: date | energy_type | location | plant
- 2 Faits: production | capacity
- 31 régions | 9,744 installations | 4,383 dates | 5 types d'énergie

---

## 🚀 Démarrage Rapide

### 1. Installation

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

### 2. Configuration .env

```
DB_USER=postgres
DB_PASSWORD=jihane
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dw_energie_france
```

### 3. Pipeline ETL

```bash
python run.py  # Bronze → Silver → Gold → PostgreSQL (~8s)
```

### 4. Serveurs

**Terminal 1 - API:**
```bash
python backend_api.py  # http://localhost:5000
```

**Terminal 2 - Dashboard:**
```bash
cd dashboard
python -m http.server 8000  # http://localhost:8000/index.html
```

### 5. Ouvrir Dashboard

```
http://localhost:8000/index.html
```

---

## 📊 Visualisations & Graphes

### Production (6 graphes)
- Par type d'énergie (Solaire/Éolien/Hydro)
- Horaire 24h
- Par région
- Mix énergétique %
- Historique annuel
- Croissance %

### Consommation (6 graphes)
- Par secteur (Industrie/Résidentiel/Tertiaire)
- Par région
- Horaire 24h
- Tendance 12 mois
- Balance vs Production
- Efficacité %

### Analyses Avancées (9 graphes)
1. **Production par région** 2020-2024 (multi-line)
2. **Comparaison régionale** 2024 (top 10)
3. **Tendance 5 ans** (mensuel)
4. **Mix énergétique** par région (stacked)
5. **Efficacité installations** Capacity Factor (scatter)
6. **Distribution efficacité** (Production/Pertes)
7. **Capacité installée** par type (polar)
8. **Résumé mensuel** 3 ans (dual-axis)
9. **Analyse distribution** (Production/Pertes/Net)

### Carte SIG
- 5 installations géolocalisées
- Pop-ups avec détails (nom, capacité, région)
- Zoom/Pan interactif
- Base map Leaflet

---

## 🔗 API REST (9 endpoints)

```
GET /health
GET /api/production-by-city-year        Production région 2020-2024
GET /api/city-comparison                Comparaison régionale 2024
GET /api/production-trend-5years        Tendance 5 ans
GET /api/energy-mix-by-city             Mix énergétique région
GET /api/optimization-analysis          Efficacité (Capacity Factor)
GET /api/distribution-analysis          Production/Pertes/Net
GET /api/capacity-installed             Capacité par type
GET /api/monthly-summary                Résumé mensuel 3 ans
```

---

## 📁 Structure

```
Data-Warehouse-nergie/
├── src/jobs/
│   ├── 01_bronze_ingest_pandas.py   CSV → Parquet
│   ├── 02_silver_clean.py            Nettoyage QA
│   └── 03_gold_dwh.py                Star Schema
├── dashboard/
│   ├── index.html                    Interface
│   ├── css/style.css                 Dark theme
│   └── js/
│       ├── charts.js                 15 graphes
│       ├── advanced-charts.js        9 graphes PostgreSQL
│       └── app.js                    Interactions
├── backend_api.py                    Flask 9 endpoints
├── run.py                            Orchestration ETL
├── requirements.txt
└── README.md
```

---

## 📊 Requêtes SQL

### Production par type

```sql
SELECT energy_type, SUM(production_mw) as production
FROM gold.fact_energy_production f
JOIN gold.dim_energy_type e ON f.energy_type_id = e.energy_type_id
GROUP BY energy_type ORDER BY production DESC;
```

### Top 10 installations

```sql
SELECT plant_name, technology, capacity_mw, region
FROM gold.dim_plant ORDER BY capacity_mw DESC LIMIT 10;
```

### Production annuelle

```sql
SELECT EXTRACT(YEAR FROM d.date) as year, SUM(f.production_mw)
FROM gold.fact_energy_production f
JOIN gold.dim_date d ON f.date_id = d.date_id
GROUP BY EXTRACT(YEAR FROM d.date);
```

---

## 🔧 Configuration

### requirements.txt (nettoyé)

```
pandas>=1.5.0
numpy>=1.23.0
pyyaml>=6.0
python-dotenv>=0.21.0
psycopg2-binary>=2.9.0
sqlalchemy>=1.4.0
flask>=3.1.0
flask-cors>=6.0.0
```

### conf/config.yaml

```yaml
bronze:
  path: data/bronze
silver:
  path: data/silver
gold:
  path: data/gold
postgres:
  schema: gold
```

---

## 📈 Performance

| Étape | Durée | Lignes | Status |
|-------|-------|--------|--------|
| Bronze | 2s | 61,554 | ✅ |
| Silver | 1.5s | 61,554 | ✅ |
| Gold | 2.5s | 20,488 | ✅ |
| PostgreSQL | 2s | 20,488 | ✅ |
| **TOTAL** | **~8s** | **20,488** | ✅ |

---

## 🐛 Dépannage

**PostgreSQL Connection Error?**
```bash
pg_isready
cat .env  # Vérifier credentials
```

**Dashboard blanc?**
```
Ctrl+Shift+R (vider cache)
F12 (vérifier console pour erreurs)
```

**API 404?**
```
Vérifier ports 5000 et 8000
Lancer python backend_api.py en premier
```

**Données vides?**
```bash
python run.py  # Recharger ETL
python reload_postgres.py  # Recharger BDD
```

---

## ✅ État: PRODUCTION

- [x] ETL complet 4 étapes
- [x] 100% Data Quality
- [x] 20,488 lignes PostgreSQL
- [x] 15+ graphes interactifs
- [x] 9 endpoints API
- [x] Carte SIG
- [x] Documentation

**Prêt pour BI et analytics.**

---

**Licence:** MIT  
**Dernière mise à jour:** Janvier 2026
