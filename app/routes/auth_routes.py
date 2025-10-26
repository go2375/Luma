from flask import Blueprint, request, jsonify
from app.models import RoleModel
from app.services.user_service import UserService

# Permet de créer un blueprint d’authentification
# Ce blueprint regroupe toutes les routes liées à la connexion et l'inscription d'un utilisateur
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# On crée la route pour login pour authentifier un utilisateur et renvoyer un token JWT
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    # Permet de vérifier que les champs requis sont bien présents
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Champs 'username' et 'password' requis."}), 400

    # On authentifie l'utilisateur
    auth_result = UserService.authenticate(data['username'], data['password'])
    
    if not auth_result['success']:
        return jsonify({'error': auth_result['error']}), 401
    
    return jsonify({
        "message": "Connexion réussie",
        "token": token,
        "user": auth_result['user']
    }), 200

# On crée la route pour un enregistrement d'un utilisateur et on l'enregistre dans notre bdd SQLite
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Champs 'username' et 'password' requis."}), 400

    # On récupère le role_id "visiteur" (rôle par défaut)
    roles = RoleModel.get_all()
    visiteur_role = next((r for r in roles if r['nom_role'] == 'visiteur'), None)
    
    if not visiteur_role:
        return jsonify({'error': 'Rôle visiteur introuvable dans la base'}), 500
    
    # On créer l'utilisateur
    user = UserService.create_user(
        username=data['username'],
        password=data['password'],
        role_id=visiteur_role['role_id']
    )
    
    if not user:
        return jsonify({'error': 'Ce username existe déjà ou le rôle est invalide'}), 409
         
    # On authentifie immédiatement après inscription
    auth_result = UserService.authenticate(data['username'], data['password'])
    
    if not auth_result['success']:
        return jsonify({'error': 'Erreur lors de la génération du token'}), 500
    
    # On vérifier si le username a été modifié pour la conformité RGPD
    warning = None
    if auth_result['user']['username'] != data['username']:
        warning = "Votre username a été modifié pour respecter la politique de confidentialité"
    
    response = {
        'message': 'Inscription réussie',
        'token': auth_result['token'],
        'user': auth_result['user']
    }
    
    if warning:
        response['warning'] = warning
    
    return jsonify(response), 201

# On crée la route pour vérifier le token, que le token JWT est valide et non expiré
@auth_bp.route("/verify", methods=["GET"])
@token_required
def verify_token(current_user):
    return jsonify({
        "message": "Token valide",
        "user": {
            'user_id': current_user['user_id'],
            'username': current_user['username'],
            'role': current_user['role']
        }
    }), 200

# On crée la route pour permettre à un utilisateur connecté de changer son mot de passe
@auth_bp.route("/change-password", methods=["PUT"])
@token_required
def change_password(current_user):
    data = request.get_json()

    if not data or "old_password" not in data or "new_password" not in data:
        return jsonify({"error": "Champ 'old_password' et 'new_password' requis."}), 400

    result = UserService.update_password(
        user_id=current_user["user_id"],
        old_password=data["old_password"],
        new_password=data["new_password"]
    )

    if not result['success']:
        return jsonify({"error": result['error']}), 401

    return jsonify({"message": "Mot de passe mis à jour avec succès."}), 200