# 🔋 Dashboard Énergie France

Dashboard professionnel en temps réel pour la visualisation des données de production énergétique .

## ✨ Caractéristiques

- 📊 **4 Graphiques interactifs**: Production par type, Évolution horaire, Capacité par région, Répartition énergies
- 📱 **Design responsive**: Desktop, Tablet, Mobile
- 🎨 **Thème dark moderne**: Couleurs cyan, rose, violet sur fond sombre
- ⚡ **Animations fluides**: Entrées/sorties élégantes, hover effects
- 📈 **4 KPI Cards**: Production totale, Solaire, Éolien, Capacité installée
- 📍 **Carte de régions**: Visualisation géographique (prête pour intégration SIG)
- 📋 **Table des installations**: Top 10 avec détails en temps réel
- 🎯 **Sidebar navigation**: Menu ergonomique avec sections

## 🚀 Démarrage rapide

### Ouvrir le dashboard

```bash
# Option 1: Double-cliquer sur index.html
cd dashboard
explorer index.html

# Option 2: Serveur local Python
python -m http.server 8000
# Puis ouvrir http://localhost:8000/dashboard/
```

### Fichiers principaux

```
dashboard/
├── index.html          ← Interface principale
├── css/
│   └── style.css       ← Styles (dark theme, animations)
├── js/
│   ├── charts.js       ← Graphiques Chart.js
│   └── app.js          ← Interactions & animations
└── data/
    └── energy_data.json ← Données mock (prêtes pour API)
```

## 🎨 Design & Couleurs

```css
--dark-bg: #0f1b3d;           /* Fond principal */
--sidebar-bg: #1a2654;        /* Sidebar */
--card-bg: #1e2e5f;           /* Cartes */
--primary: #00d4ff;           /* Cyan (accent principal) */
--accent-pink: #ff4d7d;       /* Rose */
--accent-purple: #9d5bff;     /* Violet */
--success: #00ff7f;           /* Vert */
--warning: #ffa500;           /* Orange */
```

## 📊 Graphiques

### 1. Production par type (Bar Chart)
- Solaire, Éolien, Hydro, Thermique, Autres
- Valeurs en MW
- Couleurs distinctes par type

### 2. Production horaire (Line Chart)
- 24h de données horaires
- Comparaison Production vs Consommation
- Ligne lisse avec points interactifs

### 3. Capacité par région (Horizontal Bar)
- Top 7 régions
- Valeurs en GW
- Classement par capacité

### 4. Répartition énergies (Doughnut Chart)
- Pourcentages par source
- 5 catégories
- Tooltip au survol

## 🔧 Personnalisation

### Modifier les couleurs

Éditer `css/style.css` - section `VARIABLES & COULEURS ÉNERGIE`:

```css
:root {
  --primary: #00d4ff;        /* Changer la couleur primaire */
  --accent-pink: #ff4d7d;    /* Changer la couleur rose */
  /* ... etc */
}
```

### Intégrer des données réelles

Remplacer les données mock dans `js/charts.js`:

```javascript
// Avant: données statiques
data: [342, 567, 298, 145, 82],

// Après: appel API
fetch('/api/production/by-type')
  .then(r => r.json())
  .then(data => updateChart(data))
```

### Charger depuis PostgreSQL

```javascript
// Exemple avec fetch
async function loadData() {
  const response = await fetch('http://localhost:5000/api/energy-data');
  const data = await response.json();
  updateAllCharts(data);
}

loadData();
```

## ⌨️ Raccourcis clavier

| Touche | Action |
|--------|--------|
| `Ctrl+P` | Exporter données (console) |
| `Ctrl+D` | Changer thème (dark/light) |

## 📱 Responsive

- **Desktop**: Grille 2 colonnes, sidebar fixe
- **Tablet (768px)**: Grille 1 colonne, sidebar off-canvas
- **Mobile (480px)**: Layout empilé, boutons optimisés

## 🔌 Intégration PostgreSQL

### Connecter l'API Python

```python
# backend.py
from flask import Flask, jsonify
import sqlalchemy as sa

app = Flask(__name__)
engine = sa.create_engine('postgresql://postgres:jihane@localhost:5432/dw_energie_france')

@app.route('/api/energy-data')
def get_energy_data():
    with engine.connect() as conn:
        result = conn.execute(sa.text('SELECT * FROM gold.fact_energy_production'))
        return jsonify(result.fetchall())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

Puis mettre à jour `js/app.js`:

```javascript
const API_BASE = 'http://localhost:5000/api';

async function loadFromPostgreSQL() {
  const data = await fetch(`${API_BASE}/energy-data`).then(r => r.json());
  updateDashboard(data);
}
```

## 🛠️ Outils utilisés

- **HTML5** - Structure
- **CSS3** - Styling (grid, flexbox, animations)
- **JavaScript** - Interactions
- **Chart.js** - Graphiques interactifs
- **Font Awesome** - Icônes

## 📊 Données disponibles

Voir `data/energy_data.json` pour la structure complète:

```json
{
  "kpis": { ... },
  "productionByType": { ... },
  "hourlyProduction": { ... },
  "capacityByRegion": { ... },
  "topInstallations": [ ... ],
  "alerts": [ ... ]
}
```

## 🚀 Prochaines étapes

- [ ] Connecter à PostgreSQL en temps réel
- [ ] Ajouter filtres temporels (jour, mois, année)
- [ ] Intégrer carte SIG (Leaflet/Mapbox)
- [ ] Export PDF/CSV
- [ ] Alertes en temps réel
- [ ] Dark mode toggle
- [ ] Responsivité mobile améliorée
- [ ] PWA offline mode
- [ ] Historique données (comparaisons)
- [ ] API WebSocket temps réel

## 📝 Licence

MIT - Libre d'utilisation

---

**Questions?** Consulter le fichier principal `README.md` du projet Data Warehouse.

**Version**: 1.0.0  
**Dernière mise à jour**: 11 Janvier 2026  
**Auteur**: Data Warehouse Énergie France  
