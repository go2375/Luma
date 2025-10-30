import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

# On ajoute le dossier extract au path pour importer les données
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "extract")))

# On importe df_BigData_copy depuis mon extract
from extract_BigData import df_BigData_copy

# On crée une fonction principale EDA pour df_BigData
def EDA_data_BigData(df, df_name="df_BigData_copy"):
    """
    Analyse Exploratoire des Données (EDA) pour df_BigData
    Étapes :
    1. Suppression de la colonne _id
    2. Séparation du code_postal_et_nom_commune
    3. Extraction et première normalisation de type_site
    4. Gestion des dates
    5. Visualisation des valeurs manquantes
    6. Remplissage des valeurs manquantes
    7. Suppression du code_insee si toutes les valeurs identiques et vides
    8. Normalisation des types
    9. Remplissage latitude/longitude depuis point_geo si disponible
    10. Détection et suppression des doublons sur nom_site + type_site + latitude + longitude
    11. Affichage de doublons avant suppression
    12. Remplissage nom_site manquants à partir d'autres lignes dupliquées
    13. Suppression des lignes dont nom_site reste manquant
    14. Anonymisation du nom_site et de la description
    15. Normalisation avancée du type_site et suppression des doublons internes
    16. Création des colonnes est_activite et est_lieu
    17. Nettoyage final des colonnes pour le type_site
    """

    # On travaille sur une deuxième copie pour ne pas modifier l'original
    df_copy = df.copy(deep=True)

    # On effectue une étape 1 : Suppression de la colonne _id
    if '_id' in df_copy.columns:
        df_copy = df_copy.drop(columns=['_id'])

    # On effectue une étape 2 : Séparation du code_postal_et_nom_commune
    if 'code_postal_et_nom_commune' in df_copy.columns:
        df_copy[['code_insee', 'nom_commune']] = df_copy['code_postal_et_nom_commune'].str.split('#', expand=True)
        df_copy = df_copy.drop(columns=['code_postal_et_nom_commune'])

    # On effectue une étape 3 : Extraction et première normalisation de type_site
    def extract_type_site(urls):
        if pd.isna(urls) or urls.strip() == '':
            return "Autre"
        categories = [u.split('#')[-1].strip() for u in urls.split('|')]
        return "; ".join(categories)

    df_copy['type_site'] = df_copy['type_site'].apply(extract_type_site)

    # On effectue une étape 4 : Gestion des dates
    df_copy['updated_at'] = pd.to_datetime(df_copy['updated_at'], errors='coerce')
    today = pd.Timestamp.now().normalize()
    df_copy['created_at'] = df_copy['updated_at'].fillna(today)
    df_copy['updated_at'] = df_copy['updated_at'].fillna(today)

    # On effectue une étape 5 : Visualisation des valeurs manquantes
    plt.figure(figsize=(10,4))
    sns.heatmap(df_copy.isna(), cbar=False, cmap="viridis", yticklabels=False)
    plt.title(f"Heatmap des valeurs manquantes ({df_name})")
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)
    plt.close()

    # # On effectue une étape 6 : Remplissage des valeurs manquantes
    df_copy['type_site'] = df_copy['type_site'].replace('', 'Autre').fillna('Autre')
    df_copy['description'] = df_copy['description'].fillna('Description non renseignée')
    df_copy['nom_site'] = df_copy['nom_site'].fillna('')
    df_copy['nom_commune'] = df_copy['nom_commune'].fillna('Inconnu')
    df_copy['code_insee'] = df_copy['code_insee'].fillna('00000')
    df_copy['latitude'] = df_copy['latitude'].fillna(0.0)
    df_copy['longitude'] = df_copy['longitude'].fillna(0.0)

    # On effectue une étape 7 : Suppression du code_insee si toutes les valeurs identiques et vides
    if 'code_insee' in df_copy.columns and df_copy['code_insee'].nunique() == 1 and df_copy['code_insee'].iloc[0] in ['00000', 'nan']:
        df_copy = df_copy.drop(columns=['code_insee'])

    # On effectue une étape 8 : Normalisation des types
    df_copy['latitude'] = df_copy['latitude'].astype(float)
    df_copy['longitude'] = df_copy['longitude'].astype(float)
    df_copy['updated_at'] = pd.to_datetime(df_copy['updated_at'])
    df_copy['created_at'] = pd.to_datetime(df_copy['created_at'])
    text_cols = ['nom_site', 'type_site', 'description', 'nom_commune']
    if 'code_insee' in df_copy.columns:
        text_cols.append('code_insee')
    for col in text_cols:
        df_copy[col] = df_copy[col].astype(str)

    # On effectue une étape 9 : Remplissage latitude/longitude depuis point_geo si disponible
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

    # On effectue une étape 10 : Détection et suppression des doublons sur nom_site + type_site + latitude + longitude
    cols_dup = ['nom_site', 'type_site', 'latitude', 'longitude']

    # On effectue une étape 11 : Affichage de doublons avant suppression
    num_duplicates = df_copy.duplicated(subset=cols_dup).sum()
    print(f"Nombre de doublons détectés sur {cols_dup} : {num_duplicates}")

    # On supprime les doublons en gardant la première occurrence
    df_copy = df_copy.drop_duplicates(subset=cols_dup, keep='first')

    # On vérifie après suppression
    num_duplicates_after = df_copy.duplicated(subset=cols_dup).sum()
    print(f"Nombre de doublons restants après suppression : {num_duplicates_after}")

    # On effectue une étape 12 : Remplissage nom_site manquants à partir d'autres lignes dupliquées (type_site + latitude + longitude)
    cols_dup = ['type_site', 'latitude', 'longitude']

    def fill_missing_nom_site(group):
        existing = group['nom_site'].dropna().replace('', np.nan).dropna()
        if not existing.empty:
            group['nom_site'] = group['nom_site'].replace('', np.nan).fillna(existing.iloc[0])
        return group

    df_copy = df_copy.groupby(cols_dup, group_keys=False).apply(fill_missing_nom_site)
    
    # On effectue une étape 13 : Suppression des lignes dont nom_site reste manquant
    before_drop = df_copy.shape[0]
    df_copy = df_copy[~df_copy['nom_site'].isna() & (df_copy['nom_site'] != '')]
    after_drop = df_copy.shape[0]
    print(f"Lignes supprimées car nom_site manquant après remplissage : {before_drop - after_drop}")

    # On effectue une étape 14 : Anonymisation du nom_site et de la description
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

    # On effectue une étape 15 : Normalisation avancée du type_site et suppression des doublons internes
    def remove_internal_dup(type_str):
        if pd.isna(type_str):
            return type_str
        items = [x.strip() for x in type_str.split(';') if x.strip()]
        items = list(dict.fromkeys(items))
        return "; ".join(items)

    df_copy['type_site'] = df_copy['type_site'].apply(remove_internal_dup)

    # On effectue une étape 16 : Création des colonnes est_activite et est_lieu
    # On définit la liste des mots-clés associés à des activités
    activity_keywords = [
        "visite", "surfing", "canoe", "canoë", "kayak", "balade", "voile",
        "tennis", "piscine", "surf", "nautique", "nautic", "cyclotouriste",
        "cinéma", "cine", "climb", "golf", "vélos", "velo", "gym", "pilates",
        "karting", "randos", "concert", "théâtre", "spectacle", "rando",
        "expo", "exposition", "sortie", "rencontres", "marche", "yoga",
        "relaxation", "soirée jeux", "contée", "vente directe", "handball",
        "stage", "soirée", "initiation pêche", "atelier cuisine",
        "journée immersion"
    ]

    # On compile un seul regex avec tous les mots-clés, insensible à la casse et aux accents
    activity_pattern = re.compile(
        r"|".join([re.escape(word) for word in activity_keywords]),
        flags=re.IGNORECASE
    )

    # On effectue une nettoyage du texte (retrait des accents et ponctuation simple pour uniformiser)
    def normalize_text(text):
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r"[^a-zàâäéèêëïîôöùûüç\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    # On détecte des activités
    df_copy["nom_site_clean"] = df_copy["nom_site"].apply(normalize_text)

    df_copy["est_activite"] = df_copy["nom_site_clean"].apply(
        lambda x: 1 if activity_pattern.search(x) else 0
    )

    # est_lieu = 1 si ce n’est pas une activité
    df_copy["est_lieu"] = df_copy["est_activite"].apply(lambda x: 0 if x == 1 else 1)

    # Conversion explicite en booléen
    df_copy["est_activite"] = df_copy["est_activite"].astype(bool)
    df_copy["est_lieu"] = df_copy["est_lieu"].astype(bool)

    # Vérification des types
    print("Types de colonnes après conversion :")
    print(df_copy[["est_activite", "est_lieu"]].dtypes)

    # Suppression de la colonne temporaire de nettoyage
    df_copy.drop(columns=["nom_site_clean"], inplace=True)

    print("✓ Étape 17 : Colonnes 'est_activite' et 'est_lieu' créées avec succès.")
    print(df_copy[["nom_site", "est_activite", "est_lieu"]].head(10))
    
    # On effectue une étape 17 : Nettoyage final des colonnes pour le type_site
    # On supprime les colonnes intermédiaires inutiles pour type_site
    cols_to_drop = ['type_site']
    df_copy = df_copy.drop(columns=[c for c in cols_to_drop if c in df_copy.columns])

    # On effectue une étape finale : Résumé final
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

# On exécute l'EDA pour df_BigData
df_result_BigData = EDA_data_BigData(df_BigData_copy, df_name="df_BigData_copy")

if __name__ == "__main__":
    print("\nDémarrage de l'EDA pour df_BigData\n")

    # Aperçu final
    print("\nAperçu final après EDA :")
    print(df_result_BigData.head())
    print(df_result_BigData.info())