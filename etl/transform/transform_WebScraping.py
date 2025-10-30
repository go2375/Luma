import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Définition des chemins

base_dir = os.path.dirname(__file__)
input_dir = os.path.join(base_dir, "..", "data")  # chemin du CSV d'entrée
input_csv = os.path.join(input_dir, "df_WebScrap_extract_result.csv")

output_dir = os.path.join(base_dir, "..", "data")  # chemin du CSV de sortie
os.makedirs(output_dir, exist_ok=True)
output_csv = os.path.join(output_dir, "df_WebScrap_transform_result.csv")

# Vérification que le fichier existe
if not os.path.exists(input_csv):
    raise FileNotFoundError(f"Fichier CSV introuvable : {input_csv}")


# Chargement du CSV

df_WebScrap = pd.read_csv(input_csv, encoding='utf-8-sig')
print(f"\nCSV chargé : {input_csv} ({len(df_WebScrap)} lignes)")

def EDA_data_WebScrap(df, df_name="df_WebScrap", n_departments=4):
    """
    Analyse Exploratoire des Données (EDA) pour df_WebScrap
    Étapes :
    1. Exploration initiale
    2. Détection valeurs manquantes
    3. Création colonnes communes et départements
    4. Détection et suppression des doublons
    5. Suppression colonnes initiales
    """
    df_copy = df.copy(deep=True)
    
    print("="*80)
    print(f"EDA & PRÉPARATION : {df_name}")
    print("="*80)
    
    # On effectue une étape 1 : Exploration initiale
    print(f"\nDimensions : {df_copy.shape[0]} lignes × {df_copy.shape[1]} colonnes")
    print("\nTypes de données :")
    print(df_copy.dtypes)
    print("\nAperçu des premières lignes :")
    print(df_copy.head())

    # On effectue une étape 2 : Détection valeurs manquantes
    na_counts = df_copy.isna().sum()
    na_pct = (na_counts / len(df_copy)) * 100
    na_table = pd.DataFrame({'Nb NaN': na_counts, '% NaN': na_pct})
    if not na_table[na_table['Nb NaN']>0].empty:
        print("\nValeurs manquantes détectées :")
        print(na_table[na_table['Nb NaN']>0])
        plt.figure(figsize=(10,4))
        sns.heatmap(df_copy.isna(), cbar=False, cmap="viridis", yticklabels=False)
        plt.title(f"Heatmap des valeurs manquantes ({df_name})")
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.1)
        plt.close()
    else:
        print("\nAucune valeur manquante détectée")

    # On effectue une étape 3 : Création colonnes communes et départements
    df_copy['nom_commune'] = ''
    df_copy['nom_commune_breton'] = ''
    df_copy['nom_department'] = ''
    df_copy['nom_department_breton'] = ''
    
    df_copy.loc[df_copy.index[-n_departments:], 'nom_department'] = df_copy.loc[df_copy.index[-n_departments:], 'nom']
    df_copy.loc[df_copy.index[-n_departments:], 'nom_department_breton'] = df_copy.loc[df_copy.index[-n_departments:], 'nom_breton']
    
    df_copy.loc[df_copy.index[:-n_departments], 'nom_commune'] = df_copy.loc[df_copy.index[:-n_departments], 'nom']
    df_copy.loc[df_copy.index[:-n_departments], 'nom_commune_breton'] = df_copy.loc[df_copy.index[:-n_departments], 'nom_breton']
    
    for col in ['nom_commune', 'nom_commune_breton', 'nom_department', 'nom_department_breton']:
        df_copy[col] = df_copy[col].fillna('').astype(str).str.strip()
    print("\n✓ Colonnes communes et départements créées et normalisées")

    # On effectue une étape 4 : Détection et suppression des doublons
    dupl = df_copy.duplicated().sum()
    print(f"\nDoublons détectés : {dupl}")
    if dupl > 0:
        df_copy = df_copy.drop_duplicates()
        print(f"✓ {dupl} doublons supprimés")
    else:
        print("✓ Aucun doublon détecté")
    
    # On effectue une étape 5 : Suppression colonnes initiales
    cols_to_drop = ['nom', 'nom_breton']
    df_copy = df_copy.drop(columns=[c for c in cols_to_drop if c in df_copy.columns])
    print("\n✓ Colonnes 'nom' et 'nom_breton' supprimées")

    # Aperçu final
    print("\nPremières lignes :")
    print(df_copy.head(10))
    print("\nDernières lignes :")
    print(df_copy.tail(10))

    print("\n" + "="*80)
    print(f"Préparation terminée pour : {df_name}")
    print("="*80)
    print(f"\nDimensions finales : {df_copy.shape[0]} lignes × {df_copy.shape[1]} colonnes")
    print(f"Colonnes : {df_copy.columns.tolist()}")
    print(f"Valeurs manquantes totales : {df_copy.isna().sum().sum()}")
    print(f"Doublons : {df_copy.duplicated().sum()}")
    print("\n" + "="*80 + "\n")
    
    return df_copy

if __name__ == "__main__":
    print("\nDémarrage de l'EDA pour df_WebScrap\n")  
    df_result_WebScrap = EDA_data_WebScrap(df_WebScrap, df_name="df_WebScrap")
    
    print(df_result_WebScrap.info())  # <-- ici, la variable existe
    
    # Sauvegarde du résultat
    df_result_WebScrap.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\nDataFrame df_result_WebScrap sauvegardé en CSV : {output_csv}")