import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

# On ajoute le dossier extract au path pour importer les données
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "extract")))

# On importe df_CSV_copy depuis mon extract
from extract_CSV import df_CSV_copy

# On crée une fonction principale EDA pour df_CSV
def EDA_data_CSV(df, df_name="df_CSV_copy"):
    """
    Analyse Exploratoire des Données (EDA) pour df_CSV
    Étapes :
    1. Sélection et renommage des colonnes utiles
    2. Exploration initiale
    3. Détection des valeurs manquantes
    4. Remplissage latitude/longitude depuis point_geo
    5. Suppression des lignes encore manquantes
    6. Détection et suppression des doublons
    7. Création d'une colonne est_activite
    8. Anonymisation du nom_site et de la description
    9. Suppression des colonnes inutiles
    10. Ajout de created_at
    11. Normalisation des types
    12. Vérification finale des valeurs manquantes
    13. Remplissage des dates manquantes
    14. Vérification finale des valeurs manquantes
    """
    
    # On travaille sur une deuxième copie pour ne pas modifier l'original
    df_copy = df.copy(deep=True)

    # On effectue une étape 1 : Sélection et renommage des colonnes utiles
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

    # On convertit et remplit certains champs
    df_copy['code_insee'] = df_copy['code_insee'].astype(str)
    df_copy['nom_commune'] = df_copy['nom_commune'].fillna('Inconnu')

    # On effectue une étape 2 : Exploration initiale
    print("="*80)
    print(f"EDA & PRÉPARATION : {df_name}")
    print("="*80)

    # On effectue une étape 3 : Détection des valeurs manquantes
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

    # On effectue une étape 4 : Remplissage latitude/longitude depuis point_geo
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

    # On effectue une étape 5 : Suppression des lignes encore manquantes
    df_copy = df_copy.dropna(subset=['latitude', 'longitude'])

    # On effectue une étape 6 : Détection et suppression des doublons
    dupl = df_copy.duplicated().sum()
    if dupl > 0:
        df_copy = df_copy.drop_duplicates()
        print(f"\n✓ {dupl} doublons supprimés")
    else:
        print("\n✓ Aucun doublon détecté")

    # On effectue une étape 7 : Création d'une colonne est_activite = 1 pour toutes les lignes
    df_copy['est_activite'] = 1
    df_copy['est_activite'] = df_copy['est_activite'].astype(bool)

    # Vérification
    print(df_copy['est_activite'].head(10))

    # On effectue une étape 8 : Anonymisation du nom_site et de la description
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


    print(df_copy['nom_site'])
    print(df_copy['description'])

    # On effectue une étape 9 : Suppression des colonnes inutiles
    df_copy = df_copy.drop(columns=['act_sport', 'act_cult', 'point_geo'])

    # On effectue une étape 10 : Ajout de created_at
    df_copy['created_at'] = df_copy['updated_at']

    # On effectue une étape 11 : Normalisation des types
    df_copy['created_at'] = pd.to_datetime(df_copy['created_at'], errors='coerce')
    df_copy['updated_at'] = pd.to_datetime(df_copy['updated_at'], errors='coerce')
    df_copy['latitude'] = df_copy['latitude'].astype(float)
    df_copy['longitude'] = df_copy['longitude'].astype(float)
    text_cols = ['description', 'nom_commune', 'nom_site', 'code_insee']
    for col in text_cols:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].astype(str)

    print("\n✓ Normalisation des types terminée")

    # On effectue une étape 12 :  Vérification finale des valeurs manquantes
    print("\n--- Vérification finale des valeurs manquantes ---")
    final_na = df_copy.isna().sum()
    print(final_na[final_na > 0] if final_na.sum() > 0 else "Aucune valeur manquante restante.")

    # On effectue une étape 13 : Remplissage des dates manquantes
    print("\n--- Remplissage des dates manquantes ---")
    today = pd.Timestamp.now().normalize()  # date du jour à minuit
    missing_updated = df_copy['updated_at'].isna().sum()
    missing_created = df_copy['created_at'].isna().sum()

    if missing_updated > 0 or missing_created > 0:
        df_copy['updated_at'] = df_copy['updated_at'].fillna(today)
        df_copy['created_at'] = df_copy['created_at'].fillna(today)
        print(f"→ {missing_updated} valeurs manquantes remplies dans 'updated_at'")
        print(f"→ {missing_created} valeurs manquantes remplies dans 'created_at'")
    else:
        print("✓ Aucune valeur manquante à remplir dans les colonnes de date")

    # On effectue une étape 14 : Vérification finale des valeurs manquantes
    print("\n Vérification finale des valeurs manquantes :")
    final_na = df_copy.isna().sum()
    if final_na.sum() > 0:
        print(final_na[final_na > 0].to_string())
    else:
        print("Aucune valeur manquante restante")

    # On effectue une étape finale : Résumé final
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

# On exécute l'EDA pour df_CSV
df_result_CSV = EDA_data_CSV(df_CSV_copy, df_name="df_CSV_copy")

if __name__ == "__main__":
    print("\nDémarrage de l'EDA pour df_CSV\n") 

    # Aperçu final
    print("\nAperçu final après EDA :")
    print(df_result_CSV.head())
    print(df_result_CSV.info())
    print(len(df_CSV_copy))