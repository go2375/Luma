import os
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Permet de définir les options Chrome
options = Options()
options.add_argument("--headless")  # mode invisible
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

# Permet de lancer Chrome avec ChromeDriver géré automatiquement
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# On définit URL pour le webscraper
url = "https://www.portdattache.bzh/dire-villes-bretagne-breton/"
driver.get(url)

# Permet d'utiliser WebDriverWait pour attendre que la page soit chargée
wait = WebDriverWait(driver, 10)

# Permet de créer une liste pour stocker les données
data = []

# Permet d'attendre que les <li> soient présents
li_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li")))

for li in li_elements:
    try:
        text = li.text.strip()
        # On vérifie si le texte contient un nom et sa traduction en breton
        if ":" in text:
            nom, nom_breton = map(str.strip, text.split(":", 1))
            data.append([nom, nom_breton])
    except Exception as e:
        print(f"Erreur lecture li: {e}")

# Permet de fermer le navigateur
driver.quit()

# Permet de convertir nos données en df_WebScrap
df_WebScrap = pd.DataFrame(data, columns=["nom", "nom_breton"])

# Permet d'afficher rapidement les résultats afin de les vérifier
pd.set_option('display.max_rows', 10)
print(df_WebScrap.head(10))
print(df_WebScrap)
print(f"Total lignes scrappées : {len(df_WebScrap)}")

# On créer un df_WebScrap_copy pour éviter les modifications du df original pour transform
df_WebScrap_copy = df_WebScrap.copy(deep=True)

# On sauvegarde le résultat en CSV
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(output_dir, exist_ok=True)
csv_path = os.path.join(output_dir, "df_WebScrap_extract_result.csv")

df_WebScrap_copy.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\n DataFrame df_WebScrap_copy sauvegardé en CSV : {csv_path}")