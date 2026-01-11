-- ============================================================================
-- 🐘 Data Warehouse Énergie France - PostgreSQL Schema
-- ============================================================================
-- Schéma GOLD complet : Dimensions + Fact Tables
-- À exécuter dans PostgreSQL avant le chargement
-- ============================================================================

-- 1. Créer le schéma
CREATE SCHEMA IF NOT EXISTS gold;

-- ============================================================================
-- DIMENSIONS
-- ============================================================================

-- 1.1 Dimension Date
CREATE TABLE IF NOT EXISTS gold.dim_date (
    date_id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    week_of_year INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(10) NOT NULL,
    is_weekend INTEGER NOT NULL,
    is_holiday INTEGER NOT NULL,
    
    CONSTRAINT ck_month CHECK (month BETWEEN 1 AND 12),
    CONSTRAINT ck_day CHECK (day BETWEEN 1 AND 31),
    CONSTRAINT ck_quarter CHECK (quarter BETWEEN 1 AND 4),
    CONSTRAINT ck_is_weekend CHECK (is_weekend IN (0, 1)),
    CONSTRAINT ck_is_holiday CHECK (is_holiday IN (0, 1))
);

-- Index
CREATE INDEX idx_dim_date_year_month ON gold.dim_date (year, month);
CREATE INDEX idx_dim_date_is_holiday ON gold.dim_date (is_holiday) WHERE is_holiday = 1;
CREATE INDEX idx_dim_date_is_weekend ON gold.dim_date (is_weekend) WHERE is_weekend = 1;

-- 1.2 Dimension Type d'Énergie
CREATE TABLE IF NOT EXISTS gold.dim_energy_type (
    energy_type_id INTEGER PRIMARY KEY,
    energy_type_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    
    CONSTRAINT ck_category CHECK (category IN ('Thermique', 'Renouvelable', 'Nucléaire', 'Importation'))
);

-- Data de base
INSERT INTO gold.dim_energy_type VALUES
    (1, 'Nucléaire', 'Nucléaire', 'Production nucléaire France'),
    (2, 'Éolien Terrestre', 'Renouvelable', 'Énergie éolienne onshore'),
    (3, 'Éolien Offshore', 'Renouvelable', 'Énergie éolienne offshore'),
    (4, 'Solaire', 'Renouvelable', 'Énergie photovoltaïque'),
    (5, 'Hydraulique', 'Renouvelable', 'Production hydroélectrique')
ON CONFLICT DO NOTHING;

-- 1.3 Dimension Localisation (Régions France)
CREATE TABLE IF NOT EXISTS gold.dim_location (
    location_id INTEGER PRIMARY KEY,
    nuts_code VARCHAR(10) NOT NULL UNIQUE,
    region_name VARCHAR(100) NOT NULL,
    region_code VARCHAR(3),
    latitude DECIMAL(9, 6),
    longitude DECIMAL(9, 6),
    
    CONSTRAINT ck_latitude CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_longitude CHECK (longitude BETWEEN -180 AND 180)
);

-- Index
CREATE INDEX idx_dim_location_region_name ON gold.dim_location (region_name);
CREATE INDEX idx_dim_location_nuts_code ON gold.dim_location (nuts_code);

-- 1.4 Dimension Installation (Centrales/Parcs)
CREATE TABLE IF NOT EXISTS gold.dim_plant (
    plant_id BIGINT PRIMARY KEY,
    plant_name VARCHAR(255) NOT NULL,
    plant_code VARCHAR(50),
    energy_type_id INTEGER NOT NULL REFERENCES gold.dim_energy_type(energy_type_id),
    location_id INTEGER REFERENCES gold.dim_location(location_id),
    capacity_mw DECIMAL(10, 2),
    status VARCHAR(20),
    commissioning_date DATE,
    decommissioning_date DATE,
    
    CONSTRAINT ck_status CHECK (status IN ('Operational', 'Under Construction', 'Decommissioned', 'Unknown')),
    CONSTRAINT ck_capacity CHECK (capacity_mw >= 0)
);

-- Index
CREATE INDEX idx_dim_plant_energy_type_id ON gold.dim_plant (energy_type_id);
CREATE INDEX idx_dim_plant_location_id ON gold.dim_plant (location_id);
CREATE INDEX idx_dim_plant_status ON gold.dim_plant (status);

