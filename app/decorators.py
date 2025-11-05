from functools import wraps
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Callable, Any, Awaitable, Union
from app.auth import AuthService

security = HTTPBearer(auto_error=False)  # Ne lève pas automatiquement une exception

# ---------------- Token Required ----------------
def token_required(func: Callable[..., Awaitable[Any]]):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Récupère l'objet Request depuis kwargs ou args
        request: Request = kwargs.get("request") or next((a for a in args if isinstance(a, Request)), None)
        if not request:
            raise HTTPException(status_code=500, detail="Request object not found")

        # Vérification du header Authorization
        credentials: HTTPAuthorizationCredentials = await security.__call__(request)
        token = credentials.credentials if credentials else None
        if not token:
            raise HTTPException(status_code=401, detail="Token manquant ou invalide")

        # Décodage et vérification du token
        decoded = AuthService.decode_token(token)
        if not decoded["success"]:
            raise HTTPException(status_code=401, detail=decoded.get("error", "Token invalide"))

        # On stocke l'utilisateur courant dans kwargs pour l'endpoint
        kwargs["current_user"] = decoded["data"]
        return await func(*args, **kwargs)
    return wrapper

# ---------------- Role Required ----------------
def role_required(required_role: str):
    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(status_code=401, detail="Utilisateur non authentifié")

            user_role = current_user.get("role")
            if user_role != required_role:
                raise HTTPException(status_code=403, detail=f"Accès refusé pour le rôle {user_role}")

            return await func(*args, **kwargs)
        return wrapper
    return decorator
