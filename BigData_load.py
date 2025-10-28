import pandas as pd
import json
from pymongo import MongoClient

# Je définis mon chemin pour récuperer mes données Big Data
csv_path = os.path.join(os.path.dirname(__file__), "./db/BigData_source.csv")

# Permet une connexion avec mon MongoDB de mes POIs (de mes Points of Interest)
client = MongoClient('mongodb://localhost:27017/')
db = client.POI
POI_collection = db.Points