import os
import pandas as pd

# Je définis le chemin pour récuperer mes données de mon fichier CSV
# Je définis le chemin du script courant qui est : Lumea/etl/extract
current_dir = os.path.dirname(__file__)

# Je remonte à la racine du projet
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

# Je définis le chemin vers mon fichier CSV de source
input_csv_path = os.path.join(project_root, "db_source", "CSV_source.csv")

# Je lis mon CSV et crée le dataframe
df_CSV = pd.read_csv(
    input_csv_path,
    encoding='utf-8',
    sep=';',
    engine='python',
    on_bad_lines='warn'
)

# J'affiche les 5 premières lignes de mon df_CSV
print("Aperçu des 5 premières lignes :")
print(df_CSV.head())
print("\nColonnes et types :")
print(df_CSV.info())

# Je sélectionne et renomme les colonnes pour l'extraction
df_CSV_copy = df_CSV[[
    'Updated', 
    'SyndicObjectName', 
    'GmapLatitude', 
    'GmapLongitude', 
    'DetailIDENTADRESSEINSEE', 
    'DetailIDENTADRESSECOMMUNE', 
    'DetailIDENTCATEGORIEACTSPORT', 
    'DetailIDENTCATEGORIEACTCULT', 
    'DetailIDENTDESCRIPTIONCOMMERCIALE',
    'point_geo'
]].rename(columns={
    'Updated': 'updated_at',
    'SyndicObjectName': 'nom_site',
    'GmapLatitude': 'latitude',
    'GmapLongitude': 'longitude',
    'DetailIDENTADRESSEINSEE': 'code_insee',
    'DetailIDENTADRESSECOMMUNE': 'nom_commune',
    'DetailIDENTCATEGORIEACTSPORT': 'act_sport',
    'DetailIDENTCATEGORIEACTCULT': 'act_cult',
    'DetailIDENTDESCRIPTIONCOMMERCIALE': 'description'
})

# J'affiche les 5 premières lignes de mon df_CSV
print("Aperçu après sélection et renommage :")
print(df_CSV_copy.head())

# Je sauvegarde le dataframe final en CSV
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(output_dir, exist_ok=True)
csv_path = os.path.join(output_dir, "df_CSV_extract_result.csv")

df_CSV_copy.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\nDataFrame df_CSV_copy sauvegardé en CSV : {csv_path}")

# J'affiche le nombre de lignes et de colonnes
print(f"Nombre de lignes : {df_CSV_copy.shape[0]}")
print(f"Nombre de colonnes : {df_CSV_copy.shape[1]}")