"""
📘 SILVER LAYER - Nettoyage & Data Quality
─────────────────────────────────────────
Objectif: Transformer les données BRONZE en données fiables prêtes pour l'analyse
- Nettoyage technique (types, trim, déduplication)
- Nettoyage métier (valeurs négatives, outliers, timestamps cohérents)
- Data Quality: produire 2 sorties
  • silver/ : données valides
  • dq/rejects/ : données rejetées avec motif

Architecture:
  bronze/ (Parquet brut)
    ↓
  silver/ (Parquet nettoyé, typé)
    ↓
  dq/rejects/ (Parquet rejeté)
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

import yaml
import pandas as pd
import numpy as np


def load_config(config_path: str = "conf/config.yaml") -> dict:
    """Charge la configuration"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def clean_france_time_series(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Nettoie france_time_series.csv
    
    Colonnes: utc_timestamp (str) → event_ts (datetime)
              FR_load_actual_entsoe_transparency (str) → load_mw (float)
              FR_solar_generation_actual (str) → solar_mw (float)
              FR_wind_onshore_generation_actual (str) → wind_mw (float)
    
    Returns:
        Tuple[valid_df, reject_df]
    """
    
    df = df.copy()
    reject_reasons = []
    
    print("  🔧 Nettoyage france_time_series...")
    
    # 1. Convertir timestamp
    try:
        df['event_ts'] = pd.to_datetime(df['utc_timestamp'], errors='coerce')
    except:
        df['event_ts'] = pd.NaT
    
    # 2. Convertir colonnes numériques
    for col in ['FR_load_actual_entsoe_transparency', 'FR_solar_generation_actual', 'FR_wind_onshore_generation_actual']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Renommer colonnes
    df = df.rename(columns={
        'FR_load_actual_entsoe_transparency': 'load_mw',
        'FR_solar_generation_actual': 'solar_mw',
        'FR_wind_onshore_generation_actual': 'wind_mw'
    })
    
    # 3. Appliquer règles de validation
    # Règle 1: Timestamp obligatoire
    valid = df[df['event_ts'].notna()].copy()
    invalid_ts = df[df['event_ts'].isna()].copy()
    if len(invalid_ts) > 0:
        invalid_ts['reject_reason'] = 'Timestamp invalide ou manquant'
        reject_reasons.append(invalid_ts)
    
    df = valid
    
    # Règle 2: Valeurs négatives (impossible physiquement)
    for col in ['load_mw', 'solar_mw', 'wind_mw']:
        if col in df.columns:
            invalid = df[(df[col] < 0) & (df[col].notna())].copy()
            if len(invalid) > 0:
                invalid['reject_reason'] = f'{col} < 0 (impossible physiquement)'
                reject_reasons.append(invalid)
            df = df[~((df[col] < 0) & (df[col].notna()))]
    
    # Règle 3: Timestamp futur
    now = pd.Timestamp.now(tz='UTC')
    # Comparer sans timezone si nécessaire
    event_ts_naive = df['event_ts'].dt.tz_localize(None) if df['event_ts'].dt.tz is not None else df['event_ts']
    invalid = df[event_ts_naive > now.tz_localize(None)].copy()
    if len(invalid) > 0:
        invalid['reject_reason'] = f'Timestamp futur'
        reject_reasons.append(invalid)
    df = df[event_ts_naive <= now.tz_localize(None)]
    
    # 4. Déduplication par event_ts
    df = df.drop_duplicates(subset=['event_ts'], keep='first')
    
    # Ajouter colonnes métier
    df['country'] = 'FR'
    df['energy_type'] = 'mixed'  # Mix load + solar + wind
    
    # Sélectionner colonnes finales
    final_cols = ['event_ts', 'load_mw', 'solar_mw', 'wind_mw', 'country', 'energy_type', '_source_file', '_ingest_ts', '_ingest_date']
    df = df[[c for c in final_cols if c in df.columns]]
    
    # Concaténer tous les rejets
    reject_df = pd.concat(reject_reasons, ignore_index=True) if reject_reasons else pd.DataFrame()
    
    print(f"    ✅ {len(df)} lignes valides | ❌ {len(reject_df)} rejetées")
    
    return df, reject_df


def clean_eurostat_electricity_france(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Nettoie eurostat_electricity_france.csv
    """
    
    df = df.copy()
    reject_reasons = []
    
    print("  🔧 Nettoyage eurostat_electricity_france...")
    
    # Convertir colonnes numériques
    for col in df.columns:
        if col not in ['_source_file', '_ingest_ts', '_ingest_date']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Déduplication
    df = df.drop_duplicates(keep='first')
    
    # Ajouter colonnes métier
    df['country'] = 'FR'
    
    reject_df = pd.DataFrame()
    
    print(f"    ✅ {len(df)} lignes valides | ❌ {len(reject_df)} rejetées")
    
    return df, reject_df


