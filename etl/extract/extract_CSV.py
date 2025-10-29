import os
import pandas as pd

# Je définis le chemin pour récuperer mes données du CSV
# Je définis le chemin du script courant qui est : Lumea/etl/extract
current_dir = os.path.dirname(__file__)

# Je remonte à la racine du projet
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))  # /projet

# Je définis mon chemin pour récuperer mes données du CSV
input_csv_path = os.path.join(project_root, "db_source", "CSV_source.csv")

# Permet de lire le CSV et le transformer et df_CSV
df_CSV = pd.read_csv(
    input_csv_path,
    encoding='utf-8',
    sep=';',
    # Permet de tolérer les retours à la ligne
    engine='python',
    # Permet d'avertir par rapport aux lignes mal formées
    on_bad_lines='warn'
)

# Permet d'afficher les premières lignes de mon df_CSV
print("Aperçu des 5 premières lignes :")
print(df_CSV.head())

# Permet de voir les noms de colonnes et types de données en mon df_CSV
print("\nColonnes et types :")
print(df_CSV.info())

# On créer un df_CSV_copy pour éviter les modifications du df original pour transform
df_CSV_copy = df_CSV.copy(deep=True)