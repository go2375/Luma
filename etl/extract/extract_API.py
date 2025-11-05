import requests
import pandas as pd
import os

# Je définis le chemin pour récuperer les données via API data_bretagne pour obtenir liste des communes ayant label petite cité de caractère
url = "https://data.bretagne.bzh/api/records/1.0/search/?dataset=petites-cites-de-caractere-en-bretagne&rows=100"

response = requests.get(url)
response.raise_for_status()

data = response.json()

# J'accède à la liste des résultats
results = data['records'] if 'records' in data else data.get('results', [])

# J'extrais le code_insee et les noms des communes
extracted = []
for item in results:
    fields = item.get('fields', item)  
    extracted.append({
        'code_insee': fields.get('code_insee', ''),
        'nom_commune': fields.get('nom', '')
    })

# Je convertis les données des communes en df_API
df_API = pd.DataFrame(extracted)

# J'affiche mon df_API
print(df_API.head())
print(df_API)

# Je crée un df_API_copy pour éviter les modifications du df original pour l'étape de la transformation
df_API_copy = df_API.copy(deep=True)

# Je sauvegarde le résultat en CSV
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(output_dir, exist_ok=True)
csv_path = os.path.join(output_dir, "df_API_extract_result.csv")

df_API_copy.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\n DataFrame df_API_copy sauvegardé en CSV : {csv_path}")