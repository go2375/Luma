import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re


# Chemins d'entrée et de sortie

base_dir = os.path.dirname(__file__)

# Chemin du CSV d'entrée
input_dir = os.path.join(base_dir, "..", "data")
input_csv = os.path.join(input_dir, "df_CSV_extract_result.csv")

# Chemin du CSV de sortie
output_dir = os.path.join(base_dir, "..", "data")
os.makedirs(output_dir, exist_ok=True)
output_csv = os.path.join(output_dir, "df_CSV_transform_result.csv")


# Import du DataFrame depuis extract_CSV

sys.path.append(os.path.abspath(os.path.join(base_dir, "..", "extract")))
from extract_CSV import df_CSV_copy


# Fonction EDA pour df_CSV

def EDA_data_CSV(df, df_name="df_CSV_copy"):
    df_copy = df.copy(deep=True)

    # 1. Sélection et renommage des colonnes utiles
    df_copy = df_copy[[
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

    # Type code_insee et nom_commune
    df_copy['code_insee'] = df_copy['code_insee'].astype(str)
    df_copy['nom_commune'] = df_copy['nom_commune'].fillna('Inconnu')

    print("="*80)
    print(f"EDA & PRÉPARATION : {df_name}")
    print("="*80)

    # 2. Valeurs manquantes
    na_counts = df_copy.isna().sum()
    print("\nValeurs manquantes détectées avant traitement :")
    print(na_counts[na_counts > 0])

    plt.figure(figsize=(10,4))
    sns.heatmap(df_copy.isna(), cbar=False, cmap="viridis", yticklabels=False)
    plt.title(f"Heatmap des valeurs manquantes ({df_name})")
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)
    plt.close()

    # 3. Remplissage latitude/longitude depuis point_geo
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

    # 4. Suppression des lignes encore manquantes
    df_copy = df_copy.dropna(subset=['latitude', 'longitude'])

    # 5. Détection et suppression des doublons
    dupl = df_copy.duplicated().sum()
    if dupl > 0:
        df_copy = df_copy.drop_duplicates()
        print(f"\n✓ {dupl} doublons supprimés")
    else:
        print("\n✓ Aucun doublon détecté")

    # 6. Création de la colonne est_activite
    df_copy['est_activite'] = True

    # 7. Anonymisation du nom_site et description
    def anonymize_nom_site(row):
        nom_site = row.get('nom_site','')
        site_id = row.name
        if re.search(r"[A-Z][a-z]+\s+[A-Z][a-z]+", nom_site):
            return f"Activité touristique #{site_id+1}"
        return nom_site

    def anonymize_description(desc):
        if pd.isna(desc) or desc.strip()=="":
            return "Description non renseignée"
        if re.search(r"[A-Z][a-z]+\s+[A-Z][a-z]+", desc):
            return "Description disponible sur demande"
        return desc

    df_copy['nom_site'] = df_copy.apply(anonymize_nom_site, axis=1)
    df_copy['description'] = df_copy['description'].apply(anonymize_description)

    # 8. Suppression colonnes inutiles
    df_copy = df_copy.drop(columns=['act_sport', 'act_cult', 'point_geo'])

    # 9. Ajout created_at et normalisation types
    df_copy['created_at'] = df_copy['updated_at']
    df_copy['created_at'] = pd.to_datetime(df_copy['created_at'], errors='coerce')
    df_copy['updated_at'] = pd.to_datetime(df_copy['updated_at'], errors='coerce')
    df_copy['latitude'] = df_copy['latitude'].astype(float)
    df_copy['longitude'] = df_copy['longitude'].astype(float)
    for col in ['description', 'nom_commune', 'nom_site', 'code_insee']:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].astype(str)

    print("\n✓ Normalisation des types terminée")

    # 10. Remplissage des dates manquantes
    today = pd.Timestamp.now().normalize()
    df_copy['updated_at'] = df_copy['updated_at'].fillna(today)
    df_copy['created_at'] = df_copy['created_at'].fillna(today)

    # 11. Vérification finale des valeurs manquantes
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


# Exécution de l'EDA et sauvegarde

if __name__ == "__main__":
    print("\nDémarrage de l'EDA pour df_CSV\n") 

    df_result_CSV = EDA_data_CSV(df_CSV_copy, df_name="df_CSV_copy")

    # Aperçu final
    print(df_result_CSV.head())
    print(df_result_CSV.info())

    # Sauvegarde CSV
    df_result_CSV.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\nDataFrame df_result_CSV sauvegardé en CSV : {output_csv}")
