from app.models import RoleModel, UserModel

# ===== Service de gestion des rôles =====
class RoleService:
    # Liste des rôles système qui ne peuvent pas être modifiés ou supprimés
    SYSTEM_ROLES = ["admin", "visiteur", "prestataire"]

    @staticmethod
    def get_all_roles(user_id: int = None):
        """
        Récupère tous les rôles.
        Si user_id est fourni, vérifie que l'utilisateur existe (login/token valide).
        """
        if user_id and not UserModel.get_by_id(user_id):
            return {"success": False, "error": "Utilisateur introuvable ou token invalide"}
        try:
            roles = RoleModel.get_all()
            return {"success": True, "roles": roles}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la récupération des rôles: {str(e)}"}

    @staticmethod
    def get_role_by_id(role_id: int, user_id: int = None):
        """
        Récupère un rôle spécifique par son ID.
        Vérifie l'utilisateur si user_id fourni.
        """
        if user_id and not UserModel.get_by_id(user_id):
            return {"success": False, "error": "Utilisateur introuvable ou token invalide"}

        role = RoleModel.get_by_id(role_id)
        if not role:
            return {"success": False, "error": "Rôle introuvable"}

        return {"success": True, "role": role}

    @staticmethod
    def create_role(nom_role: str, user_id: int = None):
        """
        Crée un nouveau rôle.
        Vérifie l'utilisateur et valide le nom du rôle.
        """
        if user_id and not UserModel.get_by_id(user_id):
            return {"success": False, "error": "Utilisateur introuvable ou token invalide"}

        if not nom_role or not nom_role.strip():
            return {"success": False, "error": "Le nom du rôle ne peut pas être vide"}

        try:
            role = RoleModel.create(nom_role.strip())
            return {"success": True, "role": role}
        except Exception:
            return {"success": False, "error": "Ce rôle existe déjà"}

    @staticmethod
    def update_role(role_id: int, nom_role: str, user_id: int = None):
        """
        Modifie le nom d'un rôle existant.
        Vérifie l'utilisateur, l'existence du rôle et que ce n'est pas un rôle système.
        """
        if user_id and not UserModel.get_by_id(user_id):
            return {"success": False, "error": "Utilisateur introuvable ou token invalide"}

        role = RoleModel.get_by_id(role_id)
        if not role:
            return {"success": False, "error": "Rôle introuvable"}

        if not nom_role or not nom_role.strip():
            return {"success": False, "error": "Le nom du rôle ne peut pas être vide"}

        if role["nom_role"] in RoleService.SYSTEM_ROLES:
            return {"success": False, "error": "Impossible de modifier un rôle système"}

        success = RoleModel.update(role_id, nom_role.strip())
        return {"success": success, "error": None if success else "Échec de la mise à jour"}

    @staticmethod
    def delete_role(role_id: int, user_id: int = None):
        """
        Supprime un rôle.
        Vérifie l'utilisateur, l'existence du rôle et que ce n'est pas un rôle système.
        """
        if user_id and not UserModel.get_by_id(user_id):
            return {"success": False, "error": "Utilisateur introuvable ou token invalide"}

        role = RoleModel.get_by_id(role_id)
        if not role:
            return {"success": False, "error": "Rôle introuvable"}

        if role["nom_role"] in RoleService.SYSTEM_ROLES:
            return {"success": False, "error": "Impossible de supprimer un rôle système"}

        success = RoleModel.delete(role_id)
        return {"success": success, "error": None if success else "Échec de la suppression (utilisateurs associés)"}