def clean_time_series_60min(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Nettoie time_series_60min_sample.csv
    Données haute fréquence (toutes les heures)
    """
    
    df = df.copy()
    reject_reasons = []
    
    print("  🔧 Nettoyage time_series_60min_sample...")
    
    # Convertir timestamp
    timestamp_col = [c for c in df.columns if 'time' in c.lower()][0] if any('time' in c.lower() for c in df.columns) else df.columns[0]
    try:
        df['event_ts'] = pd.to_datetime(df[timestamp_col], errors='coerce')
    except:
        df['event_ts'] = pd.NaT
    
    # Valider timestamp
    valid = df[df['event_ts'].notna()].copy()
    invalid = df[df['event_ts'].isna()].copy()
    if len(invalid) > 0:
        invalid['reject_reason'] = 'Timestamp invalide'
        reject_reasons.append(invalid)
    df = valid
    
    # Convertir colonnes numériques (sauf système)
    for col in df.columns:
        if col not in ['_source_file', '_ingest_ts', '_ingest_date', 'event_ts', timestamp_col]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Supprimer colonnes timestamp originales
    df = df.drop(columns=[timestamp_col], errors='ignore')
    
    # Ajouter colonnes métier
    df['country'] = 'FR'
    
    reject_df = pd.concat(reject_reasons, ignore_index=True) if reject_reasons else pd.DataFrame()
    
    print(f"    ✅ {len(df)} lignes valides | ❌ {len(reject_df)} rejetées")
    
    return df, reject_df


def clean_renewable_power_plants(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Nettoie renewable_power_plants_FR.csv
    Données statiques de centrales
    """
    
    df = df.copy()
    reject_reasons = []
    
    print("  🔧 Nettoyage renewable_power_plants_FR...")
    
    # Convertir capacité électrique
    if 'electrical_capacity' in df.columns:
        df['electrical_capacity'] = pd.to_numeric(df['electrical_capacity'], errors='coerce')
        
        # Capacité doit être positive
        invalid = df[(df['electrical_capacity'] <= 0) & (df['electrical_capacity'].notna())].copy()
        if len(invalid) > 0:
            invalid['reject_reason'] = 'Capacité <= 0'
            reject_reasons.append(invalid)
        df = df[~((df['electrical_capacity'] <= 0) & (df['electrical_capacity'].notna()))]
    
    # Déduplication
    df = df.drop_duplicates(keep='first')
    
    # Ajouter colonnes métier
    df['country'] = 'FR'
    
    reject_df = pd.concat(reject_reasons, ignore_index=True) if reject_reasons else pd.DataFrame()
    
    print(f"    ✅ {len(df)} lignes valides | ❌ {len(reject_df)} rejetées")
    
    return df, reject_df


def write_parquet_safe(df: pd.DataFrame, output_path: str, table_name: str) -> None:
    """Écrit Parquet de manière robuste"""
    
    os.makedirs(output_path, exist_ok=True)
    
    parquet_file = os.path.join(output_path, f"{table_name}.parquet")
    df.to_parquet(parquet_file, engine='pyarrow', index=False)
    
    print(f"    📂 {parquet_file} ({len(df)} lignes)")


def run_silver_cleaning() -> bool:
    """
    Pipeline complet SILVER
    """
    
    print(f"\n{'='*80}")
    print(f"⚪ SILVER LAYER - NETTOYAGE & DATA QUALITY")
    print(f"{'='*80}\n")
    
    try:
        # Charger config
        config = load_config("conf/config.yaml")
        bronze_path = config['paths']['bronze']
        silver_path = config['paths']['silver']
        dq_path = config['paths']['dq']
        
        print(f"📂 Bronze: {bronze_path}")
        print(f"📂 Silver: {silver_path}")
        print(f"📂 DQ:     {dq_path}\n")
        
        # Créer répertoires
        Path(silver_path).mkdir(parents=True, exist_ok=True)
        Path(dq_path).mkdir(parents=True, exist_ok=True)
        
        results = {}
        total_valid = 0
        total_reject = 0
        
        # ===== FRANCE TIME SERIES =====
        print(f"🔄 france_time_series")
        try:
            bronze_file = os.path.join(bronze_path, 'france_time_series', 'data.parquet')
            df = pd.read_parquet(bronze_file)
            
            valid_df, reject_df = clean_france_time_series(df)
            
            write_parquet_safe(valid_df, os.path.join(silver_path, 'france_time_series'), 'data')
            if len(reject_df) > 0:
                write_parquet_safe(reject_df, os.path.join(dq_path, 'france_time_series_rejects'), 'data')
            
            results['france_time_series'] = 'SUCCESS'
            total_valid += len(valid_df)
            total_reject += len(reject_df)
            
        except Exception as e:
            print(f"    ❌ ERREUR: {str(e)}\n")
            results['france_time_series'] = f'ERROR: {str(e)}'
        
        # ===== EUROSTAT =====
        print(f"\n🔄 eurostat_electricity_france")
        try:
            bronze_file = os.path.join(bronze_path, 'eurostat_electricity_france', 'data.parquet')
            df = pd.read_parquet(bronze_file)
            
            valid_df, reject_df = clean_eurostat_electricity_france(df)
            
            write_parquet_safe(valid_df, os.path.join(silver_path, 'eurostat_electricity_france'), 'data')
            if len(reject_df) > 0:
                write_parquet_safe(reject_df, os.path.join(dq_path, 'eurostat_rejects'), 'data')
            
            results['eurostat_electricity_france'] = 'SUCCESS'
            total_valid += len(valid_df)
            total_reject += len(reject_df)
            
        except Exception as e:
            print(f"    ❌ ERREUR: {str(e)}\n")
            results['eurostat_electricity_france'] = f'ERROR: {str(e)}'
        
        # ===== TIME SERIES 60MIN =====
        print(f"\n🔄 time_series_60min_sample")
        try:
            bronze_file = os.path.join(bronze_path, 'time_series_60min_sample', 'data.parquet')
            df = pd.read_parquet(bronze_file)
            
            valid_df, reject_df = clean_time_series_60min(df)
            
            write_parquet_safe(valid_df, os.path.join(silver_path, 'time_series_60min'), 'data')
            if len(reject_df) > 0:
                write_parquet_safe(reject_df, os.path.join(dq_path, 'time_series_rejects'), 'data')
            
            results['time_series_60min_sample'] = 'SUCCESS'
            total_valid += len(valid_df)
            total_reject += len(reject_df)
            
        except Exception as e:
            print(f"    ❌ ERREUR: {str(e)}\n")
            results['time_series_60min_sample'] = f'ERROR: {str(e)}'
        
        # ===== RENEWABLE PLANTS =====
        print(f"\n🔄 renewable_power_plants_FR")
        try:
            bronze_file = os.path.join(bronze_path, 'renewable_power_plants_FR', 'data.parquet')
            df = pd.read_parquet(bronze_file)
            
            valid_df, reject_df = clean_renewable_power_plants(df)
            
            write_parquet_safe(valid_df, os.path.join(silver_path, 'renewable_plants'), 'data')
            if len(reject_df) > 0:
                write_parquet_safe(reject_df, os.path.join(dq_path, 'renewable_rejects'), 'data')
            
            results['renewable_power_plants_FR'] = 'SUCCESS'
            total_valid += len(valid_df)
            total_reject += len(reject_df)
            
        except Exception as e:
            print(f"    ❌ ERREUR: {str(e)}\n")
            results['renewable_power_plants_FR'] = f'ERROR: {str(e)}'
        
        # ===== RÉSUMÉ =====
        print(f"\n{'='*80}")
        print(f"✅ SILVER LAYER - COMPLÉTÉ")
        print(f"{'='*80}\n")
        
        print(f"📊 RÉSUMÉ DATA QUALITY:")
        print(f"   • Lignes valides:  {total_valid:,}")
        print(f"   • Lignes rejetées: {total_reject:,}")
        print(f"   • Taux d'acceptation: {(total_valid/(total_valid+total_reject)*100):.1f}%" if total_valid + total_reject > 0 else "   • Aucune donnée")
        print(f"\n📁 Structure SILVER:")
        print(f"   {silver_path}/")
        print(f"   ├── france_time_series/")
        print(f"   ├── eurostat_electricity_france/")
        print(f"   ├── time_series_60min/")
        print(f"   └── renewable_plants/")
        print(f"\n📁 Rejets (DQ):")
        print(f"   {dq_path}/")
        print(f"   ├── france_time_series_rejects/")
        print(f"   ├── eurostat_rejects/")
        print(f"   ├── time_series_rejects/")
        print(f"   └── renewable_rejects/")
        print(f"\n✅ Next step: 03_gold_dwh.py (Star Schema)\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    
    try:
        success = run_silver_cleaning()
        
        if success:
            print("🎉 Pipeline SILVER terminé avec succès!\n")
            sys.exit(0)
        else:
            print("⚠️  Pipeline SILVER terminé avec des avertissements\n")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erreur fatale: {str(e)}\n")
        sys.exit(1)
