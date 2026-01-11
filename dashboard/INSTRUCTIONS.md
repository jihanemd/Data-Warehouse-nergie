<!-- 🎨 INSTRUCTIONS DASHBOARD ÉNERGIE -->

# 📊 Dashboard Énergie France - Guide d'utilisation

## 🚀 Lancer le Dashboard

### Méthode 1: Ouvrir directement (Recommandé pour démarrage rapide)

```bash
# Windows
start dashboard\index.html

# macOS
open dashboard/index.html

# Linux
xdg-open dashboard/index.html
```

### Méthode 2: Serveur Local Python

```bash
cd Data-Warehouse-nergie
python -m http.server 8000
# Ouvrir http://localhost:8000/dashboard/
```

### Méthode 3: Live Server (VS Code)

```
1. Installer l'extension Live Server
2. Clic droit sur index.html
3. Sélectionner "Open with Live Server"
```

---

## 🎯 Navigation Dashboard

### Éléments principaux

```
┌─────────────────────────────────────────────────────┐
│  🔋 Energy DW    [Actualiser]   [Jihane D.]         │  ← Header
├─────┬───────────────────────────────────────────────┤
│     │                                               │
│ ⚡  │  ⚡ 1,234 MW  ☀️ 342 MW  💨 567 MW  🔋 28.5GW│  ← KPIs
│ 📊  │                                               │
│ 📈  │  [Production par type] [Production horaire]   │
│ 📋  │  [Capacité région]     [Répartition]        │
│ ⚙️  │                                               │
│     │  [Efficacité]          [Carte régions]       │
│ 🗺️  │                                               │
│ 💾  │  Top 10 Installations  (Table)                │
│ ⚙️  │                                               │
│ ❓  │                                               │
└─────┴───────────────────────────────────────────────┘
 Sidebar          Contenu principal
```

### Menu Sidebar

**Tableau de Bord**
- 📊 Dashboard (vous êtes ici)
- 📈 Analytics
- 📋 Rapports

**Production**
- ⚡ Production
- 🔋 Capacité
- 🏭 Installations

**Données**
- 🗺️ Régions
- 💾 Export

**Paramètres**
- ⚙️ Paramètres
- ❓ Aide

---

## 📊 Comprendre les graphiques

### 1️⃣ Production par type (Graphique colonnes)
```
Montre la production actuelle par source d'énergie:
- ☀️ Solaire (342 MW) - Orange
- 💨 Éolien (567 MW) - Violet
- 💧 Hydro (298 MW) - Cyan
- 🔥 Thermique (145 MW) - Rose
- ⚡ Autres (82 MW) - Vert

👉 Utilisez pour identifier quelle source produit le plus
```

### 2️⃣ Production horaire (Graphique lignes)
```
Évolution de la production et consommation sur 24h:
- Ligne CYAN = Production réelle
- Ligne ROSE = Consommation

👉 Identifiez les pics de production/consommation
👉 Optimisez le stockage d'énergie
```

### 3️⃣ Capacité par région (Graphique barres horizontal)
```
Capacité installée (en GW) par région:
- Hauts-de-France: 4.5 GW (plus grande)
- Auvergne-Rhône-Alpes: 3.8 GW
- ...

👉 Planifiez les nouveaux projets
👉 Répartition géographique
```

### 4️⃣ Répartition énergies (Graphique camembert)
```
Pourcentage de chaque source:
- Solaire: 28%
- Éolien: 36%
- Hydro: 19%
- Thermique: 9%
- Autres: 8%

👉 Vue globale du mix énergétique
👉 Objectifs d'énergie renouvelable
```

---

## 🎯 KPI Cards (Haut du dashboard)

### Carte 1: Production totale ⚡
```
Valeur: 1,234 MW
Changement: +12.5% vs hier (HAUSSE)
👉 Production globale du système
```

### Carte 2: Production solaire ☀️
```
Valeur: 342 MW
Changement: +8.3% vs hier (HAUSSE)
👉 Suivi spécifique énergie solaire
```

### Carte 3: Production éolienne 💨
```
Valeur: 567 MW
Changement: -3.2% vs hier (BAISSE)
👉 Suivi spécifique énergie éolienne
```

### Carte 4: Capacité installée 🔋
```
Valeur: 28.5 GW
Changement: Stable
👉 Total capacité ENR installée
```

---

## 📈 Efficacité énergétique

Les barres de progression montrent:

| Métrique | Valeur | Signification |
|----------|--------|---------------|
| Utilisation réseau | 87% | 87% de la capacité du réseau utilisée |
| Capacité disponible | 64% | 64% de capacité reste disponible |
| Performance solaire | 79% | Rendement du solaire à 79% |

---

## 📋 Table des installations

Affiche le top 10 des installations avec:

| Colonne | Exemple |
|---------|---------|
| Installation | Centrale Solaire Nord |
| Type | ☀️ Solaire |
| Région | Hauts-de-France |
| Capacité | 125.5 MW |
| Production | 98.3 MW |
| Efficacité | 78% (barre) |
| Statut | 🟢 Actif / 🟡 Maintenance |

