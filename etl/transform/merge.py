import pandas as pd
import os


# Je définis le chemin pour récuperer mes CSV de dataframes transformés

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

csv_WebScrap = os.path.join(base_dir, "df_WebScrap_transform_result.csv")
csv_API = os.path.join(base_dir, "df_API_transform_result.csv")
csv_BigData = os.path.join(base_dir, "df_BigData_transform_result.csv")
csv_CSV = os.path.join(base_dir, "df_CSV_transform_result.csv")
csv_SQLite = os.path.join(base_dir, "df_SQLite_transform_result.csv")


# 1. J'importe mes CSV
df_result_WebScrap = pd.read_csv(csv_WebScrap, dtype=str)
df_result_API = pd.read_csv(csv_API, dtype=str)
df_result_BigData = pd.read_csv(csv_BigData, dtype=str)
df_result_CSV = pd.read_csv(csv_CSV, dtype=str)
df_result_SQLite = pd.read_csv(csv_SQLite, dtype=str)

# Je valide encore une conversion de mes colonns booléennes
bool_cols = ['est_activite', 'est_lieu']
for df in [df_result_BigData, df_result_CSV]:
    for col in bool_cols:
        if col not in df.columns:
            df[col] = False
        else:
            df[col] = df[col].astype(str).str.strip().str.lower().replace(
                {'true': True, 'false': False, '1': True, '0': False}
            ).fillna(False).astype(bool)

print(" CSV transformés importés et booléens convertis")


# 2. Je définis comme ma référence principale le dataframe BigData

df_final = df_result_BigData.copy()
for col in ['nom_site', 'nom_commune', 'nom_department']:
    if col in df_final.columns:
        df_final[col] = df_final[col].astype(str).str.strip()

print(f"Référence BigData : {df_final.shape[0]} lignes")


# 3. J'ajoute le dataframe CSV

df_csv_to_add = df_result_CSV.copy()
for col in bool_cols:
    if col not in df_csv_to_add.columns:
        df_csv_to_add[col] = False
    else:
        df_csv_to_add[col] = df_csv_to_add[col].astype(str).str.strip().str.lower().replace(
            {'true': True, 'false': False, '1': True, '0': False}
        ).fillna(False).astype(bool)
df_csv_to_add = df_csv_to_add[df_csv_to_add['nom_commune'].astype(bool)].copy()
df_final = pd.concat([df_final, df_csv_to_add], ignore_index=True)
print(f"Après ajout CSV : {df_final.shape[0]} lignes")


# 4. J'ajoute le nom_commune_breton depuis mon dataframe WebScrap

web_cols = df_result_WebScrap.columns.tolist()
if 'nom_commune' in web_cols and 'nom_commune_breton' in web_cols:
    df_web_breton = df_result_WebScrap[['nom_commune', 'nom_commune_breton', 'nom_department', 'nom_department_breton']].copy()
elif 'nom' in web_cols and 'nom_breton' in web_cols:
    df_web_breton = df_result_WebScrap[['nom', 'nom_breton', 'nom_department', 'nom_department_breton']].rename(
        columns={'nom': 'nom_commune', 'nom_breton': 'nom_commune_breton'}
    )
else:
    df_web_breton = pd.DataFrame(columns=['nom_commune', 'nom_commune_breton', 'nom_department', 'nom_department_breton'])

df_final = df_final.merge(
    df_web_breton[['nom_commune', 'nom_commune_breton']],
    on='nom_commune',
    how='left'
)
df_final['nom_commune_breton'] = df_final['nom_commune_breton'].fillna('')
print(f"Ajout nom_commune_breton terminé : {df_final['nom_commune_breton'].astype(bool).sum()} valeurs connues")


# 5. Je fais mise à jour de mon dataframe final depuis mon dataframe API (label_cite_caractere)

if 'label_cite_caractere' in df_result_API.columns:
    df_result_API['label_cite_caractere'] = df_result_API['label_cite_caractere'].astype(str).str.strip().str.lower().replace(
        {'true': 1, 'false': 0, '1': 1, '0': 0}
    ).fillna(0).astype(int)
else:
    df_result_API['label_cite_caractere'] = 0

merge_cols = ['code_insee'] if 'code_insee' in df_final.columns and 'code_insee' in df_result_API.columns else ['nom_commune', 'nom_department']
df_final = df_final.merge(
    df_result_API[merge_cols + ['label_cite_caractere']],
    on=merge_cols,
    how='left'
)
df_final['label_cite_caractere'] = df_final['label_cite_caractere'].fillna(0).astype(int)
print(f"Champs API mis à jour : 'label_cite_caractere' ({df_final['label_cite_caractere'].sum()} communes labellisées)")


# 6. Je fais mise à jour de mon data frame final, df_final, en prenant en compte ma base de donnée source df_result_SQLite

if 'code_insee' in df_final.columns and 'code_insee' in df_result_SQLite.columns:
    df_final = df_final.merge(df_result_SQLite, on='code_insee', how='left', suffixes=('', '_sqlite'))
    for col in ['nom_commune', 'nom_department']:
        sqlite_col = f"{col}_sqlite"
        if sqlite_col in df_final.columns:
            df_final[col] = df_final[col].fillna(df_final[sqlite_col])
            df_final.drop(columns=[sqlite_col], inplace=True, errors='ignore')
    print("Champs SQLite mis à jour : 'nom_commune' et 'nom_department'")


# 7. J'ajoute le nom_department_breton à partir de mon df_result_WebScrap

df_dept_bzh = df_result_WebScrap[['nom_department', 'nom_department_breton']].drop_duplicates()
df_final = df_final.merge(
    df_dept_bzh,
    on='nom_department',
    how='left'
)
df_final['nom_department_breton'] = df_final['nom_department_breton'].fillna('').astype(str).str.strip()
print(f"Ajout nom_department_breton terminé : {df_final['nom_department_breton'].astype(bool).sum()} valeurs connues")


# 8. Je fais une nettoyage finale et je corrige mes variables created_at et updated_at
df_final = df_final.fillna('')
clean_text_cols = ['nom_site', 'nom_commune', 'nom_commune_breton', 'nom_department', 'nom_department_breton']
for col in clean_text_cols:
    if col in df_final.columns:
        df_final[col] = df_final[col].astype(str).str.strip()

for col in bool_cols:
    if col in df_final.columns:
        df_final[col] = df_final[col].astype(str).str.strip().str.lower().replace(
            {'true': True, 'false': False, '1': True, '0': False}
        ).fillna(False).astype(bool)

for ts_col in ['created_at', 'updated_at']:
    if ts_col not in df_final.columns:
        df_final[ts_col] = pd.Timestamp.now()
    else:
        df_final[ts_col] = pd.to_datetime(df_final[ts_col], errors='coerce').fillna(pd.Timestamp.now())

print("\nAperçu final :")
print(df_final.head())
print(f"\nDataFrame final prêt pour l'insertion : {df_final.shape[0]} lignes")


# 9. Je sauvegarde mon dataframe final en CSV

output_dir = os.path.join(base_dir, "..", "data")
os.makedirs(output_dir, exist_ok=True)
csv_path = os.path.join(output_dir, "df_aggregated_result.csv")
df_final.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\n DataFrame final sauvegardé en CSV : {csv_path}")
