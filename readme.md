# 🌿 Luméa — Plateforme de données touristiques de Bretagne

## 🧭 Présentation
Luméa centralise, nettoie et expose les données touristiques et culturelles de Bretagne.  
Sources : **API, CSV, MongoDB, SQLite, Web Scraping**.  
Les données sont accessibles via une **API REST sécurisée** (FastAPI), avec un socle évolutif pour un futur **module IA** et un **frontend interactif**.

---

## ⚙️ Stack technique
| Composant              | Technologie                    |
|------------------------|--------------------------------|
| Langage principal      | Python 3.12.3                  |
| Framework API          | FastAPI                        |
| Base de données        | SQLite 3                       |
| Conteneurisation       | Docker                         |
| Extraction Web         | Selenium, Requests             |
| Traitement données     | Pandas, NumPy, Matplotlib      |
| Sécurité               | PyJWT, bcrypt                  |
| Configuration          | Dotenv (.env)                  |
| Versioning             | Git / GitHub                   |

---

## 🏗️ Architecture générale
- **Extraction** : API, CSV, MongoDB, Web Scraping  
- **Transformation** : nettoyage, normalisation, agrégation  
- **Stockage** : SQLite relationnel (Merise MCD/MLD)  
- **API REST** : routes thématiques sécurisées par JWT et rôles  

---

## 🧩 Structure du projet
Lumea/
├── app/
│ ├── routes/ # Routes REST (users, sites, parcours, etc.)
│ ├── services/ # Services
│ ├── main.py # Point d'entrée FastAPI
│ ├── models.py
│ ├── auth.py
│ ├── anonymization.py
│ ├── config.py
│ ├── decorators.py
│ └── __init__.py
├── etl/
│ ├── data/ Données sources en CSV extraites et transformées
│ ├── extract/
│ │ ├── 
│ │ ├── 
│ │ ├── 
│ │ ├── 
│ │ └── 
│ ├── transform/
│ │ ├── 
│ │ ├── 
│ │ ├── 
│ │ ├── 
│ │ └── 
│ └── load/
│ │ └── 
│ ├── __init__.py
├── BigData_load.py
├── SQLite_load.py
├── MCD_MLD_Lumea.png
├── bdd_create.py
├── docker-compose.yml
├── requirements.txt
└── README.md


---

## 🔐 Sécurité et authentification
- Routes sensibles (POST, PUT, DELETE) protégées via `@token_required` et `@role_required`  
- Routes publiques (GET) accessibles sans authentification  
- Tokens JWT contiennent : `user_id`, `username`, `role`  
- Expiration configurable (par défaut 24h)  
- Hashage sécurisé des mots de passe avec bcrypt  

---

## 🚀 Installation et lancement
```bash
# Cloner le dépôt
git clone https://github.com/go2375/Lumea.git
cd Lumea

# Créer et activer l’environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/macOS

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
.env
# Modifier SECRET_KEY, JWT_EXPIRE_HOURS, DATABASE_URL

# Lancer docker my_mongo
sudo docker-compose up -d

# Lancer l’API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8081
```bash

L’API est accessible : http://127.0.0.1:8000/docs

## 🧠 Modèle de données
Basé sur Merise (MCD/MLD) avec intégrité référentielle.

**Entités principales :**
 - 'User' : id, username, password_hash, role_id, anonymized, created_at, updated_at, deleted_at
- 'Role' : id, nom_role (admin, visiteur, prestataire)
- 'Department' : id, nom, nom_breton
- 'Commune' : id, nom, nom_breton, code_insee, label_cite_caractere, department_id
- 'SiteTouristique' : id, nom, description, latitude, longitude, commune_id, prestataire_id, est_activite, est_lieu, anonymized, created_at, updated_at, deleted_at
- 'Parcours' : id, nom, createur_id, created_at, updated_at, deleted_at
- 'Parcours_Site' : id, parcours_id, site_id, ordre_visite (N:N, suppression en cascade, unique par site par parcours)

---

## 📊 Fonctionnalités principales
- Extraction multi-sources : API, CSV, MongoDB, Web Scraping, SQLite  
- Nettoyage, normalisation et agrégation des données avec Pandas, Seaborn et Matplotlib  
- Création automatique de la base SQLite  
- API REST complète (CRUD) : `/users`, `/roles`, `/sites`, `/parcours`, `/communes`, `/departements`
- Sécurisation JWT & gestion des rôles  
- Documentation interactive (Swagger UI / OpenAPI)  
- Suivi temporel : `created_at`, `updated_at`, `deleted_at`  

---

## 🔮 Améliorations et perspectives
- Relations prestataire–site many-to-many  
- Normalisation des attributs booléens en tables de référence  
- Suivi des logs et audit JWT  
- Optimisation du pipeline ETL  
- Frontend interactif (React/Streamlit) pour consultation et filtrage des données  
- Module IA de recommandations personnalisées (sites, parcours, activités)  

---

## 👨‍💻 Auteur
Projet Luméa — 2025  
Développé par https://github.com/go2375/

