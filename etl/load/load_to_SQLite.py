import os
import sqlite3
import pandas as pd
import sys

# On ajoute le dossier extract au path pour importer les données
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "transform")))

# On importe le df_affregated depuis merge
from merge import df_aggregated

#  Définir le chemin de la base ---
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
bdd_dir = os.path.join(base_dir, "bdd")
os.makedirs(bdd_dir, exist_ok=True)
sqlite_path = os.path.join(bdd_dir, "bdd_connexion.sqlite")

conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

# Activation des clés étrangères ---
cur.execute("PRAGMA foreign_keys = ON;")

# Vérification colonnes nécessaires ---
required_cols = [
    "nom_site", "est_activite", "est_lieu", "description", "latitude", "longitude",
    "nom_commune", "nom_commune_breton", "nom_department", "nom_department_breton", "code_insee"
]
for col in required_cols:
    if col not in df_aggregated.columns:
        df_aggregated[col] = ""

# Création des tables ---
cur.execute("""
CREATE TABLE IF NOT EXISTS Department (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_department TEXT UNIQUE NOT NULL,
    nom_department_breton TEXT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Commune (
    commune_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_commune TEXT NOT NULL,
    nom_commune_breton TEXT,
    code_insee TEXT UNIQUE,
    department_id INTEGER,
    FOREIGN KEY(department_id) REFERENCES Department(department_id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Site_Touristique (
    site_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_site TEXT,
    est_activite TEXT,
    est_lieu TEXT,
    description TEXT,
    latitude REAL,
    longitude REAL,
    commune_id INTEGER,
    FOREIGN KEY(commune_id) REFERENCES Commune(commune_id)
);
""")
conn.commit()

# Insertion Departments ---
print("\nInsertion des départements...")
df_dept = df[['nom_department', 'nom_department_breton']].drop_duplicates(subset=['nom_department'])
for _, row in df_dept.iterrows():
    cur.execute("""
        INSERT OR IGNORE INTO Department (nom_department, nom_department_breton)
        VALUES (?, ?)
    """, (row['nom_department'], row['nom_department_breton']))
conn.commit()
print(f"✓ {len(df_dept)} départements insérés ou ignorés si déjà présents.")

# Mapping Department pour Communes ---
cur.execute("SELECT department_id, nom_department FROM Department;")
dept_map = {nom: did for did, nom in cur.fetchall()}

# Insertion Communes ---
print("\nInsertion des communes...")
# garder code_insee vide si manquant, mais nom_commune obligatoire
df_commune = df[['nom_commune', 'nom_commune_breton', 'code_insee', 'nom_department']].drop_duplicates(subset=['nom_commune'])
df_commune['department_id'] = df_commune['nom_department'].map(dept_map)
df_commune.drop(columns=['nom_department'], inplace=True)

for _, row in df_commune.iterrows():
    cur.execute("""
        INSERT OR IGNORE INTO Commune (nom_commune, nom_commune_breton, code_insee, department_id)
        VALUES (?, ?, ?, ?)
    """, (row['nom_commune'], row['nom_commune_breton'], row['code_insee'] if row['code_insee'] != "" else None, row['department_id']))
conn.commit()
print(f"✓ {len(df_commune)} communes insérées ou ignorées si déjà présentes.")

# Mapping Commune pour Sites ---
cur.execute("SELECT commune_id, nom_commune FROM Commune;")
commune_map = {nom: cid for cid, nom in cur.fetchall()}

# Insertion Sites touristiques ---
print("\nInsertion des sites touristiques...")
df_sites = df[['nom_site', 'est_activite', 'est_lieu', 'description', 'latitude', 'longitude', 'nom_commune']].drop_duplicates().copy()
df_sites['commune_id'] = df_sites['nom_commune'].map(commune_map)
df_sites.drop(columns=['nom_commune'], inplace=True)

for _, row in df_sites.iterrows():
    cur.execute("""
        INSERT OR IGNORE INTO Site_Touristique
        (nom_site, est_activite, est_lieu, description, latitude, longitude, commune_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (row['nom_site'], row['est_activite'], row['est_lieu'], row['description'],
          row['latitude'], row['longitude'], row['commune_id']))
conn.commit()
print(f"✓ {len(df_sites)} sites touristiques insérés ou ignorés si déjà présents.")

# Vérification finale ---
for table in ["Department", "Commune", "Site_Touristique"]:
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    count = cur.fetchone()[0]
    print(f"→ {table}: {count} lignes")

conn.close()
print(f"\n🎯 Base SQLite finalisée : {sqlite_path}")
