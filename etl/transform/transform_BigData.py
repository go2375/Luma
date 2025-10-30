import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re


# Chemins d'entrée et sortie CSV

base_dir = os.path.dirname(__file__)

# Chemin du CSV d'entrée
input_dir = os.path.join(base_dir, "..", "data")
input_csv = os.path.join(input_dir, "df_BigData_extract_result.csv")

# Chemin du CSV de sortie
output_dir = os.path.join(base_dir, "..", "data")
os.makedirs(output_dir, exist_ok=True)
output_csv = os.path.join(output_dir, "df_BigData_transform_result.csv")


# Import du DataFrame depuis extract_BigData

sys.path.append(os.path.abspath(os.path.join(base_dir, "..", "extract")))
from extract_BigData import df_BigData_copy


# Fonction EDA pour df_BigData

def EDA_data_BigData(df, df_name="df_BigData_copy"):
    df_copy = df.copy(deep=True)

    # 1. Suppression de la colonne _id
    if '_id' in df_copy.columns:
        df_copy = df_copy.drop(columns=['_id'])

    # 2. Séparation code_postal_et_nom_commune
    if 'code_postal_et_nom_commune' in df_copy.columns:
        df_copy[['code_insee', 'nom_commune']] = df_copy['code_postal_et_nom_commune'].str.split('#', expand=True)
        df_copy = df_copy.drop(columns=['code_postal_et_nom_commune'])

    # 3. Extraction et normalisation de type_site
    def extract_type_site(urls):
        if pd.isna(urls) or urls.strip() == '':
            return "Autre"
        categories = [u.split('#')[-1].strip() for u in urls.split('|')]
        return "; ".join(categories)
    df_copy['type_site'] = df_copy['type_site'].apply(extract_type_site)

    # 4. Gestion des dates
    df_copy['updated_at'] = pd.to_datetime(df_copy['updated_at'], errors='coerce')
    today = pd.Timestamp.now().normalize()
    df_copy['created_at'] = df_copy['updated_at'].fillna(today)
    df_copy['updated_at'] = df_copy['updated_at'].fillna(today)

    # 5. Heatmap valeurs manquantes
    plt.figure(figsize=(10,4))
    sns.heatmap(df_copy.isna(), cbar=False, cmap="viridis", yticklabels=False)
    plt.title(f"Heatmap des valeurs manquantes ({df_name})")
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)
    plt.close()

    # 6. Remplissage valeurs manquantes
    df_copy['type_site'] = df_copy['type_site'].replace('', 'Autre').fillna('Autre')
    df_copy['description'] = df_copy['description'].fillna('Description non renseignée')
    df_copy['nom_site'] = df_copy['nom_site'].fillna('')
    df_copy['nom_commune'] = df_copy['nom_commune'].fillna('Inconnu')
    df_copy['code_insee'] = df_copy['code_insee'].fillna('00000')
    df_copy['latitude'] = df_copy['latitude'].fillna(0.0)
    df_copy['longitude'] = df_copy['longitude'].fillna(0.0)

    # 7. Suppression code_insee si toutes valeurs identiques
    if 'code_insee' in df_copy.columns and df_copy['code_insee'].nunique() == 1 and df_copy['code_insee'].iloc[0] in ['00000', 'nan']:
        df_copy = df_copy.drop(columns=['code_insee'])

    # 8. Normalisation des types
    df_copy['latitude'] = df_copy['latitude'].astype(float)
    df_copy['longitude'] = df_copy['longitude'].astype(float)
    df_copy['updated_at'] = pd.to_datetime(df_copy['updated_at'])
    df_copy['created_at'] = pd.to_datetime(df_copy['created_at'])
    text_cols = ['nom_site', 'type_site', 'description', 'nom_commune']
    if 'code_insee' in df_copy.columns:
        text_cols.append('code_insee')
    for col in text_cols:
        df_copy[col] = df_copy[col].astype(str)

    # 9. Remplissage latitude/longitude depuis point_geo
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

    # 10 & 11. Détection et suppression des doublons
    cols_dup = ['nom_site', 'type_site', 'latitude', 'longitude']
    num_duplicates = df_copy.duplicated(subset=cols_dup).sum()
    print(f"Nombre de doublons détectés sur {cols_dup} : {num_duplicates}")
    df_copy = df_copy.drop_duplicates(subset=cols_dup, keep='first')
    print(f"Nombre de doublons restants après suppression : {df_copy.duplicated(subset=cols_dup).sum()}")

    # 12. Remplissage nom_site manquants
    cols_dup_group = ['type_site', 'latitude', 'longitude']
    def fill_missing_nom_site(group):
        existing = group['nom_site'].replace('', np.nan).dropna()
        if not existing.empty:
            group['nom_site'] = group['nom_site'].replace('', np.nan).fillna(existing.iloc[0])
        return group
    df_copy = df_copy.groupby(cols_dup_group, group_keys=False).apply(fill_missing_nom_site)

    # 13. Suppression lignes nom_site manquant
    before_drop = df_copy.shape[0]
    df_copy = df_copy[~df_copy['nom_site'].isna() & (df_copy['nom_site'] != '')]
    after_drop = df_copy.shape[0]
    print(f"Lignes supprimées car nom_site manquant après remplissage : {before_drop - after_drop}")

    # 14. Anonymisation nom_site et description
    def anonymize_nom_site(row):
        nom_site = row.get('nom_site','')
        site_id = row.name
        if re.search(r"[A-Z][a-z]+\s+[A-Z][a-z]+", nom_site):
            return f"Site touristique #{site_id}"
        return nom_site
    def anonymize_description(desc):
        if pd.isna(desc) or desc.strip()=="":
            return "Description non renseignée"
        if re.search(r"[A-Z][a-z]+\s+[A-Z][a-z]+", desc):
            return "Description disponible sur demande"
        return desc
    df_copy['nom_site'] = df_copy.apply(anonymize_nom_site, axis=1)
    df_copy['description'] = df_copy['description'].apply(anonymize_description)

    # 15. Normalisation avancée type_site
    def remove_internal_dup(type_str):
        if pd.isna(type_str):
            return type_str
        items = [x.strip() for x in type_str.split(';') if x.strip()]
        items = list(dict.fromkeys(items))
        return "; ".join(items)
    df_copy['type_site'] = df_copy['type_site'].apply(remove_internal_dup)

    # 16. Création est_activite et est_lieu
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

    # 17. Nettoyage final colonnes type_site
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


# Exécution EDA et sauvegarde CSV

if __name__ == "__main__":
    print("\nDémarrage de l'EDA pour df_BigData\n")

    df_result_BigData = EDA_data_BigData(df_BigData_copy, df_name="df_BigData_copy")

    # Aperçu final
    print(df_result_BigData.head())
    print(df_result_BigData.info())

    # Sauvegarde CSV
    df_result_BigData.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\nDataFrame df_result_BigData sauvegardé en CSV : {output_csv}")
