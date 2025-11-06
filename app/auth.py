import jwt
import bcrypt
from datetime import datetime, timedelta
from app.config import Config
from typing import Dict, Any, Union

class AuthService:
    # Gestion du mot de passe
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Je hache un mot de passe en utilisant bcrypt.
        Je génère un salt unique et je retourne le hash encodé en UTF-8.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Je vérifie qu'un mot de passe correspond au hash enregistré.
        API retourne True si le mot de passe est correct, sinon False.
        """
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    @staticmethod
    def generate_token(user_id: int, username: str, role: str) -> str:
        """
        Je génère un JWT pour un utilisateur.
        Le token contient l'ID utilisateur, le username, le rôle, la date de création et l'expiration.
        """
        expiration = Config.JWT_EXPIRATION

        if isinstance(expiration, int):
            exp = datetime.utcnow() + timedelta(seconds=expiration)
        elif isinstance(expiration, timedelta):
            exp = datetime.utcnow() + expiration
        else:
            # fallback par défaut 1h
            exp = datetime.utcnow() + timedelta(hours=1)

        # Je prépare le payload avec toutes les informations nécessaires
        payload: Dict[str, Any] = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": exp
        }

        # Je code le token avec la clé secrète et HS256
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Je décode et vérifie un JWT.
        Je retourne un dict contenant "success" et soit "data" avec le payload, soit "error".
        """
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            # Je m'assure que le payload contient les champs essentiels
            if not all(k in payload for k in ("user_id", "username", "role")):
                return {"success": False, "error": "Payload JWT incomplet"}
            return {"success": True, "data": payload}
        except jwt.ExpiredSignatureError:
            # Le token est expiré
            return {"success": False, "error": "Token expiré. Reconnectez-vous."}
        except jwt.InvalidTokenError:
            # Le token n'est pas valide
            return {"success": False, "error": "Token invalide"}
        except Exception as e:
            # Toute autre erreur inattendue
            return {"success": False, "error": f"Erreur décodage token: {str(e)}"}
