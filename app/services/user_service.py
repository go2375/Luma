from app.models import UserModel, RoleModel
from app.auth import AuthService
from app.anonymization import validate_and_fix_username, anonymize_username

class UserService:
    """Service gérant la logique métier liée aux utilisateurs."""

    # ===== Création utilisateur =====
    @staticmethod
    def create_user(username: str, password: str, role_id: int):
        """Créer un nouvel utilisateur avec validation du rôle et du username"""
        role = RoleModel.get_by_id(role_id)
        if not role:
            return {"success": False, "error": "Rôle introuvable"}

        safe_username = validate_and_fix_username(username)

        if UserModel.get_by_username(safe_username):
            return {"success": False, "error": "Nom d'utilisateur déjà existant"}

        password_hash = AuthService.hash_password(password)
        user = UserModel.create(safe_username, password_hash, role_id)

        if not user:
            return {"success": False, "error": "Erreur lors de la création de l'utilisateur"}

        return {"success": True, "user": user}

    # ===== Authentification =====
    @staticmethod
    def authenticate(username: str, password: str):
        """Vérifie les identifiants et retourne un token JWT"""
        user = UserModel.get_by_username(username)
        if not user or not AuthService.verify_password(password, user["password_hash"]):
            return {"success": False, "error": "Identifiants invalides"}

        role = RoleModel.get_by_id(user["role_id"])
        role_name = role["nom_role"] if role else "inconnu"

        token = AuthService.generate_token(
            user_id=user["user_id"],
            username=user["username"],
            role=role_name
        )

        return {"success": True, "user": user, "token": token}

    # ===== Changement mot de passe =====
    @staticmethod
    def update_password(user_id: int, new_password: str):
        """Modifier le mot de passe d’un utilisateur"""
        user = UserModel.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Utilisateur introuvable"}

        new_password_hash = AuthService.hash_password(new_password)
        success = UserModel.update_password(user_id, new_password_hash)

        if not success:
            return {"success": False, "error": "Échec de la mise à jour du mot de passe"}

        return {"success": True}

    # ===== Suppression / anonymisation =====
    @staticmethod
    def delete_account(user_id: int, anonymize: bool = True):
        """Anonymiser ou supprimer un compte utilisateur"""
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

    # ===== Récupération d’informations =====
    @staticmethod
    def get_user_info(user_id: int):
        """Récupérer les informations d’un utilisateur sans exposer le password_hash"""
        user = UserModel.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Utilisateur introuvable"}

        role = RoleModel.get_by_id(user["role_id"])
        role_name = role["nom_role"] if role else "inconnu"

        return {
            "success": True,
            "user": {
                "user_id": user["user_id"],
                "username": user["username"],
                "role": role_name,
                "role_id": user["role_id"],
                "anonymized": user.get("anonymized", 0),
                "created_at": user.get("created_at"),
                "updated_at": user.get("updated_at")
            }
        }
