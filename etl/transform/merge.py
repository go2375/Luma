import pandas as pd
import os

def merge_dataframes(df_WebScrap=None, df_API=None, df_BigData=None, df_CSV=None, df_SQLite=None):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    # Mes chemins pour mes CSV de dfs transformés
    csv_WebScrap = os.path.join(base_dir, "df_WebScrap_transform_result.csv")
    csv_API = os.path.join(base_dir, "df_API_transform_result.csv")
    csv_BigData = os.path.join(base_dir, "df_BigData_transform_result.csv")
    csv_CSV = os.path.join(base_dir, "df_CSV_transform_result.csv")
    csv_SQLite = os.path.join(base_dir, "df_SQLite_transform_result.csv")

    # 1. Je m'assure que l'import du CSV pour chaque df est bien défini
    if df_WebScrap is None:
        df_WebScrap = pd.read_csv(csv_WebScrap, dtype=str)
    if df_API is None:
        df_API = pd.read_csv(csv_API, dtype=str)
    if df_BigData is None:
        df_BigData = pd.read_csv(csv_BigData, dtype=str)
    if df_CSV is None:
        df_CSV = pd.read_csv(csv_CSV, dtype=str)
    if df_SQLite is None:
        df_SQLite = pd.read_csv(csv_SQLite, dtype=str)

    # Je gére la conversion de colonnes booléennes
    bool_cols = ['est_activite', 'est_lieu']
    for df in [df_BigData, df_CSV]:
        for col in bool_cols:
            if col not in df.columns:
                df[col] = False
            else:
                df[col] = df[col].astype(str).str.strip().str.lower().replace(
                    {'true': True, 'false': False, '1': True, '0': False}
                ).fillna(False)
                df[col] = df[col].infer_objects(copy=False).astype(bool)

    # Je gére ma colonne anonymized
    for df_copy in [df_BigData, df_CSV]:
        if 'anonymized' not in df_copy.columns:
            df_copy['anonymized'] = 0
        else:
            df_copy['anonymized'] = df_copy['anonymized'].astype(int)

    # 2. Je prends comme ma référence principale BigData
    df_final = df_BigData.copy()
    for col in ['nom_site', 'nom_commune', 'nom_department']:
        if col in df_final.columns:
            df_final[col] = df_final[col].astype(str).str.strip()

    # 3. J'ajoute des données à partir du fichier CSV
    df_CSV_copy = df_CSV.copy()
    for col in bool_cols:
        if col not in df_CSV_copy.columns:
            df_CSV_copy[col] = False
        else:
            df_CSV_copy[col] = df_CSV_copy[col].astype(str).str.strip().str.lower().replace(
                {'true': True, 'false': False, '1': True, '0': False}
            ).fillna(False)
            df_CSV_copy[col] = df_CSV_copy[col].infer_objects(copy=False).astype(bool)
    
    df_CSV_copy = df_CSV_copy[df_CSV_copy['nom_commune'].astype(bool)]
    df_final = pd.concat([df_final, df_CSV_copy], ignore_index=True)

    # 4. J'effectue la mise à jour de données en prenant mon df API (pour mon label_cite_caractere)

    if 'label_cite_caractere' in df_API.columns:
        df_API['label_cite_caractere'] = df_API['label_cite_caractere'].astype(str).str.strip().str.lower().replace(
            {'true': 1, 'false': 0, '1': 1, '0': 0}
        ).fillna(0).astype(int)
    else:
        df_API['label_cite_caractere'] = 0

    merge_cols = ['code_insee'] if 'code_insee' in df_final.columns and 'code_insee' in df_API.columns else ['nom_commune', 'nom_department']

    df_final = df_final.drop(columns=['label_cite_caractere'], errors='ignore')
    df_final = df_final.merge(
        df_API[merge_cols + ['label_cite_caractere']],
        on=merge_cols,
        how='left'
    )
    df_final['label_cite_caractere'] = df_final['label_cite_caractere'].fillna(0).astype(int)


    # 5. J'effectue la mise à jour de mon df_final en prenant mon df SQLite (avec: nom_commune, nom_department)
    if 'code_insee' in df_final.columns and 'code_insee' in df_SQLite.columns:
        df_final = df_final.merge(df_SQLite, on='code_insee', how='left', suffixes=('', '_sqlite'))
        for col in ['nom_commune', 'nom_department']:
            sqlite_col = f"{col}_sqlite"
            if sqlite_col in df_final.columns:
                df_final[col] = df_final[col].fillna(df_final[sqlite_col])
                df_final.drop(columns=[sqlite_col], inplace=True, errors='ignore')

    # 6. J'ajoute des noms des communes et des départments en breton depuis mon df WebScrap
    # nom_commune_breton
    if 'nom_commune' in df_WebScrap.columns and 'nom_commune_breton' in df_WebScrap.columns:
        df_web_breton = df_WebScrap[['nom_commune', 'nom_commune_breton']].copy()
        
        # nom_department_breton
        if 'nom_department' in df_WebScrap.columns and 'nom_department_breton' in df_WebScrap.columns:
            df_dept_bzh = df_WebScrap[['nom_department', 'nom_department_breton']].drop_duplicates()
        else:
            df_dept_bzh = pd.DataFrame(columns=['nom_department', 'nom_department_breton'])
            
    elif 'nom' in df_WebScrap.columns and 'nom_breton' in df_WebScrap.columns:
        df_web_breton = df_WebScrap[['nom', 'nom_breton']].rename(
            columns={'nom': 'nom_commune', 'nom_breton': 'nom_commune_breton'}
        )
        df_dept_bzh = pd.DataFrame(columns=['nom_department', 'nom_department_breton'])
    else:
        df_web_breton = pd.DataFrame(columns=['nom_commune', 'nom_commune_breton'])
        df_dept_bzh = pd.DataFrame(columns=['nom_department', 'nom_department_breton'])

    # Voici merge pour nom_commune_breton
    if not df_web_breton.empty and 'nom_commune' in df_final.columns:
        df_final = df_final.merge(
            df_web_breton[['nom_commune', 'nom_commune_breton']],
            on='nom_commune',
            how='left'
        )
        df_final['nom_commune_breton'] = df_final['nom_commune_breton'].fillna('')
    elif 'nom_commune_breton' not in df_final.columns:
        df_final['nom_commune_breton'] = ''

    # Voici merge pour nom_department_breton
    if not df_dept_bzh.empty and 'nom_department' in df_final.columns:
        df_final = df_final.merge(df_dept_bzh, on='nom_department', how='left')
        df_final['nom_department_breton'] = df_final['nom_department_breton'].fillna('').astype(str).str.strip()
    elif 'nom_department_breton' not in df_final.columns:
        df_final['nom_department_breton'] = ''

    # 7. J'effectue une nettoyage final
    df_final = df_final.fillna('')
    clean_text_cols = ['nom_site', 'nom_commune', 'nom_commune_breton', 'nom_department', 'nom_department_breton']
    for col in clean_text_cols:
        if col in df_final.columns:
            df_final[col] = df_final[col].astype(str).str.strip()

    for col in bool_cols:
        if col in df_final.columns:
            df_final[col] = df_final[col].astype(str).str.strip().str.lower().replace(
                {'true': True, 'false': False, '1': True, '0': False}
            ).fillna(False)
            df_final[col] = df_final[col].infer_objects(copy=False).astype(bool)  # FIX

    for ts_col in ['created_at', 'updated_at']:
        if ts_col not in df_final.columns:
            df_final[ts_col] = pd.Timestamp.now()
        else:
            df_final[ts_col] = pd.to_datetime(df_final[ts_col], errors='coerce').fillna(pd.Timestamp.now())

    # 8. Je sauvegarde mon df_final en CSV df_aggregated_result
    output_dir = os.path.join(base_dir, "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "df_aggregated_result.csv")
    df_final.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"DataFrame final sauvegardé : {csv_path}, {df_final.shape[0]} lignes")
    
    return csv_path

if __name__ == "__main__":
    merge_dataframes()