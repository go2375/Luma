import jwt
import bcrypt
from datetime import datetime, timedelta
from app.config import Config

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hacher un mot de passe en utilisant bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Vérifier qu'un mot de passe correspond à son hash."""
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    @staticmethod
    def generate_token(user_id: int, username: str, role: str) -> str:
        """Générer un JWT pour un utilisateur."""
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + Config.JWT_EXPIRATION if isinstance(Config.JWT_EXPIRATION, timedelta) else datetime.utcnow() + timedelta(seconds=Config.JWT_EXPIRATION)
        }
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
        # jwt.encode peut retourner un bytes selon la version => on force str
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token

    @staticmethod
    def decode_token(token: str) -> dict:
        """Décoder et vérifier un JWT."""
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            return {"success": True, "data": payload}
        except jwt.ExpiredSignatureError:
            return {"success": False, "error": "Token expiré. Veuillez vous reconnecter."}
        except jwt.InvalidTokenError:
            return {"success": False, "error": "Token invalide"}
        except Exception as e:
            # Cas général pour attraper d'autres erreurs
            return {"success": False, "error": f"Erreur lors du décodage du token: {str(e)}"}
