import os
import sqlite3
import pandas as pd



# Je définis le chemin pour récuperer mes données du df_aggregated_result
csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "df_aggregated_result.csv"))
if not os.path.exists(csv_path):
    raise FileNotFoundError(f" CSV introuvable : {csv_path}")
print(f" CSV trouvé : {csv_path}")

bdd_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bdd"))
os.makedirs(bdd_dir, exist_ok=True)
sqlite_path = os.path.join(bdd_dir, "bdd_connexion.sqlite")


# Je charge le CSV

df_final = pd.read_csv(csv_path, encoding="utf-8-sig")
print(f" CSV chargé : {len(df_final)} lignes")


# Je gère la connexion à SQLite

conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")
print(f" Connexion SQLite : {sqlite_path}")


# Je crée des tables

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
    department_id INTEGER NOT NULL,
    FOREIGN KEY (department_id) REFERENCES Department(department_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Site_Touristique (
    site_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_site TEXT NOT NULL,
    est_activite BOOLEAN DEFAULT 0,
    est_lieu BOOLEAN DEFAULT 0,
    description TEXT,
    latitude REAL,
    longitude REAL,
    commune_id INTEGER NOT NULL,
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
print(" Tables créées ou vérifiées")


# Permet l'insertion des rôles

roles = [("admin",), ("visiteur",), ("prestataire",)]
cur.executemany("INSERT OR IGNORE INTO Role (nom_role) VALUES (?);", roles)
conn.commit()
print("✓ Rôles insérés")


# Permet l'insertion des départements

# Permet s'assurer que Côtes-d’Armor existe avec le bon nom breton
df_final.loc[len(df_final)] = {
    "nom_department": "Côtes-d'Armor",
    "nom_department_breton": "Aodoù-an-Arvor"
}

df_dept = df_final[["nom_department", "nom_department_breton"]].drop_duplicates()
df_dept = df_dept[df_dept["nom_department"].notna() & (df_dept["nom_department"].str.strip() != "")]

for _, row in df_dept.iterrows():
    cur.execute("""
        INSERT INTO Department (nom_department, nom_department_breton)
        VALUES (?, ?)
        ON CONFLICT(nom_department) DO UPDATE SET nom_department_breton=excluded.nom_department_breton
    """, (row["nom_department"], row["nom_department_breton"]))
conn.commit()

cur.execute("SELECT department_id, nom_department FROM Department;")
dept_map = {nom: did for did, nom in cur.fetchall()}
print(f"✓ {len(df_dept)} départements insérés/mis à jour (Côtes-d’Armor inclus)")

# Permet l'insertion des communes

df_commune = df_final[["nom_commune", "nom_commune_breton", "code_insee", "label_cite_caractere", "nom_department"]].drop_duplicates()
df_commune = df_commune[df_commune["nom_commune"].notna() & (df_commune["nom_commune"].str.strip() != "")]
df_commune["department_id"] = df_commune["nom_department"].map(dept_map)

for _, row in df_commune.iterrows():
    if pd.notna(row["department_id"]):
        cur.execute("""
            INSERT OR IGNORE INTO Commune (nom_commune, nom_commune_breton, code_insee, label_cite_caractere, department_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            row["nom_commune"],
            row["nom_commune_breton"],
            row["code_insee"] if pd.notna(row["code_insee"]) and row["code_insee"] != "" else None,
            bool(row["label_cite_caractere"]),
            row["department_id"]
        ))
conn.commit()
cur.execute("SELECT commune_id, nom_commune FROM Commune;")
commune_map = {nom: cid for cid, nom in cur.fetchall()}
print(f"✓ {len(df_commune)} communes insérées")


# Permet l'insertion des sites touristiques avec created_at et updated_at

df_sites = df_final[["nom_site", "est_activite", "est_lieu", "description", "latitude", "longitude",
                     "nom_commune", "created_at", "updated_at"]].drop_duplicates()
df_sites = df_sites[df_sites["nom_site"].notna() & (df_sites["nom_site"].str.strip() != "")]
df_sites["commune_id"] = df_sites["nom_commune"].map(commune_map)

for _, row in df_sites.iterrows():
    if pd.notna(row["commune_id"]):
        cur.execute("""
            INSERT OR IGNORE INTO Site_Touristique
            (nom_site, est_activite, est_lieu, description, 
            latitude, longitude, commune_id, 
            created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["nom_site"],
            bool(row["est_activite"]),
            bool(row["est_lieu"]),
            row["description"],
            row["latitude"],
            row["longitude"],
            row["commune_id"],
            row["created_at"] if pd.notna(row["created_at"]) else None,
            row["updated_at"] if pd.notna(row["updated_at"]) else None
        ))
conn.commit()
print(f"✓ {len(df_sites)} sites touristiques insérés")


# Permet une vérification finale

print("\n Récapitulatif des lignes dans chaque table :")
for table in ["Role", "Utilisateur", "Department", "Commune", "Site_Touristique", "Parcours", "Parcours_Site"]:
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    print(f"→ {table} : {cur.fetchone()[0]} lignes")

conn.close()
print(f"\n Base SQLite mise à jour : {sqlite_path}")
