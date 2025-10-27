from functools import wraps
from fastapi import Request, HTTPException
from app.auth import AuthService

# Permet de créer un décorateur pour protéger une route Flask avec authentification JWT.
# Permet de vérifier la présence et la validité d'un token dans les headers Authorization,
# ainsi que permet de passer les données utilisateur décodées à la fonction décorée.
def token_required(f):
    @wraps(f)
    async def wrapper(*args, request: Request, **kwargs):
        token = None
        
        # Permet de récupérer le token depuis les headers Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header:
            parts = auth_header.split(" ")
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
            else:
                raise HTTPException(status_code=401, detail="Format de token invalide. Utilisez: Bearer <token>")
        
        if not token:
            raise HTTPException(status_code=401, detail="Token manquant. Authentification requise.")
        

        # On vérifie le token
        result = AuthService.decode_token(token)
        # Si pas de token trouvé un message de notification s'affiche
        if not result['success']:
            raise HTTPException(status_code=401, detail=result['error'])
        
        # Permet de passer les données utilisateur à la fonction protégée
        return await f(*args, current_user=result['data'], request=request, **kwargs)
 
    return wrapper

# Permet de créer un décorateur pour restreindre l'accès à certains rôles utilisateur, 
# mais nécessite que la route soit déjà protégée par @token_required.
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, current_user: dict, **kwargs):
            user_role = current_user.get('role')
            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail={
                    'error': 'Accès refusé - Permissions insuffisantes',
                    'roles_autorises': list(allowed_roles),
                    'votre_role': user_role
                    }
                )
            return await f(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator