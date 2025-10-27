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
            return None
        
        # On valide et sécurise le username
        safe_username = validate_and_fix_username(username)
        
        # On vérifie si le username existe déjà
        if UserModel.get_by_username(safe_username):
            return None
        
        # On hache le mot de passe
        password_hash = AuthService.hash_password(password)
        
        # On créer l'utilisateur
        user = UserModel.create(safe_username, password_hash, role_id)
        
        return user
    
    @staticmethod
    # Permet d'authentifier un utilisateur
    def authenticate(username: str, password: str):
        # On récupère l'utilisateur
        user = UserModel.get_by_username(username)
        
        if not user:
            return {'success': False, 'error': 'Identifiants invalides'}
        
        # On vérifie le mot de passe
        if not AuthService.verify_password(password, user['password_hash']):
            return {'success': False, 'error': 'Identifiants invalides'}
        
        # On génère le token JWT
        token = AuthService.generate_token(
            user_id=user['user_id'],
            username=user['username'],
            role=user['nom_role']
        )
        
        return {
            'success': True,
            'user': {
                'user_id': user['user_id'],
                'username': user['username'],
                'role': user['nom_role'],
                'created_at': user.get('created_at')
            },
            'token': token
        }
    
    # Permet de modifier le mot de passe d'un utilisateur
    @staticmethod
    def update_password(user_id: int, old_password: str, new_password: str):
        # On récupère l'utilisateur
        user = UserModel.get_by_id(user_id)
        if not user:
            return {'success': False, 'error': 'Utilisateur introuvable'}
        
        # On récupère le hash complet (avec get_by_username)
        user_full = UserModel.get_by_username(user['username'])
        
        # On vérifie l'ancien mot de passe
        if not AuthService.verify_password(old_password, user_full['password_hash']):
            return {'success': False, 'error': 'Ancien mot de passe incorrect'}
        
        # On hache le nouveau mot de passe
        new_password_hash = AuthService.hash_password(new_password)
        
        # On effectue une mise à jour
        success = UserModel.update_password(user_id, new_password_hash)
        
        if success:
            return {'success': True}
        return {'success': False, 'error': 'Échec de la mise à jour'}
    
    @staticmethod
    # Permet d’anonymiser ou de marquer comme supprimé le compte d’un utilisateur
    def delete_account(user_id: int, password: str, anonymize: bool = True) -> dict:
        # On récupère l’utilisateur depuis la base de données
        user = UserModel.get_by_id(user_id)
        if not user:
            return {'success': False, 'error': 'Utilisateur introuvable'}
        
        # On récupère le hash complet (avec get_by_username)
        user_full = UserModel.get_by_username(user['username'])

        # On vérifie le mot de passe
        if not AuthService.verify_password(password, user_full['password_hash']):
            return {'success': False, 'error': 'Mot de passe incorrect'}
        
        # Si l’utilisateur demande l’anonymisation ou si son nom d’utilisateur est identifiable
        if anonymize or is_identifiable(user['username']):
            new_username = anonymize_username(user_id)
            return {
                'success': True,
                'method': 'anonymized',
                'new_username': new_username,
                'message': 'Compte anonymisé conformément au RGPD'
            }
        
        # Sinon on marque le compte comme supprimé
        success = UserModel.delete(user_id)
        if success:
                return {'success': True, 'method': 'deleted', 'message': 'Compte supprimé avec succès.'}
        else:
            return {'success': False, 'error': 'Échec de la suppression (parcours associés)'}
    
    @staticmethod
    # Permet de récupérer les informations d'un utilisateur sans le password_hash
    def get_user_info(user_id: int):
        user = UserModel.get_by_id(user_id)
        if not user:
            return None
        
        # On retourne les informations d'un utilisateur sans le password_hash
        return {
            'user_id': user['user_id'],
            'username': user['username'],
            'role': user['nom_role'],
            'role_id': user['role_id'],
            'anonymized': user.get('anonymized', 0),
            'created_at': user.get('created_at'),
            'updated_at': user.get('updated_at')
        }