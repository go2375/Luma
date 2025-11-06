from functools import wraps
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Callable, Any, Awaitable
from app.auth import AuthService

# Sécurité
# J'utilise HTTPBearer pour extraire le token Bearer depuis les headers Authorization
# auto_error=False permet de gérer l'erreur par API pour renvoyer un message personnalisé
security = HTTPBearer(auto_error=False)

# Décorateur : token_required
def token_required(func: Callable[..., Awaitable[Any]]):
    """
    Je protège une route pour qu'elle ne soit accessible qu'avec un token JWT valide.
    Je décode le token et je passe l'utilisateur authentifié dans kwargs['current_user'].
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Je récupère l'objet Request depuis les kwargs ou args
        request: Request = kwargs.get("request") or next((a for a in args if isinstance(a, Request)), None)
        if not request:
            raise HTTPException(status_code=500, detail="Request object not found")

        # Je récupère le token dans l'en-tête Authorization
        credentials: HTTPAuthorizationCredentials = await security(request)
        if not credentials or not credentials.credentials:
            raise HTTPException(status_code=401, detail="Token manquant ou invalide")

        token = credentials.credentials
        # Je décode le token pour récupérer le payload
        decoded = AuthService.decode_token(token)
        if not decoded["success"]:
            raise HTTPException(status_code=401, detail=decoded.get("error", "Token invalide"))

        # Je passe l'utilisateur décodé à la route
        kwargs["current_user"] = decoded["data"]
        return await func(*args, **kwargs)
    return wrapper

# Décorateur : role_required
def role_required(required_role: str):
    """
    Je protège une route pour qu'elle ne soit accessible qu'à un rôle spécifique.
    Je dois appeler ce décorateur après token_required pour avoir current_user.
    """
    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Je récupère l'utilisateur authentifié passé par token_required
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(status_code=401, detail="Utilisateur non authentifié")

            # Je vérifie si le rôle correspond à celui requis
            user_role = current_user.get("role") or current_user.get("nom_role")
            if user_role != required_role:
                raise HTTPException(status_code=403, detail=f"Accès refusé pour le rôle {user_role}")

            return await func(*args, **kwargs)
        return wrapper
    return decorator
