import os
import sqlite3
import pandas as pd

# Je définis le chemin pour récuperer mes données de ma base SQLite_data_brut
# Je définis le chemin du script courant qui est : Lumea/etl/extract
current_dir = os.path.dirname(__file__)

# Je remonte à la racine du projet
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))  # /projet

# Je définis le chemin vers ma base SQLite de data brut
sqlite_path = os.path.join(project_root, "db", "SQLite_data_brut.sqlite")

# Permet de gérer la connexion à SQLite
conn = sqlite3.connect(sqlite_path)

# Permet de lire la table Commune et la table Département
query = """
SELECT c.code_insee, c.nom_commune, d.code_department, d.nom_department
FROM Commune c
JOIN Department d ON c.department_id = d.department_id
ORDER BY d.department_id, c.nom_commune
"""

df_SQLite = pd.read_sql_query(query, conn)

# Fermeture de la connexion
conn.close()

# Affichage rapide
print(df_SQLite.head())
print(df_SQLite.info())