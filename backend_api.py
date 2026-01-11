"""
🔌 Flask API Backend - Dashboard Énergie France
Connecte le dashboard HTML aux données PostgreSQL en temps réel

Installation:
    pip install flask flask-cors sqlalchemy psycopg2-binary

Utilisation:
    python backend_api.py
    Puis modifier dashboard/js/charts.js pour utiliser l'API
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlalchemy as sa
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Configuration
app = Flask(__name__)
CORS(app)

# Connexion PostgreSQL
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'jihane')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'dw_energie_france')

DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = sa.create_engine(DATABASE_URL)

print(f"✅ Connexion PostgreSQL: {DB_HOST}:{DB_PORT}/{DB_NAME}")

# ====================================
# ROUTES API AVANCÉES
# ====================================

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    try:
        with engine.connect() as conn:
            conn.execute(sa.text('SELECT 1'))
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@app.route('/api/production-by-city-year', methods=['GET'])
def production_by_city_year():
    """Production par ville et par année (données multi-années)"""
    try:
        query = """
        SELECT 
            EXTRACT(YEAR FROM d.date) as year,
            l.region as city,
            ROUND(SUM(f.production_mw)::numeric, 2) as production_mw
        FROM gold.fact_energy_production f
        JOIN gold.dim_date d ON f.date_id = d.date_id
        JOIN gold.dim_location l ON f.location_id = l.location_id
        WHERE EXTRACT(YEAR FROM d.date) >= 2020
        GROUP BY EXTRACT(YEAR FROM d.date), l.region
        ORDER BY year, production_mw DESC
        LIMIT 100
        """
        with engine.connect() as conn:
            result = conn.execute(sa.text(query))
            data = [dict(row._mapping) for row in result]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/city-comparison', methods=['GET'])
def city_comparison():
    """Comparaison production par région"""
    try:
        query = """
        SELECT 
            l.region,
            COUNT(DISTINCT f.plant_id) as nb_installations,
            ROUND(SUM(f.production_mw)::numeric, 2) as total_production,
            ROUND(AVG(f.production_mw)::numeric, 2) as avg_production,
            ROUND(MAX(f.production_mw)::numeric, 2) as max_production
        FROM gold.fact_energy_production f
        JOIN gold.dim_location l ON f.location_id = l.location_id
        JOIN gold.dim_date d ON f.date_id = d.date_id
        WHERE EXTRACT(YEAR FROM d.date) = EXTRACT(YEAR FROM NOW())
        GROUP BY l.region
        ORDER BY total_production DESC
        """
        with engine.connect() as conn:
            result = conn.execute(sa.text(query))
            data = [dict(row._mapping) for row in result]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/production-trend-5years', methods=['GET'])
def production_trend_5years():
    """Tendance production 5 dernières années"""
    try:
        query = """
        SELECT 
            EXTRACT(YEAR FROM d.date) as year,
            EXTRACT(MONTH FROM d.date) as month,
            ROUND(AVG(f.production_mw)::numeric, 2) as avg_production
        FROM gold.fact_energy_production f
        JOIN gold.dim_date d ON f.date_id = d.date_id
        WHERE EXTRACT(YEAR FROM d.date) >= EXTRACT(YEAR FROM NOW()) - 5
        GROUP BY EXTRACT(YEAR FROM d.date), EXTRACT(MONTH FROM d.date)
        ORDER BY year, month
        """
        with engine.connect() as conn:
            result = conn.execute(sa.text(query))
            data = [dict(row._mapping) for row in result]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/energy-mix-by-city', methods=['GET'])
def energy_mix_by_city():
    """Mix énergétique par région"""
    try:
        query = """
        SELECT 
            l.region,
            et.energy_type,
            ROUND(SUM(f.production_mw)::numeric, 2) as production_mw,
            ROUND(SUM(f.production_mw) * 100.0 / 
                SUM(SUM(f.production_mw)) OVER (PARTITION BY l.region)::numeric, 1) as percentage
        FROM gold.fact_energy_production f
        JOIN gold.dim_location l ON f.location_id = l.location_id
        JOIN gold.dim_energy_type et ON f.energy_type_id = et.energy_type_id
        JOIN gold.dim_date d ON f.date_id = d.date_id
        WHERE EXTRACT(YEAR FROM d.date) = EXTRACT(YEAR FROM NOW())
        GROUP BY l.region, et.energy_type
        ORDER BY l.region, production_mw DESC
        """
        with engine.connect() as conn:
            result = conn.execute(sa.text(query))
            data = [dict(row._mapping) for row in result]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/optimization-analysis', methods=['GET'])
def optimization_analysis():
    """Analyse d'optimisation - Efficacité des installations"""
    try:
        query = """
        SELECT 
            l.region,
            p.plant_name,
            ROUND(AVG(f.production_mw)::numeric, 2) as avg_production,
            ROUND(MAX(f.production_mw)::numeric, 2) as max_capacity,
            ROUND((AVG(f.production_mw) / MAX(f.production_mw) * 100)::numeric, 1) as capacity_factor
        FROM gold.fact_energy_production f
        JOIN gold.dim_location l ON f.location_id = l.location_id
        JOIN gold.dim_plant p ON f.plant_id = p.plant_id
        JOIN gold.dim_date d ON f.date_id = d.date_id
        WHERE EXTRACT(YEAR FROM d.date) = EXTRACT(YEAR FROM NOW())
        GROUP BY l.region, p.plant_name
        ORDER BY capacity_factor DESC
        LIMIT 50
        """
        with engine.connect() as conn:
            result = conn.execute(sa.text(query))
            data = [dict(row._mapping) for row in result]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/distribution-analysis', methods=['GET'])
