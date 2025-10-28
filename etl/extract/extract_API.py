import requests
import pandas as pd

# Je définis le chemin pour récuperer les données via API data_bretagne pour obtenir liste des communes ayant label petite cité de caractère
url = "https://data.bretagne.bzh/api/records/1.0/search/?dataset=petites-cites-de-caractere-en-bretagne&rows=100"

response = requests.get(url)
response.raise_for_status()

data = response.json()

# Permet d'accéder à la liste des résultats
results = data['records'] if 'records' in data else data.get('results', [])

# Permet d'extraire code_insee et nom des communes
extracted = []
for item in results:
    fields = item.get('fields', item)  
    extracted.append({
        'code_insee': fields.get('code_insee', ''),
        'nom': fields.get('nom', '')
    })

# Permet de convertir des données des communes en df_API
df_API = pd.DataFrame(extracted)

# Permet une affichage rapide de mon df_API
print(df_API.head())
print(df_API)