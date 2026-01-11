# 🚀 Data Warehouse Énergie France

**Pipeline ETL avec Apache Spark - Architecture Bronze/Silver/Gold**

Projet complet de Data Warehouse pour l'analyse des données d'énergie en France, implémentant une architecture moderne de data lakehouse avec Spark et Parquet.

---

## 📋 Table des matières

- [🎯 Aperçu](#-aperçu)
- [🏗️ Architecture](#️-architecture)
- [📦 Installation](#-installation)
- [🚀 Démarrage rapide](#-démarrage-rapide)
- [📂 Structure du projet](#-structure-du-projet)
- [🔧 Configuration](#-configuration)
- [📊 Données sources](#-données-sources)
- [🎯 Utilisation](#-utilisation)
- [💾 Star Schema](#-star-schema)
- [📈 Requêtes BI](#-requêtes-bi)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [📝 Licence](#-licence)

---

## 🎯 Aperçu

Ce projet implémente un **pipeline ETL complet** pour ingérer, nettoyer et transformer des données d'énergie françaises en un data warehouse **prêt pour Business Intelligence**.

### ✨ Caractéristiques principales

- ✅ **3 couches de données** : Bronze (RAW) → Silver (CLEAN) → Gold (ANALYTICS)
- ✅ **Data Quality** : Validation automatique avec rejet des records invalides
- ✅ **Star Schema Enrichi** : 4 dimensions + 3 fact tables pour analyses multi-niveaux
- ✅ **Format Parquet** : Compression, columnar storage, compatible avec tous les outils BI
- ✅ **Orchestration** : Script Python avec modes d'exécution flexibles
- ✅ **Performance** : Traitement de 61k+ lignes en ~7 secondes
- ✅ **Dimension géographique** : 31 régions françaises (NUTS codes)
- ✅ **Master data ENR** : 9,744 installations avec métadonnées (technologie, capacité, localisation)

### 📊 Données couvertes

| Source | Lignes | Description |
|--------|--------|-------------|
| **france_time_series.csv** | 50,393 | Séries chronologiques horaires de production |
| **eurostat_electricity_france.csv** | 417 | Données Eurostat électricité |
| **time_series_60min_sample.csv** | 1,000 | Échantillon haute fréquence (60min) |
| **renewable_power_plants_FR.csv** | 9,744 | Registre des installations ENR |
| **TOTAL** | **61,554** | Données prêtes pour analyse |

---

## 🏗️ Architecture

### Flux de données

```
Data Sources (CSV)
      ↓
   BRONZE LAYER (Raw Ingestion)
      • Lecture CSV directe
      • Ajout colonnes système (_source_file, _ingest_ts, _ingest_date)
      • Format Parquet sans transformation
      • 61,554 lignes
      ↓
   SILVER LAYER (Data Quality & Cleaning)
      • Type casting (string → numeric/date)
      • Validation métier (pas de valeurs négatives)
      • Deduplication
      • Timestamp validation
      • Rejet des records invalides
      • 61,554 lignes valides (100% acceptance)
      ↓
   GOLD LAYER (Star Schema Enrichi - 7 Tables)
      • 4 Dimensions: dim_date, dim_energy_type, dim_location, dim_plant
      • 3 Fact Tables: fact_energy_production, fact_renewable_capacity, fact_monthly_summary
      ↓
   BI TOOLS (Power BI, Tableau, Metabase, etc.)
```

### Schéma en étoile enrichi (Star Schema)

```
                    ┌─ dim_date ────────┐
                    │ (4,383 rows)       │
                    │ • date_id          │
                    │ • date, year, etc. │
                    └────────────────────┘
                          ↑
                          │ FK
              ┌───────────┴────────────┐
              │ fact_energy_production │
              │     (6,301 rows)       │
              │ • date_id (FK)         │
              │ • energy_type_id (FK)  │
              │ • value_mw, avg_mw     │
              └────────────┬───────────┘
                           │ FK
                    ┌──────────────────┐
                    │ dim_energy_type  │
                    │  (5 rows)        │
                    │ • energy_type_id │
                    │ • Solar, Wind    │
                    └──────────────────┘

              ┌──────────────────────────────┐
              │ fact_renewable_capacity      │
              │     (24 rows)                │
              │ • region (FK)                │
              │ • energy_type_id (FK)        │
              │ • total_capacity_mw          │
              └──────┬────────────┬──────────┘
                     │ FK         │ FK
              ┌──────┴──┐    ┌────┴──────────┐
              │dim_location  │ dim_plant     │
              │  (31 rows)   │ (9,744 rows)  │
              │• region_name │ • plant_name  │
              │• region_code │ • technology  │
              └─────────┘    └───────────────┘

              ┌────────────────────────┐
              │fact_monthly_summary    │
              │     (x rows)           │
              │ • date_id (FK)         │
              │ • energy_type_id (FK)  │
              │ • production_mwh       │
              └────────────────────────┘
```

---

## 📦 Installation

### Prérequis

- **Python 3.11+** (testé avec 3.11)
- **Windows/Linux/Mac**
- **~2 GB** d'espace disque (données + venv)

### 1. Cloner le projet

```bash
git clone <repository>
cd Spark_dataSpace_Projet
```

### 2. Créer l'environnement virtuel

```bash
# Windows
python -m venv venv_spark
.\venv_spark\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv_spark
source venv_spark/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Vérifier l'installation

```bash
python -c "import pandas, pyspark, pyarrow; print('✅ Installation OK')"
```

---

## 🚀 Démarrage rapide

### Exécution du pipeline complet

```bash
# Run.py utilise auto-détection du Python venv
python run.py

# Ou avec le Python du venv explicite
.\venv_spark\Scripts\python.exe run.py
```

**Résultat attendu:**
```
🚀 PIPELINE ETL - Data Warehouse Énergie France
📂 Projet: c:\...\Spark_dataSpace_Projet
🐍 Python: .\venv_spark\Scripts\python.exe

📋 ÉTAPES: BRONZE → SILVER → GOLD

✅ 🟤 BRONZE (Ingestion RAW) - SUCCÈS
✅ ⚪ SILVER (Nettoyage) - SUCCÈS
✅ 🟡 GOLD (Star Schema) - SUCCÈS

📊 RÉSUMÉ FINAL
   • Étapes réussies: 3/3
   • Durée totale: 7.2s
   • Fichiers Parquet: 11
```

### Modes d'exécution

```bash
# Mode 1: Pipeline complet (par défaut)
python run.py
# Exécute: BRONZE → SILVER → GOLD

# Mode 2: Seulement BRONZE
python run.py --bronze
# Exécute: BRONZE uniquement

# Mode 3: BRONZE + SILVER
python run.py --silver
# Exécute: BRONZE → SILVER

# Mode 4: Nettoyer + relancer
python run.py --clean
# Supprime data/warehouse puis exécute BRONZE → SILVER → GOLD

# Mode 5: Nettoyer + BRONZE
python run.py --clean --bronze
# Supprime data/warehouse puis exécute BRONZE uniquement
```

---

## 📂 Structure du projet

```
Spark_dataSpace_Projet/
│
├── README.md                          ← Ce fichier
├── requirements.txt                   ← Dépendances Python
├── run.py                             ← Orchestrateur principal
│
├── conf/
│   └── config.yaml                    ← Configuration centralisée
│
├── src/
│   ├── jobs/                          ← Pipeline ETL
│   │   ├── 01_bronze_ingest_pandas.py      (Ingestion RAW)
│   │   ├── 02_silver_clean.py              (Nettoyage & DQ)
│   │   └── 03_gold_dwh.py                  (Star Schema)
│   │
│   └── lib/                           ← Librairies communes
│       ├── spark_utils.py             (Utilitaires Spark)
│       └── dq_utils.py                (Data Quality)
│
├── data/
│   ├── landing/                       ← Fichiers CSV sources
│   │   ├── france_time_series.csv
│   │   ├── eurostat_electricity_france.csv
│   │   ├── time_series_60min_sample.csv
│   │   └── renewable_power_plants_FR.csv
│   │
│   └── warehouse/                     ← Data Warehouse
│       ├── bronze/                    ← Raw data (Parquet)
│       │   ├── france_time_series/
│       │   ├── eurostat_electricity_france/
│       │   ├── time_series_60min_sample/
│       │   └── renewable_power_plants_FR/
│       │
│       ├── silver/                    ← Cleaned data (Parquet)
│       │   ├── france_time_series/
│       │   ├── eurostat_electricity_france/
│       │   ├── time_series_60min/
│       │   └── renewable_plants/
│       │
│       ├── gold/                      ← Analytics (Star Schema Enrichi)
│       │   ├── dim_date/               ← 4,383 dates (2015-2026)
│       │   ├── dim_energy_type/        ← 5 types d'énergie
│       │   ├── dim_location/           ← 31 régions françaises
│       │   ├── dim_plant/              ← 9,744 installations ENR
│       │   ├── fact_energy_production/ ← 6,301 records d'agrégation journalière
│       │   ├── fact_renewable_capacity/← 24 records capacité par région/tech
│       │   └── fact_monthly_summary/   ← Résumés mensuels consolidés
│       │
│       └── dq/                        ← Rejected records
│           ├── france_time_series_rejects/
│           ├── eurostat_rejects/
│           ├── time_series_rejects/
│           └── renewable_rejects/
│
└── venv_spark/                        ← Environnement Python (auto-créé)
    ├── lib/site-packages/
    ├── Scripts/ (Windows) / bin/ (Linux)
    └── pyvenv.cfg
```

---

## 🔧 Configuration

### Fichier: `conf/config.yaml`

```yaml
# Chemins de données
paths:
  landing: "data/landing"
  warehouse: "data/warehouse"
  bronze: "data/warehouse/bronze"
  silver: "data/warehouse/silver"
  gold: "data/warehouse/gold"
  dq: "data/warehouse/dq"

# Sources CSV
sources:
  france_time_series:
    path: "data/landing/france_time_series.csv"
    delimiter: ","
    header: true
    
  eurostat_electricity_france:
    path: "data/landing/eurostat_electricity_france.csv"
    delimiter: ","
    header: true

# Paramètres Spark
spark:
  app_name: "DataWarehouse_Energie_France"
  master: "local[*]"
  adaptive_execution: true
  shuffle_partitions: 4
  memory: "2g"
  cores: "4"
```

Modifiez ce fichier pour adapter les chemins, délimiteurs ou paramètres Spark à votre environnement.

---

## 📊 Données sources

### 1. france_time_series.csv

**Production électrique horaire 2015-2026**

```
DateTime,Load,Solar,Wind Onshore,Wind Offshore,Hydro,Thermal,Pumping
2015-01-01T00:00:00+0100,52620,0,1380,0,7560,27400,-1500
2015-01-01T01:00:00+0100,50850,0,1286,0,7480,26900,-1500
...
```

**Colonnes** : DateTime, Load, Solar, Wind Onshore, Wind Offshore, Hydro, Thermal, Pumping  
**Lignes** : 50,393  
**Période** : 2015-2026  

---

### 2. eurostat_electricity_france.csv

**Données officielles Eurostat**

```
Year,Month,Renewable_Production,Total_Production,Renewable_Percentage
2015,01,4500,45000,10.0
2015,02,4800,46000,10.4
...
```

**Colonnes** : Year, Month, Renewable_Production, Total_Production, Renewable_Percentage  
**Lignes** : 417  

---

### 3. time_series_60min_sample.csv

**Échantillon haute fréquence**

```
timestamp,value_mw,source
2015-01-01 01:00:00,5726.0,Load
2015-01-01 02:00:00,6593.0,Load
...
```

**Colonnes** : timestamp, value_mw, source  
**Lignes** : 1,000  

---

### 4. renewable_power_plants_FR.csv

**Registre des installations ENR (Open Data Réseaux Énergies)**

```
electrical_capacity,energy_source_level_1,technology,lat,lon,...
0.1,Renewable,Photovoltaics,48.69,7.78,...
2.2,Renewable,Hydro,45.15,5.72,...
...
```

**Colonnes** : 30 (electrical_capacity, technology, location, status, etc.)  
**Lignes** : 9,744  

---

## 🎯 Utilisation

### Exécuter une seule couche

```bash
# Ingérer les données brutes uniquement
python run.py --bronze

# Nettoyer et valider les données
python run.py --silver

# Créer le data warehouse analytique
python run.py --gold
```

### Relancer le pipeline

```bash
# Supprimer toutes les données et recommencer
python run.py --clean

# Supprimer et relancer seulement BRONZE
python run.py --clean --bronze
```

### Exécuter un job spécifique

```bash
# Job Bronze seul
.\venv_spark\Scripts\python.exe src/jobs/01_bronze_ingest_pandas.py

# Job Silver seul
.\venv_spark\Scripts\python.exe src/jobs/02_silver_clean.py

# Job Gold seul
.\venv_spark\Scripts\python.exe src/jobs/03_gold_dwh.py
```

---

## 💾 Star Schema

### Dimension: dim_date

**Couverture:** 2015-01-01 à 2026-12-31 (4,383 dates)

```sql
SELECT * FROM gold.dim_date LIMIT 5;

date_id       date  year  month  day  quarter  week_of_year  day_of_week  day_name    is_weekend  is_holiday
─────────────────────────────────────────────────────────────────────────────────────────────────────────
20150101      2015-01-01  2015  1     1        1             1            3          Thursday     0          1
20150102      2015-01-02  2015  1     2        1             1            4          Friday       0          0
20150103      2015-01-03  2015  1     3        1             1            5          Saturday     1          0
20150104      2015-01-04  2015  1     4        1             1            6          Sunday       1          0
20150105      2015-01-05  2015  1     5        1             2            1          Monday       0          0
```

### Dimension: dim_energy_type

**5 catégories d'énergie**

```sql
SELECT * FROM gold.dim_energy_type;

energy_type_id  energy_type_name    description                      unit  category
──────────────────────────────────────────────────────────────────────────────────
1               Solar               Solar photovoltaic generation     MW    Renewable
2               Wind Onshore        Wind onshore generation           MW    Renewable
3               Load (Consumption)  Electrical load / consumption     MW    Consumption
4               Hydro               Hydroelectric generation          MW    Renewable
5               Other               Other renewable/thermal sources   MW    Other
```

### Dimension: dim_location

**31 régions françaises avec codes NUTS**

```sql
SELECT * FROM gold.dim_location LIMIT 5;

location_id  nuts_1_code  nuts_2_code  region_name           region_code  country
─────────────────────────────────────────────────────────────────────────────────
1            FRF          FRF1         Grand-Est             44           FR
2            FRF          FRF1         Alsace                42           FR
3            FRK          FRK2         Auvergne-Rhône-Alpes  84           FR
4            FRK          FRK2         Isère                 38           FR
5            FRL          FRL1         Île-de-France         75           FR
```

### Dimension: dim_plant

**9,744 installations ENR avec caractéristiques**

```sql
SELECT * FROM gold.dim_plant LIMIT 3;

plant_id  plant_name             technology      energy_source     capacity_mw  latitude   longitude   commissioning_date  region
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
1         SABLIERE ENERGIE       Photovoltaics   Renewable energy  0.1          48.69      7.78        2015-01-03          Grand-Est
2         CENTRALE DU RONDEAU    Hydro           Renewable energy  2.2          45.15      5.72        2015-01-03          Auvergne-Rhône-Alpes
3         Unknown                Photovoltaics   Renewable energy  0.0828       46.14      2.35        2015-01-04          Nouvelle-Aquitaine
```

### Fact Table: fact_energy_production

**6,301 enregistrements d'agrégation journalière**

```sql
SELECT * FROM gold.fact_energy_production 
WHERE date_id = 20150101 
LIMIT 3;

date_id  energy_type_id  country  value_mw   value_min_mw  value_max_mw  value_avg_mw  nb_records
──────────────────────────────────────────────────────────────────────────────────────────────────
20150101 3               FR       1521956.0  60798.0       71682.0       66172.0       23
20150102 3               FR       1637422.0  60686.0       73971.0       68225.9       24
20150103 3               FR       1510660.0  57700.0       68498.0       62944.1       24
```

### Fact Table: fact_renewable_capacity

**24 enregistrements de capacité installée par région et type**

```sql
SELECT * FROM gold.fact_renewable_capacity 
ORDER BY total_capacity_mw DESC 
LIMIT 3;

date_id    energy_type_id  region               total_capacity_mw  avg_capacity_mw  nb_plants
─────────────────────────────────────────────────────────────────────────────────────────────
20260111   1               Nouvelle-Aquitaine  1250.5             0.45             2781
20260111   1               Auvergne-Rhône-Alpes 890.2             0.38             2340
20260111   2               Hauts-de-France     1650.8             2.15             765
```

### Fact Table: fact_monthly_summary

**Résumés mensuels consolidés pour requêtes BI rapides**

```sql
SELECT * FROM gold.fact_monthly_summary 
WHERE date_id >= 20260101 
LIMIT 3;

date_id    energy_type_id  country  production_mwh  avg_mw  min_mw  max_mw  nb_records
─────────────────────────────────────────────────────────────────────────────────────
20260101   3               FR       37259812.0      51388   45690   62145   744
20260101   1               FR       2156400.5       2984    125     8945    744
20260101   2               FR       4128750.2       5716    450     12350   744
```

---

## 📈 Requêtes BI

### Requête 1: Capacité ENR par région et technologie

```sql
SELECT 
    l.region_name,
    l.region_code,
    e.energy_type_name,
    ROUND(f.total_capacity_mw, 2) as total_capacity_mw,
    ROUND(f.avg_capacity_mw, 4) as avg_capacity_per_plant,
    f.nb_plants,
    RANK() OVER (PARTITION BY e.energy_type_id ORDER BY f.total_capacity_mw DESC) as rank_by_energy_type
FROM gold.fact_renewable_capacity f
JOIN gold.dim_location l ON f.region = l.region_name
JOIN gold.dim_energy_type e ON f.energy_type_id = e.energy_type_id
WHERE f.date_id = 20260111
ORDER BY total_capacity_mw DESC;
```

### Requête 2: Production journalière par type d'énergie

```sql
SELECT 
    d.date,
    d.day_name,
    e.energy_type_name,
    ROUND(f.value_avg_mw, 2) as avg_production_mw,
    ROUND(f.value_min_mw, 2) as min_production_mw,
    ROUND(f.value_max_mw, 2) as max_production_mw,
    f.nb_records as nb_hourly_records,
    ROUND(100 * f.value_avg_mw / (SUM(f.value_avg_mw) OVER (PARTITION BY f.date_id)), 2) as pct_of_total
FROM gold.fact_energy_production f
JOIN gold.dim_date d ON f.date_id = d.date_id
JOIN gold.dim_energy_type e ON f.energy_type_id = e.energy_type_id
WHERE d.year = 2026 AND f.country = 'FR'
ORDER BY d.date DESC, e.energy_type_name;
```

### Requête 3: Installations ENR par région et technologie

```sql
SELECT 
    l.region_name,
    p.technology,
    COUNT(*) as nb_installations,
    ROUND(SUM(p.capacity_mw), 2) as total_capacity_mw,
    ROUND(AVG(p.capacity_mw), 4) as avg_capacity_mw,
    MIN(p.commissioning_date) as first_commissioning,
    MAX(p.commissioning_date) as last_commissioning,
    COUNT(DISTINCT YEAR(p.commissioning_date)) as years_of_deployment
FROM gold.dim_plant p
JOIN gold.dim_location l ON p.region = l.region_name
WHERE p.commissioning_date <= CURRENT_DATE
GROUP BY l.region_name, p.technology
ORDER BY total_capacity_mw DESC;
```

### Requête 4: Résumé mensuel production vs consommation

```sql
SELECT 
    d.date,
    d.year,
    d.month,
    SUM(CASE WHEN e.energy_type_id = 3 THEN f.production_mwh ELSE 0 END) as consumption_mwh,
    SUM(CASE WHEN e.energy_type_id IN (1, 2, 4) THEN f.production_mwh ELSE 0 END) as renewable_production_mwh,
    ROUND(100 * SUM(CASE WHEN e.energy_type_id IN (1, 2, 4) THEN f.production_mwh ELSE 0 END)
          / SUM(CASE WHEN e.energy_type_id = 3 THEN f.production_mwh ELSE 0 END), 2) as renewable_percentage
FROM gold.fact_monthly_summary f
JOIN gold.dim_date d ON f.date_id = d.date_id
JOIN gold.dim_energy_type e ON f.energy_type_id = e.energy_type_id
WHERE f.country = 'FR'
GROUP BY d.date, d.year, d.month
ORDER BY d.year DESC, d.month DESC;
```

---

## 🔌 Connexion BI

### Power BI

1. **Obtenir les données** → **Parquet**
2. Pointer vers `data/warehouse/gold/`
3. Charger les 7 tables:
   - Dimensions: `dim_date`, `dim_energy_type`, `dim_location`, `dim_plant`
   - Facts: `fact_energy_production`, `fact_renewable_capacity`, `fact_monthly_summary`
4. Créer relations dans Power Query:
   - `fact_energy_production.date_id` → `dim_date.date_id`
   - `fact_energy_production.energy_type_id` → `dim_energy_type.energy_type_id`
   - `fact_renewable_capacity.region` → `dim_location.region_name`
   - `fact_renewable_capacity.energy_type_id` → `dim_energy_type.energy_type_id`
   - `dim_plant.region` → `dim_location.region_name`
5. Créer rapports avec DAX sur fact tables

### Tableau

1. **Connect** → **Parquet**
2. Sélectionner `data/warehouse/gold/fact_energy_production/`
3. Ajouter les dimensions via relationship panel:
   - Date dimension pour filtrage temporel
   - Energy type pour segmentation
4. Pour capacité: charger `fact_renewable_capacity` + `dim_location`
5. Créer dashboards avec cross-filtering

### Metabase

1. **Settings** → **Admin** → **Databases**
2. **New Database** → **Parquet**
3. Pointer vers `data/warehouse/gold/`
4. Metabase scanne automatiquement les 7 tables
5. Créer questions avec UI builder, puis dashboards

### DuckDB / Trino / Presto

```sql
-- DuckDB
SELECT * FROM read_parquet('data/warehouse/gold/fact_energy_production/*.parquet') LIMIT 5;
SELECT * FROM read_parquet('data/warehouse/gold/dim_plant/*.parquet') LIMIT 5;

-- Trino
SELECT * FROM hive.default.fact_energy_production;
SELECT * FROM hive.default.dim_plant;

-- Requête multi-table (DuckDB)
SELECT 
    d.region_name,
    SUM(c.total_capacity_mw) as region_capacity
FROM read_parquet('data/warehouse/gold/fact_renewable_capacity/*.parquet') c
JOIN read_parquet('data/warehouse/gold/dim_location/*.parquet') d
    ON c.region = d.region_name
GROUP BY d.region_name
ORDER BY region_capacity DESC;
```

---

## 🛠️ Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'pyspark'"

```bash
# Solution: Réinstaller les dépendances
pip install -r requirements.txt
```

### ❌ "No such file or directory: 'conf/config.yaml'"

```bash
# Solution: Vérifier que vous êtes dans le bon répertoire
cd Spark_dataSpace_Projet
python run.py
```

### ❌ "WinError 5: Access is denied" (lors de l'écriture Parquet)

```bash
# Solution: Exécuter avec --clean pour nettoyer les fichiers verrouillés
python run.py --clean
```

### ❌ "DataFrame is highly fragmented" (Warning pandas)

```
⚠️ This is a performance warning, not an error
Le pipeline continue et fonctionne correctement
La prochaine version optimisera pd.concat
```

### ❌ "Parquet file not found"

```bash
# Solution: Vérifier que Bronze a été exécuté
python run.py --bronze

# Vérifier les fichiers
ls data/warehouse/bronze/*/data.parquet
```

### 🔍 Déboguer un job spécifique

```bash
# Exécuter directement avec output verbose
.\venv_spark\Scripts\python.exe -u src/jobs/02_silver_clean.py

# Checker les erreurs stderr
python run.py 2>&1 | tee pipeline.log
```

---

## 📝 Licence

Ce projet est fourni à titre éducatif et professionnel.  
Les données sources proviennent de :
- **RTE** (france_time_series.csv)
- **Eurostat** (eurostat_electricity_france.csv)
- **Open Data Réseaux Énergies** (renewable_power_plants_FR.csv)

---

## 🤝 Contribution

Pour contribuer :

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📞 Support

Pour toute question ou problème :

1. Vérifier les logs : `pipeline.log`
2. Consulter la section [Troubleshooting](#️-troubleshooting)
3. Vérifier la configuration : `conf/config.yaml`
4. Relancer avec `--clean` : `python run.py --clean`

---

## 📅 Roadmap

### Phase 1 ✅
- [x] Bronze layer (ingestion)
- [x] Silver layer (nettoyage)
- [x] Gold layer (star schema)
- [x] Orchestrateur

### Phase 2 (À venir)
- [ ] Airflow DAG pour scheduling
- [ ] Tests unitaires et d'intégration
- [ ] Monitoring et alertes
- [ ] Incremental loading

### Phase 3 (Futur)
- [ ] Real-time streaming
- [ ] dbt integration
- [ ] ML pipeline (forecasting)

---

**Made with ❤️ for Energy Data in France**

*Dernière mise à jour: 2026-01-11*