def distribution_analysis():
    """Analyse distribution - Pertes de réseau estimées"""
    try:
        query = """
        SELECT 
            l.region,
            COUNT(DISTINCT f.plant_id) as nb_installations,
            ROUND(SUM(f.production_mw)::numeric, 2) as total_production,
            ROUND(SUM(f.production_mw) * 0.05::numeric, 2) as estimated_losses,
            ROUND((SUM(f.production_mw) * 0.95)::numeric, 2) as net_distribution,
            ROUND((95)::numeric, 1) as distribution_efficiency
        FROM gold.fact_energy_production f
        JOIN gold.dim_location l ON f.location_id = l.location_id
        JOIN gold.dim_date d ON f.date_id = d.date_id
        WHERE EXTRACT(YEAR FROM d.date) = EXTRACT(YEAR FROM NOW())
        GROUP BY l.region
        ORDER BY total_production DESC
        """
        with engine.connect() as conn:
            result = conn.execute(sa.text(query))
            data = [dict(row._mapping) for row in result]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/capacity-installed', methods=['GET'])
def capacity_installed():
    """Capacité installée par type et région"""
    try:
        query = """
        SELECT 
            l.region,
            et.energy_type,
            ROUND(SUM(rc.capacity_mw)::numeric, 2) as capacity_mw
        FROM gold.fact_renewable_capacity rc
        JOIN gold.dim_location l ON rc.location_id = l.location_id
        JOIN gold.dim_energy_type et ON rc.energy_type_id = et.energy_type_id
        GROUP BY l.region, et.energy_type
        ORDER BY l.region, capacity_mw DESC
        """
        with engine.connect() as conn:
            result = conn.execute(sa.text(query))
            data = [dict(row._mapping) for row in result]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monthly-summary', methods=['GET'])
