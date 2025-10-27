from app.models import UserModel, RoleModel
from app.auth import AuthService
from app.anonymization import validate_and_fix_username, anonymize_username

# Permet de créer un service de gestion des utilisateurs
class UserService:
    @staticmethod
    # Permet de créer un nouvel utilisateur
    def create_user(username: str, password: str, role_id: int):
        # On vérifie que le rôle existe
        role = RoleModel.get_by_id(role_id)
        if not role:
            return {"success": False, "error": "Rôle introuvable"}
        
        # On valide et sécurise le username
        safe_username = validate_and_fix_username(username)
        
        # On vérifie si le username existe déjà
        if UserModel.get_by_username(safe_username):
            return {"success": False, "error": "Username déjà existant"}
        
        # On hache le mot de passe
        password_hash = AuthService.hash_password(password)
        
        # On créer l'utilisateur
        user = UserModel.create(safe_username, password_hash, role_id)
        
        return {"success": True, "user": user}
    
    @staticmethod
    # Permet d'authentifier un utilisateur
    def authenticate(username: str, password: str):
        # On récupère l'utilisateur
        user = UserModel.get_by_username(username)
        
        if not user or not AuthService.verify_password(password, user["password_hash"]):
            return {"success": False, "error": "Identifiants invalides"}
                      
        # On génère le token JWT
        token = AuthService.generate_token(
            user_id=user["user_id"],
            username=user["username"],
            role=user["nom_role"]
        )
        
        return {"success": True, "user": user, "token": token}
    
    # Permet de modifier le mot de passe d'un utilisateur
    @staticmethod
    def update_password(user_id: int, new_password: str):
        # On récupère l'utilisateur
        user = UserModel.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Utilisateur introuvable"}
            
        # On hache le nouveau mot de passe
        new_password_hash = AuthService.hash_password(new_password)
        
        # On effectue une mise à jour
        success = UserModel.update_password(user_id, new_password_hash)
        
        return {"success": success, "error": None if success else "Échec de la mise à jour"}
    
    @staticmethod
    # Permet d’anonymiser ou de marquer comme supprimé le compte d’un utilisateur
    def delete_account(user_id: int, anonymize: bool = True):
        # On récupère l’utilisateur depuis la base de données
        user = UserModel.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Utilisateur introuvable"}
        
        if anonymize:
            new_username = anonymize_username(user_id)
            return {
                "success": True,
                "method": "anonymized",
                "new_username": new_username,
                "message": "Compte anonymisé"
            }

        success = UserModel.delete(user_id)
        return {
            "success": success,
            "method": "deleted" if success else None,
            "message": "Compte supprimé" if success else "Échec de la suppression"
        }

    @staticmethod
    # Permet de récupérer les informations d'un utilisateur sans le password_hash
    def get_user_info(user_id: int):
        user = UserModel.get_by_id(user_id)
        if not user:
            return None
        
        # On retourne les informations d'un utilisateur sans le password_hash
        return {
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["nom_role"],
            "role_id": user["role_id"],
            "anonymized": user.get("anonymized", 0),
            "created_at": user.get("created_at"),
            "updated_at": user.get("updated_at")
        }