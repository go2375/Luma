import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# On ajoute le dossier extract au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "extract")))

# On importe le df_API_copy depuis extract_API
from extract_API import df_API_copy

# On créer l'EDA pour df_API
def EDA_data_API(df, df_name="df_API_copy"):
    """
    EDA et préparation d'un DataFrame de type API (communes).
    Travaille sur une copie pour ne pas modifier l'original.
    """
    df_copy = df.copy()
    
    print("="*80)
    print(f"EDA & Préparation : {df_name}")
    print("="*80)
    
    # On affiche les dimensions et les types
    print("\n Dimensions :", df_copy.shape)
    print("\n Types de données :\n", df_copy.dtypes)
    print("\n Aperçu :\n", df_copy.head())
    
    # On vérifie des valeurs manquantes
    na_counts = df_copy.isna().sum()
    na_pct = (na_counts / len(df_copy)) * 100
    na_table = pd.DataFrame({'Nb NaN': na_counts, '% NaN': na_pct})
    if not na_table[na_table['Nb NaN'] > 0].empty:
        print("\n🚨 Valeurs manquantes :\n", na_table[na_table['Nb NaN'] > 0])
        plt.figure(figsize=(10, 4))
        sns.heatmap(df_copy.isna(), cbar=False, cmap="viridis")
        plt.title(f"Heatmap valeurs manquantes ({df_name})")
        plt.show()
    
    # On vérifie des doublons
    dupl = df_copy.duplicated().sum()
    print("\n📋 Doublons :", dupl)
    if dupl > 0:
        df_copy = df_copy.drop_duplicates()
        print("Doublons supprimés")
    
    # On examine des valeurs uniques
    for col in df_copy.columns:
        print(f"\n🔢 Colonne '{col}' : {df_copy[col].nunique()} valeurs uniques")
    
    # Permet de nettoyer les noms des communes
    if 'nom_commune' in df_copy.columns:
        df_copy['nom_commune'] = df_copy['nom_commune'].str.strip()
        df_copy['nom_commune'] = df_copy['nom_commune'].str.normalize('NFKD')\
                                             .str.encode('ascii', errors='ignore')\
                                             .str.decode('utf-8')
    
    print("\n Préparation terminée pour :", df_name)
    print("="*80 + "\n")
    
    return df_copy

# Permet d'exécuter si le script est lancé directement
if __name__ == "__main__":
    df_result = EDA_data_API(df_API_copy, df_name="df_API_copy")
    # Permet une vérification rapide
    print("\n📌 Aperçu final après EDA :")
    print(df_result.head())
    print(df_result.info())