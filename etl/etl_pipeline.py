"""
etl_pipeline.py
Orchestre l'ensemble du processus ETL :
1. Extract
2. Transform
3. Merge
4. Load
"""

import os
import sys
import pandas as pd

# -----------------------
# Configuration des chemins
# -----------------------
base_dir = os.path.dirname(__file__)
sys.path.extend([
    os.path.join(base_dir, "extract"),
    os.path.join(base_dir, "transform"),
    os.path.join(base_dir, "load")
])
data_dir = os.path.join(base_dir, "data")
os.makedirs(data_dir, exist_ok=True)

print("\n--- ETAPE 1 : EXTRACTION ---\n")

# ======== Extract API ========
try:
    from extract_API import df_API_copy
except Exception as e:
    print("Extraction API échouée :", e)
    api_path = os.path.join(data_dir, "df_API_extract_result.csv")
    if os.path.exists(api_path):
        df_API_copy = pd.read_csv(api_path, encoding='utf-8-sig')
        print(f"Chargement du CSV existant pour API : {api_path}")
    else:
        df_API_copy = pd.DataFrame()
        print("Aucun CSV API disponible, création d'un DataFrame vide")

# ======== Extract BigData ========
try:
    from extract_BigData import df_BigData_copy
except Exception as e:
    print("Extraction BigData échouée :", e)
    big_path = os.path.join(data_dir, "df_BigData_extract_result.csv")
    if os.path.exists(big_path):
        df_BigData_copy = pd.read_csv(big_path, encoding='utf-8-sig')
        print(f"Chargement du CSV existant pour BigData : {big_path}")
    else:
        df_BigData_copy = pd.DataFrame()
        print("Aucun CSV BigData disponible, création d'un DataFrame vide")

# ======== Extract SQLite ========
try:
    from extract_SQLite import df_SQLite_copy
except Exception as e:
    print("Extraction SQLite échouée :", e)
    sqlite_path = os.path.join(data_dir, "df_SQLite_extract_result.csv")
    if os.path.exists(sqlite_path):
        df_SQLite_copy = pd.read_csv(sqlite_path, encoding='utf-8-sig')
        print(f"Chargement du CSV existant pour SQLite : {sqlite_path}")
    else:
        df_SQLite_copy = pd.DataFrame()
        print("Aucun CSV SQLite disponible, création d'un DataFrame vide")

# ======== Extract CSV ========
try:
    from extract_CSV import df_CSV_copy
except Exception as e:
    print("Extraction CSV échouée :", e)
    csv_path = os.path.join(data_dir, "df_CSV_extract_result.csv")
    if os.path.exists(csv_path):
        df_CSV_copy = pd.read_csv(csv_path, encoding='utf-8-sig')
        print(f"Chargement du CSV existant pour CSV : {csv_path}")
    else:
        df_CSV_copy = pd.DataFrame()
        print("Aucun CSV CSV disponible, création d'un DataFrame vide")

# ======== Extract WebScrap ========
try:
    from extract_WebScrap import df_WebScrap_copy
except Exception as e:
    print("WebScraping échoué :", e)
    web_path = os.path.join(data_dir, "df_WebScrap_extract_result.csv")
    if os.path.exists(web_path):
        df_WebScrap_copy = pd.read_csv(web_path, encoding='utf-8-sig')
        print(f"Chargement du CSV existant pour WebScrap : {web_path}")
    else:
        df_WebScrap_copy = pd.DataFrame()
        print("Aucun CSV WebScrap disponible, création d'un DataFrame vide")

# Sauvegardes d’extraction
df_SQLite_copy.to_csv(os.path.join(data_dir, "df_SQLite_extract_result.csv"), index=False, encoding='utf-8-sig')
df_CSV_copy.to_csv(os.path.join(data_dir, "df_CSV_extract_result.csv"), index=False, encoding='utf-8-sig')
df_WebScrap_copy.to_csv(os.path.join(data_dir, "df_WebScrap_extract_result.csv"), index=False, encoding='utf-8-sig')
print("Extraction terminée ")

# -----------------------
# 2. TRANSFORMATION
# -----------------------
print("\n--- ETAPE 2 : TRANSFORMATION ---\n")

from transform_API import EDA_data_API
from transform_BigData import EDA_data_BigData
from transform_SQLite import EDA_data_SQLite
from transform_CSV import EDA_data_CSV
from transform_WebScraping import EDA_data_WebScrap

try:
    df_API_transformed = EDA_data_API(df_API_copy)
    df_BigData_transformed = EDA_data_BigData(df_BigData_copy)
    df_SQLite_transformed = EDA_data_SQLite(df_SQLite_copy)
    df_CSV_transformed = EDA_data_CSV(df_CSV_copy)
    df_WebScrap_transformed = EDA_data_WebScrap(df_WebScrap_copy)
    print("Transformation terminée ")
except Exception as e:
    print("Erreur pendant la transformation :", e)
    df_API_transformed = df_BigData_transformed = df_SQLite_transformed = df_CSV_transformed = df_WebScrap_transformed = pd.DataFrame()

# -----------------------
# 3. MERGE
# -----------------------
print("\n--- ETAPE 3 : MERGE ---\n")

from merge import merge_dataframes
try:
    df_merged = merge_dataframes(
        df_API_transformed,
        df_BigData_transformed,
        df_SQLite_transformed,
        df_CSV_transformed,
        df_WebScrap_transformed
    )
    print("Fusion des DataFrames terminée ")
except Exception as e:
    print("Erreur pendant le merge :", e)
    df_merged = pd.DataFrame()

# -----------------------
# 4. LOAD
# -----------------------
print("\n--- ETAPE 4 : LOAD ---\n")

from bdd_create_and_load_to_SQLite import load_to_sqlite

try:
    load_to_sqlite(df_merged)
    print("Chargement dans SQLite terminé ")
except Exception as e:
    print("Erreur pendant le chargement :", e)

print("\n--- PIPELINE COMPLET --- ")