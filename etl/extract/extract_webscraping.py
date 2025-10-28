import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://www.geobreizh.bzh/nom-des-villes-bretonnes-en-breton/?page={}"

all_data = []

# Permet de faire du webscraping des 71 pages, pages de 1 à 71 
for page in range(1, 72):
    print(f"Scraping page {page}")
    url = BASE_URL.format(page)
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "html.parser")
    
    rows = soup.find_all("tr", class_=lambda c: c and c.startswith("rown"))

    for row in rows:
        td1 = row.find("td", class_="column-1")
        td2 = row.find("td", class_="column-2")
        td3 = row.find("td", class_="column-3")
        if td1 and td2 and td3:
            all_data.append({
                "nom_commune": td1.text.strip(),
                "nom_commune_breton": td2.text.strip(),
                "code_department": int(td3.text.strip())
            })
            
    time.sleep(1)

# Pour visualiser un exemple
print(all_data[:5])

df = pd.DataFrame(all_data)
print(df.head())