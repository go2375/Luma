import jwt
import bcrypt
from datetime import datetime, timedelta
from app.config import Config
from typing import Union, Dict, Any

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hacher un mot de passe en utilisant bcrypt.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Vérifier qu'un mot de passe correspond à son hash.
        """
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    @staticmethod
    def generate_token(user_id: int, username: str, role: str) -> str:
        """
        Générer un JWT pour un utilisateur avec expiration.
        """
        expiration = Config.JWT_EXPIRATION
        if isinstance(expiration, int):
            exp = datetime.utcnow() + timedelta(seconds=expiration)
        elif isinstance(expiration, timedelta):
            exp = datetime.utcnow() + expiration
        else:
            exp = datetime.utcnow() + timedelta(hours=1)  # fallback 1h

        payload: Dict[str, Any] = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": exp
        }

        token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
        # jwt.encode peut retourner bytes selon la version
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Décoder et vérifier un JWT.
        Retourne un dict avec "success": bool et "data" ou "error".
        """
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            # Vérifie que les champs essentiels sont présents
            if not all(k in payload for k in ("user_id", "username", "role")):
                return {"success": False, "error": "Payload JWT incomplet"}
            return {"success": True, "data": payload}
        except jwt.ExpiredSignatureError:
            return {"success": False, "error": "Token expiré. Veuillez vous reconnecter."}
        except jwt.InvalidTokenError:
            return {"success": False, "error": "Token invalide"}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors du décodage du token: {str(e)}"}
