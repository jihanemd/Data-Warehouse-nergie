"""
Script pour préparer et charger les données avec IDs
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine

gold_path = Path("data/warehouse/gold")

# Configuration PostgreSQL
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "dw_energie_france"
DB_USER = "postgres"
DB_PASSWORD = "jihane"

conn_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(conn_string)

print("🐘 Préparation et chargement des données...")
print()

# 1. Charger les fact tables existantes
print("📥 Lecture des Parquet...")

df_prod = pd.read_parquet(gold_path / 'fact_energy_production' / 'data.parquet')
df_cap = pd.read_parquet(gold_path / 'fact_renewable_capacity' / 'data.parquet')

print(f"  ✅ fact_energy_production: {len(df_prod)} lignes")
print(f"  ✅ fact_renewable_capacity: {len(df_cap)} lignes")

# 2. Ajouter les IDs manquants
print()
print("🔧 Ajout des IDs...")

df_prod['production_id'] = range(1, len(df_prod) + 1)
df_cap['capacity_id'] = range(1, len(df_cap) + 1)

# 3. Charger dans PostgreSQL
print()
print("📤 Chargement dans PostgreSQL...")

try:
    df_prod.to_sql(
        'fact_energy_production',
        engine,
        schema='gold',
        if_exists='append',
        index=False,
        method='multi',
        chunksize=1000
    )
    print(f"  ✅ fact_energy_production: {len(df_prod)} lignes chargées")
except Exception as e:
    print(f"  ❌ Erreur: {str(e)[:60]}")

try:
    df_cap.to_sql(
        'fact_renewable_capacity',
        engine,
        schema='gold',
        if_exists='append',
        index=False,
        method='multi',
        chunksize=1000
    )
    print(f"  ✅ fact_renewable_capacity: {len(df_cap)} lignes chargées")
except Exception as e:
    print(f"  ❌ Erreur: {str(e)[:60]}")

engine.dispose()

# 4. Vérifier
print()
print("📊 Vérification finale...")

conn = engine.connect()

tables = {
    'dim_date': 'should be 4383',
    'dim_energy_type': 'should be 5',
    'dim_location': 'should be 31',
    'dim_plant': 'should be 9744',
    'fact_energy_production': f'should be {len(df_prod)}',
    'fact_renewable_capacity': f'should be {len(df_cap)}',
}

for table_name, desc in tables.items():
    result = conn.execute(f"SELECT COUNT(*) FROM gold.{table_name}")
    count = result.fetchone()[0]
    icon = "✅" if count > 0 else "⚠️"
    print(f"  {icon} {table_name:30s} → {count:>10,} lignes ({desc})")

conn.close()

print()
print("🎉 Data Warehouse PostgreSQL complet!")
print()
print("✨ Prochaines étapes:")
print("   • Connecter à Power BI / Tableau")
print("   • Requêtes SQL directes")
print("   • Créer des dashboards")
