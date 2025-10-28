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

# --- Lancer Chrome avec ChromeDriver géré automatiquement ---
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- URL de départ ---
url = "https://www.portdattache.bzh/dire-villes-bretagne-breton/"
driver.get(url)

# --- WebDriverWait pour attendre que la page soit chargée ---
wait = WebDriverWait(driver, 10)

# --- Liste pour stocker les données ---
data = []

# --- Attendre que les <li> soient présents ---
li_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li")))

for li in li_elements:
    try:
        text = li.text.strip()
        if ":" in text:  # Vérifie si le texte contient un département et sa traduction
            nom, nom_breton = map(str.strip, text.split(":", 1))
            data.append([nom, nom_breton])
    except Exception as e:
        print(f"Erreur lecture li: {e}")

# --- Fermer le navigateur ---
driver.quit()

# --- Convertir en DataFrame ---
df_WebScrap = pd.DataFrame(data, columns=["nom", "nom_breton"])

# --- Affichage des 10 premières lignes ---
pd.set_option('display.max_rows', 10)
print(df_WebScrap.head(10))
print(df_WebScrap)
print(f"Total lignes scrappées : {len(df_WebScrap)}")