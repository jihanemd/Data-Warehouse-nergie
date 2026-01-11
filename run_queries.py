"""
Script Python pour exécuter les requêtes SQL
"""
import psycopg2
import pandas as pd

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "dw_energie_france"
DB_USER = "postgres"
DB_PASSWORD = "jihane"

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

# Requête 1: Production par type d'énergie
query1 = """
SELECT 
    e.energy_type_name,
    COUNT(*) as nb_jours,
    ROUND(AVG(f.value_mw)::numeric, 2) as production_moyenne_mw,
    ROUND(MAX(f.value_mw)::numeric, 2) as production_max_mw,
    ROUND(MIN(f.value_mw)::numeric, 2) as production_min_mw
FROM gold.fact_energy_production f
JOIN gold.dim_energy_type e ON f.energy_type_id = e.energy_type_id
GROUP BY e.energy_type_id, e.energy_type_name
ORDER BY production_moyenne_mw DESC;
"""

print("📊 Requête 1: Production par type d'énergie")
print("=" * 80)
df = pd.read_sql(query1, conn)
print(df.to_string(index=False))
print()

# Requête 2: Top installations
query2 = """
SELECT 
    plant_name,
    technology,
    region,
    ROUND(capacity_mw::numeric, 2) as capacite_mw
FROM gold.dim_plant
WHERE capacity_mw > 0
ORDER BY capacity_mw DESC
LIMIT 10;
"""

print("📊 Requête 2: Top 10 installations par capacité")
print("=" * 80)
df = pd.read_sql(query2, conn)
print(df.to_string(index=False))
print()

# Requête 3: Production par année
query3 = """
SELECT 
    d.year,
    e.energy_type_name,
    ROUND(AVG(f.value_mw)::numeric, 2) as mw_moyen,
    ROUND(SUM(f.value_mw)::numeric, 0) as mwh_total
FROM gold.fact_energy_production f
JOIN gold.dim_date d ON f.date_id = d.date_id
JOIN gold.dim_energy_type e ON f.energy_type_id = e.energy_type_id
GROUP BY d.year, e.energy_type_id, e.energy_type_name
ORDER BY d.year DESC, mw_moyen DESC;
"""

print("📊 Requête 3: Production par année et type")
print("=" * 80)
df = pd.read_sql(query3, conn)
print(df.to_string(index=False))
print()

# Requête 4: Capacité par région
query4 = """
SELECT 
    p.region,
    p.technology,
    COUNT(*) as nb_installations,
    ROUND(SUM(p.capacity_mw)::numeric, 2) as capacite_totale_mw
FROM gold.dim_plant p
WHERE p.region IS NOT NULL
GROUP BY p.region, p.technology
ORDER BY capacite_totale_mw DESC
LIMIT 15;
"""

print("📊 Requête 4: Top régions par capacité")
print("=" * 80)
df = pd.read_sql(query4, conn)
print(df.to_string(index=False))
print()

conn.close()

print("✅ Requêtes exécutées avec succès!")
