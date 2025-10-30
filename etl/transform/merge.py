import pandas as pd
import re
import os

# On importe des dataframes transformés
from transform_WebScraping import df_result_WebScrap
from transform_API import df_result_API
from transform_BigData import df_result_BigData
from transform_CSV import df_result_CSV
from transform_SQLite import df_result_SQLite

print("==============================================================================")
print(" Démarrage du merge final...")

# =====================================================================
# 1️⃣ RÉFÉRENCE PRINCIPALE : BigData
# =====================================================================
df_final = df_result_BigData.copy()

# Colonnes booléennes
bool_cols = ['est_activite', 'est_lieu']

# Initialisation et conversion booléenne
for col in bool_cols:
    if col not in df_final.columns:
        df_final[col] = 0
    df_final[col] = df_final[col].fillna(0).astype(int).astype(bool)

# Colonnes texte
text_cols = ['nom_site', 'nom_commune', 'nom_department']
for col in text_cols:
    if col in df_final.columns:
        df_final[col] = df_final[col].astype(str).str.strip()

print(f"Référence BigData : {df_final.shape[0]} lignes")

# =====================================================================
# 2️⃣ AJOUT DES LIGNES CSV
# =====================================================================
df_csv_to_add = df_result_CSV.copy()

# Initialisation et conversion booléenne
for col in bool_cols:
    if col not in df_csv_to_add.columns:
        df_csv_to_add[col] = 0
    df_csv_to_add[col] = df_csv_to_add[col].fillna(0).astype(int).astype(bool)

# Conserver uniquement les lignes avec nom_commune
df_csv_to_add = df_csv_to_add[df_csv_to_add['nom_commune'].astype(bool)].copy()

df_final = pd.concat([df_final, df_csv_to_add], ignore_index=True)
print(f"Après ajout CSV : {df_final.shape[0]} lignes")

# =====================================================================
# 3️⃣ AJOUT NOM_COMMUNE_BRETON DEPUIS WEBSCRAP
# =====================================================================
web_cols = df_result_WebScrap.columns.tolist()
if 'nom_commune' in web_cols and 'nom_commune_breton' in web_cols:
    df_web_breton = df_result_WebScrap[['nom_commune','nom_commune_breton','nom_department','nom_department_breton']].copy()
elif 'nom' in web_cols and 'nom_breton' in web_cols:
    df_web_breton = df_result_WebScrap[['nom','nom_breton','nom_department','nom_department_breton']].rename(
        columns={'nom':'nom_commune','nom_breton':'nom_commune_breton'}
    )
else:
    raise KeyError("Colonnes nom/nom_commune ou nom_breton/nom_commune_breton introuvables dans df_result_WebScrap")

df_final = pd.merge(
    df_final,
    df_web_breton[['nom_commune','nom_commune_breton']],
    on='nom_commune',
    how='left'
)
df_final['nom_commune_breton'] = df_final['nom_commune_breton'].fillna('')
print(f"Ajout nom_commune_breton terminé : {df_final['nom_commune_breton'].astype(bool).sum()} valeurs connues")

# =====================================================================
# 4️⃣ MISE À JOUR DEPUIS API
# =====================================================================
if 'code_insee' in df_final.columns and 'code_insee' in df_result_API.columns:
    df_final = pd.merge(df_final, df_result_API, on='code_insee', how='left', suffixes=('','_api'))
    for col in ['label_cite_caractere']:
        api_col = f"{col}_api"
        if api_col in df_final.columns:
            df_final[col] = df_final[col].fillna(df_final[api_col])
            df_final.drop(columns=[api_col], inplace=True, errors='ignore')
    print("Champs API mis à jour : 'label_cite_caractere'")

# =====================================================================
# 5️⃣ MISE À JOUR DEPUIS SQLITE
# =====================================================================
if 'code_insee' in df_final.columns and 'code_insee' in df_result_SQLite.columns:
    df_final = pd.merge(df_final, df_result_SQLite, on='code_insee', how='left', suffixes=('','_sqlite'))
    for col in ['nom_commune','nom_department']:
        sqlite_col = f"{col}_sqlite"
        if sqlite_col in df_final.columns:
            df_final[col] = df_final[col].fillna(df_final[sqlite_col])
            df_final.drop(columns=[sqlite_col], inplace=True, errors='ignore')
    print("Champs SQLite mis à jour : 'nom_commune' et 'nom_department'")

# =====================================================================
# 6️⃣ AJOUT DES DÉPARTEMENTS BRETONS
# =====================================================================
if 'nom_department_breton' in df_web_breton.columns:
    df_dept_bzh = df_web_breton[['nom_department','nom_department_breton']].drop_duplicates()
elif 'nom_department' in df_result_SQLite.columns:
    df_dept_bzh = df_result_SQLite[['nom_department','nom_department_breton']].drop_duplicates()
else:
    df_dept_bzh = pd.DataFrame(columns=['nom_department','nom_department_breton'])

if 'nom_department' in df_final.columns and not df_final['nom_department'].empty:
    df_final = pd.merge(df_final, df_dept_bzh, on='nom_department', how='left')
    df_final['nom_department_breton'] = df_final['nom_department_breton'].fillna('')
else:
    df_final['nom_department_breton'] = ''

print("Ajout nom_department_breton terminé.")

# =====================================================================
# 7️⃣ VÉRIFICATION DES DOUBLONS
# =====================================================================
duplicate_cols = ['nom_site','code_insee','latitude','longitude']
doublons = df_final[df_final.duplicated(subset=duplicate_cols, keep=False)]
print(f"🔎 {len(doublons)} doublons potentiels détectés")
if not doublons.empty:
    print(doublons.head(10))

# =====================================================================
# 8️⃣ NETTOYAGE FINAL
# =====================================================================
df_final = df_final.fillna('')
clean_text_cols = ['nom_site','nom_commune','nom_commune_breton','nom_department','nom_department_breton']
for col in clean_text_cols:
    df_final[col] = df_final[col].astype(str).str.strip()
df_final['code_insee'] = df_final['code_insee'].astype(str)
for col in bool_cols:
    df_final[col] = df_final[col].astype(bool)

print("\nAperçu final :")
print(df_final.head(10))
print(f"\nDataFrame final prêt pour l'insertion : {df_final.shape[0]} lignes")



# =====================================================================
# 9️⃣ SAUVEGARDE DU DF FINAL EN CSV
# =====================================================================


# Définir le chemin du CSV (dans le même dossier que le script ou à adapter)
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "transform"))
os.makedirs(output_dir, exist_ok=True)
csv_path = os.path.join(output_dir, "df_final_merge.csv")

# Sauvegarde
df_final.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\n DataFrame final sauvegardé en CSV : {csv_path}")
