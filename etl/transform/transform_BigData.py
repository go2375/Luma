import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

# Je définis le chemin du script courant qui est : Lumea/etl/transform
base_dir = os.path.dirname(__file__)

# Je définis le chemin pour récuperer mon CSV du dataframe API à la sortie de l'extraction 
input_dir = os.path.join(base_dir, "..", "data")
input_csv = os.path.join(input_dir, "df_BigData_extract_result.csv")

# Je définis le chemin pour créer le CSV à la fin de phase de transformation 
output_dir = os.path.join(base_dir, "..", "data")
os.makedirs(output_dir, exist_ok=True)
output_csv = os.path.join(output_dir, "df_BigData_transform_result.csv")

# J'importe le dataframe depuis extract_BigData
sys.path.append(os.path.abspath(os.path.join(base_dir, "..", "extract")))
from extract_BigData import df_BigData_copy

# Je crée ma fonction de la transformation pour df_BigData
def transform_data_BigData(df, df_name="df_BigData_copy"):
    df_copy = df.copy(deep=True)

    # Suppression de la colonne _id
    if '_id' in df_copy.columns:
        df_copy = df_copy.drop(columns=['_id'])

    # Séparation de code_postal_et_nom_commune
    if 'code_postal_et_nom_commune' in df_copy.columns:
        df_copy[['code_insee', 'nom_commune']] = df_copy['code_postal_et_nom_commune'].str.split('#', expand=True)
        df_copy = df_copy.drop(columns=['code_postal_et_nom_commune'])

    # Extraction et normalisation de type_site
    def extract_type_site(urls):
        if pd.isna(urls) or urls.strip() == '':
            return "Autre"
        categories = [u.split('#')[-1].strip() for u in urls.split('|')]
        return "; ".join(categories)
    df_copy['type_site'] = df_copy['type_site'].apply(extract_type_site)

    # Gestion des dates
    df_copy['updated_at'] = pd.to_datetime(df_copy['updated_at'], errors='coerce')
    today = pd.Timestamp.now().normalize()
    df_copy['created_at'] = df_copy['updated_at'].fillna(today)
    df_copy['updated_at'] = df_copy['updated_at'].fillna(today)

    # Heatmap pour les valeurs manquantes : Pour notre ETL automatisé l’affichage en pause
    # plt.figure(figsize=(10,4))
    # sns.heatmap(df_copy.isna(), cbar=False, cmap="viridis", yticklabels=False)
    # plt.title(f"Heatmap des valeurs manquantes ({df_name})")
    # plt.tight_layout()
    # plt.show(block=False)
    # plt.pause(0.1)
    # plt.close()

    # Remplissage des valeurs manquantes
    df_copy['type_site'] = df_copy['type_site'].replace('', 'Autre').fillna('Autre')
    df_copy['description'] = df_copy['description'].fillna('Description non renseignée')
    df_copy['nom_site'] = df_copy['nom_site'].fillna('')
    df_copy['nom_commune'] = df_copy['nom_commune'].fillna('Inconnu')
    df_copy['code_insee'] = df_copy['code_insee'].fillna('00000')
    df_copy['latitude'] = df_copy['latitude'].fillna(0.0)
    df_copy['longitude'] = df_copy['longitude'].fillna(0.0)

    # Suppression du code_insee si toutes valeurs sont identiques
    if 'code_insee' in df_copy.columns and df_copy['code_insee'].nunique() == 1 and df_copy['code_insee'].iloc[0] in ['00000', 'nan']:
        df_copy = df_copy.drop(columns=['code_insee'])

    # Normalisation des types
    df_copy['latitude'] = df_copy['latitude'].astype(float)
    df_copy['longitude'] = df_copy['longitude'].astype(float)
    df_copy['updated_at'] = pd.to_datetime(df_copy['updated_at'])
    df_copy['created_at'] = pd.to_datetime(df_copy['created_at'])
    text_cols = ['nom_site', 'type_site', 'description', 'nom_commune']
    if 'code_insee' in df_copy.columns:
        text_cols.append('code_insee')
    for col in text_cols:
        df_copy[col] = df_copy[col].astype(str)

    # Remplissage de latitude et longitude depuis point_geo
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
    if 'point_geo' in df_copy.columns:
        df_copy = df_copy.apply(fill_lat_lon, axis=1)

    # Détection et suppression des doublons
    cols_dup = ['nom_site', 'type_site', 'latitude', 'longitude']
    num_duplicates = df_copy.duplicated(subset=cols_dup).sum()
    print(f"Nombre de doublons détectés sur {cols_dup} : {num_duplicates}")
    df_copy = df_copy.drop_duplicates(subset=cols_dup, keep='first')
    print(f"Nombre de doublons restants après suppression : {df_copy.duplicated(subset=cols_dup).sum()}")

    # Remplissage nom_site manquants
    cols_dup_group = ['type_site', 'latitude', 'longitude']
    def fill_missing_nom_site(group):
        existing = group['nom_site'].replace('', np.nan).dropna()
        if not existing.empty:
            group['nom_site'] = group['nom_site'].replace('', np.nan).fillna(existing.iloc[0])
        return group
    df_copy = df_copy.groupby(cols_dup_group, group_keys=False).apply(fill_missing_nom_site)

    # Suppression lignes nom_site manquant
    before_drop = df_copy.shape[0]
    df_copy = df_copy[~df_copy['nom_site'].isna() & (df_copy['nom_site'] != '')]
    after_drop = df_copy.shape[0]
    print(f"Lignes supprimées car nom_site manquant après remplissage : {before_drop - after_drop}")

    # Anonymisation nom_site et description
    # Calculation des masques avant modification
    orig_nom = df_copy['nom_site'].astype(str).fillna('')
    orig_desc = df_copy['description'].astype(str).fillna('')

    mask_nom = orig_nom.apply(lambda x: bool(re.search(r"[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+", x)))
    mask_desc = orig_desc.apply(lambda x: bool(re.search(r"[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+", x)))

    # Création de la colonne anonymized à 0 par défaut
    df_copy['anonymized'] = 0

    # Mes fonctions d'anonymisation
    def anonymize_nom_site_row(row):
        nom_site = row.get('nom_site', '')
        site_id = row.name
        if re.search(r"[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+", str(nom_site)):
            return f"Site touristique #{site_id}"
        return nom_site

    def anonymize_description_text(text):
        if pd.isna(text) or str(text).strip() == "":
            return "Description non renseignée"
        if re.search(r"[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+", str(text)):
            return "Description disponible sur demande"
        return text

    # Application de l'anonymisation
    df_copy['nom_site'] = df_copy.apply(anonymize_nom_site_row, axis=1)
    df_copy['description'] = df_copy['description'].apply(anonymize_description_text)

    # Lignes anonymisées
    df_copy.loc[mask_nom | mask_desc, 'anonymized'] = 1

    print(f"[{df_name}] Anonymisation BigData effectuée sur {int(df_copy['anonymized'].sum())} lignes.")

    # Normalisation avancée type_site
    def remove_internal_dup(type_str):
        if pd.isna(type_str):
            return type_str
        items = [x.strip() for x in type_str.split(';') if x.strip()]
        items = list(dict.fromkeys(items))
        return "; ".join(items)
    df_copy['type_site'] = df_copy['type_site'].apply(remove_internal_dup)

    # Création des colonnes : est_activite et est_lieu
    activity_keywords = ["visite", "surfing", "canoe", "canoë", "kayak", "balade", "voile", "tennis",
                         "piscine", "surf", "nautique", "nautic", "cyclotouriste", "cinéma", "cine",
                         "climb", "golf", "vélos", "velo", "gym", "pilates", "karting", "randos",
                         "concert", "théâtre", "spectacle", "rando", "expo", "exposition", "sortie",
                         "rencontres", "marche", "yoga", "relaxation", "soirée jeux", "contée",
                         "vente directe", "handball", "stage", "soirée", "initiation pêche",
                         "atelier cuisine", "journée immersion"]
    activity_pattern = re.compile("|".join([re.escape(w) for w in activity_keywords]), flags=re.IGNORECASE)
    def normalize_text(text):
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r"[^a-zàâäéèêëïîôöùûüç\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()
    df_copy["nom_site_clean"] = df_copy["nom_site"].apply(normalize_text)
    df_copy["est_activite"] = df_copy["nom_site_clean"].apply(lambda x: 1 if activity_pattern.search(x) else 0)
    df_copy["est_lieu"] = df_copy["est_activite"].apply(lambda x: 0 if x == 1 else 1)
    df_copy["est_activite"] = df_copy["est_activite"].astype(bool)
    df_copy["est_lieu"] = df_copy["est_lieu"].astype(bool)
    df_copy.drop(columns=["nom_site_clean"], inplace=True)

    # Nettoyage final colonnes type_site
    if 'type_site' in df_copy.columns:
        df_copy = df_copy.drop(columns=['type_site'])

    # Résumé final
    print("\n" + "="*80)
    print(f"Préparation terminée pour : {df_name}")
    print("="*80)
    print(f"Dimensions finales : {df_copy.shape[0]} lignes × {df_copy.shape[1]} colonnes")
    print(f"Colonnes : {df_copy.columns.tolist()}")
    print(df_copy.dtypes)
    print(f"Valeurs manquantes totales : {df_copy.isna().sum().sum()}")
    print(f"Doublons : {df_copy.duplicated().sum()}")
    print("\n" + "="*80 + "\n")

    return df_copy


# Exécution de la transformation et sauvegarde CSV
if __name__ == "__main__":
    print("\n Démarrage de la transformation pour df_BigData \n")

    df_result_BigData = transform_data_BigData(df_BigData_copy, df_name="df_BigData_copy")

    # Aperçu final
    print(df_result_BigData.head())
    print(df_result_BigData.info())

    # Sauvegarde en CSV
    df_result_BigData.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\nDataFrame df_result_BigData sauvegardé en CSV : {output_csv}")
