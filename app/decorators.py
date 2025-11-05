from functools import wraps
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Callable, Any, Awaitable
from app.auth import AuthService

security = HTTPBearer(auto_error=False)

# ---------------- Token Required ----------------
def token_required(func: Callable[..., Awaitable[Any]]):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Récupère Request depuis kwargs ou args
        request: Request = kwargs.get("request") or next((a for a in args if isinstance(a, Request)), None)
        if not request:
            raise HTTPException(status_code=500, detail="Request object not found")

        credentials: HTTPAuthorizationCredentials = await security(request)
        if not credentials or not credentials.credentials:
            raise HTTPException(status_code=401, detail="Token manquant ou invalide")

        token = credentials.credentials
        decoded = AuthService.decode_token(token)
        if not decoded["success"]:
            raise HTTPException(status_code=401, detail=decoded.get("error", "Token invalide"))

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

            # Vérifie role ou nom_role selon le payload JWT
            user_role = current_user.get("role") or current_user.get("nom_role")
            if user_role != required_role:
                raise HTTPException(status_code=403, detail=f"Accès refusé pour le rôle {user_role}")

            return await func(*args, **kwargs)
        return wrapper
    return decorator
