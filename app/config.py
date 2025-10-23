import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # SECRET_KEY pour JWT
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        print("Erreur : SECRET_KEY non définie. Veuillez définir votre SECRET_KEY.")
        sys.exit(1)
    
    # Base de données
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "./bdd/bdd_connexion.sqlite")

    # CORS pour Streamlit local et production
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:8501').split(',')

    # Durée de validité des tokens JWT
    JWT_EXPIRATION = timedelta(hours=24)

    # Durée de conservation des utilisateurs inactifs (en jours)
    USER_RETENTION_DAYS = 365 * 3

    # Limiter le nombre maximum de tentatives de connexion pour assurer la sécurité côté login
    MAX_LOGIN_ATTEMPTS = 5   