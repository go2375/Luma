from flask import Blueprint, request, jsonify
from app.auth import token_required, role_required
from app.models import SiteModel

# Ces routes permettent aux prestataires de gérer leurs sites touristiques
prestataire_bp = Blueprint('prestataire', __name__, url_prefix='/api/prestataire')

# Cette route permet à un prestataire de récupérer tous les sites appartenant à ce prestataire
@prestataire_bp.route('/sites', methods=['GET'])
@token_required
@role_required('prestataire')
def get_my_sites(current_user):
    sites = SiteModel.get_by_prestataire(current_user['user_id'])
    return jsonify({'sites': sites}), 200

# Cette route permet à un prestataire de récupérer un site spécifique choisi
@prestataire_bp.route('/sites/<int:site_id>', methods=['GET'])
@token_required
@role_required('prestataire')
def get_site(current_user, site_id):
    site = SiteModel.get_by_id(site_id, include_prestataire=True)
    
    if not site:
        return jsonify({'error': 'Site introuvable'}), 404
    
    # Permet de vérifier que le site appartient au prestataire
    if site['prestataire_id'] != current_user['user_id']:
        return jsonify({'error': 'Accès refusé'}), 403
    
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
    site = SiteModel.create(
        nom_site=data['nom_site'],
        commune_id=data['commune_id'],
        prestataire_id=current_user['user_id'],
        type_site=data.get('type_site'),
        description=data.get('description'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )
    
    return jsonify({
        'message': 'Site créé avec succès',
        'site': site
    }), 201

# Cette route permet à un prestataire de modifier son site touristique
@prestataire_bp.route('/sites/<int:site_id>', methods=['PUT'])
@token_required
@role_required('prestataire')
def update_site(current_user, site_id):
    """Modifier un site touristique"""
    site = SiteModel.get_by_id(site_id, include_prestataire=True)
    
    if not site:
        return jsonify({'error': 'Site introuvable'}), 404
    
    # Permet de vérifier que le site appartient au prestataire
    if site['prestataire_id'] != current_user['user_id']:
        return jsonify({'error': 'Accès refusé'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Données manquantes'}), 400
    
    success = SiteModel.update(site_id, **data)
    
    if success:
        return jsonify({'message': 'Site mis à jour avec succès'}), 200
    return jsonify({'error': 'Échec de la mise à jour'}), 400

# Cette route permet à un prestataire de supprimer son site touristique
@prestataire_bp.route('/sites/<int:site_id>', methods=['DELETE'])
@token_required
@role_required('prestataire')
def delete_site(current_user, site_id):
    site = SiteModel.get_by_id(site_id, include_prestataire=True)
    
    if not site:
        return jsonify({'error': 'Site introuvable'}), 404
    
    # Permet de vérifier que le site appartient au prestataire
    if site['prestataire_id'] != current_user['user_id']:
        return jsonify({'error': 'Accès refusé'}), 403
    
    success = SiteModel.delete(site_id)
    
    if success:
        return jsonify({'message': 'Site supprimé avec succès'}), 200
    return jsonify({'error': 'Échec de la suppression (site utilisé dans des parcours)'}), 400