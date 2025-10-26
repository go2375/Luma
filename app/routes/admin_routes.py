from flask import Blueprint, request, jsonify
from app.auth import AuthService
from app.decorators import token_required, role_required
from app.services.role_service import RoleService
from app.services.user_service import UserService
from app.models import RoleModel, UserModel

### Ces routes permettent à un admin de gérer des rôles et des comptes des utilisateurs
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

## Ces routes permettent à un admin de gérer des rôles des utilisateurs
# Cette route permet à un admin de récupérer tous les rôles
@admin_bp.route('/roles', methods=['GET'])
@token_required
@role_required('admin')
def get_roles(current_user):
    roles = RoleService.get_all_roles()
    return jsonify({'roles': roles}), 200

# Cette route permet à un admin de créer un nouveau rôle
@admin_bp.route('/roles', methods=['POST'])
@token_required
@role_required('admin')
def create_role(current_user):
    data = request.get_json()
    
    if not data or 'nom_role' not in data:
        return jsonify({'error': 'nom_role requis'}), 400
    
    result = RoleService.create_role(data['nom_role'])
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    return jsonify({
        'message': 'Rôle créé avec succès',
        'role': result['role']
    }), 201

# Cette route permet à un admin de modifier un rôle existant
@admin_bp.route('/roles/<int:role_id>', methods=['PUT'])
@token_required
@role_required('admin')
def update_role(current_user, role_id):
    data = request.get_json()
    
    if not data or 'nom_role' not in data:
        return jsonify({'error': 'nom_role requis'}), 400
    
    # Permet de vérifier que le rôle existe
    if not RoleModel.get_by_id(role_id):
        return jsonify({'error': 'Rôle introuvable'}), 404
    
    success = RoleModel.update(role_id, data['nom_role'])
    
    if success:
        return jsonify({'message': 'Rôle mis à jour avec succès'}), 200
    return jsonify({'error': 'Échec de la mise à jour'}), 400

# Cette route permet à un admin de supprimer un rôle existant
@admin_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_role(current_user, role_id):
    result = RoleService.update_role(role_id, data['nom_role'])
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    return jsonify({'message': 'Rôle mis à jour avec succès'}), 200

## Ces routes permettent à un admin de gérer des comptes des utilisateurs
# Cette route permet à un admin de récupérer tous les utilisateurs
@admin_bp.route('/users', methods=['GET'])
@token_required
@role_required('admin')
def get_users(current_user):
    users = UserModel.get_all()
    return jsonify({'users': users}), 200

# Cette route permet à un admin de récupérer les données d'un utilisateur spécifique
@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
@role_required('admin')
def get_user(current_user, user_id):
    user = UserService.get_user_info(user_id)
    
    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404
    
    return jsonify({'user': user}), 200

# Cette route permet à un admin de créer un nouvel utilisateur
@admin_bp.route('/users', methods=['POST'])
@token_required
@role_required('admin')
def create_user(current_user):
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data or 'role_id' not in data:
        return jsonify({'error': 'username, password et role_id requis'}), 400
    
    # Permet de vérifier si l'utilisateur existe déjà
    if UserModel.get_by_username(data['username']):
        return jsonify({'error': 'Ce username existe déjà'}), 409
    
    # Permet de créer l'utilisateur
    user = UserService.create_user(
        username=data['username'],
        password_hash=password_hash,
        role_id=data['role_id']
    )
    
    if not user:
        return jsonify({'error': 'Ce username existe déjà ou le rôle est invalide'}), 409
    
    return jsonify({
        'message': 'Utilisateur créé avec succès',
        'user': user
    }), 201

# Cette route permet à un admin de modifier le mot de passe d'un utilisateur
@admin_bp.route('/users/<int:user_id>/password', methods=['PUT'])
@token_required
@role_required('admin')
def update_user_password(current_user, user_id):
    data = request.get_json()
    
    if not data or 'new_password' not in data:
        return jsonify({'error': 'new_password requis'}), 400
    
    # Permet de vérifier que l'utilisateur existe
    user = UserModel.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404
    
    # Permet d'hasher le nouveau mot de passe
    password_hash = AuthService.hash_password(data['new_password'])
    
    success = UserModel.update_password(user_id, password_hash)
    
    if success:
        return jsonify({'message': 'Mot de passe mis à jour avec succès'}), 200
    return jsonify({'error': 'Échec de la mise à jour'}), 400

# Cette route permet à un admin de modifier un rôle d'un utilisateur
@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@token_required
@role_required('admin')
def update_user_role(current_user, user_id):
    data = request.get_json()
    
    if not data or 'role_id' not in data:
        return jsonify({'error': 'role_id requis'}), 400
    
    # Permet de vérifier que l'utilisateur existe
    user = UserModel.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404
    
    # Permet de vérifier que le rôle existe
    role = RoleModel.get_by_id(data['role_id'])
    if not role:
        return jsonify({'error': 'Rôle invalide'}), 400
    
    # Permet d'empêcher un admin de changer son propre rôle (sécurité)
    if current_user['user_id'] == user_id:
        return jsonify({'error': 'Impossible de modifier son propre rôle'}), 403
    
    success = UserModel.update_role(user_id, data['role_id'])
    
    if success:
        return jsonify({'message': 'Rôle mis à jour avec succès'}), 200
    return jsonify({'error': 'Échec de la mise à jour'}), 400

# Cette route permet à un admin de supprimer un utilisateur
@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_user(current_user, user_id):
    # Permet d'empêcher un admin de se supprimer lui-même
    if current_user['user_id'] == user_id:
        return jsonify({'error': 'Impossible de supprimer son propre compte'}), 403
    
    # Permet de vérifier que l'utilisateur existe
    user = UserModel.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404
    
    success = UserModel.delete(user_id)
    
    if success:
        return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200
    return jsonify({'error': 'Échec de la suppression (parcours ou sites associés)'}), 400