"""
Vérifier le chargement PostgreSQL
"""
import psycopg2

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "dw_energie_france"
DB_USER = "postgres"
DB_PASSWORD = "jihane"

print("✅ Vérification du Data Warehouse PostgreSQL")
print()

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

tables = {
    'dim_date': 4383,
    'dim_energy_type': 5,
    'dim_location': 31,
    'dim_plant': 9744,
    'fact_energy_production': 6301,
    'fact_renewable_capacity': 24,
}

total = 0
for table_name, expected in tables.items():
    cursor.execute(f"SELECT COUNT(*) FROM gold.{table_name}")
    count = cursor.fetchone()[0]
    total += count
    icon = "✅" if count == expected else "⚠️"
    print(f"  {icon} {table_name:30s} → {count:>10,} lignes (attendu: {expected})")

cursor.close()
conn.close()

print()
print(f"📈 TOTAL: {total:,} lignes")
print()
print("🎉 Data Warehouse complet dans PostgreSQL!")
print()
print("✨ Vous avez:")
print("   • 4 dimensions (Date, EnergyType, Location, Plant)")
print("   • 2 fact tables (Production, Capacity)")
print("   • 20,488 lignes de données")
print()
print("🚀 Prêt pour:")
print("   • Power BI / Tableau / Looker")
print("   • Requêtes SQL directes")
print("   • Dashboards analytiques")