-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- 2.1 Fact: Production d'Énergie (Horaire/Journalière)
CREATE TABLE IF NOT EXISTS gold.fact_energy_production (
    production_id BIGINT PRIMARY KEY,
    date_id INTEGER NOT NULL REFERENCES gold.dim_date(date_id),
    plant_id BIGINT NOT NULL REFERENCES gold.dim_plant(plant_id),
    energy_type_id INTEGER NOT NULL REFERENCES gold.dim_energy_type(energy_type_id),
    location_id INTEGER REFERENCES gold.dim_location(location_id),
    production_mwh DECIMAL(15, 2) NOT NULL,
    expected_mwh DECIMAL(15, 2),
    efficiency_percent DECIMAL(5, 2),
    data_quality_score DECIMAL(5, 2),
    source_name VARCHAR(100),
    inserted_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_production_mwh CHECK (production_mwh >= 0),
    CONSTRAINT ck_expected_mwh CHECK (expected_mwh IS NULL OR expected_mwh >= 0),
    CONSTRAINT ck_efficiency CHECK (efficiency_percent IS NULL OR (efficiency_percent >= 0 AND efficiency_percent <= 100)),
    CONSTRAINT ck_dq_score CHECK (data_quality_score IS NULL OR (data_quality_score >= 0 AND data_quality_score <= 100))
);

-- Index
CREATE INDEX idx_fact_production_date_id ON gold.fact_energy_production (date_id);
CREATE INDEX idx_fact_production_plant_id ON gold.fact_energy_production (plant_id);
CREATE INDEX idx_fact_production_energy_type ON gold.fact_energy_production (energy_type_id);
CREATE INDEX idx_fact_production_location ON gold.fact_energy_production (location_id);
CREATE INDEX idx_fact_production_date_plant ON gold.fact_energy_production (date_id, plant_id);

-- 2.2 Fact: Capacité Installée Renouvelable
CREATE TABLE IF NOT EXISTS gold.fact_renewable_capacity (
    capacity_id BIGINT PRIMARY KEY,
    date_id INTEGER NOT NULL REFERENCES gold.dim_date(date_id),
    energy_type_id INTEGER NOT NULL REFERENCES gold.dim_energy_type(energy_type_id),
    location_id INTEGER REFERENCES gold.dim_location(location_id),
    total_capacity_mw DECIMAL(15, 2) NOT NULL,
    operational_capacity_mw DECIMAL(15, 2),
    new_installations_count INTEGER,
    net_capacity_change_mw DECIMAL(15, 2),
    source_name VARCHAR(100),
    
    CONSTRAINT ck_capacity_total CHECK (total_capacity_mw >= 0),
    CONSTRAINT ck_capacity_operational CHECK (operational_capacity_mw IS NULL OR operational_capacity_mw >= 0)
);

-- Index
CREATE INDEX idx_fact_renewable_date_id ON gold.fact_renewable_capacity (date_id);
CREATE INDEX idx_fact_renewable_energy_type ON gold.fact_renewable_capacity (energy_type_id);
CREATE INDEX idx_fact_renewable_location ON gold.fact_renewable_capacity (location_id);

-- 2.3 Fact: Résumé Mensuel
CREATE TABLE IF NOT EXISTS gold.fact_monthly_summary (
    summary_id BIGINT PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    energy_type_id INTEGER NOT NULL REFERENCES gold.dim_energy_type(energy_type_id),
    location_id INTEGER REFERENCES gold.dim_location(location_id),
    total_production_mwh DECIMAL(18, 2) NOT NULL,
    avg_daily_production_mwh DECIMAL(15, 2),
    min_daily_production_mwh DECIMAL(15, 2),
    max_daily_production_mwh DECIMAL(15, 2),
    days_with_data INTEGER,
    data_completeness_percent DECIMAL(5, 2),
    
    CONSTRAINT ck_month_range CHECK (month BETWEEN 1 AND 12),
    CONSTRAINT ck_production_total CHECK (total_production_mwh >= 0),
    CONSTRAINT ck_days_count CHECK (days_with_data BETWEEN 0 AND 31),
    CONSTRAINT ck_completeness CHECK (data_completeness_percent IS NULL OR (data_completeness_percent >= 0 AND data_completeness_percent <= 100))
);

