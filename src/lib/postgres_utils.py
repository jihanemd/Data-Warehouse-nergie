"""
Utilitaires PostgreSQL pour charger les tables GOLD
"""

import psycopg2
from psycopg2 import sql, Error
from sqlalchemy import create_engine
import pandas as pd
from typing import Dict, List
import yaml


def load_config(config_path: str = "conf/config.yaml") -> dict:
    """Charge la configuration"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def get_connection_string(config: dict) -> str:
    """
    Génère la string de connexion PostgreSQL
    
    Args:
        config: Configuration avec section 'postgres'
        
    Returns:
        str: Connection string SQLAlchemy
    """
    pg_config = config['postgres']
    conn_string = (
        f"postgresql://{pg_config['user']}:{pg_config['password']}"
        f"@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
    )
    return conn_string


def create_connection(config: dict):
    """
    Crée une connexion directe psycopg2
    
    Args:
        config: Configuration avec section 'postgres'
        
    Returns:
        Connexion psycopg2
    """
    pg_config = config['postgres']
    try:
        conn = psycopg2.connect(
            host=pg_config['host'],
            port=pg_config['port'],
            database=pg_config['database'],
            user=pg_config['user'],
            password=pg_config['password']
        )
        print(f"✅ Connexion PostgreSQL établie: {pg_config['host']}:{pg_config['port']}/{pg_config['database']}")
        return conn
    except Error as e:
        print(f"❌ Erreur connexion PostgreSQL: {e}")
        raise


def check_database_exists(config: dict) -> bool:
    """
    Vérifie que la base de données existe
    
    Args:
        config: Configuration
        
    Returns:
        bool: True si existe
    """
    try:
        conn = create_connection(config)
        conn.close()
        return True
    except:
        return False


def load_dataframe_to_postgres(
    df: pd.DataFrame,
    table_name: str,
    config: dict,
    if_exists: str = "replace"
) -> int:
    """
    Charge un DataFrame Pandas dans PostgreSQL
    
    Args:
        df: DataFrame à charger
        table_name: Nom de la table (sans schéma)
        config: Configuration
        if_exists: 'fail', 'replace', 'append'
        
    Returns:
        int: Nombre de lignes chargées
    """
    pg_config = config['postgres']
    schema = pg_config.get('schema', 'gold')
    
    try:
        engine = create_engine(get_connection_string(config))
        
        print(f"  📤 Chargement {table_name}...")
        rows_affected = df.to_sql(
            table_name,
            engine,
            schema=schema,
            if_exists=if_exists,
            index=False,
            method='multi',
            chunksize=1000
        )
        
        print(f"    ✅ {len(df):,} lignes chargées dans {schema}.{table_name}")
        return len(df)
        
    except Exception as e:
        print(f"    ❌ Erreur lors du chargement: {e}")
        raise
    finally:
        if 'engine' in locals():
            engine.dispose()


def truncate_table(table_name: str, config: dict) -> None:
    """
    Vide une table (TRUNCATE)
    
    Args:
        table_name: Nom de la table
        config: Configuration
    """
    pg_config = config['postgres']
    schema = pg_config.get('schema', 'gold')
    
    try:
        conn = create_connection(config)
        cursor = conn.cursor()
        
        query = sql.SQL("TRUNCATE TABLE {}.{} CASCADE").format(
            sql.Identifier(schema),
            sql.Identifier(table_name)
        )
        
        cursor.execute(query)
        conn.commit()
        print(f"    ✅ Table {schema}.{table_name} vidée")
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"    ❌ Erreur TRUNCATE: {e}")
        raise


def get_table_row_count(table_name: str, config: dict) -> int:
    """
    Retourne le nombre de lignes dans une table
    
    Args:
        table_name: Nom de la table
        config: Configuration
        
    Returns:
        int: Nombre de lignes
    """
    pg_config = config['postgres']
    schema = pg_config.get('schema', 'gold')
    
    try:
        conn = create_connection(config)
        cursor = conn.cursor()
        
        query = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
            sql.Identifier(schema),
            sql.Identifier(table_name)
        )
        
        cursor.execute(query)
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return count
        
    except Error as e:
        print(f"❌ Erreur lors du COUNT: {e}")
        return -1


def create_schema_if_not_exists(config: dict) -> None:
    """
    Crée le schéma s'il n'existe pas
    
    Args:
        config: Configuration
    """
    pg_config = config['postgres']
    schema = pg_config.get('schema', 'gold')
    
    try:
        conn = create_connection(config)
        cursor = conn.cursor()
        
        query = sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
            sql.Identifier(schema)
        )
        
        cursor.execute(query)
        conn.commit()
        print(f"✅ Schéma '{schema}' prêt")
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"❌ Erreur création schéma: {e}")
        raise
