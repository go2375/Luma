import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# On ajoute le dossier extract au path pour importer les données
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "extract")))

# On importe le df_API_copy depuis extract_API
from extract_API import df_API_copy

# On crée une fonction principale EDA pour df_API
def EDA_data_API(df, df_name="df_API_copy"):
    """
    Analyse Exploratoire des Données (EDA) pour le df_API
    Étapes :
    1. Exploration initiale (dimensions, types, aperçu)
    2. Détection des valeurs manquantes
    3. Détection et suppression des doublons
    4. Analyse des valeurs uniques
    5. Création et validation de la colonne label_cite_caractere
    6. Normalisation des noms de communes
    7. Normalisation des types
    """
    # On créer une deuxième copie profonde pour éviter les modifications du df original
    df_copy = df.copy(deep=True)
    
    print("=" * 80)
    print(f"EDA & PRÉPARATION : {df_name}")
    print("=" * 80)
    
    # On effectue une étape 1: Exploration initiale (dimensions, types, aperçu)
    print(f"\n Dimensions : {df_copy.shape[0]} lignes × {df_copy.shape[1]} colonnes")
    
    print("\n Types de données :")
    print(df_copy.dtypes)
    
    print("\n Aperçu des premières lignes :")
    print(df_copy.head())
    
    # On effectue une étape 2: Détection des valeurs manquantes  
    na_counts = df_copy.isna().sum()
    na_pct = (na_counts / len(df_copy)) * 100
    na_table = pd.DataFrame({'Nb NaN': na_counts, '% NaN': na_pct})
    
    if not na_table[na_table['Nb NaN'] > 0].empty:
        print("\n Valeurs manquantes détectées :")
        print(na_table[na_table['Nb NaN'] > 0])
        
        # On visualise les valeurs manquantes
        plt.figure(figsize=(10, 4))
        sns.heatmap(df_copy.isna(), cbar=False, cmap="viridis", yticklabels=False)
        plt.title(f"Heatmap des valeurs manquantes ({df_name})")
        plt.xlabel("Colonnes")
        plt.ylabel("Lignes")
        plt.tight_layout()
        plt.show()
        
        # On traite des valeurs manquantes
        print("\n Traitement des valeurs manquantes :")
        for col in df_copy.columns:
            if df_copy[col].isna().sum() > 0:
                if col == 'code_insee':
                    # On garde les NaN pour pouvoir compléter depuis d'autres sources plus tard
                    nb_missing = df_copy[col].isna().sum()
                if nb_missing > 0:
                    print(f"  - {col} : {nb_missing} valeurs manquantes conservées pour futur merge")
                elif col == 'nom_commune':
                    # Remplacer par 'Inconnu' si nom manquant
                    df_copy[col] = df_copy[col].fillna('Inconnu')
                    print(f"  - {col} : valeurs manquantes remplacées par 'Inconnu'")
                elif col == 'label_cite_caractere':
                    # Remplir avec 1 (toutes les communes de l'API sont labellisées)
                    df_copy[col] = df_copy[col].fillna(1)
                    print(f"  - {col} : valeurs manquantes remplacées par 1")
    else:
        print("\n Aucune valeur manquante détectée")
    
    # On effectue une étape 3: Détection et suppression des doublons
    dupl = df_copy.duplicated().sum()
    print(f"\n Doublons détectés : {dupl}")
    
    if dupl > 0:
        df_copy = df_copy.drop_duplicates()
        print(f"✓ {dupl} doublons supprimés")
    else:
        print("✓ Aucun doublon détecté")
    
    # On vérifier les doublons sur code_insee (clé unique)
    dupl_code = df_copy.duplicated(subset=['code_insee']).sum()
    if dupl_code > 0:
        print(f"\n  {dupl_code} doublons détectés sur code_insee")
        print("Doublons :")
        print(df_copy[df_copy.duplicated(subset=['code_insee'], keep=False)].sort_values('code_insee'))
        df_copy = df_copy.drop_duplicates(subset=['code_insee'], keep='first')
        print(f"✓ Doublons supprimés (conservation de la première occurrence)")
    
    # On effectue une étape 4: Analyse des valeurs uniques
    print("\n Analyse des valeurs uniques :")
    for col in df_copy.columns:
        n_unique = df_copy[col].nunique()
        print(f"  - '{col}' : {n_unique} valeurs uniques")
        
        # On afficher exemples pour chaque colonne
        if n_unique <= 10:
            print(f"    Valeurs : {df_copy[col].unique().tolist()}")
    
    # On effectue une étape 5: Création de la colonne label_cite_caractere    
    print("\n  Création de la colonne label_cite_caractere :")
    print("  Ajout de la colonne avec valeur par défaut = 1")
    df_copy['label_cite_caractere'] = 1
    
    # On effectue une étape 6 : On normalise des noms de communes
    print("\n Normalisation des noms de communes :")
    
    if 'nom_commune' in df_copy.columns:
        # On supprime les espaces superflus
        df_copy['nom_commune'] = df_copy['nom_commune'].str.strip()
        print("  ✓ Espaces superflus supprimés")
             
        # On affiche quelques exemples
        print("\n  Exemples de noms normalisés :")
        print(df_copy['nom_commune'].head(10).tolist())

    # On effectue une étape 7 : Normalisation des types
    # On convertit code_insee et nom_commune en string
    df_copy['code_insee'] = df_copy['code_insee'].astype(str)
    df_copy['nom_commune'] = df_copy['nom_commune'].astype(str)

    # On convertit label_cite_caractere en booléen
    # On considère 0 = False, tout autre valeur = True
    df_copy['label_cite_caractere'] = df_copy['label_cite_caractere'].astype(bool)

    # On vérifie
    print(df_copy.dtypes)
    
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

# On exécute l'EDA pour df_API
if __name__ == "__main__":
    print("\n Démarrage de l'EDA pour df_API\n")
    
    # On exécute l'EDA sur df_API_copy
    df_result_API = EDA_data_API(df_API_copy, df_name="df_API_copy")
    
    # On vérifie
    print("\n" + "=" * 80)
    print("\nPremières lignes :")
    print(df_result_API.head(10))

    print(" Aperçu final après EDA")
    print(df_result_API)  
    
    print("\nInformations complètes :")
    print(df_result_API.info())
    
    print("\nStatistiques descriptives :")
    print(df_result_API.describe(include='all'))