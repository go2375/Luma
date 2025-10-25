from flask import Blueprint, request, jsonify
from app.decorators import token_required
from app.services.site_service import SiteService
from app.services.user_service import UserService
from app.services.parcours_service import ParcoursService
from app.models import CommuneModel, DepartmentModel

# On crée le blueprint
public_bp = Blueprint('public', __name__, url_prefix='/api')

## Permet de créer des routes publiques qui ne nécessitent pas d'authentification et permettent de récupérer les données anonymisées sur les sites touristiques

@public_bp.route('/sites', methods=['GET'])
# Permet de récupérer les données anonymisées sur tous les sites touristiques
def get_all_sites():
    sites = SiteService.get_all_sites_public()
    return jsonify({'sites': sites}), 200


@public_bp.route('/sites/<int:site_id>', methods=['GET'])
# Permet de récupérer les données anonymisées sur un site spécifique
def get_site(site_id):
    site = SiteService.get_site_by_id_public(site_id)
    
    if not site:
        return jsonify({'error': 'Site introuvable'}), 404
    
    return jsonify({'site': site}), 200


@public_bp.route('/communes', methods=['GET'])
# Permet de récupérer toutes les communes
def get_all_communes():
    communes = CommuneModel.get_all()
    return jsonify({'communes': communes}), 200


@public_bp.route('/departments', methods=['GET'])
# Permet de récupérer tous les départements
def get_all_departments():
    departments = DepartmentModel.get_all()
    return jsonify({'departments': departments}), 200


# Permet de gérer des parcours qui nécessitent une authentification et permet aux utilisateurs authentifiés d'accéder à leurs parcours
@public_bp.route('/parcours', methods=['GET'])
@token_required
# Permet de récupérer tous les parcours d'un utilisateur authentifié
def get_my_parcours(current_user):
    parcours_list = ParcoursService.get_user_parcours(current_user['user_id'])
    return jsonify({'parcours': parcours_list}), 200


@public_bp.route('/parcours/<int:parcours_id>', methods=['GET'])
@token_required
# Permet à un utilisateur authentifié de récupérer un parcours avec tous les sites
def get_parcours_detail(current_user, parcours_id):
    result = ParcoursService.get_parcours_by_id(parcours_id, current_user['user_id'])
    
    if not result['success']:
        status_code = 403 if 'Accès refusé' in result['error'] else 404
        return jsonify({'error': result['error']}), status_code
    
    return jsonify({'parcours': result['parcours']}), 200


@public_bp.route('/parcours', methods=['POST'])
@token_required
# Permet de créer un nouveau parcours
def create_parcours(current_user):
    data = request.get_json()
    
    if not data or 'nom_parcours' not in data:
        return jsonify({'error': 'nom_parcours requis'}), 400
    
    result = ParcoursService.create_parcours(
        nom_parcours=data['nom_parcours'],
        createur_id=current_user['user_id'],
        sites=data.get('sites')
    )
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    return jsonify({
        'message': 'Parcours créé avec succès',
        'parcours_id': result['parcours_id']
    }), 201


@public_bp.route('/parcours/<int:parcours_id>', methods=['PUT'])
@token_required
# Permet de modifier le nom d'un parcours
def update_parcours(current_user, parcours_id):
    data = request.get_json()
    
    if not data or 'nom_parcours' not in data:
        return jsonify({'error': 'nom_parcours requis'}), 400
    
    # On effectue une mise à jour
    result = ParcoursService.update_parcours(
        parcours_id=parcours_id,
        user_id=current_user['user_id'],
        nom_parcours=data['nom_parcours']
    )
    
    if not result['success']:
        status_code = 403 if 'Accès refusé' in result['error'] else 404
        return jsonify({'error': result['error']}), status_code
    
    return jsonify({'message': 'Parcours mis à jour avec succès'}), 200


@public_bp.route('/parcours/<int:parcours_id>', methods=['DELETE'])
@token_required
# Permet de supprimer un parcours
def delete_parcours(current_user, parcours_id):
    result = ParcoursService.delete_parcours(
        parcours_id=parcours_id,
        user_id=current_user['user_id']
    )
    
    if not result['success']:
        status_code = 403 if 'Accès refusé' in result['error'] else 404
        return jsonify({'error': result['error']}), status_code
    
    return jsonify({'message': 'Parcours supprimé avec succès'}), 200

@public_bp.route('/parcours/<int:parcours_id>/sites/<int:site_id>', methods=['DELETE'])
@token_required
# Permet de retirer un site d'un parcours
def remove_site_from_parcours(current_user, parcours_id, site_id):
    result = ParcoursService.remove_site_from_parcours(
        parcours_id=parcours_id,
        user_id=current_user['user_id'],
        site_id=site_id
    )
    
    if not result['success']:
        status_code = 403 if 'Accès refusé' in result['error'] else 404
        return jsonify({'error': result['error']}), status_code
    
    return jsonify({'message': 'Site retiré du parcours avec succès'}), 200


## Permet de gérer les comptes des utilisateurs

@public_bp.route('/me', methods=['GET'])
@token_required
# Permet à un utilisateur de récupérer son profil
def get_my_profile(current_user):
    user = UserService.get_user_info(current_user['user_id'])
    
    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404
    
    return jsonify({'user': user}), 200


@public_bp.route('/me/password', methods=['PUT'])
@token_required
# Permet à un utilisateur de modifier son mot de passe
def update_my_password(current_user):
    data = request.get_json()
    
    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'old_password et new_password requis'}), 400
    
    result = UserService.update_password(
        user_id=current_user['user_id'],
        old_password=data['old_password'],
        new_password=data['new_password']
    )
    
    if not result['success']:
        return jsonify({'error': result['error']}), 401
    
    return jsonify({'message': 'Mot de passe mis à jour avec succès'}), 200


@public_bp.route('/me', methods=['DELETE'])
@token_required
# Permet d'anonymiser ou marquer comme supprimé un compte par un utilisateur
def delete_my_account(current_user):
    data = request.get_json()
    
    if not data or 'password' not in data:
        return jsonify({'error': 'password requis pour confirmer la suppression'}), 400
    
    # On vérifie si l'utilisateur a demandé l'anonymisation de son compte (False par défaut)
    # Si False, le compte sera supprimé directement.
    # Si True ou si le username est identifiable, il sera anonymisé avant d'être marqué comme supprimé.
    anonymize = data.get('anonymize', False)
    
    # On supprime le compte
    result = UserService.delete_account(
        user_id=current_user['user_id'],
        password=data['password'],
        anonymize=anonymize
    )
    
    if not result['success']:
        return jsonify({'error': result['error']}), 401
    
    if result['method'] == 'anonymized':
        return jsonify({
            'message': 'Compte anonymisé avec succès',
            'info': result['message']
        }), 200
    else:
        return jsonify({'message': 'Compte supprimé avec succès'}), 200