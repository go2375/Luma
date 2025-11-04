from fastapi import APIRouter, HTTPException, Body
from app.models import RoleModel
from app.services.user_service import UserService
from app.decorators import token_required

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentification"]
)

# ---------------- LOGIN ----------------
@router.post("/login", tags=["Authentification"])
async def login(
    username: str = Body(..., description="Nom d'utilisateur", example="jean123"),
    password: str = Body(..., description="Mot de passe", example="Password123!")
):
    """
    Authentifie un utilisateur et retourne un token JWT.
    """
    auth_result = UserService.authenticate(username, password)

    if not auth_result["success"]:
        raise HTTPException(status_code=401, detail=auth_result["error"])

    return {
        "success": True,
        "message": "Connexion réussie",
        "token": auth_result["token"],
        "user": auth_result["user"]
    }

# ---------------- REGISTER ----------------
@router.post("/register", tags=["Authentification"])
async def register(
    username: str = Body(..., description="Nom d'utilisateur", example="newuser"),
    password: str = Body(..., description="Mot de passe", example="Pass123!")
):
    """
    Crée un nouvel utilisateur avec le rôle par défaut `visiteur`.  
    Retourne un token JWT directement après inscription.
    """
    roles = RoleModel.get_all()
    visiteur_role = next((r for r in roles if r["nom_role"] == "visiteur"), None)
    if not visiteur_role:
        raise HTTPException(status_code=500, detail="Rôle visiteur introuvable")

    user_result = UserService.create_user(username, password, visiteur_role["role_id"])
    if not user_result["success"]:
        raise HTTPException(status_code=409, detail=user_result["error"])

    auth_result = UserService.authenticate(username, password)
    if not auth_result["success"]:
        raise HTTPException(status_code=500, detail="Échec de l'authentification après inscription")

    return {
        "success": True,
        "message": "Inscription réussie",
        "token": auth_result["token"],
        "user": auth_result["user"]
    }

# ---------------- VERIFY TOKEN ----------------
@router.get("/verify", tags=["Authentification"])
@token_required
async def verify_token(current_user: dict):
    """
    Vérifie la validité d’un token JWT et retourne les informations de l’utilisateur.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    return {
        "success": True,
        "message": "Token valide",
        "user": {
            "user_id": current_user["user_id"],
            "username": current_user["username"],
            "role": current_user["role"]
        }
    }

# ---------------- CHANGE PASSWORD ----------------
@router.put("/change-password", tags=["Authentification"])
@token_required
async def change_password(
    current_user: dict,
    old_password: str = Body(..., description="Ancien mot de passe", example="OldPass123!"),
    new_password: str = Body(..., description="Nouveau mot de passe", example="NewPass456!")
):
    """
    Permet à un utilisateur connecté de changer son mot de passe.
    Vérifie l’ancien mot de passe avant de l’appliquer.
    """
    auth_check = UserService.authenticate(current_user["username"], old_password)
    if not auth_check["success"]:
        raise HTTPException(status_code=401, detail="Ancien mot de passe incorrect")

    update_result = UserService.update_password(current_user["user_id"], new_password)
    if not update_result["success"]:
        raise HTTPException(status_code=500, detail=update_result.get("error", "Erreur lors de la mise à jour"))

    return {"success": True, "message": "Mot de passe mis à jour avec succès."}
