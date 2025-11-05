import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


# Je définis le chemin du script courant qui est : Lumea/etl/transform
base_dir = os.path.dirname(__file__)

# Je définis le chemin pour récuperer mon CSV du dataframe SQLite à la sortie de l'extraction 
input_dir = os.path.join(base_dir, "..", "data")
input_csv = os.path.join(input_dir, "df_SQLite_extract_result.csv")

# Je définis le chemin pour créer le CSV à la fin de phase de transformation 
output_dir = os.path.join(base_dir, "..", "data")
os.makedirs(output_dir, exist_ok=True)
output_csv = os.path.join(output_dir, "df_SQLite_transform_result.csv")

# J'importe le dataframe depuis extract_SQLite 
sys.path.append(os.path.abspath(os.path.join(base_dir, "..", "extract")))
from extract_SQLite import df_SQLite_copy

# Je crée ma fonction de la transformation pour df_SQLite
def transform_data_SQLite(df, df_name="df_SQLite_copy"):
    df_copy = df.copy(deep=True)

    print("=" * 80)
    print(f"Transformation : {df_name}")
    print("=" * 80)

    # Exploration initiale
    print(f"\nDimensions : {df_copy.shape[0]} lignes × {df_copy.shape[1]} colonnes")
    print("\nTypes de données :")
    print(df_copy.dtypes)
    print("\nAperçu des premières lignes :")
    print(df_copy.head())

    # Détection des valeurs manquantes
    na_counts = df_copy.isna().sum()
    na_pct = (na_counts / len(df_copy)) * 100
    na_table = pd.DataFrame({'Nb NaN': na_counts, '% NaN': na_pct})
    if not na_table[na_table['Nb NaN'] > 0].empty:
        print("\nValeurs manquantes détectées :")
        print(na_table[na_table['Nb NaN'] > 0])

        # Pour notre ETL automatisé l’affichage en pause
        # plt.figure(figsize=(10, 4))
        # sns.heatmap(df_copy.isna(), cbar=False, cmap="viridis", yticklabels=False)
        # plt.title(f"Heatmap des valeurs manquantes ({df_name})")
        # plt.xlabel("Colonnes")
        # plt.ylabel("Lignes")
        # plt.tight_layout()
        # plt.show()

        # Traitement simplifié des valeurs manquantes
        for col in df_copy.columns:
            if df_copy[col].isna().sum() > 0:
                if col in ['nom_commune', 'nom_department']:
                    df_copy[col] = df_copy[col].fillna('Inconnu')
    else:
        print("\nAucune valeur manquante détectée")

    # Gestion des doublons
    dupl = df_copy.duplicated().sum()
    print(f"\nDoublons détectés : {dupl}")
    if dupl > 0:
        df_copy = df_copy.drop_duplicates()
        print(f"✓ {dupl} doublons supprimés")
    else:
        print("✓ Aucun doublon détecté")

    # Gestion des doublons sur code_insee
    dupl_code = df_copy.duplicated(subset=['code_insee']).sum()
    if dupl_code > 0:
        print(f"\n{dupl_code} doublons détectés sur code_insee")
        df_copy = df_copy.drop_duplicates(subset=['code_insee'], keep='first')
        print(f"✓ Doublons supprimés (première occurrence conservée)")

    # Analyse des valeurs uniques
    print("\nAnalyse des valeurs uniques :")
    for col in df_copy.columns:
        n_unique = df_copy[col].nunique()
        print(f"  - '{col}' : {n_unique} valeurs uniques")
        if n_unique <= 10:
            print(f"    Valeurs : {df_copy[col].unique().tolist()}")

    # Suppression de la colonne code_department
    if 'code_department' in df_copy.columns:
        df_copy = df_copy.drop(columns=['code_department'])
        print("\n✓ Colonne 'code_department' supprimée")

    # Normalisation des noms
    for col in ['nom_commune', 'nom_department', 'code_insee']:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].astype(str).str.strip()
    print("\n✓ Normalisation des noms et codes terminée")

    # Résumé final
    print("\n" + "=" * 80)
    print(f"Préparation terminée pour : {df_name}")
    print("=" * 80)
    print(f"\nDimensions finales : {df_copy.shape[0]} lignes × {df_copy.shape[1]} colonnes")
    print(f"Colonnes : {df_copy.columns.tolist()}")
    print(f"Valeurs manquantes : {df_copy.isna().sum().sum()}")
    print(f"Doublons : {df_copy.duplicated().sum()}")
    print("\n" + "=" * 80 + "\n")

    return df_copy

# Exécution de la transformation et sauvegarde
if __name__ == "__main__":
    print("\nDémarrage de la transformation pour df_SQLite\n")

    df_result_SQLite = transform_data_SQLite(df_SQLite_copy, df_name="df_SQLite_copy")

    # Aperçu final
    print("\nAperçu final après transform :")
    print(df_result_SQLite.head())
    print(df_result_SQLite.info())

    # Sauvegarde en CSV
    df_result_SQLite.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\nDataFrame df_result_SQLite sauvegardé en CSV : {output_csv}")