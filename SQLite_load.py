import os
import sqlite3
import csv

# Je définis mes chemins
sqlite_path = os.path.join(os.path.dirname(__file__), "./db/SQLite_data_brut.sqlite")
csv_path = os.path.join(os.path.dirname(__file__), "./db/SQLite_data_source.csv")

# Je vérifie que le dossier existe
os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)

# Je gère ma connexion à SQLite
conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

# Je crée mes tables
cur.executescript("""
DROP TABLE IF EXISTS Commune;
DROP TABLE IF EXISTS Department;

CREATE TABLE IF NOT EXISTS Department (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_department TEXT NOT NULL UNIQUE,
    nom_department TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Commune (
    commune_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_insee TEXT UNIQUE NOT NULL,
    nom_commune TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    FOREIGN KEY (department_id) REFERENCES Department(department_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
""")

# Je lis le CSV et j'insère des données dans les tables
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    print("Colonnes détectées :", reader.fieldnames)
    for row in reader:
        # Dans la table Department
        cur.execute("""
            INSERT OR IGNORE INTO Department (code_department, nom_department)
            VALUES (?, ?)
        """, (row['Code Officiel Département'].strip(), row['Nom Officiel Département'].strip()))
        
        # Je récupère l'id du département
        cur.execute("SELECT department_id FROM Department WHERE code_department = ?", 
                    (row['Code Officiel Département'].strip(),))
        department_id = cur.fetchone()[0]
        
        # Dans la table Commune
        cur.execute("""
            INSERT OR IGNORE INTO Commune (code_insee, nom_commune, department_id)
            VALUES (?, ?, ?)
        """, (row['Code Officiel Commune'].strip(), row['Nom Officiel Commune'].strip(), department_id))

# Je valide et je ferme ma connexion à SQLite
conn.commit()
conn.close()

print(f"Base SQLite avec les données des communes et des départments crée et remplie dans {sqlite_path}.")