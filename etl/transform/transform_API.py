import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Je définis le chemin du script courant qui est : Lumea/etl/transform
base_dir = os.path.dirname(__file__)

# Je définis le chemin pour récuperer mon CSV du dataframe API à la sortie de l'extraction 
input_dir = os.path.join(base_dir, "..", "data")
input_csv = os.path.join(input_dir, "df_API_extract_result.csv")

# Je définis le chemin pour créer le CSV à la fin de phase de transformation 
output_dir = os.path.join(base_dir, "..", "data")
os.makedirs(output_dir, exist_ok=True)
output_csv = os.path.join(output_dir, "df_API_transform_result.csv")


# J'importe le dataframe depuis extract_API

sys.path.append(os.path.abspath(os.path.join(base_dir, "..", "extract")))
from extract_API import df_API_copy


# Je crée ma fonction de la transformation pour df_API

def EDA_data_API(df, df_name="df_API_copy"):
    df_copy = df.copy(deep=True)
    
    print("=" * 80)
    print(f"EDA & PRÉPARATION : {df_name}")
    print("=" * 80)
    
    # Exploration initiale
    print(f"\n Dimensions : {df_copy.shape[0]} lignes × {df_copy.shape[1]} colonnes")
    print("\n Types de données :")
    print(df_copy.dtypes)
    print("\n Aperçu des premières lignes :")
    print(df_copy.head())
    
    # Détection des valeurs manquantes
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
        # Traitement des valeurs manquantes
        print("\nTraitement des valeurs manquantes :")
        for col in df_copy.columns:
            nb_missing = df_copy[col].isna().sum()
            if nb_missing > 0:
                if col == 'code_insee':
                    print(f"  - {col} : {nb_missing} valeurs manquantes (seront supprimées plus tard)")
                elif col == 'nom_commune':
                    df_copy[col] = df_copy[col].fillna('Inconnu')
                    print(f"  - {col} : valeurs manquantes remplacées par 'Inconnu'")
                elif col == 'label_cite_caractere':
                    df_copy[col] = df_copy[col].fillna(1)
                    print(f"  - {col} : valeurs manquantes remplacées par 1")
    else:
        print("\nAucune valeur manquante détectée")
    
    # Détection et suppression des doublons
    dupl = df_copy.duplicated().sum()
    print(f"\n Doublons détectés : {dupl}")
    if dupl > 0:
        df_copy = df_copy.drop_duplicates()
        print(f"✓ {dupl} doublons supprimés")
    else:
        print("✓ Aucun doublon détecté")
    
    # Vérification doublons sur code_insee
    dupl_code = df_copy.duplicated(subset=['code_insee']).sum()
    if dupl_code > 0:
        print(f"\n  {dupl_code} doublons détectés sur code_insee")
        print(df_copy[df_copy.duplicated(subset=['code_insee'], keep=False)].sort_values('code_insee'))
        df_copy = df_copy.drop_duplicates(subset=['code_insee'], keep='first')
        print(f"✓ Doublons supprimés (conservation de la première occurrence)")
    
    # Analyse des valeurs uniques
    print("\n Analyse des valeurs uniques :")
    for col in df_copy.columns:
        n_unique = df_copy[col].nunique()
        print(f"  - '{col}' : {n_unique} valeurs uniques")
        if n_unique <= 10:
            print(f"    Valeurs : {df_copy[col].unique().tolist()}")
    
    # Création colonne label_cite_caractere
    print("\n  Création de la colonne label_cite_caractere : valeur par défaut = 1")
    df_copy['label_cite_caractere'] = 1
    
    # Normalisation noms de communes
    if 'nom_commune' in df_copy.columns:
        df_copy['nom_commune'] = df_copy['nom_commune'].str.strip()
        print("  ✓ Espaces superflus supprimés")
        print("\n  Exemples de noms normalisés :")
        print(df_copy['nom_commune'].head(10).tolist())
    
    # Normalisation des types
    df_copy['code_insee'] = df_copy['code_insee'].astype(str)
    df_copy['nom_commune'] = df_copy['nom_commune'].astype(str)
    df_copy['label_cite_caractere'] = df_copy['label_cite_caractere'].astype(bool)
    
    print(df_copy.dtypes)
    
    # Résumé final
    print("\n" + "=" * 80)
    print(f" Préparation terminée pour : {df_name}")
    print("=" * 80)
    print(f"\nDimensions finales : {df_copy.shape[0]} lignes × {df_copy.shape[1]} colonnes")
    print(f"Colonnes : {df_copy.columns.tolist()}")
    print(f"Valeurs manquantes : {df_copy.isna().sum().sum()}")
    print(f"Doublons : {df_copy.duplicated().sum()}")
    print("\n" + "=" * 80 + "\n")
    
    return df_copy


# Exécution EDA et sauvegarde CSV

if __name__ == "__main__":
    print("\n Démarrage de l'EDA pour df_API\n")
    
    df_result_API = EDA_data_API(df_API_copy, df_name="df_API_copy")
    
    # Aperçu final
    print("\nPremières lignes :")
    print(df_result_API.head(10))
    
    print("\nInformations complètes :")
    print(df_result_API.info())
    
    print("\nStatistiques descriptives :")
    print(df_result_API.describe(include='all'))
    
    # Sauvegarde CSV
    df_result_API.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\nDataFrame df_result_API sauvegardé en CSV : {output_csv}")
