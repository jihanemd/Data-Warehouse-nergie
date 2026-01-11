"""
📘 BRONZE LAYER - Ingestion RAW Data (Version PANDAS - Simple & Robuste)
─────────────────────────────────────
Version alternative utilisant Pandas au lieu de Spark
- Pas de dépendance Java
- Même logique: ingestion RAW → Parquet
- Parfait pour validation et petits volumes

Note: Version Spark est preferée pour production/gros volumes
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

import yaml
import pandas as pd


def load_config(config_path: str = "conf/config.yaml") -> dict:
    """
    Charge la configuration depuis le fichier YAML
    
    Args:
        config_path: Chemin vers config.yaml
        
    Returns:
        dict: Configuration
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def ingest_csv_to_bronze_pandas(
    csv_path: str,
    source_name: str,
    delimiter: str = ",",
    encoding: str = "utf-8"
) -> pd.DataFrame:
    """
    Ingère un fichier CSV en BRONZE (RAW, sans transformation)
    
    Args:
        csv_path: Chemin vers le fichier CSV
        source_name: Nom logique de la source
        delimiter: Délimiteur du CSV
        encoding: Encodage du fichier
        
    Returns:
        DataFrame avec colonnes métier + système (_source_file, _ingest_ts)
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
    """
    
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"Fichier non trouvé: {csv_path}")
    
    print(f"  📥 Lecture CSV: {Path(csv_path).name}")
    
    # Lire le CSV AS-IS (aucun transformation!)
    df = pd.read_csv(
        csv_path,
        sep=delimiter,
        encoding=encoding,
        dtype=str  # Garder tous les types comme string (RAW)
    )
    
    # Ajouter les colonnes système
    ingest_timestamp = pd.Timestamp.now()
    ingest_date = ingest_timestamp.strftime("%Y-%m-%d")
    
    df['_source_file'] = Path(csv_path).name
    df['_ingest_ts'] = ingest_timestamp
    df['_ingest_date'] = ingest_date
    
    row_count = len(df)
    col_count = len(df.columns)
    
    print(f"    ✅ {row_count:,} lignes ingérées")
    print(f"    📊 {col_count} colonnes (dont 3 techniques)")
    
    return df


def write_parquet(
    df: pd.DataFrame,
    output_path: str,
    source_name: str
) -> None:
    """
    Écrit le DataFrame en Parquet
    
    Args:
        df: DataFrame à écrire
        output_path: Chemin de destination (parent directory)
        source_name: Nom de la source (pour path)
    """
    
    full_path = os.path.join(output_path, source_name)
    
    # Créer le répertoire parent d'abord
    try:
        os.makedirs(output_path, exist_ok=True)
    except Exception as e:
        print(f"    ⚠️  Impossible de créer {output_path}: {str(e)}")
    
    # Créer le sous-répertoire pour la source
    try:
        os.makedirs(full_path, exist_ok=True)
    except Exception as e:
        print(f"    ⚠️  Impossible de créer {full_path}: {str(e)}")
    
    print(f"  💾 Écriture Parquet: {source_name}")
    
    # Écrire le fichier parquet directement (sans sous-dossier)
    parquet_file = os.path.join(full_path, "data.parquet")
    df.to_parquet(parquet_file, engine='pyarrow', index=False)
    
    print(f"    ✅ Parquet écrit")
    print(f"    📂 {parquet_file}")


def print_schema(df: pd.DataFrame, max_cols: int = 15) -> None:
    """
    Affiche le schéma du DataFrame de manière lisible
    
    Args:
        df: DataFrame
        max_cols: Nombre max de colonnes à afficher
    """
    cols = list(df.columns)
    
    print(f"    📋 Schéma ({len(cols)} colonnes):")
    
    for i, col in enumerate(cols):
        if i < max_cols:
            dtype = df[col].dtype
            print(f"       {i+1:2d}. {col:30s} : {str(dtype):20s}")
        elif i == max_cols:
            print(f"       ... (+{len(cols) - max_cols} colonnes)")
            break


