-- ============================================================================
-- 🐘 Data Warehouse Énergie France - PostgreSQL Schema (Simplifié)
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
    is_holiday INTEGER NOT NULL
);

CREATE INDEX idx_dim_date_year_month ON gold.dim_date (year, month);

-- 1.2 Dimension Type d'Énergie
CREATE TABLE IF NOT EXISTS gold.dim_energy_type (
    energy_type_id INTEGER PRIMARY KEY,
    energy_type_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    unit VARCHAR(10),
    category VARCHAR(50) NOT NULL
);

-- 1.3 Dimension Localisation (Régions France)
CREATE TABLE IF NOT EXISTS gold.dim_location (
    location_id INTEGER PRIMARY KEY,
    nuts_1_code VARCHAR(10),
    nuts_2_code VARCHAR(10),
    region_name VARCHAR(100) NOT NULL,
    region_code VARCHAR(3),
    country VARCHAR(2) NOT NULL
);

-- 1.4 Dimension Installation (Centrales/Parcs)
CREATE TABLE IF NOT EXISTS gold.dim_plant (
    plant_id BIGINT PRIMARY KEY,
    plant_name VARCHAR(255),
    technology VARCHAR(100),
    energy_source VARCHAR(100),
    capacity_mw DECIMAL(10, 2),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(10, 8),
    commissioning_date TIMESTAMP,
    region VARCHAR(100)
);

-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- 2.1 Fact: Production d'Énergie (Journalière)
CREATE TABLE IF NOT EXISTS gold.fact_energy_production (
    production_id BIGINT PRIMARY KEY,
    date_id INTEGER REFERENCES gold.dim_date(date_id),
    energy_type_id INTEGER REFERENCES gold.dim_energy_type(energy_type_id),
    value_mw DECIMAL(15, 2),
    value_min_mw DECIMAL(15, 2),
    value_max_mw DECIMAL(15, 2),
    value_avg_mw DECIMAL(15, 2),
    nb_records INTEGER,
    created_at TIMESTAMP,
    country VARCHAR(2)
);

CREATE INDEX idx_fact_production_date_id ON gold.fact_energy_production (date_id);
CREATE INDEX idx_fact_production_energy_type ON gold.fact_energy_production (energy_type_id);

-- 2.2 Fact: Capacité Installée Renouvelable
CREATE TABLE IF NOT EXISTS gold.fact_renewable_capacity (
    capacity_id BIGINT PRIMARY KEY,
    region VARCHAR(100),
    energy_type_id INTEGER REFERENCES gold.dim_energy_type(energy_type_id),
    total_capacity_mw DECIMAL(15, 2),
    avg_capacity_mw DECIMAL(15, 2),
    nb_plants INTEGER,
    first_commission_date DATE,
    date_id INTEGER REFERENCES gold.dim_date(date_id),
    country VARCHAR(2)
);

CREATE INDEX idx_fact_renewable_date ON gold.fact_renewable_capacity (date_id);
CREATE INDEX idx_fact_renewable_energy_type ON gold.fact_renewable_capacity (energy_type_id);

-- 2.3 Fact: Résumé Mensuel (optionnel)
CREATE TABLE IF NOT EXISTS gold.fact_monthly_summary (
    summary_id BIGINT PRIMARY KEY,
    date_id INTEGER REFERENCES gold.dim_date(date_id),
    energy_type_id INTEGER REFERENCES gold.dim_energy_type(energy_type_id),
    production_mwh DECIMAL(18, 2),
    avg_mw DECIMAL(15, 2),
    country VARCHAR(2)
);

-- ============================================================================
-- PERMISSIONS
-- ============================================================================

GRANT USAGE ON SCHEMA gold TO PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA gold TO PUBLIC;

-- ============================================================================
-- FIN - Schéma Gold PostgreSQL Simplifié
-- ============================================================================
