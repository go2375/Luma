import os
import sqlite3
import pandas as pd

def load_to_sqlite(csv_path=None):
    if isinstance(csv_path, pd.DataFrame):
        temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        os.makedirs(temp_dir, exist_ok=True)
        csv_path_str = os.path.join(temp_dir, "df_aggregated_result.csv")
        csv_path.to_csv(csv_path_str, index=False, encoding='utf-8-sig')
        csv_path = csv_path_str

    # Je définis le chemin pour récupérer mes données du df_aggregated_result
    if csv_path is None:
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "df_aggregated_result.csv"))

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f" CSV introuvable : {csv_path}")
    print(f" CSV trouvé : {csv_path}")

    # Je m'assure que le dossier existe avant ma connexion à SQLite
    bdd_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bdd"))
    os.makedirs(bdd_dir, exist_ok=True)
    sqlite_path = os.path.join(bdd_dir, "bdd_connexion.sqlite")

    # Je lis le CSV
    df_final = pd.read_csv(csv_path, encoding="utf-8-sig")
    print(f" CSV chargé : {len(df_final)} lignes")

    # J'effectue une correction minimale des booléens
    for col in ['est_activite', 'est_lieu']:
        if col not in df_final.columns:
            df_final[col] = False
        else:
            df_final[col] = df_final[col].astype(str).str.strip().str.lower().map(
                {
                    'true': True, '1': True, 'vrai': True, 'yes': True,
                    'false': False, '0': False, 'faux': False, 'non': False, '': False, None: False
                }
            ).fillna(False).astype(bool)

    # Je m'assure de la présence et la propreté des colonnes bretonnes
    for col in ["nom_commune_breton", "nom_department_breton"]:
        if col not in df_final.columns:
            df_final[col] = ""
        else:
            df_final[col] = df_final[col].astype(str).str.strip()

    # Je gére ma connexion à SQLite
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    print(f" Connexion SQLite : {sqlite_path}")

    # Je valide anonymized
    if 'anonymized' not in df_final.columns:
        df_final['anonymized'] = 0
    else:
        df_final['anonymized'] = df_final['anonymized'].astype(int)

    # Voici je crée mes tables
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
    print(" Tables créées et vérifiées")

    # Insertion des rôles
    roles = [("admin",), ("visiteur",), ("prestataire",)]
    cur.executemany("INSERT OR IGNORE INTO Role (nom_role) VALUES (?);", roles)
    conn.commit()
    print("✓ Rôles insérés")

    # J'insère les départements
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
    print(f"✓ {len(df_dept)} départements insérés/mis à jour (Côtes-d'Armor inclus)")

    # J'insère les communes
    df_commune = df_final[["nom_commune", "nom_commune_breton", "code_insee", "label_cite_caractere", "nom_department"]].drop_duplicates()
    df_commune = df_commune[df_commune["nom_commune"].notna() & (df_commune["nom_commune"].str.strip() != "")]
    df_commune["department_id"] = df_commune["nom_department"].map(dept_map)

    for _, row in df_commune.iterrows():
        if pd.notna(row["department_id"]):
            label_cite = bool(row["label_cite_caractere"]) if pd.notna(row["label_cite_caractere"]) else False
            cur.execute("""
                INSERT OR IGNORE INTO Commune (nom_commune, nom_commune_breton, code_insee, label_cite_caractere, department_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                row["nom_commune"],
                row["nom_commune_breton"],
                row["code_insee"] if pd.notna(row["code_insee"]) and row["code_insee"] != "" else None,
                label_cite,
                row["department_id"]
            ))
    conn.commit()
    cur.execute("SELECT commune_id, nom_commune FROM Commune;")
    commune_map = {nom: cid for cid, nom in cur.fetchall()}
    print(f"✓ {len(df_commune)} communes insérées")

    # Je nettoie les noms de communes avant mapping (pour éviter problèmes de correspondance)
    df_sites = df_final[["nom_site", "est_activite", "est_lieu", "description", "latitude", "longitude", "nom_commune", "created_at", "updated_at", "anonymized"]].drop_duplicates()
    df_sites["nom_commune"] = df_sites["nom_commune"].astype(str).str.strip()
    df_final["nom_commune"] = df_final["nom_commune"].astype(str).str.strip()

    # J'affiche les communes sans commune_id
    df_sites["commune_id"] = df_sites["nom_commune"].map(commune_map)
    missing_communes = df_sites[df_sites["commune_id"].isna()]["nom_commune"].unique()
    if len(missing_communes) > 0:
        print("Communes sans id dans la base :", missing_communes)

    # J'insère les sites touristiques
    df_sites = df_sites[df_sites["nom_site"].notna() & (df_sites["nom_site"].str.strip() != "")]
    for _, row in df_sites.iterrows():
        if pd.notna(row["commune_id"]):
            cur.execute("""
                INSERT OR IGNORE INTO Site_Touristique
                (nom_site, est_activite, est_lieu, description, latitude, longitude, commune_id, created_at, updated_at, anonymized)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["nom_site"],
                bool(row["est_activite"]),
                bool(row["est_lieu"]),
                row["description"],
                row["latitude"],
                row["longitude"],
                row["commune_id"],
                row["created_at"] if pd.notna(row["created_at"]) else None,
                row["updated_at"] if pd.notna(row["updated_at"]) else None,
                bool(row["anonymized"])
            ))
    conn.commit()
    print(f"✓ {len(df_sites)} sites touristiques insérés")

    # J'effectue ma vérification finale
    print("\n Récapitulatif des lignes dans chaque table :")
    for table in ["Role", "Utilisateur", "Department", "Commune", "Site_Touristique", "Parcours", "Parcours_Site"]:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        print(f"→ {table} : {cur.fetchone()[0]} lignes")

    conn.close()
    print(f"\n Base SQLite mise à jour : {sqlite_path}")

if __name__ == "__main__":
    load_to_sqlite()
