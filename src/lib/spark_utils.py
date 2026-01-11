"""
Utilitaires Spark pour le projet DWH Énergie France
"""
from pyspark.sql import SparkSession
from pyspark import SparkConf
import yaml
import os
from pathlib import Path


def load_config(config_path: str = "conf/config.yaml") -> dict:
    """
    Charge la configuration depuis le fichier YAML
    
    Args:
        config_path: Chemin vers le fichier de configuration
        
    Returns:
        dict: Configuration chargée
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def create_spark_session(app_name: str = "DWH_Energie", log_level: str = "WARN") -> SparkSession:
    """
    Crée une session Spark avec configuration optimale
    
    Args:
        app_name: Nom de l'application Spark
        log_level: Niveau de log (WARN, INFO, ERROR, DEBUG)
        
    Returns:
        SparkSession: Session Spark configurée
    """
    conf = SparkConf()
    conf.set("spark.sql.adaptive.enabled", "true")
    conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
    conf.set("spark.sql.shuffle.partitions", "8")
    
    spark = (SparkSession.builder
             .appName(app_name)
             .config(conf=conf)
             .getOrCreate())
    
    spark.sparkContext.setLogLevel(log_level)
    
    return spark


def ensure_directory(path: str) -> None:
    """
    Crée un répertoire s'il n'existe pas
    
    Args:
        path: Chemin du répertoire à créer
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def get_source_file_name(file_path: str) -> str:
    """
    Extrait le nom du fichier depuis un chemin complet
    
    Args:
        file_path: Chemin complet du fichier
        
    Returns:
        str: Nom du fichier sans le chemin
    """
    return os.path.basename(file_path)


def log_dataframe_info(df, dataset_name: str) -> None:
    """
    Affiche des informations sur un DataFrame
    
    Args:
        df: DataFrame Spark
        dataset_name: Nom du dataset pour le log
    """
    print(f"\n{'='*60}")
    print(f"📊 Dataset: {dataset_name}")
    print(f"{'='*60}")
    print(f"Nombre de lignes: {df.count():,}")
    print(f"Nombre de colonnes: {len(df.columns)}")
    print(f"\nSchéma:")
    df.printSchema()
    print(f"\nAperçu des données:")
    df.show(5, truncate=False)
    print(f"{'='*60}\n")