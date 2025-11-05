import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

# Je définis le chemin du script courant qui est : Lumea/etl/transform
base_dir = os.path.dirname(__file__)

# Je définis le chemin pour récuperer mon CSV du dataframe CSV à la sortie de l'extraction 
input_dir = os.path.join(base_dir, "..", "data")
input_csv = os.path.join(input_dir, "df_CSV_extract_result.csv")

# Je définis le chemin pour créer le CSV à la fin de phase de transformation 
output_dir = os.path.join(base_dir, "..", "data")
os.makedirs(output_dir, exist_ok=True)
output_csv = os.path.join(output_dir, "df_CSV_transform_result.csv")

# J'importe le dataframe depuis extract_CSV
sys.path.append(os.path.abspath(os.path.join(base_dir, "..", "extract")))
from extract_CSV import df_CSV_copy

# Je crée ma fonction de la transformation pour df_CSV
def transform_data_CSV(df, df_name="df_CSV_copy"):
    df_copy = df.copy(deep=True)

    # Conversion de code_insee en chaîne de caractères et remplissage des valeurs manquantes de nom_commune
    df_copy['code_insee'] = df_copy['code_insee'].astype(str)
    df_copy['nom_commune'] = df_copy['nom_commune'].fillna('Inconnu')

    print("="*80)
    print(f"Transformation : {df_name}")
    print("="*80)

    # Détection des valeurs manquantes
    na_counts = df_copy.isna().sum()
    print("\nValeurs manquantes détectées avant traitement :")
    print(na_counts[na_counts > 0])

    # Pour notre ETL automatisé l’affichage en pause
    # plt.figure(figsize=(10,4))
    # sns.heatmap(df_copy.isna(), cbar=False, cmap="viridis", yticklabels=False)
    # plt.title(f"Heatmap des valeurs manquantes ({df_name})")
    # plt.tight_layout()
    # plt.show(block=False)
    # plt.pause(0.1)
    # plt.close()

    # Remplissage de latitude et de longitude depuis point_geo
    def fill_lat_lon(row):
        if pd.isna(row['latitude']) or pd.isna(row['longitude']) or row['latitude']==0.0 or row['longitude']==0.0:
            point = row.get('point_geo', '')
            if pd.notna(point) and ',' in point:
                lat_str, lon_str = point.split(',')
                try:
                    row['latitude'] = float(lat_str.strip())
                    row['longitude'] = float(lon_str.strip())
                except:
                    pass
        return row

    df_copy = df_copy.apply(fill_lat_lon, axis=1)

    # Suppression des lignes encore manquantes
    df_copy = df_copy.dropna(subset=['latitude', 'longitude'])

    # Détection et suppression des doublons
    dupl = df_copy.duplicated().sum()
    if dupl > 0:
        df_copy = df_copy.drop_duplicates()
        print(f"\n✓ {dupl} doublons supprimés")
    else:
        print("\n✓ Aucun doublon détecté")

    # Création de la colonne est_activite
    df_copy['est_activite'] = True

    # Anonymisation
    # Calculation des masques
    orig_nom = df_copy['nom_site'].astype(str).fillna('')
    orig_desc = df_copy['description'].astype(str).fillna('')

    mask_nom = orig_nom.apply(lambda x: bool(re.search(r"[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+", x)))
    mask_desc = orig_desc.apply(lambda x: bool(re.search(r"[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+", x)))

    # Initialisation de la colonne anonymized à partir de 0
    df_copy['anonymized'] = 0

    # Application de l'anonymisation pour nom_site et description
    def anonymize_nom_site_row(row):
        nom_site = row.get('nom_site','')
        site_id = row.name
        if re.search(r"[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+", str(nom_site)):
            return f"Activité touristique #{site_id+1}"
        return nom_site

    def anonymize_description_text(text):
        if pd.isna(text) or str(text).strip() == "":
            return "Description non renseignée"
        if re.search(r"[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+", str(text)):
            return "Description disponible sur demande"
        return text

    df_copy['nom_site'] = df_copy.apply(anonymize_nom_site_row, axis=1)
    df_copy['description'] = df_copy['description'].apply(anonymize_description_text)

    # Anonymized = 1 pour toutes les lignes détectées
    df_copy.loc[mask_nom | mask_desc, 'anonymized'] = 1

    print(f"[{df_name}] Anonymisation effectuée sur {int(df_copy['anonymized'].sum())} lignes.")

    # Suppression des colonnes inutiles
    df_copy = df_copy.drop(columns=['act_sport', 'act_cult', 'point_geo'])

    # Ajout created_at et normalisation des types
    df_copy['created_at'] = df_copy['updated_at']
    df_copy['created_at'] = pd.to_datetime(df_copy['created_at'], errors='coerce')
    df_copy['updated_at'] = pd.to_datetime(df_copy['updated_at'], errors='coerce')
    df_copy['latitude'] = df_copy['latitude'].astype(float)
    df_copy['longitude'] = df_copy['longitude'].astype(float)
    for col in ['description', 'nom_commune', 'nom_site', 'code_insee']:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].astype(str)

    print("\n✓ Normalisation des types terminée")

    # Remplissage des dates manquantes
    today = pd.Timestamp.now().normalize()
    df_copy['updated_at'] = df_copy['updated_at'].fillna(today)
    df_copy['created_at'] = df_copy['created_at'].fillna(today)

    # Vérification finale des valeurs manquantes
    final_na = df_copy.isna().sum()
    print("\nVérification finale des valeurs manquantes :")
    print(final_na[final_na > 0] if final_na.sum() > 0 else "Aucune valeur manquante restante.")

    print("\n" + "="*80)
    print(f"Préparation terminée pour : {df_name}")
    print("="*80)
    print(f"\nDimensions finales : {df_copy.shape[0]} lignes × {df_copy.shape[1]} colonnes")
    print(f"Colonnes : {df_copy.columns.tolist()}")
    print(df_copy.dtypes)
    print(f"\nValeurs manquantes totales : {df_copy.isna().sum().sum()}")
    print(f"Doublons : {df_copy.duplicated().sum()}")
    print("\n" + "="*80 + "\n")

    return df_copy

# Exécution de la transformation et sauvegarde
if __name__ == "__main__":
    print("\nDémarrage de la transformation pour df_CSV\n") 

    df_result_CSV = transform_data_CSV(df_CSV_copy, df_name="df_CSV_copy")

    # Aperçu final
    print(df_result_CSV.head())
    print(df_result_CSV.info())

    # Sauvegarde en CSV
    df_result_CSV.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\nDataFrame df_result_CSV sauvegardé en CSV : {output_csv}")
