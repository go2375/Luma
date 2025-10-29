import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# On ajoute le dossier extract au path pour importer les données
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "extract")))

# On importe le df_SQLite_copy depuis mon extract_SQLite
from extract_SQLite import df_SQLite_copy

# On crée une fonction principale EDA pour df_SQLite
def EDA_data_SQLite(df, df_name="df_SQLite_copy"):
    """
    Analyse Exploratoire des Données (EDA) pour df_SQLite
    Étapes :
    1. Exploration initiale (dimensions, types, aperçu)
    2. Détection des valeurs manquantes
    3. Détection et suppression des doublons
    4. Analyse des valeurs uniques
    5. Suppression de la colonne code_department (non nécessaire pour la bdd finale)
    6. Normalisation des noms de communes et de départements
    7. Normalisation des types
    """
    # On travaille sur une deuxième copie pour ne pas modifier l'original
    df_copy = df.copy(deep=True)

    print("=" * 80)
    print(f"EDA & PRÉPARATION : {df_name}")
    print("=" * 80)

    # On effectue une étape  : Exploration initiale (dimensions, types, aperçu)
    print(f"\n Dimensions : {df_copy.shape[0]} lignes × {df_copy.shape[1]} colonnes")
    print("\n Types de données :")
    print(df_copy.dtypes)
    print("\n Aperçu des premières lignes :")
    print(df_copy.head())

    # On effectue une étape 2 : Détection des valeurs manquantes  
    na_counts = df_copy.isna().sum()
    na_pct = (na_counts / len(df_copy)) * 100
    na_table = pd.DataFrame({'Nb NaN': na_counts, '% NaN': na_pct})

    if not na_table[na_table['Nb NaN'] > 0].empty:
        print("\n Valeurs manquantes détectées :")
        print(na_table[na_table['Nb NaN'] > 0])

        plt.figure(figsize=(10, 4))
        sns.heatmap(df_copy.isna(), cbar=False, cmap="viridis", yticklabels=False)
        plt.title(f"Heatmap des valeurs manquantes ({df_name})")
        plt.xlabel("Colonnes")
        plt.ylabel("Lignes")
        plt.tight_layout()
        plt.show()

        # On traite les valeurs manquantes
        print("\n  Traitement des valeurs manquantes :")
        for col in df_copy.columns:
            if df_copy[col].isna().sum() > 0:
                if col == 'code_insee':
                    # On garde les NaN pour pouvoir compléter depuis d'autres sources plus tard
                    nb_missing = df_copy[col].isna().sum()
                    print(f"  - {col} : {nb_missing} valeurs manquantes conservées pour futur merge")
                elif col == 'nom_commune':
                    # On remplace les communes manquantes par 'Inconnu'
                    df_copy[col] = df_copy[col].fillna('Inconnu')
                    print(f"  - {col} : valeurs manquantes remplacées par 'Inconnu'")
                elif col == 'nom_department':
                    # On remplace les départements manquants par 'Inconnu'
                    df_copy[col] = df_copy[col].fillna('Inconnu')
                    print(f"  - {col} : valeurs manquantes remplacées par 'Inconnu'")
                    
    else:
        print("\n Aucune valeur manquante détectée")

    # On effectue une étape 3 : Détection et suppression des doublons
    dupl = df_copy.duplicated().sum()
    print(f"\n Doublons détectés : {dupl}")
    if dupl > 0:
        df_copy = df_copy.drop_duplicates()
        print(f"✓ {dupl} doublons supprimés")
    else:
        print("✓ Aucun doublon détecté")

    # On vérifie des doublons sur code_insee
    dupl_code = df_copy.duplicated(subset=['code_insee']).sum()
    if dupl_code > 0:
        print(f"\n {dupl_code} doublons détectés sur code_insee")
        print(df_copy[df_copy.duplicated(subset=['code_insee'], keep=False)].sort_values('code_insee'))
        df_copy = df_copy.drop_duplicates(subset=['code_insee'], keep='first')
        print(f"✓ Doublons supprimés (première occurrence conservée)")

    # On effectue une étape 4 : Analyse des valeurs uniques
    print("\n Analyse des valeurs uniques :")
    for col in df_copy.columns:
        n_unique = df_copy[col].nunique()
        print(f"  - '{col}' : {n_unique} valeurs uniques")
        if n_unique <= 10:
            print(f"    Valeurs : {df_copy[col].unique().tolist()}")

    # Trouver les noms de communes qui apparaissent plusieurs fois
    doublons_communes = df_copy[df_copy.duplicated(subset=['nom_commune'], keep=False)]
    print(f"\nCommunes en double ({len(doublons_communes)} lignes) :")
    print(doublons_communes[['code_insee', 'nom_commune', 'nom_department']].sort_values('nom_commune'))


    # On effectue une étape 5 : Suppression de la colonne code_department (non nécessaire pour la bdd finale)
    print("\n Suppression de la colonne code_department :")
    if 'code_department' in df_copy.columns:
        df_copy = df_copy.drop(columns=['code_department'])
    print("\n  ✓ Colonne 'code_department' supprimée (non nécessaire pour la bdd finale)")

    # On effectue une étape 6 : Normalisation des noms de communes et de départements
    
    if 'nom_commune' in df_copy.columns:
        df_copy['nom_commune'] = df_copy['nom_commune'].str.strip()
        print("  ✓ Espaces superflus supprimés")
        print("\n  Exemples de noms normalisés :")
        print(df_copy['nom_commune'].head(10).tolist())

    if 'nom_department' in df_copy.columns:
        df_copy['nom_department'] = df_copy['nom_department'].str.strip()
        print("  ✓ Espaces superflus supprimés")
        print("\n  Exemples de noms normalisés :")
        print(df_copy['nom_department'].head(10).tolist())


    # On effectue une étape 7 : Normalisation des noms de communes, départements et codes INSEE
    df_copy['nom_commune'] = df_copy['nom_commune'].str.strip()
    df_copy['nom_department'] = df_copy['nom_department'].str.strip()
    df_copy['code_insee'] = df_copy['code_insee'].str.strip()    
    print("\n✓ Normalisation des noms de communes, départements et codes INSEE terminée")

    # On effectue une étape finale : Résumé final
    print("\n" + "=" * 80)
    print(f" Préparation terminée pour : {df_name}")
    print("=" * 80)
    print(f"\nDimensions finales : {df_copy.shape[0]} lignes × {df_copy.shape[1]} colonnes")
    print(f"Colonnes : {df_copy.columns.tolist()}")
    print(f"Valeurs manquantes : {df_copy.isna().sum().sum()}")
    print(f"Doublons : {df_copy.duplicated().sum()}")
    print("\n" + "=" * 80 + "\n")

    return df_copy

# On exécute l'EDA pour df_SQLite
if __name__ == "__main__":
    print("\n Démarrage de l'EDA pour df_SQLite\n")
    df_result_SQLite = EDA_data_SQLite(df_SQLite_copy, df_name="df_SQLite_copy")

    # Aperçu final
    print("\n Aperçu final après EDA :")
    print(df_result_SQLite)
    print(df_result_SQLite.head())
    print(df_result_SQLite.info())