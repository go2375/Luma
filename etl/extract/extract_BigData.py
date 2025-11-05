import pandas as pd
from pymongo import MongoClient
import os

# Je configure ma connexion à MongoDB
MONGO_URI = "mongodb://isen:isen@localhost:27017/POI?authSource=admin"
DB_NAME = "POI"
COLLECTION_NAME = "Points"

# Je gère ma connexion à MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# J'extrais les documents de ma base MongoDB
cursor = collection.find()

# Je transforme ces documents en liste de dictionnaires
data = list(cursor)

# Je crée mon df_BigData
df_BigData = pd.DataFrame(data)

# J'affiche les 5 premières lignes de mon df_BigData
print(df_BigData.columns)
pd.set_option('display.max_columns', None)
print(df_BigData.head())

# Je crée un df_BigData_copy pour éviter les modifications du df original pour l'étape de la transformation
df_BigData_copy = df_BigData.copy(deep=True)

# Je sauvegarde le résultat en CSV
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(output_dir, exist_ok=True)
csv_path = os.path.join(output_dir, "df_BigData_extract_result.csv")

df_BigData_copy.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\n DataFrame df_BigData_copy sauvegardé en CSV : {csv_path}")