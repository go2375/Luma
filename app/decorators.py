from functools import wraps
from flask import request, jsonify
from app.auth import AuthService

# Permet de créer un décorateur pour protéger une route Flask avec authentification JWT.
# Permet de vérifier la présence et la validité d'un token dans les headers Authorization,
# ainsi que permet de passer les données utilisateur décodées à la fonction décorée.
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Permet de récupérer le token depuis les headers Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Ici le format attendu c'est Bearer <token>
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Format de token invalide. Utilisez: Bearer <token>'}), 401
        
        # Si pas de token trouvé un message de notification s'affiche
        if not token:
            return jsonify({'error': 'Token manquant. Authentification requise.'}), 401
        
        # Permet de vérifier le token
        result = AuthService.decode_token(token)
        if not result['success']:
            return jsonify({'error': result['error']}), 401
        
        # Permet de passer les données utilisateur à la fonction protégée
        return f(current_user=result['data'], *args, **kwargs)
    
    return decorated

# Permet de créer un décorateur pour restreindre l'accès à certains rôles utilisateur, 
# mais nécessite que la route soit déjà protégée par @token_required.
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            user_role = current_user.get('role')
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'Accès refusé - Permissions insuffisantes',
                    'roles_autorises': list(allowed_roles),
                    'votre_role': user_role
                }), 403
            return f(current_user=current_user, *args, **kwargs)
        return decorated
    return decorator