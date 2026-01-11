#!/bin/bash

# Script pour pousser le projet vers GitHub

cd "$(dirname "$0")"

echo "🚀 Configuration Git pour GitHub..."
echo ""

# Initialiser le dépôt git
echo "1️⃣  Initialisation du dépôt git..."
git init

# Configurer l'auteur
echo "2️⃣  Configuration utilisateur git..."
git config user.name "Jihane"
git config user.email "jihanemd@example.com"

# Ajouter le remote GitHub
echo "3️⃣  Ajout du remote GitHub..."
git remote add origin https://github.com/jihanemd/Data-Warehouse-nergie.git

# Créer fichier .gitignore
echo "4️⃣  Création du fichier .gitignore..."
cat > .gitignore << 'EOF'
# Environnement Python
venv_spark/
venv/
__pycache__/
*.pyc
*.pyo
*.egg-info/
.Python

# Données volumineuses
data/warehouse/bronze/
data/warehouse/silver/
data/warehouse/gold/
data/warehouse/dq/

# Logs et fichiers temporaires
*.log
*.tmp
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Fichiers systèmes
hadoop/
.env

# Cache
.pytest_cache/
.mypy_cache/
EOF

# Ajouter les fichiers
echo "5️⃣  Ajout des fichiers au staging..."
git add .

# Vérifier les fichiers
echo ""
echo "📋 Fichiers à être pushés:"
git ls-files | head -20

# Faire le commit
echo ""
echo "6️⃣  Création du commit..."
git commit -m "Initial commit: Data Warehouse Énergie France - Architecture Bronze/Silver/Gold avec 7-table Star Schema

- Bronze layer: Ingestion de 61,554 lignes depuis 4 sources CSV
- Silver layer: Nettoyage et validation avec 100% acceptance rate
- Gold layer: Star Schema enrichi avec 4 dimensions + 3 fact tables
- Orchestrateur Python avec modes d'exécution flexibles
- Format Parquet pour compatibilité BI (Power BI, Tableau, Metabase)
- Performance: Traitement complet en ~7 secondes

Technologies: Python 3.11, Pandas, PyArrow, PySpark
Données: RTE, Eurostat, Open Data Réseaux Énergies"

# Renommer la branche principale
echo ""
echo "7️⃣  Configuration branche principal..."
git branch -M main

# Afficher l'URL pour authentification
echo ""
echo "✅ Configuration complète!"
echo ""
echo "🔐 Avant de pousser, vous devez configurer l'authentification:"
echo "   - GitHub Token: https://github.com/settings/tokens"
echo "   - Ou utiliser SSH: https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
echo ""
echo "8️⃣  Push vers GitHub (nécessite authentification)..."
git push -u origin main

echo ""
echo "🎉 SUCCÈS! Votre projet est maintenant sur GitHub:"
echo "   https://github.com/jihanemd/Data-Warehouse-nergie"
