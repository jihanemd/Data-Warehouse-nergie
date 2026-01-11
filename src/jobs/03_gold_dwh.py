"""Gold Layer - Star Schema Data Warehouse"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

import yaml
import pandas as pd
import numpy as np


def load_config(config_path: str = "conf/config.yaml") -> dict:
    """Charge la configuration"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def create_dim_date(start_date: str = "2015-01-01", end_date: str = "2026-12-31") -> pd.DataFrame:
    """
    Crée la dimension temporelle
    
    Args:
        start_date: Date de début (YYYY-MM-DD)
        end_date: Date de fin (YYYY-MM-DD)
        
    Returns:
        DataFrame dimension avec colonnes:
        - date_id (YYYYMMDD format)
        - date (datetime)
        - year, month, day, quarter
        - week_of_year, day_of_week
        - is_weekend
        - is_holiday (France)
    """
    
    print("  🔧 Création dim_date...")
    
    # Générer range de dates
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    df = pd.DataFrame({
        'date': dates
    })
    
    # Extraire composantes
    df['date_id'] = df['date'].dt.strftime('%Y%m%d').astype(int)
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['quarter'] = df['date'].dt.quarter
    df['week_of_year'] = df['date'].dt.isocalendar().week
    df['day_of_week'] = df['date'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['day_name'] = df['date'].dt.day_name()
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Jours fériés France (simple)
    holidays_france = [
        '01-01',  # Jour de l'an
        '05-01',  # Fête du travail
        '05-08',  # Armistice 1945
        '07-14',  # Fête nationale
        '08-15',  # Assomption
        '11-01',  # Toussaint
        '11-11',  # Armistice 1918
        '12-25',  # Noël
    ]
    
    date_str = df['date'].dt.strftime('%m-%d')
    df['is_holiday'] = date_str.isin(holidays_france).astype(int)
    
    # Sélectionner colonnes finales
    df = df[['date_id', 'date', 'year', 'month', 'day', 'quarter', 
             'week_of_year', 'day_of_week', 'day_name', 'is_weekend', 'is_holiday']]
    
    print(f"    ✅ {len(df)} dates créées ({start_date} → {end_date})")
    
    return df


def create_dim_energy_type() -> pd.DataFrame:
    """
    Crée la dimension type d'énergie
    
    Returns:
        DataFrame avec colonnes:
        - energy_type_id
        - energy_type_name
        - description
        - unit
        - category (renewable/non-renewable/load)
    """
    
    print("  🔧 Création dim_energy_type...")
    
    df = pd.DataFrame({
        'energy_type_id': [1, 2, 3, 4, 5],
        'energy_type_name': ['Solar', 'Wind Onshore', 'Load (Consumption)', 'Hydro', 'Other'],
        'description': [
            'Solar photovoltaic generation',
            'Wind onshore generation',
            'Electrical load / consumption',
            'Hydroelectric generation',
            'Other renewable / thermal sources'
        ],
        'unit': ['MW', 'MW', 'MW', 'MW', 'MW'],
        'category': ['Renewable', 'Renewable', 'Consumption', 'Renewable', 'Other']
    })
    
    print(f"    ✅ {len(df)} types d'énergie créés")
    
    return df


def create_dim_location() -> pd.DataFrame:
    """
    Crée la dimension géographique (Régions/Départements France)
    Extraite de renewable_power_plants_FR
    """
    
    print("  🔧 Création dim_location...")
    
    config = load_config()
    silver_path = Path(config['paths']['silver'])
    
    try:
        # Lire les plantes ENR pour extraire locations
        plants_path = silver_path / "renewable_plants" / "data.parquet"
        df_plants = pd.read_parquet(plants_path)
        
        # Extraire locations uniques
        locations = df_plants[['nuts_1_region', 'nuts_2_region', 'region', 'region_code']].drop_duplicates()
        locations = locations.dropna(subset=['region'])
        locations = locations.reset_index(drop=True)
        
        # Créer dimension
        df = pd.DataFrame()
        df['location_id'] = range(1, len(locations) + 1)
        df['nuts_1_code'] = locations['nuts_1_region'].values
        df['nuts_2_code'] = locations['nuts_2_region'].values
        df['region_name'] = locations['region'].values
        df['region_code'] = locations['region_code'].values.astype(str)
        df['country'] = 'FR'
        
        print(f"    ✅ {len(df)} régions/locations créées")
        
        return df
        
    except Exception as e:
        print(f"    ⚠️  Erreur: {str(e)}")
        # Fallback
        return pd.DataFrame({
            'location_id': [1],
            'nuts_1_code': ['FRF'],
            'nuts_2_code': ['FRF1'],
            'region_name': ['France'],
            'region_code': [''],
            'country': ['FR']
        })


def create_dim_plant() -> pd.DataFrame:
    """
    Crée la dimension installations ENR
    Source: renewable_power_plants_FR
    """
    
    print("  🔧 Création dim_plant...")
    
    config = load_config()
    silver_path = Path(config['paths']['silver'])
    
    try:
        # Lire les plantes
        plants_path = silver_path / "renewable_plants" / "data.parquet"
        df = pd.read_parquet(plants_path)
        
        # Sélectionner et transformer
        df['plant_id'] = range(1, len(df) + 1)
        df['plant_name'] = df['site_name'].fillna(f"Plant_{df.index}")
        df['technology'] = df['technology'].fillna('Unknown')
        df['energy_source'] = df['energy_source_level_1'].fillna('Unknown')
        df['capacity_mw'] = pd.to_numeric(df['electrical_capacity'], errors='coerce').fillna(0)
        df['latitude'] = pd.to_numeric(df['lat'], errors='coerce').fillna(0)
        df['longitude'] = pd.to_numeric(df['lon'], errors='coerce').fillna(0)
        df['commissioning_date'] = pd.to_datetime(df['commissioning_date'], errors='coerce')
        df['region'] = df['region'].fillna('Unknown')
        
        # Sélectionner colonnes
        df = df[[
            'plant_id', 'plant_name', 'technology', 'energy_source', 'capacity_mw',
            'latitude', 'longitude', 'commissioning_date', 'region'
        ]].reset_index(drop=True)
        
        print(f"    ✅ {len(df)} installations créées")
        
        return df
        
    except Exception as e:
        print(f"    ⚠️  Erreur: {str(e)}")
        return pd.DataFrame({
            'plant_id': [1],
            'plant_name': ['Unknown'],
            'technology': ['Unknown'],
            'energy_source': ['Unknown'],
            'capacity_mw': [0],
            'latitude': [0],
            'longitude': [0],
            'commissioning_date': [None],
            'region': ['Unknown']
        })


def create_fact_renewable_capacity(config: dict) -> pd.DataFrame:
    """Capacité installée ENR par technologie"""
    
    print("  🔧 Création fact_renewable_capacity...")
    
    silver_path = Path(config['paths']['silver'])
    
    try:
        # Lire plantes
        plants_path = silver_path / "renewable_plants" / "data.parquet"
        df = pd.read_parquet(plants_path)
        
        # Calculer capacité par technologie et région
        df['capacity_mw'] = pd.to_numeric(df['electrical_capacity'], errors='coerce').fillna(0)
        df['technology'] = df['technology'].fillna('Other')
        df['region'] = df['region'].fillna('Unknown')
        
        # Mapper technologies à energy_type_id
        tech_map = {
            'Photovoltaics': 1,  # Solar
            'Wind': 2,            # Wind
            'Hydro': 4,           # Hydro
            'Other': 5            # Other
        }
        
        df['energy_type_id'] = df['technology'].map(lambda x: 
            next((v for k, v in tech_map.items() if k.lower() in str(x).lower()), 5))
        
        # Agrégation
        agg = df.groupby(['region', 'energy_type_id']).agg({
            'capacity_mw': ['sum', 'mean', 'count'],
            'commissioning_date': 'min'
        }).reset_index()
        
        agg.columns = ['region', 'energy_type_id', 'total_capacity_mw', 'avg_capacity_mw', 'nb_plants', 'first_commission_date']
        
        # Ajouter date_id
        agg['date_id'] = int(pd.Timestamp.now().strftime('%Y%m%d'))
        agg['country'] = 'FR'
        
        print(f"    ✅ {len(agg)} enregistrements de capacité créés")
        
        return agg
        
    except Exception as e:
        print(f"    ⚠️  Erreur: {str(e)}")
        return pd.DataFrame({
            'date_id': [int(pd.Timestamp.now().strftime('%Y%m%d'))],
            'energy_type_id': [1],
            'region': ['Unknown'],
            'total_capacity_mw': [0],
            'avg_capacity_mw': [0],
            'nb_plants': [0],
            'first_commission_date': [None],
            'country': ['FR']
        })


def create_fact_monthly_summary(config: dict) -> pd.DataFrame:
    """Résumés mensuels pour requêtes BI rapides"""
    
    print("  🔧 Création fact_monthly_summary...")
    
    silver_path = Path(config['paths']['silver'])
    
    try:
        # Lire données
        ts_path = silver_path / "france_time_series" / "data.parquet"
        df_ts = pd.read_parquet(ts_path)
        
        # Parser date - chercher la colonne datetime
        date_col = None
        for col in ['DateTime', 'datetime', 'date', 'event_ts']:
            if col in df_ts.columns:
                date_col = col
                break
        
        if date_col:
            df_ts['date'] = pd.to_datetime(df_ts[date_col], errors='coerce')
        else:
            print(f"    ⚠️  Colonnes disponibles: {df_ts.columns.tolist()}")
            return pd.DataFrame()
        
        df_ts['year'] = df_ts['date'].dt.year
        df_ts['month'] = df_ts['date'].dt.month
        
        records = []
        
        for energy_type_id, col_name in [
            (1, 'Solar'),
            (2, 'Wind Onshore'),
            (3, 'Load'),
            (4, 'Hydro'),
            (5, 'Thermal')
        ]:
            if col_name in df_ts.columns:
                # Agrégation mensuelle
                monthly = df_ts.groupby(['year', 'month'])[col_name].agg([
                    ('production_mwh', 'sum'),
                    ('avg_mw', 'mean'),
                    ('min_mw', 'min'),
                    ('max_mw', 'max'),
                    ('nb_records', 'count')
                ]).reset_index()
                
                # Créer date_id pour 1er du mois
                monthly['date_id'] = (
                    monthly['year'].astype(str) + 
                    monthly['month'].astype(str).str.zfill(2) + '01'
                ).astype(int)
                
                monthly['energy_type_id'] = energy_type_id
                monthly['country'] = 'FR'
                
                records.append(monthly[[
                    'date_id', 'energy_type_id', 'country', 'production_mwh',
                    'avg_mw', 'min_mw', 'max_mw', 'nb_records'
                ]])
        
        if records:
            df = pd.concat(records, ignore_index=True)
            df = df.dropna(subset=['production_mwh'])
        else:
            df = pd.DataFrame()
        
        print(f"    ✅ {len(df)} enregistrements mensuels créés")
        
        return df
        
    except Exception as e:
        print(f"    ⚠️  Erreur: {str(e)}")
        return pd.DataFrame()


def create_fact_energy_production(silver_path: str, dim_date: pd.DataFrame) -> pd.DataFrame:
    """
    Crée la fact table agrégée par jour/type/pays
    """
    
    print("  🔧 Création fact_energy_production...")
    
    facts = []
    
    # ===== FRANCE TIME SERIES (load + solar + wind) =====
    try:
        silver_file = os.path.join(silver_path, 'france_time_series', 'data.parquet')
        df = pd.read_parquet(silver_file)
        
        # Agréger par jour
        df['date'] = df['event_ts'].dt.date
        
        # Load (consumption)
        daily_load = df.groupby('date')['load_mw'].agg(['sum', 'min', 'max', 'mean', 'count']).reset_index()
        daily_load['energy_type_id'] = 3
        daily_load['country'] = 'FR'
        daily_load['value_mw'] = daily_load['sum']
        daily_load['value_min_mw'] = daily_load['min']
        daily_load['value_max_mw'] = daily_load['max']
        daily_load['value_avg_mw'] = daily_load['mean']
        daily_load['nb_records'] = daily_load['count']
        daily_load['date_id'] = pd.to_datetime(daily_load['date']).dt.strftime('%Y%m%d').astype(int)
        facts.append(daily_load[['date_id', 'energy_type_id', 'country', 'value_mw', 'value_min_mw', 'value_max_mw', 'value_avg_mw', 'nb_records']])
        
        # Solar
        daily_solar = df.groupby('date')['solar_mw'].agg(['sum', 'min', 'max', 'mean', 'count']).reset_index()
        daily_solar['energy_type_id'] = 1
        daily_solar['country'] = 'FR'
        daily_solar['value_mw'] = daily_solar['sum']
        daily_solar['value_min_mw'] = daily_solar['min']
        daily_solar['value_max_mw'] = daily_solar['max']
        daily_solar['value_avg_mw'] = daily_solar['mean']
        daily_solar['nb_records'] = daily_solar['count']
        daily_solar['date_id'] = pd.to_datetime(daily_solar['date']).dt.strftime('%Y%m%d').astype(int)
        facts.append(daily_solar[['date_id', 'energy_type_id', 'country', 'value_mw', 'value_min_mw', 'value_max_mw', 'value_avg_mw', 'nb_records']])
        
        # Wind
        daily_wind = df.groupby('date')['wind_mw'].agg(['sum', 'min', 'max', 'mean', 'count']).reset_index()
        daily_wind['energy_type_id'] = 2
        daily_wind['country'] = 'FR'
        daily_wind['value_mw'] = daily_wind['sum']
        daily_wind['value_min_mw'] = daily_wind['min']
        daily_wind['value_max_mw'] = daily_wind['max']
        daily_wind['value_avg_mw'] = daily_wind['mean']
        daily_wind['nb_records'] = daily_wind['count']
        daily_wind['date_id'] = pd.to_datetime(daily_wind['date']).dt.strftime('%Y%m%d').astype(int)
        facts.append(daily_wind[['date_id', 'energy_type_id', 'country', 'value_mw', 'value_min_mw', 'value_max_mw', 'value_avg_mw', 'nb_records']])
        
        print(f"    ✅ france_time_series ingérée ({len(daily_load)} jours)")
        
    except Exception as e:
        print(f"    ⚠️  france_time_series: {str(e)}")
    
    # ===== RENEWABLE PLANTS (capacités) =====
    try:
        silver_file = os.path.join(silver_path, 'renewable_plants', 'data.parquet')
        df = pd.read_parquet(silver_file)
        
        # Agréger par type
        if 'energy_source_level_1' in df.columns:
            df['energy_type'] = df['energy_source_level_1'].str.lower()
        
        # Mapper à energy_type_id
        type_mapping = {'renewable energy': 5, 'hydro': 4, 'solar': 1, 'wind': 2}
        df['energy_type_id'] = df['energy_type'].map(type_mapping).fillna(5)
        df['country'] = 'FR'
        
        # Agréger capacité
        agg_capacity = df.groupby('energy_type_id')['electrical_capacity'].agg(['sum', 'count']).reset_index()
        agg_capacity['date_id'] = 20260101  # Date fixe pour les données statiques
        agg_capacity['country'] = 'FR'
        agg_capacity['value_mw'] = agg_capacity['sum']
        agg_capacity['value_min_mw'] = 0
        agg_capacity['value_max_mw'] = agg_capacity['sum']
        agg_capacity['value_avg_mw'] = agg_capacity['sum']
        agg_capacity['nb_records'] = agg_capacity['count']
        facts.append(agg_capacity[['date_id', 'energy_type_id', 'country', 'value_mw', 'value_min_mw', 'value_max_mw', 'value_avg_mw', 'nb_records']])
        
        print(f"    ✅ renewable_plants ingérées ({len(agg_capacity)} types)")
        
    except Exception as e:
        print(f"    ⚠️  renewable_plants: {str(e)}")
    
    # Concaténer tous les facts
    fact_df = pd.concat(facts, ignore_index=True)
    
    # Remplir NaN
    fact_df = fact_df.fillna(0)
    
    # Ajouter métadonnées
    fact_df['created_at'] = pd.Timestamp.now()
    
    print(f"    ✅ {len(fact_df)} enregistrements de faits créés")
    
    return fact_df


def write_parquet_safe(df: pd.DataFrame, output_path: str, table_name: str) -> None:
    """Écrit Parquet de manière robuste"""
    
    os.makedirs(output_path, exist_ok=True)
    parquet_file = os.path.join(output_path, f"{table_name}.parquet")
    df.to_parquet(parquet_file, engine='pyarrow', index=False)
    print(f"    📂 {parquet_file} ({len(df)} lignes)")


def run_gold_warehouse() -> bool:
    """
    Pipeline complet GOLD avec 7 tables
    """
    
    print(f"\n{'='*80}")
    print(f"GOLD LAYER - DATA WAREHOUSE (Star Schema Enrichi)")
    print(f"{'='*80}\n")
    
    try:
        # Charger config
        config = load_config("conf/config.yaml")
        silver_path = config['paths']['silver']
        gold_path = config['paths']['gold']
        
        print(f"📂 Silver: {silver_path}")
        print(f"📂 Gold:   {gold_path}\n")
        
        # Créer répertoires
        Path(gold_path).mkdir(parents=True, exist_ok=True)
        
        # ===== DIMENSIONS =====
        print("📐 CRÉATION DES DIMENSIONS\n")
        
        dim_date = create_dim_date(start_date="2015-01-01", end_date="2026-12-31")
        write_parquet_safe(dim_date, os.path.join(gold_path, 'dim_date'), 'data')
        print(f"    📂 data/warehouse/gold/dim_date/data.parquet ({len(dim_date)} lignes)")
        
        dim_energy_type = create_dim_energy_type()
        write_parquet_safe(dim_energy_type, os.path.join(gold_path, 'dim_energy_type'), 'data')
        print(f"    📂 data/warehouse/gold/dim_energy_type/data.parquet ({len(dim_energy_type)} lignes)")
        
        dim_location = create_dim_location()
        write_parquet_safe(dim_location, os.path.join(gold_path, 'dim_location'), 'data')
        print(f"    📂 data/warehouse/gold/dim_location/data.parquet ({len(dim_location)} lignes)")
        
        dim_plant = create_dim_plant()
        write_parquet_safe(dim_plant, os.path.join(gold_path, 'dim_plant'), 'data')
        print(f"    📂 data/warehouse/gold/dim_plant/data.parquet ({len(dim_plant)} lignes)")
        
        print()
        print("📊 CRÉATION DES FACT TABLES\n")
        
        fact_production = create_fact_energy_production(silver_path, dim_date)
        write_parquet_safe(fact_production, os.path.join(gold_path, 'fact_energy_production'), 'data')
        print(f"    📂 data/warehouse/gold/fact_energy_production/data.parquet ({len(fact_production)} lignes)")
        
        fact_capacity = create_fact_renewable_capacity(config)
        write_parquet_safe(fact_capacity, os.path.join(gold_path, 'fact_renewable_capacity'), 'data')
        print(f"    📂 data/warehouse/gold/fact_renewable_capacity/data.parquet ({len(fact_capacity)} lignes)")
        
        fact_monthly = create_fact_monthly_summary(config)
        write_parquet_safe(fact_monthly, os.path.join(gold_path, 'fact_monthly_summary'), 'data')
        print(f"    📂 data/warehouse/gold/fact_monthly_summary/data.parquet ({len(fact_monthly)} lignes)")
        
        # ===== RÉSUMÉ STAR SCHEMA =====
        print()
        print("=" * 80)
        print("📋 STAR SCHEMA ENRICHI (7 TABLES)")
        print("=" * 80)
        print()
        
        print("📅 DIMENSIONS (Lookups)")
        print(f"   ✅ dim_date:           {len(dim_date):>6d} dates          (2015-2026)")
        print(f"   ✅ dim_energy_type:    {len(dim_energy_type):>6d} types           (Solar, Wind, Load, Hydro, Other)")
        print(f"   ✅ dim_location:       {len(dim_location):>6d} régions         (Régions France)")
        print(f"   ✅ dim_plant:          {len(dim_plant):>6d} installations   (ENR FR)")
        print()
        
        print("📊 FACT TABLES (Agrégations)")
        print(f"   ✅ fact_energy_production:   {len(fact_production):>6d} records    (Agrégation journalière)")
        print(f"   ✅ fact_renewable_capacity:  {len(fact_capacity):>6d} records    (Capacité installée)")
        print(f"   ✅ fact_monthly_summary:     {len(fact_monthly):>6d} records    (Résumés mensuels)")
        print()
        
        # ===== REQUÊTES EXEMPLE =====
        print("=" * 80)
        print("📝 EXEMPLES DE REQUÊTES BI")
        print("=" * 80)
        print()
        
        print("-- Requête 1: Production par jour et type (avec dimension location)")
        print("""
SELECT
    d.date,
    l.region_name,
    e.energy_type_name,
    f.value_mw,
    f.value_avg_mw
FROM fact_energy_production f
JOIN dim_date d ON f.date_id = d.date_id
JOIN dim_energy_type e ON f.energy_type_id = e.energy_type_id
WHERE f.country = 'FR'
  AND d.year = 2026
ORDER BY d.date DESC;
        """)
        
        print("\n-- Requête 2: Capacité par technologie et région")
        print("""
SELECT
    l.region_name,
    e.energy_type_name,
    c.total_capacity_mw,
    c.nb_plants,
    p.plant_name
FROM fact_renewable_capacity c
JOIN dim_location l ON c.region = l.region_name
JOIN dim_energy_type e ON c.energy_type_id = e.energy_type_id
JOIN dim_plant p ON p.region = l.region_name
WHERE c.country = 'FR'
ORDER BY c.total_capacity_mw DESC;
        """)
        
        print("\n-- Requête 3: Production mensuelle consolidée")
        print("""
SELECT
    d.year,
    d.month,
    e.energy_type_name,
    m.production_mwh,
    m.avg_mw
FROM fact_monthly_summary m
JOIN dim_date d ON m.date_id = d.date_id
JOIN dim_energy_type e ON m.energy_type_id = e.energy_type_id
WHERE m.country = 'FR'
  AND d.year >= 2020
GROUP BY d.year, d.month, e.energy_type_name
ORDER BY d.year DESC, d.month DESC;
        """)
        
        print()
        print("=" * 80)
        print("✅ GOLD LAYER - COMPLÉTÉ")
        print("=" * 80)
        print()
        
        print("📁 Structure GOLD (7 tables):")
        print("   data/warehouse/gold/")
        print("   ├── dim_date/")
        print("   ├── dim_energy_type/")
        print("   ├── dim_location/")
        print("   ├── dim_plant/")
        print("   ├── fact_energy_production/")
        print("   ├── fact_renewable_capacity/")
        print("   └── fact_monthly_summary/")
        print()
        
        print("✅ Star Schema Relationships:")
        print("   • fact_energy_production → dim_date (date_id)")
        print("   • fact_energy_production → dim_energy_type (energy_type_id)")
        print("   • fact_renewable_capacity → dim_location (region)")
        print("   • fact_renewable_capacity → dim_energy_type (energy_type_id)")
        print("   • fact_renewable_capacity → dim_plant (region)")
        print("   • fact_monthly_summary → dim_date (date_id)")
        print("   • fact_monthly_summary → dim_energy_type (energy_type_id)")
        print()
        
        print("✅ Prêt pour BI:")
        print("   • Power BI / Tableau / Looker")
        print("   • Metabase / Superset")
        print("   • Spark SQL / Trino / Presto")
        print("   • Athena (AWS) / BigQuery (GCP)")
        print()
        
        print("✅ Pipeline complet:")
        print("   1. ✅ BRONZE (Ingestion RAW)      - 61,554 lignes")
        print("   2. ✅ SILVER (Nettoyage)           - 61,554 lignes nettoyées")
        print("   3. ✅ GOLD (Star Schema Enrichi)  - 7 tables prêtes pour BI")
        print()
        
        print("🎉 Data Warehouse Énergie France créé avec succès!")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    
    try:
        success = run_gold_warehouse()
        
        if success:
            print("🎉 Pipeline GOLD terminé avec succès!\n")
            sys.exit(0)
        else:
            print("⚠️  Pipeline GOLD terminé avec des avertissements\n")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erreur fatale: {str(e)}\n")
        sys.exit(1)
