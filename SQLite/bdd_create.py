import sqlite3, os

os.makedirs("./bdd", exist_ok=True)

sqlite_path = "./bdd/bdd_connexion.sqlite"
conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

# Activer les contraintes de clés étrangères
cur.execute("PRAGMA foreign_keys = ON;")

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
        FOREIGN KEY (role_id) REFERENCES Role(role_id)
            ON DELETE RESTRICT
            ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Department (
        department_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_department TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Commune (
        commune_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_commune TEXT NOT NULL,
        nom_commune_breton TEXT,
        code_insee TEXT UNIQUE NOT NULL,
        label_cite_caractere BOOLEAN DEFAULT 0,
        department_id INTEGER NOT NULL,
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
        commune_id INTEGER NOT NULL,
        prestataire_id INTEGER,
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
        date_creation DATE DEFAULT CURRENT_DATE,
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

roles = [
    ("admin",),
    ("visiteur",),
    ("prestataire",)
]
cur.executemany("INSERT INTO Role (nom_role) VALUES (?);", roles)

conn.commit()
conn.close()

print(f"Base SQLite créée et roles insérés dans {sqlite_path}.")