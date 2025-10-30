import os
import sqlite3
import pandas as pd
import sys

# --- 1️⃣ Ajouter le dossier transform au path ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "transform")))

# --- 2️⃣ Importer le DataFrame agrégé ---
from merge import df_aggregated

# --- 3️⃣ Connexion SQLite ---
os.makedirs("./bdd", exist_ok=True)
sqlite_path = "./bdd/bdd_connexion.sqlite"
conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

# --- 4️⃣ Activation des clés étrangères ---
cur.execute("PRAGMA foreign_keys = ON;")

# --- 5️⃣ Création de toutes les tables ---
cur.executescript("""
CREATE TABLE IF NOT EXISTS Role(
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_role TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS Utilisateur(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    deleted_at TIMESTAMP NULL,
    anonymized BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES Role(role_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Department (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_department TEXT NOT NULL UNIQUE,
    nom_department_breton TEXT
);

CREATE TABLE IF NOT EXISTS Commune (
    commune_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_commune TEXT NOT NULL,
    nom_commune_breton TEXT,
    code_insee TEXT UNIQUE,
    label_cite_caractere BOOLEAN DEFAULT 0,
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES Department(department_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Site_Touristique (
    site_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_site TEXT NOT NULL,
    type_site TEXT,
    description TEXT,
    latitude REAL,
    longitude REAL,
    commune_id INTEGER,
    prestataire_id INTEGER,
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    anonymized BOOLEAN DEFAULT 0,
    FOREIGN KEY (commune_id) REFERENCES Commune(commune_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (prestataire_id) REFERENCES Utilisateur(user_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Parcours (
    parcours_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_parcours TEXT NOT NULL,
    createur_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (createur_id) REFERENCES Utilisateur(user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Parcours_Site (
    parcours_site_id INTEGER PRIMARY KEY AUTOINCREMENT,
    parcours_id INTEGER NOT NULL,
    site_id INTEGER NOT NULL,
    ordre_visite INTEGER,
    FOREIGN KEY (parcours_id) REFERENCES Parcours(parcours_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (site_id) REFERENCES Site_Touristique(site_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT uq_parcours_site UNIQUE (parcours_id, site_id)
);
""")

conn.commit()

# --- 6️⃣ Insertion des rôles de base ---
roles = [("admin",), ("visiteur",), ("prestataire",)]
cur.executemany("INSERT OR IGNORE INTO Role (nom_role) VALUES (?);", roles)
conn.commit()

print("✓ Base SQLite initialisée avec les tables et rôles.")

# --- 7️⃣ Vérification colonnes présentes ---
required_cols = [
    "nom_site", "type_site", "description", "latitude", "longitude",
    "nom_commune", "nom_commune_breton", "nom_department",
    "nom_department_breton", "code_insee"
]

missing = [c for c in required_cols if c not in df_aggregated.columns]
if missing:
    print(f"⚠️ Colonnes manquantes dans df_aggregated : {missing}")
    for col in missing:
        df_aggregated[col] = ""

df = df_aggregated[required_cols].fillna("")

# --- 8️⃣ Insertion Department ---
print("\nInsertion des départements...")
df_dept = df[['nom_department', 'nom_department_breton']].drop_duplicates(subset=['nom_department'])
df_dept.to_sql('Department', conn, if_exists='append', index=False)
print(f"✓ {len(df_dept)} départements insérés.")

# --- 9️⃣ Insertion Commune ---
print("\nInsertion des communes...")
df_commune = df_aggregated[['nom_commune','nom_commune_breton','code_insee','label_cite_caractere','department_id']].drop_duplicates(subset=['code_insee'])
cur.execute("SELECT department_id, nom_department FROM Department;")
dept_map = {nom: did for did, nom in cur.fetchall()}

df_commune = df[['nom_commune', 'nom_commune_breton', 'code_insee', 'nom_department']].drop_duplicates()
df_commune['department_id'] = df_commune['nom_department'].map(dept_map)
df_commune = df_commune.drop(columns=['nom_department'])

df_commune.to_sql('Commune', conn, if_exists='append', index=False)
print(f"✓ {len(df_commune)} communes insérées.")

# --- 🔟 Insertion Site_Touristique ---
print("\nInsertion des sites touristiques...")
cur.execute("SELECT commune_id, nom_commune FROM Commune;")
commune_map = {nom: cid for cid, nom in cur.fetchall()}

df_sites = df[['nom_site', 'type_site', 'description', 'latitude', 'longitude', 'nom_commune']].drop_duplicates()
df_sites['commune_id'] = df_sites['nom_commune'].map(commune_map)
df_sites = df_sites.drop(columns=['nom_commune'])

df_sites.to_sql('Site_Touristique', conn, if_exists='append', index=False)
print(f"✓ {len(df_sites)} sites touristiques insérés.")

# --- ✅ Vérification finale ---
for table in ["Department", "Commune", "Site_Touristique"]:
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    count = cur.fetchone()[0]
    print(f"→ {table}: {count} lignes")

conn.commit()
conn.close()
print(f"\n🎯 Base SQLite finalisée : {sqlite_path}")
