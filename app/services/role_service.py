from app.models import RoleModel

# Permet de créer un service de gestion des rôles
class RoleService:
    SYSTEM_ROLES = ['admin', 'visiteur', 'prestataire']
    
    @staticmethod
    # Permet de récupérer tous les rôles
    def get_all_roles():
        return RoleModel.get_all()
    
    @staticmethod
    # Permet de récupérer un rôle par son ID
    def get_role_by_id(role_id: int):
        return RoleModel.get_by_id(role_id)
    
    @staticmethod
    # Permet de créer un nouveau rôle
    def create_role(nom_role: str):
        # On vérifie que le nom n'est pas vide
        if not nom_role or len(nom_role.strip()) == 0:
            return {'success': False, 'error': 'Le nom du rôle ne peut pas être vide'}
        
        try:
            role = RoleModel.create(nom_role.strip())
            return {'success': True, 'role': role}
        except Exception as e:
            return {'success': False, 'error': f'Ce rôle existe déjà'}
    
    @staticmethod
    # Permet de modifier un rôle
    def update_role(role_id: int, nom_role: str):
        # On vérifie que le rôle existe
        role = RoleModel.get_by_id(role_id)
        if not role:
            return {'success': False, 'error': 'Rôle introuvable'}
        
        # On vérifie que le nom n'est pas vide
        if not nom_role or len(nom_role.strip()) == 0:
            return {'success': False, 'error': 'Le nom du rôle ne peut pas être vide'}
        
        # Les rôles système ne peuvent pas être supprimés
        if role['nom_role'] in RoleService.SYSTEM_ROLES:
            return {'success': False, 'error': 'Impossible de modifier un rôle système'}
        
        success = RoleModel.update(role_id, nom_role.strip())
        
        if success:
            return {'success': True}
        return {'success': False, 'error': 'Échec de la mise à jour'}
    
    @staticmethod
    # Permet de supprimer un rôle
    def delete_role(role_id: int):
        # On vérifie que le rôle existe
        role = RoleModel.get_by_id(role_id)
        if not role:
            return {'success': False, 'error': 'Rôle introuvable'}
        
        # Les rôles système ne peuvent pas être supprimés
        if role['nom_role'] in RoleService.SYSTEM_ROLES:
            return {'success': False, 'error': 'Impossible de supprimer un rôle système'}
        
        success = RoleModel.delete(role_id)
        
        if success:
            return {'success': True}
        return {'success': False, 'error': 'Échec de la suppression (utilisateurs associés)'}