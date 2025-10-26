from flask import Blueprint, request, jsonify
from app.decorators import token_required, role_required
from app.services.site_service import SiteService

# Ces routes permettent aux prestataires de gérer leurs sites touristiques
prestataire_bp = Blueprint('prestataire', __name__, url_prefix='/api/prestataire')

# Cette route permet à un prestataire de récupérer tous les sites appartenant à ce prestataire
@prestataire_bp.route('/sites', methods=['GET'])
@token_required
@role_required(current_user)
def get_my_sites(current_user):
    sites = SiteService.get_sites_by_prestataire(current_user['user_id'])
    return jsonify({'sites': sites}), 200

# Cette route permet à un prestataire de récupérer un site spécifique choisi
@prestataire_bp.route('/sites/<int:site_id>', methods=['GET'])
@token_required
@role_required('prestataire')
def get_site(current_user, site_id):
    mes_sites = SiteService.get_sites_by_prestataire(current_user['user_id'])
    
    # Permet de vérifier que le site appartient au prestataire
    site = next((s for s in mes_sites if s['site_id'] == site_id), None)

    if not site:
        return jsonify({'error': 'Site introuvable ou accès refusé'}), 404 
    
    return jsonify({'site': site}), 200

# Cette route permet à un prestataire de créer un nouveau site touristique
@prestataire_bp.route('/sites', methods=['POST'])
@token_required
@role_required('prestataire')
def create_site(current_user):
    data = request.get_json()
    
    if not data or 'nom_site' not in data or 'commune_id' not in data:
        return jsonify({'error': 'nom_site et commune_id requis'}), 400
    
    # Permet de créer le site avec le prestataire_id de l'utilisateur connecté
    result = SiteService.create_site(
        nom_site=data['nom_site'],
        commune_id=data['commune_id'],
        prestataire_id=current_user['user_id'],
        type_site=data.get('type_site'),
        description=data.get('description'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400

    return jsonify({
        'message': 'Site créé avec succès',
        'site_id': result['site_id']
    }), 201

# Cette route permet à un prestataire de modifier son site touristique
@prestataire_bp.route('/sites/<int:site_id>', methods=['PUT'])
@token_required
@role_required('prestataire')
def update_site(current_user, site_id):
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Données manquantes'}), 400
    
    result = SiteService.update_site(
        site_id=site_id,
        prestataire_id=current_user['user_id'],
        **data
    )
    
    if not result['success']:
        return jsonify({'error': result['error']}), 403 if 'Accès refusé' in result['error'] else 400
    
    return jsonify({'message': 'Site mis à jour avec succès'}), 200
    
# Cette route permet à un prestataire de supprimer son site touristique
@prestataire_bp.route('/sites/<int:site_id>', methods=['DELETE'])
@token_required
@role_required('prestataire')
def delete_site(current_user, site_id):
    result = SiteService.delete_site(
        site_id=site_id,
        prestataire_id=current_user['user_id']
    )

    if not result['success']:
        return jsonify({'error': result['error']}), 403 if 'Accès refusé' in result['error'] else 400

    return jsonify({'message': 'Site supprimé avec succès'}), 200