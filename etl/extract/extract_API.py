import requests
import pandas as pd

# Dataset API
url = "https://data.bretagne.bzh/api/records/1.0/search/?dataset=petites-cites-de-caractere-en-bretagne&rows=100"

# Requête
response = requests.get(url)
response.raise_for_status()

data = response.json()

# Accéder à la liste des résultats
results = data['records'] if 'records' in data else data.get('results', [])

# Extraire code_insee et nom
extracted = []
for item in results:
    # Selon la structure de l'API, parfois les champs sont directement dans item['fields']
    fields = item.get('fields', item)  
    extracted.append({
        'code_insee': fields.get('code_insee', ''),
        'nom': fields.get('nom', '')
    })

# Conversion en DataFrame
df_API = pd.DataFrame(extracted)

# Affichage
print(df_API.head())
print(df_API)