def run_bronze_ingestion_pandas() -> bool:
    """
    Pipeline complet d'ingestion BRONZE (Pandas)
    
    Returns:
        bool: True si succès, False sinon
    """
    
    print(f"\n{'='*80}")
    print(f"🟤 BRONZE LAYER - INGESTION RAW DATA (PANDAS)")
    print(f"{'='*80}\n")
    
    try:
        # 1️⃣ Charger config
        config = load_config("conf/config.yaml")
        landing_path = config['paths']['landing']
        bronze_path = config['paths']['bronze']
        sources = config['sources']
        
        print(f"📂 Landing: {landing_path}")
        print(f"📂 Bronze:  {bronze_path}\n")
        
        # 2️⃣ Créer répertoires
        Path(bronze_path).mkdir(parents=True, exist_ok=True)
        
        # 3️⃣ Ingérer et écrire chaque source
        results = {}
        success_count = 0
        
        for source in sources:
            source_name = source['name']
            filename = source['file']
            delimiter = source.get('delimiter', ',')
            
            csv_path = os.path.join(landing_path, filename)
            
            print(f"🔄 Source: {source_name}")
            
            try:
                # Ingérer
                df_bronze = ingest_csv_to_bronze_pandas(
                    csv_path=csv_path,
                    source_name=source_name,
                    delimiter=delimiter
                )
                
                # Afficher schéma
                print_schema(df_bronze)
                
                # Afficher aperçu (3 lignes)
                print(f"    🔍 Aperçu:")
                print(df_bronze.head(3).to_string())
                
                # Écrire en Parquet
                write_parquet(
                    df=df_bronze,
                    output_path=bronze_path,
                    source_name=source_name
                )
                
                results[source_name] = "SUCCESS"
                success_count += 1
                
            except FileNotFoundError as e:
                print(f"    ⚠️  SKIP - {str(e)}\n")
                results[source_name] = "FILE_NOT_FOUND"
                
            except Exception as e:
                print(f"    ❌ ERREUR - {str(e)}\n")
                import traceback
                traceback.print_exc()
                results[source_name] = f"ERROR: {str(e)}"
            
            print()
        
        # 4️⃣ Vérification des fichiers écrits
        print(f"{'='*80}")
        print(f"🔍 VÉRIFICATION")
        print(f"{'='*80}\n")
        
        for source_name, result in results.items():
            if result == "SUCCESS":
                bronze_table_path = os.path.join(bronze_path, source_name)
                try:
                    df = pd.read_parquet(bronze_table_path)
                    count = len(df)
                    print(f"✅ {source_name:35s} : {count:10,} lignes")
                except:
                    print(f"⚠️  {source_name:35s} : Parquet non accessible")
            else:
                print(f"⏭️  {source_name:35s} : {result}")
        
        # 5️⃣ Résumé final
        print(f"\n{'='*80}")
        print(f"✅ BRONZE LAYER - COMPLÉTÉ")
        print(f"{'='*80}\n")
        print(f"📊 RÉSUMÉ:")
        print(f"   • Sources ingérées: {success_count}/{len(sources)}")
        print(f"   • Destination: {bronze_path}")
        print(f"   • Format: Parquet (compatible Spark)")
        print(f"   • Colonnes système: _source_file, _ingest_ts, _ingest_date")
        print(f"   • Engine: Pandas + PyArrow")
        print(f"   • Next step: 02_silver_clean.py\n")
        
        return success_count == len(sources)
        
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    
    try:
        success = run_bronze_ingestion_pandas()
        
        if success:
            print("🎉 Pipeline BRONZE (PANDAS) terminé avec succès!\n")
            sys.exit(0)
        else:
            print("⚠️  Pipeline BRONZE (PANDAS) terminé avec des avertissements\n")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erreur fatale: {str(e)}\n")
        sys.exit(1)
