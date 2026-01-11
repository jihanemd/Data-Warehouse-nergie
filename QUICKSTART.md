# ⚡ QUICKSTART - Dashboard en 2 minutes

## Option 1️⃣: Dashboard seul (Sans données PostgreSQL)

```bash
# Ouvrir directement
cd Data-Warehouse-nergie\dashboard
start index.html

# ✅ Le dashboard s'ouvre avec données mock (déjà intégrées)
# 📊 Tous les graphiques fonctionnent immédiatement
# ⏱️ Durée: 10 secondes
```

**Bon pour:**
- Démonstration design
- Prototype rapide
- Tests interface

---

## Option 2️⃣: Dashboard + API PostgreSQL (Recommandé)

### Étape 1: Lancer l'API (Terminal 1)

```bash
cd c:\Users\dell\Documents\DataSPACE\Data-Warehouse-nergie

# Option A: Directement
python backend_api.py

# Option B: Via venv
.\.venv\Scripts\python.exe backend_api.py

# ✅ Vous devriez voir:
# ✅ Connexion PostgreSQL: localhost:5432/dw_energie_france
# 🚀 Serveur démarré sur http://localhost:5000
```

**Vérifier la connexion:**
```bash
# Ouvrir navigateur
http://localhost:5000/health

# Résultat attendu:
# {"status": "healthy", "database": "connected"}
```

### Étape 2: Lancer Dashboard (Terminal 2)

```bash
cd dashboard
python -m http.server 8000

# ✅ Vous devriez voir:
# Serving HTTP on 0.0.0.0 port 8000
```

### Étape 3: Ouvrir Dashboard (Terminal 3 ou Navigateur)

```bash
# Ouvrir navigateur
http://localhost:8000/index.html

# ✅ Dashboard s'ouvre
# 📊 Graphiques affichent données PostgreSQL EN TEMPS RÉEL
```

**Durée totale: 2 minutes** ⏱️

---

## 📊 Vérifier que ça marche

### Test 1: Graphiques chargent
- ✅ Onglet "Production par type" affiche des barres
- ✅ Onglet "Horaire" affiche des lignes
- ✅ Onglet "Régions" affiche des valeurs
- ✅ Onglet "Mix énergies" affiche camembert

### Test 2: Chiffres s'animent
- ✅ KPI cards affichent: 1,234 MW, 342 MW, 567 MW, 28.5 GW
- ✅ Animations fluides
- ✅ Couleurs cyan/rose/violet

### Test 3: Table affiche installations
- ✅ "Top 10 installations" affiche 5+ lignes
- ✅ Colonnes: Name, Type, Region, Capacity, Production, Status
- ✅ Statuts: "Actif" (vert) ou "Maintenance" (orange)

### Test 4: Interactions
- ✅ Hovrer sur cartes → shadow augmente
- ✅ Survol graphiques → tooltip affiche valeurs
- ✅ Clic "Actualiser" → graphiques se rechargent

---

## 🎯 Utilisation courante

### ✅ Je veux voir la production en temps réel
```
1. Terminal 1: python backend_api.py
2. Terminal 2: python -m http.server 8000
3. Navigateur: http://localhost:8000/index.html
4. Regarder la carte "Production par type"
```

### ✅ Je veux exporter les données
```
1. Dashboard ouvert
2. Appuyer Ctrl+P
3. Ouvrir Console (F12)
4. Copier les données affichées
5. Coller dans Excel/JSON viewer
```

### ✅ Je veux modifier les couleurs
```
1. Éditer: dashboard/css/style.css
2. Ligne 10: --primary: #00d4ff
3. Changer la couleur (ex: #ff0000 pour rouge)
4. Rafraîchir navigateur (F5)
5. Les couleurs changent partout!
```

### ✅ Je veux ajouter mes propres données
```
1. Éditer: backend_api.py
2. Ajouter nouvelle route @app.route('/api/ma-route')
3. Écrire requête SQL
4. Retourner en JSON
5. Appeler depuis dashboard/js/charts.js
```

---

## 🔧 Commandes utiles

```bash
# Vérifier PostgreSQL connectée
curl http://localhost:5000/health

# Voir toutes les routes API
# Aller à: backend_api.py ligne 1-150

# Redémarrer services
# Fermer tous les terminaux (Ctrl+C)
# Relancer les 2 terminaux

# Vider cache
F5 (rafraîchir page)
Ctrl+Shift+Delete (vider cache navigateur)

# Voir logs erreurs
F12 (Console) dans navigateur

# Arrêter proprement
# Terminal: Appuyer Ctrl+C
# Python: Attend quelques secondes avant de fermer
```

---

## ❓ FAQ rapide

**Q: Ça ne marche pas?**
A: 
1. Vérifier PostgreSQL est lancé: `pg_isready`
2. Vérifier credentials dans `backend_api.py` (ligne 18)
3. Voir console erreurs: F12 dans navigateur

**Q: Comment changer les données?**
A: Modifier fichiers dans `dashboard/data/energy_data.json` ou créer API routes dans `backend_api.py`

**Q: Puis-je déployer en production?**
A: Oui! Voir `INTEGRATION_GUIDE.md` - section "Déploiement Production"

**Q: Comment ajouter filtres temporels?**
A: Modifier `backend_api.py` routes pour accepter paramètres date, puis filtrer SQL queries

**Q: Les données sont en cache?**
A: Non, actualisées toutes les 5 secondes. Voir `backend_api.py` ligne 300+

---

## ⏱️ Timing attendu

| Étape | Durée |
|-------|-------|
| Lancer API | 5s |
| Lancer Dashboard | 3s |
| Charger données PostgreSQL | 2s |
| Afficher graphiques | 1s |
| Totale | **~12s** |

---

## 🎓 Prochaines étapes

1. **Intégration Power BI**: Utiliser endpoints API dans Power BI Desktop
2. **Alertes temps réel**: Ajouter WebSocket pour notifications
3. **Carte SIG**: Intégrer Leaflet/Mapbox pour géolocalisation
4. **Dashboard mobile**: PWA pour utilisation sur téléphone
5. **Rapports PDF**: Générer rapports automatiques

---

## 📞 Support

**Fichiers importants:**
- `INTEGRATION_GUIDE.md` - Setup détaillé
- `dashboard/README.md` - Customisation dashboard
- `dashboard/INSTRUCTIONS.md` - Guide utilisateur

**Commandes utiles:**
```bash
# Recréer base PostgreSQL
.\.venv\Scripts\python.exe reload_postgres.py

# Vérifier intégrité données
.\.venv\Scripts\python.exe verify_postgres.py

# Voir requêtes SQL exemples
cat QUERIES.sql
```

---

**⚡ Prêt?** → Lancer `python backend_api.py` en Terminal 1 et profitez du dashboard! 🎉
