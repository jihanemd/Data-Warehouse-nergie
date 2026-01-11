"""
📘 LOAD LAYER - Chargement des tables GOLD vers PostgreSQL
───────────────────────────────────────────────────────
Objectif: Charger les tables dimensionnelles et de faits depuis Parquet vers PostgreSQL

Flux:
  gold/ (Parquet Star Schema)
    ↓
  PostgreSQL (Tables relationnelles - Gold Schema)
    ├── dim_date
    ├── dim_energy_type
    ├── dim_location
    ├── dim_plant
    ├── fact_energy_production
    ├── fact_renewable_capacity
    └── fact_monthly_summary

Usage:
  python 04_load_postgres.py                    # Charge tous les fichiers Parquet
  python 04_load_postgres.py --truncate         # Vide les tables avant reload
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple
import pandas as pd

# Ajouter le chemin src pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.postgres_utils import (
    load_config,
    create_connection,
    create_schema_if_not_exists,
    load_dataframe_to_postgres,
    truncate_table,
    get_table_row_count
)


def load_parquet_to_dataframe(parquet_path: str) -> pd.DataFrame:
    """
    Charge un fichier Parquet en DataFrame
    
    Args:
        parquet_path: Chemin du fichier Parquet
        
    Returns:
        pd.DataFrame
    """
    if not Path(parquet_path).exists():
        raise FileNotFoundError(f"Fichier Parquet non trouvé: {parquet_path}")
    
    return pd.read_parquet(parquet_path)


def load_gold_to_postgres(config: dict, truncate: bool = False) -> Dict[str, int]:
    """
    Charge toutes les tables GOLD vers PostgreSQL
    
    Args:
        config: Configuration
        truncate: Si True, vide les tables avant chargement
        
    Returns:
        dict: Statistiques de chargement
    """
    
    print(f"\n{'='*80}")
    print(f"📤 LOAD POSTGRES - Gold → PostgreSQL")
    print(f"{'='*80}\n")
    
    # Étape 1: Créer schéma
    print("🔧 Préparation...")
    create_schema_if_not_exists(config)
    
    # Étape 2: Définir les tables à charger
    gold_path = Path(config['paths']['gold'])
    
    tables_to_load = {
        'dim_date': gold_path / 'dim_date',
        'dim_energy_type': gold_path / 'dim_energy_type',
        'dim_location': gold_path / 'dim_location',
        'dim_plant': gold_path / 'dim_plant',
        'fact_energy_production': gold_path / 'fact_energy_production',
        'fact_renewable_capacity': gold_path / 'fact_renewable_capacity',
        'fact_monthly_summary': gold_path / 'fact_monthly_summary',
    }
    
    stats = {}
    
    print(f"\n📥 Chargement des tables...\n")
    
    for table_name, table_path in tables_to_load.items():
        try:
            # Vérifier existence du répertoire
            if not table_path.exists():
                print(f"  ⚠️  Fichier/répertoire manquant: {table_name}")
                stats[table_name] = 0
                continue
            
            # Charger le Parquet
            df = load_parquet_to_dataframe(str(table_path))
            
            # Optionnel: Truncate
            if truncate:
                try:
                    truncate_table(table_name, config)
                except:
                    pass  # Ignorer si la table n'existe pas
            
            # Charger dans PostgreSQL
            rows_loaded = load_dataframe_to_postgres(
                df,
                table_name,
                config,
                if_exists='replace' if truncate else 'append'
            )
            
            stats[table_name] = rows_loaded
            
        except Exception as e:
            print(f"  ❌ Erreur {table_name}: {str(e)}")
            stats[table_name] = -1
    
    return stats


def print_statistics(stats: Dict[str, int]) -> None:
    """
    Affiche les statistiques de chargement
    
    Args:
        stats: Dictionnaire {table: nb_lignes}
    """
    print(f"\n{'='*80}")
    print(f"📊 STATISTIQUES DE CHARGEMENT")
    print(f"{'='*80}\n")
    
    total_rows = 0
    success_count = 0
    
    for table_name, row_count in stats.items():
        if row_count > 0:
            print(f"  ✅ {table_name:30} → {row_count:>10,} lignes")
            total_rows += row_count
            success_count += 1
        elif row_count == 0:
            print(f"  ⚠️  {table_name:30} → Fichier manquant")
        else:
            print(f"  ❌ {table_name:30} → Erreur chargement")
    
    print(f"\n{'─'*80}")
    print(f"  📈 Total: {total_rows:,} lignes chargées ({success_count}/{len(stats)} tables)")
    print(f"  ⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")


def main():
    """Fonction principale"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Charge GOLD → PostgreSQL")
    parser.add_argument("--truncate", action="store_true", help="Vide les tables avant chargement")
    parser.add_argument("--config", default="conf/config.yaml", help="Chemin config.yaml")
    
    args = parser.parse_args()
    
    try:
        # Charger configuration
        config = load_config(args.config)
        
        # Charger les données
        stats = load_gold_to_postgres(config, truncate=args.truncate)
        
        # Afficher statistiques
        print_statistics(stats)
        
        # Retour succès
        success = all(v > 0 for v in stats.values())
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {str(e)}\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
