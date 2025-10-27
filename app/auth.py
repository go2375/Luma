# On importe la bibliothèque pour encoder et décoder les tokens
import jwt
# Permet de hasher les mots de passe
import bcrypt
# Permet de gérer les dates et les durées pour l’expiration des tokens
from datetime import datetime, timedelta
from app.config import Config

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        # Permet de générer un salt (sel) aléatoire
        salt = bcrypt.gensalt()
        # Permet de hacher le mot de passe avec le salt et ensuite encode('utf-8') convertit le texte en bytes, 
        # car bcrypt ne travaille pas directement avec des strings. Finalement, decode('utf-8') reconvertit en string pour stocker en bdd SQLite.
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    # Permet de vérifier si un mot de passe correspond à son hash
    def verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            password_hash.encode('utf-8')
        )
    
    @staticmethod
    # Permet de générer un token JWT pour un utilisateur
    def generate_token(user_id: int, username: str, role: str) -> str:
        # Permet de créer le payload, les données, du token
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            # Permet de créer une date d'expiration
            'exp': datetime.utcnow() + Config.JWT_EXPIRATION,  
            # Permet de créer une date de création
            'iat': datetime.utcnow()
        }
        
        # Permet d'encoder le payload avec la clé secrète
        return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    # Permet de décoder et vérifier un token JWT
    def decode_token(token: str) -> dict:
        try:
            # Décoder le token
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            return {'success': True, 'data': payload}
        except jwt.ExpiredSignatureError:
            # Token expiré
            return {'success': False, 'error': 'Token expiré. Veuillez vous reconnecter.'}
        except jwt.InvalidTokenError:
            # Token invalide
            return {'success': False, 'error': 'Token invalide'}