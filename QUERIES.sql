-- ============================================================================
-- 📊 REQUÊTES SIMPLES - Data Warehouse Énergie France
-- ============================================================================
-- Exécutez ces requêtes dans pgAdmin ou DBeaver

-- ============================================================================
-- 1️⃣ EXPLORATIONS BASIQUES
-- ============================================================================

-- Production totale par type d'énergie
SELECT 
    e.energy_type_name,
    COUNT(*) as nb_jours,
    ROUND(AVG(f.value_mw)::numeric, 2) as production_moyenne_mw,
    ROUND(MAX(f.value_mw)::numeric, 2) as production_max_mw,
    ROUND(MIN(f.value_mw)::numeric, 2) as production_min_mw
FROM gold.fact_energy_production f
JOIN gold.dim_energy_type e ON f.energy_type_id = e.energy_type_id
GROUP BY e.energy_type_id, e.energy_type_name
ORDER BY production_moyenne_mw DESC;

-- ============================================================================
-- 2️⃣ PRODUCTION PAR ANNÉE
-- ============================================================================

-- Production annuelle par type d'énergie
SELECT 
    d.year,
    e.energy_type_name,
    COUNT(*) as nb_jours,
    ROUND(AVG(f.value_mw)::numeric, 2) as mw_moyen,
    ROUND(SUM(f.value_mw)::numeric, 0) as mwh_total
FROM gold.fact_energy_production f
JOIN gold.dim_date d ON f.date_id = d.date_id
JOIN gold.dim_energy_type e ON f.energy_type_id = e.energy_type_id
GROUP BY d.year, e.energy_type_id, e.energy_type_name
ORDER BY d.year DESC, mw_moyen DESC;

-- ============================================================================
-- 3️⃣ INSTALLATIONS PAR RÉGION
-- ============================================================================

-- Nombre de plantes par région et technologie
SELECT 
    p.region,
    p.technology,
    COUNT(*) as nb_installations,
    ROUND(SUM(p.capacity_mw)::numeric, 2) as capacite_totale_mw,
    ROUND(AVG(p.capacity_mw)::numeric, 2) as capacite_moyenne_mw
FROM gold.dim_plant p
WHERE p.region IS NOT NULL
GROUP BY p.region, p.technology
ORDER BY capacite_totale_mw DESC;

-- ============================================================================
-- 4️⃣ TOP 10 INSTALLATIONS PAR CAPACITÉ
-- ============================================================================

SELECT 
    plant_name,
    technology,
    region,
    ROUND(capacity_mw::numeric, 2) as capacite_mw,
    TO_CHAR(commissioning_date, 'YYYY-MM-DD') as date_mise_en_service
FROM gold.dim_plant
WHERE capacity_mw > 0
ORDER BY capacity_mw DESC
LIMIT 10;

-- ============================================================================
-- 5️⃣ PRODUCTION MOYENNE PAR MOIS DE L'ANNÉE
-- ============================================================================

SELECT 
    d.month,
    CASE d.month
        WHEN 1 THEN 'Janvier'
        WHEN 2 THEN 'Février'
        WHEN 3 THEN 'Mars'
        WHEN 4 THEN 'Avril'
        WHEN 5 THEN 'Mai'
        WHEN 6 THEN 'Juin'
        WHEN 7 THEN 'Juillet'
        WHEN 8 THEN 'Août'
        WHEN 9 THEN 'Septembre'
        WHEN 10 THEN 'Octobre'
        WHEN 11 THEN 'Novembre'
        WHEN 12 THEN 'Décembre'
    END as mois,
    COUNT(DISTINCT d.date_id) as nb_jours,
    ROUND(AVG(f.value_mw)::numeric, 2) as mw_moyen,
    ROUND(MAX(f.value_mw)::numeric, 2) as mw_max,
    ROUND(MIN(f.value_mw)::numeric, 2) as mw_min
FROM gold.fact_energy_production f
JOIN gold.dim_date d ON f.date_id = d.date_id
GROUP BY d.month
ORDER BY d.month;

-- ============================================================================
-- 6️⃣ PRODUCTION LES JOURS DE WEEK-END vs SEMAINE
-- ============================================================================

SELECT 
    CASE d.is_weekend
        WHEN 0 THEN 'Semaine'
        WHEN 1 THEN 'Week-end'
    END as jour_type,
    COUNT(DISTINCT d.date_id) as nb_jours,
    ROUND(AVG(f.value_mw)::numeric, 2) as mw_moyen,
    ROUND(MAX(f.value_mw)::numeric, 2) as mw_max
FROM gold.fact_energy_production f
JOIN gold.dim_date d ON f.date_id = d.date_id
GROUP BY d.is_weekend;

-- ============================================================================
-- 7️⃣ CAPACITÉ INSTALLÉE TOTALE
-- ============================================================================

-- Capacité par type d'énergie (dernière date disponible)
SELECT 
    rc.energy_type_id,
    e.energy_type_name,
    COUNT(DISTINCT rc.region) as nb_regions,
    ROUND(SUM(rc.total_capacity_mw)::numeric, 2) as capacite_totale_mw,
    rc.date_id
FROM gold.fact_renewable_capacity rc
JOIN gold.dim_energy_type e ON rc.energy_type_id = e.energy_type_id
WHERE rc.date_id = (SELECT MAX(date_id) FROM gold.fact_renewable_capacity)
GROUP BY rc.energy_type_id, e.energy_type_name, rc.date_id
ORDER BY capacite_totale_mw DESC;

-- ============================================================================
-- 8️⃣ ÉVOLUTION DE LA CAPACITÉ DANS LE TEMPS
-- ============================================================================

SELECT 
    rc.date_id,
    d.date,
    e.energy_type_name,
    ROUND(rc.total_capacity_mw::numeric, 2) as capacite_mw,
    rc.nb_plants
FROM gold.fact_renewable_capacity rc
JOIN gold.dim_date d ON rc.date_id = d.date_id
JOIN gold.dim_energy_type e ON rc.energy_type_id = e.energy_type_id
WHERE rc.energy_type_id = 1  -- Solar
ORDER BY rc.date_id DESC
LIMIT 20;

-- ============================================================================
-- 9️⃣ STATISTIQUES GLOBALES
-- ============================================================================

SELECT 
    'Dimensions' as categorie,
    'Jours' as table_name,
    COUNT(*) as total
FROM gold.dim_date

UNION ALL

SELECT 'Dimensions', 'Types d\'énergie', COUNT(*) FROM gold.dim_energy_type
UNION ALL
SELECT 'Dimensions', 'Régions', COUNT(*) FROM gold.dim_location
UNION ALL
SELECT 'Dimensions', 'Installations', COUNT(*) FROM gold.dim_plant
UNION ALL
SELECT 'Fact Tables', 'Production', COUNT(*) FROM gold.fact_energy_production
UNION ALL
SELECT 'Fact Tables', 'Capacité', COUNT(*) FROM gold.fact_renewable_capacity;

-- ============================================================================
-- 🔟 RECHERCHE SPÉCIFIQUE - Installations solaires en Île-de-France
-- ============================================================================

SELECT 
    plant_name,
    technology,
    ROUND(capacity_mw::numeric, 2) as capacite_mw,
    TO_CHAR(commissioning_date, 'YYYY-MM-DD') as date_mise_en_service,
    latitude,
    longitude
FROM gold.dim_plant
WHERE region ILIKE '%Île%' 
  AND technology ILIKE '%solar%'
  AND capacity_mw > 0
ORDER BY capacity_mw DESC;

-- ============================================================================
-- FIN DES REQUÊTES
-- ============================================================================