def monthly_summary():
    """Résumé mensuel - Tendances annuelles"""
    try:
        query = """
        SELECT 
            EXTRACT(YEAR FROM ms.month) as year,
            EXTRACT(MONTH FROM ms.month) as month,
            ROUND(ms.total_production_mw::numeric, 2) as production,
            ROUND(ms.avg_capacity_factor::numeric, 3) as capacity_factor
        FROM gold.fact_monthly_summary ms
        WHERE EXTRACT(YEAR FROM ms.month) >= EXTRACT(YEAR FROM NOW()) - 3
        ORDER BY year DESC, month DESC
        LIMIT 48
        """
        with engine.connect() as conn:
            result = conn.execute(sa.text(query))
            data = [dict(row._mapping) for row in result]
        return jsonify(sorted(data, key=lambda x: (x['year'], x['month'])))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    """Obtenir les KPIs principaux"""
    try:
        with engine.connect() as conn:
            # Production totale
            sql_total = """
            SELECT SUM(value_mw) as production 
            FROM gold.fact_energy_production 
            WHERE date_id = (SELECT MAX(date_id) FROM gold.fact_energy_production)
            """
            
            # Production par type
            sql_by_type = """
            SELECT e.energy_type_name, SUM(f.value_mw) as value
            FROM gold.fact_energy_production f
            JOIN gold.dim_energy_type e ON f.energy_type_id = e.energy_type_id
            WHERE date_id = (SELECT MAX(date_id) FROM gold.fact_energy_production)
            GROUP BY e.energy_type_name
            """
            
            # Capacité totale
            sql_capacity = """
            SELECT SUM(capacity_mw) / 1000.0 as total_gw
            FROM gold.dim_plant
            """
            
            total_result = conn.execute(sa.text(sql_total)).fetchone()
            by_type = conn.execute(sa.text(sql_by_type)).fetchall()
            capacity = conn.execute(sa.text(sql_capacity)).fetchone()
            
            return jsonify({
                'totalProduction': float(total_result[0] or 0),
                'byType': {row[0]: float(row[1]) for row in by_type},
                'installedCapacity': float(capacity[0] or 0),
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/production/by-type', methods=['GET'])
def get_production_by_type():
    """Production par type d'énergie"""
    try:
        with engine.connect() as conn:
            sql = """
            SELECT e.energy_type_name, SUM(f.value_mw) as production
            FROM gold.fact_energy_production f
            JOIN gold.dim_energy_type e ON f.energy_type_id = e.energy_type_id
            WHERE f.date_id >= (SELECT MAX(date_id) - 30 FROM gold.fact_energy_production)
            GROUP BY e.energy_type_name
            ORDER BY production DESC
            """
            result = conn.execute(sa.text(sql)).fetchall()
            
            return jsonify({
                'labels': [row[0] for row in result],
                'values': [float(row[1]) for row in result]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/production/hourly', methods=['GET'])
def get_production_hourly():
    """Production horaire dernières 24h"""
    try:
        with engine.connect() as conn:
            sql = """
            SELECT 
                EXTRACT(HOUR FROM d.date)::int as hour,
                AVG(f.value_mw) as production
            FROM gold.fact_energy_production f
            JOIN gold.dim_date d ON f.date_id = d.date_id
            WHERE d.date >= NOW()::date - INTERVAL '1 day'
            GROUP BY hour
            ORDER BY hour
            """
            result = conn.execute(sa.text(sql)).fetchall()
            
            return jsonify({
                'hours': [f"{int(row[0]):02d}h" for row in result],
                'production': [float(row[1]) for row in result]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/capacity/by-region', methods=['GET'])
def get_capacity_by_region():
    """Capacité installée par région"""
    try:
        with engine.connect() as conn:
            sql = """
            SELECT region, SUM(capacity_mw) / 1000.0 as capacity_gw
            FROM gold.dim_plant
            WHERE region IS NOT NULL
            GROUP BY region
            ORDER BY capacity_gw DESC
            LIMIT 10
            """
            result = conn.execute(sa.text(sql)).fetchall()
            
            return jsonify({
                'regions': [row[0] for row in result],
                'capacity': [float(row[1]) for row in result]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/installations', methods=['GET'])
def get_top_installations():
    """Top 10 installations par capacité"""
    try:
        with engine.connect() as conn:
            sql = """
            SELECT 
                plant_id,
                plant_name,
                technology,
                region,
                capacity_mw,
                energy_source_level_1
            FROM gold.dim_plant
            WHERE capacity_mw > 0
            ORDER BY capacity_mw DESC
            LIMIT 10
            """
            result = conn.execute(sa.text(sql)).fetchall()
            
            installations = []
            for row in result:
                installations.append({
                    'id': row[0],
                    'name': row[1],
                    'technology': row[2],
                    'region': row[3],
                    'capacity': float(row[4]),
                    'type': row[5]
                })
            
            return jsonify(installations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/energy-mix', methods=['GET'])
def get_energy_mix():
    """Répartition des énergies (%)"""
    try:
        with engine.connect() as conn:
            sql = """
            SELECT 
                energy_source_level_1,
                COUNT(*) as count,
                SUM(capacity_mw) as total_capacity
            FROM gold.dim_plant
            WHERE capacity_mw > 0
            GROUP BY energy_source_level_1
            ORDER BY total_capacity DESC
            """
            result = conn.execute(sa.text(sql)).fetchall()
            
            total = sum(row[2] for row in result)
            
            return jsonify({
                'sources': [row[0] for row in result],
                'percentages': [round(float(row[2]) / total * 100, 1) for row in result],
                'counts': [row[1] for row in result]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/regions', methods=['GET'])
def get_regions():
    """Liste des régions avec statistiques"""
    try:
        with engine.connect() as conn:
            sql = """
            SELECT 
                region,
                COUNT(*) as installations,
                SUM(capacity_mw) / 1000.0 as capacity_gw,
                AVG(capacity_mw) as avg_capacity
            FROM gold.dim_plant
            WHERE region IS NOT NULL AND capacity_mw > 0
            GROUP BY region
            ORDER BY capacity_gw DESC
            """
            result = conn.execute(sa.text(sql)).fetchall()
            
            regions = []
            for row in result:
                regions.append({
                    'name': row[0],
                    'installations': row[1],
                    'capacity': float(row[2]),
                    'avgCapacity': float(row[3])
                })
            
            return jsonify(regions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Statistiques générales"""
    try:
        with engine.connect() as conn:
            sql = """
            SELECT 
                COUNT(DISTINCT date_id) as days_recorded,
                COUNT(DISTINCT energy_type_id) as energy_types,
                MAX(value_mw) as peak_production,
                MIN(value_mw) as min_production,
                AVG(value_mw) as avg_production
            FROM gold.fact_energy_production
            """
            result = conn.execute(sa.text(sql)).fetchone()
            
            return jsonify({
                'daysRecorded': result[0],
                'energyTypes': result[1],
                'peakProduction': float(result[2]),
                'minProduction': float(result[3]),
                'avgProduction': float(result[4])
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ====================================
# ERROR HANDLERS
# ====================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Route not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ====================================
# MAIN
# ====================================

if __name__ == '__main__':
    print("""
    
    ╔════════════════════════════════════════════╗
    ║   🔋 Energy DW France - Backend API       ║
    ╚════════════════════════════════════════════╝
    
    📡 Serveur démarré sur http://localhost:5000
    
    📋 Routes disponibles:
       GET  /health                    - Health check
       GET  /api/kpis                  - KPIs principaux
       GET  /api/production/by-type    - Production par type
       GET  /api/production/hourly     - Production horaire
       GET  /api/capacity/by-region    - Capacité par région
       GET  /api/installations         - Top installations
       GET  /api/energy-mix            - Mix énergétique
       GET  /api/regions               - Régions
       GET  /api/statistics            - Statistiques générales
    
    🔗 Dashboard: http://localhost:8000/dashboard/
    📚 Docs: http://localhost:5000/api/ (add endpoints)
    
    """)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