**Couleurs statut:**
- 🟢 **Vert** = Actif et fonctionnel
- 🟡 **Orange** = En maintenance
- ⚫ **Gris** = Hors service

---

## 🎨 Thème et customisation

### Boutons d'action

**Actualiser** (haut à droite)
- Clique le bouton bleu
- Recharge les données du dashboard
- Animation de rotation pendant l'actualisation

### Raccourcis clavier

```
Ctrl+P  → Exporter données (affiche en console)
Ctrl+D  → Changer thème (Dark ↔ Light)
```

---

## 🔌 Connexion API PostgreSQL

### Pour connecter vos données réelles

#### Étape 1: Lancer le serveur backend (Python)

Créer fichier `backend.py`:

```python
from flask import Flask, jsonify
from flask_cors import CORS
import sqlalchemy as sa

app = Flask(__name__)
CORS(app)

engine = sa.create_engine(
    'postgresql://postgres:jihane@localhost:5432/dw_energie_france'
)

@app.route('/api/production-by-type')
def get_production():
    with engine.connect() as conn:
        sql = """
        SELECT energy_type_name, SUM(value_mw) as total
        FROM gold.fact_energy_production f
        JOIN gold.dim_energy_type e ON f.energy_type_id = e.energy_type_id
        GROUP BY energy_type_name
        """
        result = conn.execute(sa.text(sql))
        return jsonify([dict(row._mapping) for row in result])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

Lancer:
```bash
pip install flask flask-cors sqlalchemy psycopg2-binary
python backend.py
```

#### Étape 2: Modifier `js/charts.js`

Remplacer les données statiques par des appels API:

```javascript
// AVANT (données mock)
data: {
  labels: ['Solaire', 'Éolien', 'Hydro', 'Thermique', 'Autres'],
  datasets: [{
    data: [342, 567, 298, 145, 82],
    ...
  }]
}

// APRÈS (données réelles)
fetch('http://localhost:5000/api/production-by-type')
  .then(r => r.json())
  .then(data => {
    // Transformer et afficher
    chart.data.labels = data.map(d => d.energy_type_name);
    chart.data.datasets[0].data = data.map(d => d.total);
    chart.update();
  });
```

---

## 📊 Interprétation des données

### Bon vs Mauvais

| Métrique | Bon | Mauvais |
|----------|-----|--------|
| Production totale | 📈 Augmente | 📉 Diminue |
| Efficacité | ✅ > 80% | ❌ < 50% |
| Disponibilité réseau | 📊 80-95% | 🔴 < 50% ou > 99% |
| Capacité installée | 📈 Augmente | ❌ Stable = pas croissance |

### Alertes à surveiller

- ⚠️ **Production < 800 MW**: Risque de délestage
- ⚠️ **Efficacité < 60%**: Maintenance requise
- ✅ **Production > 1200 MW**: Excédent possible (stockage)
- 🟡 **Capacité > 95%**: Réseau saturé

---

## 🎯 Cas d'usage

### Cas 1: Vérifier production en temps réel
```
1. Ouvrir le dashboard
2. Regarder les KPI cards
3. Production totale = situation actuelle
```

### Cas 2: Analyser efficacité par région
```
1. Consulter graphique "Capacité par région"
2. Identifier régions sous-performantes
3. Planifier investissements
```

### Cas 3: Prévoir pics de consommation
```
1. Voir graphique "Production horaire"
2. Identifier patterns (pics matin/soir)
3. Organiser production
```

### Cas 4: Exporter rapport
```
1. Appuyer Ctrl+P
2. Console affiche données JSON
3. Copier-coller dans Excel/Power BI
```

---

## 🔧 Troubleshooting

| Problème | Solution |
|----------|----------|
| Graphiques vides | Actualiser (F5) ou Ctrl+Shift+R |
| Layout cassé | Vérifier zoom (Ctrl+0) |
| Données périmées | Cliquer "Actualiser" en haut |
| Pas de données PostgreSQL | Vérifier connection en console (F12) |

---

## 📱 Utilisation Mobile

```
Sur téléphone:
1. Accéder: http://votre-serveur:8000/dashboard/
2. Sidebar: Clic hamburger (menu) pour ouvrir
3. Charts: Scroller horizontalement si nécessaire
4. Tactile: Swipe sur graphiques pour zoomer
```

---

## 💡 Astuces

✅ **Sauvegarder un screenshot**: Cmd+Shift+4 (Mac) ou PrtScn (Windows)  
✅ **Exporter un graphique**: Clic droit → Copier image  
✅ **Fullscreen**: F11 (votre navigateur)  
✅ **Zoom optimisé**: Ctrl+0 (reset) ou Ctrl++ (agrandir)  

---

## 📞 Support

Pour questions sur:
- **Dashboard**: Voir `dashboard/README.md`
- **Données**: Consulter `README.md` principal du projet
- **PostgreSQL**: Voir `QUERIES.sql` pour requêtes exemples

---

**Version**: 1.0.0  
**Dernière maj**: 11 Janvier 2026  
**Source**: Energy DW France 🔋
