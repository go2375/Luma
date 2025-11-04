from functools import wraps
from fastapi import Request, HTTPException
from app.auth import AuthService
import inspect

def token_required(func):
    """
    Décorateur FastAPI : protège une route avec authentification JWT.
    Vérifie la présence et la validité du token dans les headers "Authorization".
    Passe l'utilisateur décodé à la fonction décorée via current_user.
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        # Récupération du header Authorization
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Token manquant. Authentification requise.")

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Format de token invalide. Utilisez: Bearer <token>")

        token = parts[1]

        # Vérification et décodage du token
        result = AuthService.decode_token(token)
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result["error"])

        user_data = result["data"]

        # Normalisation du rôle : on s'assure que 'role' existe
        if "nom_role" in user_data:
            user_data["role"] = user_data.pop("nom_role")
        elif "role" not in user_data:
            # si aucun rôle n'existe, mettre un rôle vide
            user_data["role"] = ""

        # Appel dynamique (supporte sync et async)
        if inspect.iscoroutinefunction(func):
            return await func(*args, current_user=user_data, request=request, **kwargs)
        else:
            return func(*args, current_user=user_data, request=request, **kwargs)

    return wrapper


def role_required(*allowed_roles):
    """
    Décorateur FastAPI : restreint l’accès à certaines routes selon le rôle utilisateur.
    Nécessite l’utilisation préalable de @token_required.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: dict = None, **kwargs):
            # Récupère le rôle depuis 'role' normalisé
            user_role = current_user.get("role") if current_user else None

            if not user_role or user_role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Accès refusé - Permissions insuffisantes",
                        "roles_autorises": list(allowed_roles),
                        "votre_role": user_role
                    }
                )

            # Appel dynamique (supporte sync et async)
            if inspect.iscoroutinefunction(func):
                return await func(*args, current_user=current_user, **kwargs)
            else:
                return func(*args, current_user=current_user, **kwargs)

        return wrapper
    return decorator