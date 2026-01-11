"""
Script Python pour nettoyer et recharger PostgreSQL
"""
import psycopg2
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

# Configuration
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "dw_energie_france"
DB_USER = "postgres"
DB_PASSWORD = "jihane"
SQL_FILE = "sql/schema_gold_simple.sql"

print("🐘 Rechargement complet du schéma PostgreSQL...")
print()

try:
    # 1. Nettoyer les tables existantes
    print("🧹 Étape 1: Suppression des tables existantes...")
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.set_session(autocommit=True)
    cursor = conn.cursor()
    
    # Supprimer les tables dans le bon ordre
    drop_sql = """
    DROP TABLE IF EXISTS gold.fact_monthly_summary CASCADE;
    DROP TABLE IF EXISTS gold.fact_renewable_capacity CASCADE;
    DROP TABLE IF EXISTS gold.fact_energy_production CASCADE;
    DROP TABLE IF EXISTS gold.dim_plant CASCADE;
    DROP TABLE IF EXISTS gold.dim_location CASCADE;
    DROP TABLE IF EXISTS gold.dim_energy_type CASCADE;
    DROP TABLE IF EXISTS gold.dim_date CASCADE;
    DROP SCHEMA IF EXISTS gold CASCADE;
    """
    
    cursor.execute(drop_sql)
    print("✅ Tables supprimées")
    cursor.close()
    conn.close()
    
    # 2. Créer le schéma
    print()
    print("📝 Étape 2: Création du schéma...")
    
    sql_path = Path(SQL_FILE)
    if not sql_path.exists():
        print(f"❌ Fichier SQL non trouvé: {SQL_FILE}")
        exit(1)
    
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.set_session(autocommit=True)
    cursor = conn.cursor()
    
    cursor.execute(sql_script)
    print("✅ Schéma créé!")
    
    cursor.close()
    conn.close()
    
    # 3. Charger les données Parquet
    print()
    print("📤 Étape 3: Chargement des données...")
    
    conn_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(conn_string)
    
    gold_path = Path("data/warehouse/gold")
    
    tables = {
        'dim_date': gold_path / 'dim_date' / 'data.parquet',
        'dim_energy_type': gold_path / 'dim_energy_type' / 'data.parquet',
        'dim_location': gold_path / 'dim_location' / 'data.parquet',
        'dim_plant': gold_path / 'dim_plant' / 'data.parquet',
        'fact_energy_production': gold_path / 'fact_energy_production' / 'data.parquet',
        'fact_renewable_capacity': gold_path / 'fact_renewable_capacity' / 'data.parquet',
    }
    
    for table_name, parquet_path in tables.items():
        try:
            if not parquet_path.exists():
                print(f"  ⚠️  {table_name:30s}: Fichier manquant")
                continue
            
            df = pd.read_parquet(parquet_path)
            print(f"  📥 {table_name:30s} ({len(df):>7,} lignes)...", end="", flush=True)
            
            # Charger dans PostgreSQL
            df.to_sql(
                table_name,
                engine,
                schema='gold',
                if_exists='append',
                index=False,
                method='multi',
                chunksize=1000
            )
            
            print(f" ✅")
            
        except Exception as e:
            print(f" ❌ {str(e)[:40]}")
    
    engine.dispose()
    
    # 4. Vérifier
    print()
    print("📊 Étape 4: Vérification...")
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    total_rows = 0
    for table_name in tables.keys():
        cursor.execute(f"SELECT COUNT(*) FROM gold.{table_name}")
        count = cursor.fetchone()[0]
        total_rows += count
        icon = "✅" if count > 0 else "⚠️"
        print(f"  {icon} {table_name:30s} → {count:>10,} lignes")
    
    cursor.close()
    conn.close()
    
    print()
    print(f"📈 Total: {total_rows:,} lignes chargées")
    print()
    print("🎉 Data Warehouse PostgreSQL prêt!")
    print()
    print("✨ Vous pouvez maintenant:")
    print("   • Connecter PostgreSQL à Power BI / Tableau")
    print("   • Faire des requêtes SQL directement")
    print("   • Créer des dashboards analytiques")
    
except Exception as e:
    print(f"❌ Erreur: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
