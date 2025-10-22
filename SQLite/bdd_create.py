import sqlite3, os

os.makedirs("./bdd", exist_ok=True)

sqlite_path = "./bdd/bdd_connexion.sqlite"
conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

cur.executescript("""
    CREATE TABLE Role(
        role_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_role TEXT UNIQUE NOT NULL
    );
    
    CREATE TABLE Utilisateur(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role_id INTEGER NOT NULL,
        FOREIGN KEY (role_id) REFERENCES Role(role_id)
    );

    CREATE TABLE Department (
        department_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_department TEXT NOT NULL
    );

    CREATE TABLE Commune (
        commune_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_commune TEXT NOT NULL,
        nom_commune_breton TEXT NOT NULL,
        code_insee TEXT UNIQUE,
        label_cite_caractere BOOL,
        department_id INTEGER NOT NULL,
        FOREIGN KEY (department_id) REFERENCES Department(department_id)
    );

    CREATE TABLE Site_Touristique (
        site_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_site TEXT NOT NULL,
        type_site TEXT,
        description TEXT,
        latitude REAL,
        longitude REAL,
        commune_id INTEGER NOT NULL,
        prestataire_id INTEGER,
        FOREIGN KEY (commune_id) REFERENCES Commune(commune_id),
        FOREIGN KEY (prestataire_id) REFERENCES Utilisateur(user_id)
    );


    CREATE TABLE Parcours (
        parcours_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_parcours TEXT NOT NULL,
        createur_id INTEGER NOT NULL,
        date_creation DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (createur_id) REFERENCES Utilisateur(user_id)
    );

    CREATE TABLE Parcours_Site (
        parcours_site_id INTEGER PRIMARY KEY AUTOINCREMENT,
        parcours_id INTEGER NOT NULL,
        site_id INTEGER NOT NULL,
        ordre_visite INTEGER,
        FOREIGN KEY (parcours_id) REFERENCES Parcours(parcours_id),
        FOREIGN KEY (site_id) REFERENCES Site_Touristique(site_id),
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