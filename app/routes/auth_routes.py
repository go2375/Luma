from fastapi import APIRouter, HTTPException, Request, Body
from app.models import RoleModel
from app.services.user_service import UserService
from app.decorators import token_required

# Permet de créer un router API auth 
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentification"]
)

# On crée le router pour login pour authentifier un utilisateur et renvoyer un token JWT
@router.post("/login", tags=["Authentification"])
async def login(
    username: str = Body(..., description="Nom d'utilisateur", example="jean123"),
    password: str = Body(..., description="Mot de passe", example="Password123!")
):
    """
    Authentifie un utilisateur avec son nom d'utilisateur et son mot de passe.  
    Retourne un **token JWT** si la connexion réussit.
    """
    # Permet de vérifier que les champs requis sont bien présents
    if not data or "username" not in data or "password" not in data:
        raise HTTPException(status_code=400, detail="'Champs username' et 'password' requis.")

    # On authentifie l'utilisateur
    auth_result = UserService.authenticate(data["username"], data["password"])
    
    if not auth_result["success"]:
        raise HTTPException(status_code=401, detail=auth_result["error"])
    
    return {
        "message": "Connexion réussie",
        "token": auth_result["token"],
        "user": auth_result["user"]
    }

# On crée le router pour un enregistrement d'un utilisateur et on l'enregistre dans notre bdd SQLite
@router.post("/register", tags=["Authentification"])
async def register(
    username: str = Body(..., description="Nom d'utilisateur", example="newuser"),
    password: str = Body(..., description="Mot de passe", example="Pass123!")
):
    """
    Crée un **nouvel utilisateur** avec le rôle par défaut `visiteur`.  
    Retourne un token JWT directement après l’inscription.
    """
    if not data or "username" not in data or "password" not in data:
        raise HTTPException(status_code=400, detail="Champs 'username' et 'password' requis")
    # On récupère le role_id "visiteur" (rôle par défaut)
    roles = RoleModel.get_all()
    visiteur_role = next((r for r in roles if r["nom_role"] == "visiteur"), None)
    
    if not visiteur_role:
        raise HTTPException(status_code=500, detail="Rôle visiteur introuvable")
    
    # On créer l'utilisateur
    user = UserService.create_user(
        username=data["username"],
        password=data["password"],
        role_id=visiteur_role["role_id"]
    )
    
    if not user:
        raise HTTPException(status_code=409, detail="Username existant ou rôle invalide")
         
    # On authentifie immédiatement après inscription
    auth_result = UserService.authenticate(data["username"], data["password"])
    return {
        "message": "Inscription réussie",
        "token": auth_result["token"],
        "user": auth_result["user"]
    }

# On crée le router pour vérifier le token, que le token JWT est valide et non expiré
@router.get("/verify", tags=["Authentification"])
@token_required
async def verify_token(current_user: dict):
    """
    Vérifie la validité d’un **token JWT**.  
    Retourne les informations de l’utilisateur si le token est encore valide.
    """
    return {
        "message": "Token valide",
        "user": {
            "user_id": current_user["user_id"],
            "username": current_user["username"],
            "role": current_user["role"]
        }
    }

# On crée le router pour permettre à un utilisateur connecté de changer son mot de passe
@router.put("/change-password", tags=["Authentification"])
@token_required
async def change_password(
    current_user: dict,
    old_password: str = Body(..., description="Ancien mot de passe", example="OldPass123!"),
    new_password: str = Body(..., description="Nouveau mot de passe", example="NewPass456!")
):
    """
    Permet à un utilisateur **connecté** de changer son mot de passe.  
    Vérifie l’ancien mot de passe avant de l’appliquer.
    """
    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="Champs 'old_password' et 'new_password' requis.")

    result = UserService.update_password(
        user_id=current_user["user_id"],
        old_password=data["old_password"],
        new_password=data["new_password"]
    )

    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])

    return {"message": "Mot de passe mis à jour avec succès."}