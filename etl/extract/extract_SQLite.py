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

# Permet de fermer la connexion
conn.close()

# Permet une affichage rapide
print(df_SQLite.head())
print(df_SQLite.info())

# On créer un df_SQLite_copy pour éviter les modifications du df original pour transform
df_SQLite_copy = df_SQLite.copy(deep=True)

# On sauvegarde le résultat en CSV
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(output_dir, exist_ok=True)
csv_path = os.path.join(output_dir, "df_SQLite_extract_result.csv")

df_SQLite_copy.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\n DataFrame df_SQLite_copy sauvegardé en CSV : {csv_path}")