import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # SECRET_KEY pour JWT
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        print("Erreur : SECRET_KEY non définie. Veuillez définir votre SECRET_KEY.")
        sys.exit(1)

    # Base de données
    DATABASE_PATH: str = os.environ.get("DATABASE_PATH", "./bdd/bdd_connexion.sqlite")

    # Origines autorisées pour CORS
    raw_origins = os.environ.get("CORS_ORIGINS", "http://localhost:8500")
    if raw_origins.strip() == "":
        CORS_ORIGINS = []
    else:
        # Convertit la chaîne en liste et supprime les espaces superflus
        CORS_ORIGINS = [origin.strip() for origin in raw_origins.split(",")]

    # Durée de validité des tokens JWT
    JWT_EXPIRATION: timedelta = timedelta(hours=24)

    # Durée de conservation des utilisateurs inactifs (en jours)
    USER_RETENTION_DAYS: int = 365 * 3

    # Limitation du nombre maximum de tentatives de connexion
    MAX_LOGIN_ATTEMPTS: int = 5
