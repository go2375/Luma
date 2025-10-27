from fastapi import APIRouter, HTTPException, Request
from app.models import RoleModel
from app.services.user_service import UserService
from app.decorators import token_required

# Permet de créer un router API auth 
router = APIRouter(prefix="/api/auth", tags=["auth"])

# On crée le router pour login pour authentifier un utilisateur et renvoyer un token JWT
@router.post("/login")
async def login(request: Request):
    data = await request.json()
    # Permet de vérifier que les champs requis sont bien présents
    if not data or "username" not in data or "password" not in data:
        raise HTTPException(status_code=400, detail="Champs 'username' et 'password' requis.")

    # On authentifie l'utilisateur
    auth_result = UserService.authenticate(data['username'], data['password'])
    
    if not auth_result['success']:
        raise HTTPException(status_code=401, detail=auth_result['error'])
    
    return {
        "message": "Connexion réussie",
        "token": auth_result['token'],
        "user": auth_result['user']
    }

# On crée le router pour un enregistrement d'un utilisateur et on l'enregistre dans notre bdd SQLite
@router.post("/register")
async def register(data: dict):
    data = await request.json()

    if not data or "username" not in data or "password" not in data:
        raise HTTPException(status_code=400, detail="Champs 'username' et 'password' requis")
    # On récupère le role_id "visiteur" (rôle par défaut)
    roles = RoleModel.get_all()
    visiteur_role = next((r for r in roles if r['nom_role'] == 'visiteur'), None)
    
    if not visiteur_role:
        raise HTTPException(status_code=500, detail="Rôle visiteur introuvable")
    
    # On créer l'utilisateur
    user = UserService.create_user(
        username=data['username'],
        password=data['password'],
        role_id=visiteur_role['role_id']
    )
    
    if not user:
        raise HTTPException(status_code=409, detail="Username existant ou rôle invalide")
         
    # On authentifie immédiatement après inscription
    auth_result = UserService.authenticate(data['username'], data['password'])
    return {
        'message': 'Inscription réussie',
        'token': auth_result['token'],
        'user': auth_result['user']
    }

# On crée le router pour vérifier le token, que le token JWT est valide et non expiré
@router.get("/verify")
@token_required
async def verify_token(current_user: dict):
    return {
        "message": "Token valide",
        "user": {
            'user_id': current_user['user_id'],
            'username': current_user['username'],
            'role': current_user['role']
        }
    }

# On crée le router pour permettre à un utilisateur connecté de changer son mot de passe
@auth_bp.route("/change-password", methods=["PUT"])
@token_required
async def change_password(request: Request, current_user: dict):
    data = await request.json()

    if not data or "old_password" not in data or "new_password" not in data:
        raise HTTPException(status_code=400, detail="Champ 'old_password' et 'new_password' requis.")

    result = UserService.update_password(
        user_id=current_user["user_id"],
        old_password=data["old_password"],
        new_password=data["new_password"]
    )

    if not result['success']:
        raise HTTPException(status_code=401, detail=result['error'])

    return {"message": "Mot de passe mis à jour avec succès."}