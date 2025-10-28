import os
import csv
import json
from datetime import datetime, timezone
from pymongo import MongoClient

# Permet de configurer MongoDB
MONGO_URI = "mongodb://isen:isen@localhost:27017/POI?authSource=admin"
DB_NAME = "POI"
COLLECTION_NAME = "Points"

# Je définis mon chemin pour récuperer mes données Big Data
input_csv_path = os.path.join(os.path.dirname(__file__), "./db_source/BigData_source.csv")

# --- Connexion à MongoDB ---
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# --- Lecture CSV et insertion directe dans MongoDB ---
count = 0
with open(input_csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        point = {
            "nom_site": row["Nom_du_POI"],
            "type_site": row.get("Categories_de_POI"),
            "description": row.get("Description"),
            "localisation": {
                "latitude": float(row["Latitude"]) if row.get("Latitude") else None,
                "longitude": float(row["Longitude"]) if row.get("Longitude") else None
            },
            "nom_commune": row.get("Code_postal_et_commune"),
            "updated_at": (
                datetime.strptime(row["Date_de_mise_a_jour"], "%Y-%m-%d")
                .astimezone(timezone.utc)
                .isoformat()
                if row.get("Date_de_mise_a_jour") else datetime.now(timezone.utc).isoformat()
            )
        }

        collection.insert_one(point)
        count += 1

print(f"{count} documents insérés dans la collection '{COLLECTION_NAME}' de la base '{DB_NAME}'.")