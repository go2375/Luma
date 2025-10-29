import os
import sys
import pandas as pd
import sqlite3

# On ajoute le dossier extract au path pour importer les données
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# On importe tous les dfs transformés
from transform_WebScraping import df_result_WebScrap
from transform_API import df_result_API
from transform_BigData import df_result_BigData
from transform_CSV import df_result_CSV
from transform_SQLite import df_result_SQLite

# On fait une concaténation de tous les dfs
# On choisit uniquement les colonnes communes aux dfs si nécessaire
dfs_to_concat = [
    df_result_WebScrap,
    df_result_API,
    df_result_BigData,
    df_result_CSV,
    df_result_SQLite
]

# Pour éviter erreur sur colonnes non présentes, on peut faire union des colonnes
all_cols = set().union(*[df.columns for df in dfs_to_concat])
dfs_normalized = [df.reindex(columns=all_cols, fill_value="") for df in dfs_to_concat]

df_aggregated = pd.concat(dfs_normalized, ignore_index=True)
print(f"\n✓ DataFrames concaténés : {df_aggregated.shape[0]} lignes × {df_aggregated.shape[1]} colonnes")