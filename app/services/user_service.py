# J'importe le modèle UserModel pour interagir avec la table Utilisateur dans la base de données
from app.models import UserModel

class UserService:
    """
    Service métier pour gérer les utilisateurs.
    Je centralise ici toute la logique métier concernant les utilisateurs,
    séparant l'accès direct à la base de l'API.
    """
    @staticmethod
    def get_all():
        """
        Récupère tous les utilisateurs.
        Utile pour l'administration.
        """
        return UserModel.get_all()

    @staticmethod
    def get_by_id(user_id: int):
        """
        Récupère un utilisateur spécifique par son identifiant.
        user_id : identifiant unique de l'utilisateur
        """
        return UserModel.get_by_id(user_id)

    @staticmethod
    def get_by_username(username: str):
        """
        Récupère un utilisateur par son nom d'utilisateur.
        - username : string unique
        Cela permet notamment la vérification lors du login ou de l'inscription.
        """
        return UserModel.get_by_username(username)

    @staticmethod
    def create(username: str, password: str, role_id: int):
        """
        Crée un nouvel utilisateur.
        - username : nom de l'utilisateur
        - password : mot de passe en clair (sera hashé avant insertion)
        - role_id : rôle associé (1=admin, 2=visiteur, 3=prestataire, etc.)
        
        Je hache le mot de passe via AuthService pour la sécurité avant insertion.
        """
        from app.auth import AuthService
        password_hash = AuthService.hash_password(password)
        return UserModel.create(username, password_hash, role_id)

    @staticmethod
    def update(user_id: int, username: str = None, role_id: int = None):
        """
        Met à jour un utilisateur existant.
        - user_id : identifiant de l'utilisateur à mettre à jour
        - username : nouveau nom d'utilisateur (facultatif)
        - role_id : nouveau rôle (facultatif)
        
        Je ne mets à jour que les champs fournis pour éviter d'écraser
        les données existantes.
        """
        updates = {}
        if username:
            updates["username"] = username
        if role_id:
            updates["role_id"] = role_id
        return UserModel.update(user_id, **updates)

    @staticmethod
    def delete(user_id: int):
        """
        Supprime un utilisateur de la base.
        - user_id : identifiant de l'utilisateur à supprimer
        Retourne True si la suppression a réussi, False sinon.
        """
        return UserModel.delete(user_id)
