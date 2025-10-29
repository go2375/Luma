import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# On ajoute le dossier extract au path pour importer les données
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "extract")))

# On importe le df_WebScrap_copy depuis mon extract_WebScraping
from extract_WebScraping import df_WebScrap_copy

def EDA_data_WebScrap(df, df_name="df_WebScrap_copy", n_departments=4):
    """
    Analyse Exploratoire des Données (EDA) pour df_WebScrap
    Étapes :
        1. Exploration initiale
        2. Détection des valeurs manquantes
        3. Création et remplissage des colonnes de communes et départements
        4. Détection et suppression des doublons
        5. Suppression des colonnes initiale nom et nom_breton
        6. Affichage des premières et dernières lignes
    """
    # On travaille sur une deuxième copie pour ne pas modifier l'original
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
    
    # On effectue une étape 2 : Détection des valeurs manquantes
    na_counts = df_copy.isna().sum()
    na_pct = (na_counts / len(df_copy)) * 100
    na_table = pd.DataFrame({'Nb NaN': na_counts, '% NaN': na_pct})
    
    if not na_table[na_table['Nb NaN']>0].empty:
        print("\nValeurs manquantes détectées :")
        print(na_table[na_table['Nb NaN']>0])
        
        # On visualise un heatmap
        plt.figure(figsize=(10,4))
        sns.heatmap(df_copy.isna(), cbar=False, cmap="viridis", yticklabels=False)
        plt.title(f"Heatmap des valeurs manquantes ({df_name})")
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.1)
        plt.close()
    else:
        print("\nAucune valeur manquante détectée")
    
    # On effectue une étape 3 : Création et remplissage des colonnes de communes et départements
    df_copy['nom_commune'] = ''
    df_copy['nom_commune_breton'] = ''
    df_copy['nom_department'] = ''
    df_copy['nom_department_breton'] = ''
    
    # Voyant que les dernières lignes sont des départements
    df_copy.loc[df_copy.index[-n_departments:], 'nom_department'] = df_copy.loc[df_copy.index[-n_departments:], 'nom']
    df_copy.loc[df_copy.index[-n_departments:], 'nom_department_breton'] = df_copy.loc[df_copy.index[-n_departments:], 'nom_breton']
    
    # Voyant que les autres lignes sont des communes
    df_copy.loc[df_copy.index[:-n_departments], 'nom_commune'] = df_copy.loc[df_copy.index[:-n_departments], 'nom']
    df_copy.loc[df_copy.index[:-n_departments], 'nom_commune_breton'] = df_copy.loc[df_copy.index[:-n_departments], 'nom_breton']
    
    # On effectue une lormalisation : string et suppression espaces superflus
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
    
    # On effectue une étape 5 : Suppression des colonnes initiale nom et nom_breton
    cols_to_drop = ['nom', 'nom_breton']
    df_copy = df_copy.drop(columns=[c for c in cols_to_drop if c in df_copy.columns])
    print("\n✓ Colonnes 'nom' et 'nom_breton' supprimées")

    # On effectue une étape 6 : Affichage des premières et dernières lignes
    print("\nPremières lignes :")
    print(df_copy.head(10))
    print("\nDernières lignes :")
    print(df_copy.tail(10))
    
    # On effectue une étape finale : Résumé final
    print("\n" + "="*80)
    print(f"Préparation terminée pour : {df_name}")
    print("="*80)
    print(f"\nDimensions finales : {df_copy.shape[0]} lignes × {df_copy.shape[1]} colonnes")
    print(f"Colonnes : {df_copy.columns.tolist()}")
    print(f"Valeurs manquantes totales : {df_copy.isna().sum().sum()}")
    print(f"Doublons : {df_copy.duplicated().sum()}")
    print("\n" + "="*80 + "\n")
    
    return df_copy

# On exécute l'EDA pour df_WebScrap
if __name__ == "__main__":
    print("\nDémarrage de l'EDA pour df_WebScrap\n")
    df_result_WebScrap = EDA_data_WebScrap(df_WebScrap_copy, df_name="df_WebScrap_copy")
    
    # Aperçu final
    print("\nAperçu final après EDA :")
    print(df_result_WebScrap.info())
