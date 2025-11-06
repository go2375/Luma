# J'importe le modèle RoleModel qui gère les opérations SQL sur la table des rôles
from app.models import RoleModel

class RoleService:
    """
    Service métier pour gérer les rôles d'utilisateurs.
    Ici, je centralise toute la logique métier liée aux rôles,
    ce qui me permet de séparer la logique de la base de données (RoleModel)
    de la logique de présentation et des routes FastAPI.
    """
    @staticmethod
    def get_all():
        """
        Retourne la liste complète des rôles disponibles dans l'application.
        Cela me permet par exemple de récupérer les rôles pour vérifier les droits d'accès.
        """
        return RoleModel.get_all()

    @staticmethod
    def create(nom_role: str):
        """
        Crée un nouveau rôle dans la base de données.
        - nom_role : le nom du rôle à créer (ex : 'admin', 'visiteur', 'prestataire').
        Je renvoie le rôle créé pour que l'API ou l'admin puisse le visualiser directement.
        """
        return RoleModel.create(nom_role)

    @staticmethod
    def update(role_id: int, nom_role: str):
        """
        Met à jour le nom d'un rôle existant.
        - role_id : identifiant unique du rôle à modifier
        - nom_role : nouveau nom du rôle
        Retourne True si la mise à jour a réussi, False sinon.
        """
        return RoleModel.update(role_id, nom_role)

    @staticmethod
    def delete(role_id: int):
        """
        Supprime un rôle existant dans la base de données.
        - role_id : identifiant unique du rôle à supprimer
        Retourne True si la suppression a réussi, False sinon.
        Cette opération peut être utilisée par un admin pour nettoyer des rôles obsolètes.
        """
        return RoleModel.delete(role_id)
