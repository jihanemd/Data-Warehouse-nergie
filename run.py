"""
🚀 ORCHESTRATION PIPELINE - Data Warehouse Énergie France
─────────────────────────────────────────────────────
Script principal pour exécuter le pipeline ETL complet:
  BRONZE (Ingestion) → SILVER (Nettoyage) → GOLD (Star Schema) → POSTGRES (Load)

Usage:
  python run.py                    # Exécute toutes les étapes
  python run.py --bronze           # Seulement BRONZE
  python run.py --silver           # BRONZE + SILVER
  python run.py --gold             # BRONZE + SILVER + GOLD (sans PostgreSQL)
  python run.py --load             # BRONZE + SILVER + GOLD + POSTGRES (complet)
  python run.py --clean            # Efface les données et relance tout
"""

import os
import sys
import subprocess
import argparse
import shutil
from datetime import datetime
from pathlib import Path


class PipelineRunner:
    """Orchestrateur du pipeline ETL"""
    
    def __init__(self, venv_python: str = None):
        """
        Initialise le runner
        
        Args:
            venv_python: Chemin vers le Python du venv (auto-détection si None)
        """
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / ".venv"
        
        if venv_python:
            self.python_exe = venv_python
        else:
            # Auto-detect
            self.python_exe = str(self.venv_path / "Scripts" / "python.exe")
            if not Path(self.python_exe).exists():
                self.python_exe = "python"
        
        self.jobs_dir = self.project_root / "src" / "jobs"
        self.data_dir = self.project_root / "data" / "warehouse"
        
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def print_header(self):
        """Affiche le header du pipeline"""
        print(f"\n{'='*80}")
        print(f"🚀 PIPELINE ETL - Data Warehouse Énergie France")
        print(f"{'='*80}\n")
        print(f"📂 Projet:       {self.project_root}")
        print(f"🐍 Python:       {self.python_exe}")
        print(f"⏰ Démarrage:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    def run_job(self, job_name: str, job_file: str) -> bool:
        """
        Exécute un job
        
        Args:
            job_name: Nom du job (pour affichage)
            job_file: Fichier Python du job
            
        Returns:
            bool: True si succès, False sinon
        """
        job_path = self.jobs_dir / job_file
        
        if not job_path.exists():
            print(f"❌ Job non trouvé: {job_path}")
            return False
        
        print(f"{'─'*80}")
        print(f"🔄 Exécution: {job_name}")
        print(f"{'─'*80}\n")
        
        try:
            result = subprocess.run(
                [self.python_exe, str(job_path)],
                cwd=self.project_root,
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                print(f"\n✅ {job_name} - SUCCÈS\n")
                self.results[job_name] = "SUCCESS"
                return True
            else:
                print(f"\n❌ {job_name} - ERREUR (exit code: {result.returncode})\n")
                self.results[job_name] = "FAILED"
                return False
                
        except Exception as e:
            print(f"\n❌ {job_name} - EXCEPTION: {str(e)}\n")
            self.results[job_name] = f"ERROR: {str(e)}"
            return False
    
    def clean_data(self):
        """Efface les données warehouse"""
        print(f"{'─'*80}")
        print(f"🧹 Nettoyage des données...")
        print(f"{'─'*80}\n")
        
        try:
            if self.data_dir.exists():
                shutil.rmtree(self.data_dir)
                print(f"✅ Répertoires supprimés: {self.data_dir}\n")
            else:
                print(f"ℹ️  Aucune donnée à nettoyer\n")
        except Exception as e:
            print(f"⚠️  Erreur lors du nettoyage: {str(e)}\n")
    
    def run_bronze(self) -> bool:
        """Exécute la couche BRONZE"""
        return self.run_job("🟤 BRONZE (Ingestion RAW)", "01_bronze_ingest_pandas.py")
    
    def run_silver(self) -> bool:
        """Exécute la couche SILVER"""
        # Vérifier que BRONZE existe
        bronze_path = self.data_dir / "bronze"
        if not bronze_path.exists():
            print(f"❌ ERREUR: Bronze non trouvée. Exécutez BRONZE d'abord!")
            return False
        
        return self.run_job("⚪ SILVER (Nettoyage)", "02_silver_clean.py")
    
    def run_gold(self) -> bool:
        """Exécute la couche GOLD"""
        # Vérifier que SILVER existe
        silver_path = self.data_dir / "silver"
        if not silver_path.exists():
            print(f"❌ ERREUR: Silver non trouvée. Exécutez SILVER d'abord!")
            return False
        
        return self.run_job("🟡 GOLD (Star Schema)", "03_gold_dwh.py")
    
    def run_postgres(self) -> bool:
        """Exécute le chargement PostgreSQL"""
        # Vérifier que GOLD existe
        gold_path = self.data_dir / "gold"
        if not gold_path.exists():
            print(f"❌ ERREUR: Gold non trouvée. Exécutez GOLD d'abord!")
            return False
        
        return self.run_job("🐘 LOAD (PostgreSQL)", "04_load_postgres.py")
    
    def run_full_pipeline(self):
        """Exécute le pipeline complet: BRONZE → SILVER → GOLD → POSTGRES"""
        self.start_time = datetime.now()
        
        print(f"📋 ÉTAPES: BRONZE → SILVER → GOLD → POSTGRES\n")
        
        # BRONZE
        if not self.run_bronze():
            print(f"❌ Pipeline interrompu à l'étape BRONZE")
            self.end_time = datetime.now()
            self.print_summary()
            return False
        
        # SILVER
        if not self.run_silver():
            print(f"❌ Pipeline interrompu à l'étape SILVER")
            self.end_time = datetime.now()
            self.print_summary()
            return False
        
        # GOLD
        if not self.run_gold():
            print(f"❌ Pipeline interrompu à l'étape GOLD")
            self.end_time = datetime.now()
            self.print_summary()
            return False
        
        # POSTGRES
        if not self.run_postgres():
            print(f"❌ Pipeline interrompu à l'étape POSTGRES")
            self.end_time = datetime.now()
            self.print_summary()
            return False
        
        self.end_time = datetime.now()
        return True
    
    def print_summary(self):
        """Affiche le résumé final"""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0
        
        print(f"\n{'='*80}")
        print(f"📊 RÉSUMÉ FINAL")
        print(f"{'='*80}\n")
        
        for job_name, status in self.results.items():
            status_icon = "✅" if status == "SUCCESS" else "❌"
            print(f"{status_icon} {job_name:40s} : {status}")
        
        success_count = len([s for s in self.results.values() if s == "SUCCESS"])
        total_count = len(self.results)
        
        print(f"\n📈 Statistiques:")
        print(f"   • Étapes réussies: {success_count}/{total_count}")
        print(f"   • Durée totale: {duration:.1f}s")
        print(f"   • Démarrage: {self.start_time.strftime('%H:%M:%S') if self.start_time else 'N/A'}")
        print(f"   • Fin: {self.end_time.strftime('%H:%M:%S') if self.end_time else 'N/A'}")
        
        print(f"\n📁 Répertoires générés:")
        if (self.data_dir / "bronze").exists():
            bronze_files = list((self.data_dir / "bronze").rglob("*.parquet"))
            print(f"   • bronze/: {len(bronze_files)} fichiers Parquet")
        
        if (self.data_dir / "silver").exists():
            silver_files = list((self.data_dir / "silver").rglob("*.parquet"))
            print(f"   • silver/: {len(silver_files)} fichiers Parquet")
        
        if (self.data_dir / "gold").exists():
            gold_files = list((self.data_dir / "gold").rglob("*.parquet"))
            print(f"   • gold/: {len(gold_files)} fichiers Parquet")
        
        if (self.data_dir / "dq").exists():
            dq_files = list((self.data_dir / "dq").rglob("*.parquet"))
            if dq_files:
                print(f"   • dq/: {len(dq_files)} fichiers Parquet (rejets)")
        
        # Status final
        print(f"\n{'─'*80}")
        if success_count == total_count and total_count > 0:
            print(f"🎉 PIPELINE COMPLÉTÉ AVEC SUCCÈS!")
            print(f"\n✅ Data Warehouse prêt:")
            print(f"   • Parquet Spark SQL compatible")
            print(f"   • PostgreSQL chargé et prêt pour requêtes")
            print(f"   • Power BI, Tableau, Metabase")
            print(f"   • Athena, BigQuery, Trino")
            print(f"\n📝 Prochaines étapes:")
            print(f"   1. Connecter PostgreSQL à un outil BI")
            print(f"   2. Créer des dashboards analytiques")
            print(f"   3. Configurer Airflow pour la récurrence")
        else:
            print(f"⚠️  PIPELINE INCOMPLÈTE ({success_count}/{total_count} étapes réussies)")
        
        print(f"{'─'*80}\n")


def main():
    """Point d'entrée principal"""
    
    parser = argparse.ArgumentParser(
        description="Orchestrateur pipeline ETL - Data Warehouse Énergie France",
        epilog="""
Exemples:
  python run.py                    # Pipeline complet (BRONZE → SILVER → GOLD → POSTGRES)
  python run.py --bronze           # Seulement BRONZE
  python run.py --silver           # BRONZE + SILVER
  python run.py --gold             # BRONZE + SILVER + GOLD (sans PostgreSQL)
  python run.py --load             # BRONZE + SILVER + GOLD + POSTGRES (alias du défaut)
  python run.py --clean            # Efface données + relance tout
  python run.py --clean --bronze   # Efface + seulement BRONZE
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--bronze",
        action="store_true",
        help="Exécuter seulement BRONZE"
    )
    
    parser.add_argument(
        "--silver",
        action="store_true",
        help="Exécuter BRONZE + SILVER"
    )
    
    parser.add_argument(
        "--gold",
        action="store_true",
        help="Exécuter BRONZE + SILVER + GOLD (sans PostgreSQL)"
    )
    
    parser.add_argument(
        "--load",
        action="store_true",
        help="Exécuter BRONZE + SILVER + GOLD + POSTGRES (complet, défaut)"
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Nettoyer données existantes avant d'exécuter"
    )
    
    parser.add_argument(
        "--python",
        type=str,
        default=None,
        help="Chemin vers l'exécutable Python (auto-détection si non spécifié)"
    )
    
    args = parser.parse_args()
    
    # Créer runner
    runner = PipelineRunner(venv_python=args.python)
    runner.print_header()
    
    # Nettoyage optionnel
    if args.clean:
        runner.clean_data()
    
    # Déterminer les étapes à exécuter
    if args.bronze:
        print(f"📋 ÉTAPE: BRONZE\n")
        runner.start_time = datetime.now()
        success = runner.run_bronze()
        runner.end_time = datetime.now()
    
    elif args.silver:
        print(f"📋 ÉTAPES: BRONZE → SILVER\n")
        runner.start_time = datetime.now()
        
        if not runner.run_bronze():
            runner.end_time = datetime.now()
            runner.print_summary()
            sys.exit(1)
        
        if not runner.run_silver():
            runner.end_time = datetime.now()
            runner.print_summary()
            sys.exit(1)
        
        runner.end_time = datetime.now()
        success = True
    
    elif args.gold:
        print(f"📋 ÉTAPES: BRONZE → SILVER → GOLD\n")
        runner.start_time = datetime.now()
        
        if not runner.run_bronze():
            runner.end_time = datetime.now()
            runner.print_summary()
            sys.exit(1)
        
        if not runner.run_silver():
            runner.end_time = datetime.now()
            runner.print_summary()
            sys.exit(1)
        
        if not runner.run_gold():
            runner.end_time = datetime.now()
            runner.print_summary()
            sys.exit(1)
        
        runner.end_time = datetime.now()
        success = True
    
    else:  # défaut: load (complet BRONZE → SILVER → GOLD → POSTGRES)
        success = runner.run_full_pipeline()
    
    runner.print_summary()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()