-- Index composé pour agréger rapidement par mois/année
CREATE UNIQUE INDEX idx_fact_monthly_unique ON gold.fact_monthly_summary (year, month, energy_type_id, location_id);
CREATE INDEX idx_fact_monthly_energy_type ON gold.fact_monthly_summary (energy_type_id);
CREATE INDEX idx_fact_monthly_location ON gold.fact_monthly_summary (location_id);
CREATE INDEX idx_fact_monthly_year_month ON gold.fact_monthly_summary (year, month);

-- ============================================================================
-- VUES UTILES POUR L'ANALYTIQUE
-- ============================================================================

-- Vue: Production totale par jour et type d'énergie
CREATE OR REPLACE VIEW gold.v_daily_production_by_type AS
SELECT 
    dd.date_id,
    dd.date,
    dd.year,
    dd.month,
    de.energy_type_name,
    de.category,
    SUM(fp.production_mwh) AS total_production_mwh,
    COUNT(DISTINCT fp.plant_id) AS num_plants,
    AVG(fp.efficiency_percent) AS avg_efficiency
FROM gold.fact_energy_production fp
JOIN gold.dim_date dd ON fp.date_id = dd.date_id
JOIN gold.dim_energy_type de ON fp.energy_type_id = de.energy_type_id
GROUP BY dd.date_id, dd.date, dd.year, dd.month, de.energy_type_id, de.energy_type_name, de.category;

-- Vue: Capacité installée actuelle par région
CREATE OR REPLACE VIEW gold.v_capacity_by_region AS
SELECT 
    dl.region_name,
    dl.nuts_code,
    de.energy_type_name,
    COUNT(DISTINCT dp.plant_id) AS num_plants,
    SUM(dp.capacity_mw) AS total_capacity_mw,
    AVG(dp.capacity_mw) AS avg_capacity_mw
FROM gold.dim_plant dp
JOIN gold.dim_location dl ON dp.location_id = dl.location_id
JOIN gold.dim_energy_type de ON dp.energy_type_id = de.energy_type_id
WHERE dp.status = 'Operational'
GROUP BY dl.location_id, dl.region_name, dl.nuts_code, de.energy_type_id, de.energy_type_name;

-- Vue: Performances mensuelles
CREATE OR REPLACE VIEW gold.v_monthly_performance AS
SELECT 
    fms.year,
    fms.month,
    de.energy_type_name,
    dl.region_name,
    fms.total_production_mwh,
    fms.avg_daily_production_mwh,
    fms.data_completeness_percent
FROM gold.fact_monthly_summary fms
LEFT JOIN gold.dim_energy_type de ON fms.energy_type_id = de.energy_type_id
LEFT JOIN gold.dim_location dl ON fms.location_id = dl.location_id
ORDER BY fms.year DESC, fms.month DESC;

-- ============================================================================
-- PERMISSIONS
-- ============================================================================

GRANT USAGE ON SCHEMA gold TO PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA gold TO PUBLIC;

-- ============================================================================
-- COMMENTAIRES (Metadata)
-- ============================================================================

COMMENT ON SCHEMA gold IS 'Couche GOLD - Star Schema pour analytique Data Warehouse Énergie';

COMMENT ON TABLE gold.dim_date IS 'Dimension temporelle complète (2015-2026)';
COMMENT ON TABLE gold.dim_energy_type IS 'Types d''énergie couverts: Nucléaire, Éolien, Solaire, Hydro, Thermique';
COMMENT ON TABLE gold.dim_location IS 'Localisations: Régions France avec codes NUTS';
COMMENT ON TABLE gold.dim_plant IS 'Master data installations: Centrales, Parcs éoliens, Panneaux solaires';

COMMENT ON TABLE gold.fact_energy_production IS 'Production horaire/quotidienne d''énergie avec qualité des données';
COMMENT ON TABLE gold.fact_renewable_capacity IS 'Capacité installée renouvelable par date, type, localisation';
COMMENT ON TABLE gold.fact_monthly_summary IS 'Agrégations mensuelles pour performance rapide';

-- ============================================================================
-- FIN - Schéma Gold PostgreSQL
-- ============================================================================
