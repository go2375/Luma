from flask import Blueprint, request, jsonify
from app.auth import AuthService
from app.models import UserModel, RoleModel
from app.decorators import token_required

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

    username = data["username"]
    password = data["password"]

    # On recherche un utilisateur dans notre bdd SQLite
    user = UserModel.get_by_username(username)
    if not user:
        return jsonify({"error": "Utilisateur introuvable."}), 404

    # On vérifie son mot de passe
    if not AuthService.verify_password(password, user["password_hash"]):
        return jsonify({"error": "Mot de passe incorrect."}), 401

    # On génère le token JWT
    token = AuthService.generate_token(
        user_id=user["user_id"],
        username=user["username"],
        role=user["nom_role"]
    )

    return jsonify({
        "message": "Connexion réussie",
        "token": token,
        "user": {
            "id": user["user_id"],
            "username": user["username"],
            "role": user["nom_role"]
        }
    }), 200

# On crée la route pour un enregistrement d'un utilisateur et on l'enregistre dans notre bdd SQLite
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Champs 'username' et 'password' requis."}), 400

    username = data["username"]
    password = data["password"]

    # On vérifie existence utilisateur
    if UserModel.get_by_username(username):
        return jsonify({"error": "Ce nom d'utilisateur existe déjà."}), 409

    # On hache son mot de passe
    password_hash = AuthService.hash_password(password)

    # On récupère le rôle par défaut 'visiteur'
    roles = RoleModel.get_all()
    default_role = next((r for r in roles if r["nom_role"] == "visiteur"), None)
    if not default_role:
        return jsonify({"error": "Rôle 'visiteur' introuvable. Contactez un administrateur."}), 500

    role_id = default_role["role_id"]

    # Crée l’utilisateur
    new_user = UserModel.create(username=username, password_hash=password_hash, role_id=role_id)

    return jsonify({
        "message": "Utilisateur créé avec succès.",
        "user": {
            "user_id": new_user["user_id"],
            "username": new_user["username"],
            "role_id": new_user["role_id"]
        }
    }), 201

# On crée la route pour vérifier le token, que le token JWT est valide et non expiré
@auth_bp.route("/verify", methods=["GET"])
@token_required
def verify_token(current_user):
    return jsonify({
        "message": "Token valide",
        "user": current_user
    }), 200

# On crée la route pour permettre à un utilisateur connecté de changer son mot de passe
@auth_bp.route("/change-password", methods=["PUT"])
@token_required
def change_password(current_user):
    data = request.get_json()

    if not data or "new_password" not in data:
        return jsonify({"error": "Champ 'new_password' requis."}), 400

    new_password_hash = AuthService.hash_password(data["new_password"])

    success = UserModel.update_password(current_user["user_id"], new_password_hash)
    if not success:
        return jsonify({"error": "Échec de la mise à jour du mot de passe."}), 400

    return jsonify({"message": "Mot de passe mis à jour avec succès."}), 200