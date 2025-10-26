import sqlite3, os

os.makedirs("./bdd", exist_ok=True)

sqlite_path = "./bdd/bdd_connexion.sqlite"
conn = sqlite3.connect(sqlite_path)
# On crée un curseur sur la connexion qui sert à exécuter des requêtes SQL et à récupérer leurs résultat
cur = conn.cursor()

# Permet d'activer les contraintes de clés étrangères
cur.execute("PRAGMA foreign_keys = ON;")

# Choix pour les tables :
# Table Role : chaque role_id a un nom unique.

# Table Utilisateur : chaque utilisateur peut avoir un seul rôle (cela peut évoluer facilement et être
# modifié pour que chaque utilisateur puisse avoir plusieurs rôles, notamment si l’on passe d’un modèle
# B2C à un modèle hybride B2C/B2B, où les prestataires pourraient également devenir "visiteurs" —
# c’est-à-dire ceux qui recherchent des prestations, par exemple des activités à proposer au sein de
# leurs hébergements) ; chaque username est unique ;
# chaque utilisateur doit avoir un username, un password_hash et un rôle attribués.
# Si, dans la table Role, on supprime un role_id, on ne peut pas le faire tant qu’il existe des utilisateurs
# associés à ce rôle (ON DELETE RESTRICT) ; en revanche, si l’on modifie la valeur de role_id, tous les
# utilisateurs liés seront automatiquement mis à jour avec ce nouveau role_id (ON UPDATE CASCADE).
# RGPD : Les variables deleted_at DATETIME NULL, anonymized BOOLEAN DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP et updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ont été ajoutées pour assurer le respect du RGPD concernant les données des utilisateurs, y compris celles des prestataires. Si nécessaire, le username sera modifié pour être anonymisé.
# RGPD : Si deleted_at est utilisé, le compte de l’utilisateur est marqué comme supprimé, mais la BDD conserve l’utilisateur pour audit.

# Table Department : chaque department_id est associé à un nom unique : 'nom_department TEXT NOT NULL UNIQUE'.

# Table Commune : si, dans la table Commune, on supprime un department_id, on ne peut pas le faire tant
# qu’il existe des communes appartenant à ce département (ON DELETE RESTRICT) ; en revanche, si l’on modifie
# la valeur de department_id, toutes les communes correspondantes seront automatiquement mises à jour
# avec ce nouveau department_id (ON UPDATE CASCADE). Par défaut, une commune n’a pas le label
# (BOOLEAN DEFAULT 0) de "Cité de caractère". Ce choix est justifié par le fait que la majorité des
# communes ne sont pas labellisées.

# Table Site_Touristique : si, dans la table Site_Touristique, on supprime un commune_id, on ne peut pas le faire
# tant qu’il existe des sites appartenant à cette commune (ON DELETE RESTRICT) ; en revanche, si l’on modifie
# la valeur de commune_id, tous les sites correspondants seront automatiquement mis à jour avec ce nouveau
# commune_id (ON UPDATE CASCADE). Par contre, si un prestataire supprime son compte utilisateur, le site
# lié à ce compte reste dans la base, mais le prestataire_id devient NULL. Cela permet qu’un site touristique
# continue d’exister indépendamment de l’existence du compte de son prestataire (ON DELETE SET NULL). En revanche,
# si l’id du prestataire change, le prestataire_id associé au site correspondant est mis à jour
# (ON UPDATE CASCADE).
# RGPD côté prestataires : Les parcours et sites restent accessibles, mais sans révéler l’identité du prestataire, car le prestataire ne révèle pas l’identité réelle de la personne 
# RGPD : De plus, si un prestataire supprime son compte, le site reste dans la BDD mais n’expose pas le prestataire (ON DELETE SET NULL) 
# RGPD : (Si c’est le cas, son username ainsi que le nom_site de son site touristique sont correctement anonymisés).
# RGPD : Les variables deleted_at DATETIME NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, anonymized BOOLEAN DEFAULT 0 ont été ajoutées pour assurer le respect du RGPD concernant les données des prestataires.

# Table Parcours : un utilisateur ne peut pas supprimer son compte tant qu’un parcours qu’il a créé existe,
# car un parcours doit toujours avoir un créateur identifiable (ON DELETE RESTRICT). En revanche, si
# utilisateur_id change, sa valeur est automatiquement mise à jour dans les parcours associés (ON UPDATE CASCADE).

# Table Parcours_Site : (ON DELETE CASCADE pour Parcours et Site_Touristique) : si l’on supprime un parcours,
# cela supprime automatiquement les lignes associées dans Parcours_Site, car ces liaisons n’auraient plus de sens.
# Même logique pour les sites : si un site est supprimé, toutes ses apparitions dans les parcours le sont aussi.
# ON UPDATE CASCADE est également appliqué pour Parcours et Site_Touristique.
# CONSTRAINT uq_parcours_site UNIQUE (parcours_id, site_id) (contrainte d’unicité) : cela empêche d’ajouter
# deux fois le même site dans un même parcours, mais permet au même site d’apparaître dans plusieurs parcours différents.

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
        code_department INTEGER NOT NULL UNIQUE
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

roles = [
    ("admin",),
    ("visiteur",),
    ("prestataire",)
]
cur.executemany("INSERT INTO Role (nom_role) VALUES (?);", roles)

conn.commit()
conn.close()

print(f"Base SQLite créée et roles insérés dans {sqlite_path}.")