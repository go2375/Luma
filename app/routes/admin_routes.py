from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.decorators import token_required, role_required
from app.services.role_service import RoleService
from app.services.user_service import UserService
from app.models import RoleModel, UserModel

### Ce router permet à un admin de gérer des rôles et des comptes des utilisateurs
admin_router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)

## Ces routers permettent à un admin de gérer des rôles des utilisateurs
# Cet router permet à un admin de récupérer tous les rôles
@admin_router.get("/roles")
@token_required
@role_required("admin")
async def get_roles(current_user: dict):
    roles = RoleService.get_all_roles()
    return {"roles": roles}

# Cet router permet à un admin de créer un nouveau rôle
@admin_router.post("/roles")
@token_required
@role_required("admin")
async def create_role(request: Request, current_user: dict):
    data = await request.json()
    nom_role = data.get("nom_role")
    
    if not data or "nom_role" not in data:
        raise HTTPException(status_code=400, detail="nom_role requis")
    
    result = RoleService.create_role(nom_role)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Échec de la création"))
    
    return JSONResponse(content={
        "message": "Rôle créé avec succès",
        "role": result["role"]
    }, status_code=201)

# Cet router permet à un admin de modifier un rôle existant
@admin_router.put("/roles/{role_id}")
@token_required
@role_required("admin")
async def update_role(role_id: int, request: Request, current_user: dict):
    data = await request.json()
    nom_role = data.get("nom_role")
    
    if not data or "nom_role" not in data:
        raise HTTPException(status_code=400, detail="nom_role requis")
    
    # Permet de vérifier que le rôle existe
    if not RoleModel.get_by_id(role_id):
        raise HTTPException(status_code=404, detail="Rôle introuvable")
    
    result = RoleService.update_role(role_id, nom_role)
    
    if not result["success"]:
       raise HTTPException(status_code=400, detail=result.get("error", "Échec de la mise à jour"))

    return {"message": "Rôle mis à jour avec succès"}

# Cet router permet à un admin de supprimer un rôle existant
@admin_router.delete("/roles/{role_id}")
@token_required
@role_required("admin")
async def delete_role(role_id: int, current_user: dict):
    result = RoleService.delete_role(role_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Échec de la suppression"))

    return {"message": "Rôle supprimé avec succès"}

## Ces routers permettent à un admin de gérer des comptes des utilisateurs
# Cet router permet à un admin de récupérer tous les utilisateurs
@admin_router.get("/users")
@token_required
@role_required("admin")
async def get_users(current_user: dict):
    users = UserModel.get_all()
    return {"users": users}

# Cet router permet à un admin de récupérer les données d'un utilisateur spécifique
@admin_router.get("/users/{user_id}")
@token_required
@role_required("admin")
async def get_user(user_id: int, current_user: dict):
    user = UserService.get_user_info(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    return {"user": user}

# Cet router permet à un admin de créer un nouvel utilisateur
@admin_router.post("/users")
@token_required
@role_required("admin")
async def create_user(request: Request, current_user: dict):
    data = await request.json()
    username = payload.get("username")
    password = payload.get("password")
    role_id = payload.get("role_id")
    
    if not data or "username" not in data or "password" not in data or "role_id" not in data:
        raise HTTPException(status_code=400, detail="username, password et role_id requis")
    
    # Permet de vérifier si l'utilisateur existe déjà
    if UserModel.get_by_username(username):
        raise HTTPException(status_code=409, detail="Ce username existe déjà")
    
    # Permet de créer l'utilisateur
    user = UserService.create_user(
        username=username,
        password_hash=password_hash,
        role_id=role_id
    )
    
    if not user:
        raise HTTPException(status_code=409, detail="Impossible de créer l'utilisateur")

    return JSONResponse(content={
        "message": "Utilisateur créé avec succès", 
        "user": user
    }, status_code=201)

# Cet router permet à un admin de modifier le mot de passe d'un utilisateur
@admin_router.put("/users/{user_id}/password")
@token_required
@role_required("admin")
async def update_user_password(user_id: int, request: Request, current_user: dict):
    data = await request.json()
    new_password = payload.get("new_password")
    
    if not data or "new_password" not in data:
        raise HTTPException(status_code=400, detail="new_password requis")
    
    # Permet de vérifier que l'utilisateur existe
    user = UserModel.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    success = UserModel.update_password(user_id, UserService.hash_password(new_password))
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Échec de la mise à jour du mot de passe"))

    return {"message": "Mot de passe mis à jour avec succès"}

# Cet router permet à un admin de modifier un rôle d'un utilisateur
@admin_router.put("/users/{user_id}/role")
@token_required
@role_required("admin")
async def update_user_role(user_id: int, request: Request, current_user: dict):
    data = await request.json()
    role_id = data.get("role_id")
    
    if not data or "role_id" not in data:
        raise HTTPException(status_code=400, detail="role_id requis")
    
    # Permet de vérifier que l'utilisateur existe
    user = UserModel.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    # Permet de vérifier que le rôle existe
    if not RoleModel.get_by_id(role_id):
        raise HTTPException(status_code=400, detail="Rôle invalide")
    
    # Permet d'empêcher un admin de changer son propre rôle (sécurité)
    if current_user["user_id"] == user_id:
        raise HTTPException(status_code=403, detail="Impossible de modifier son propre rôle")
    
    success = UserModel.update_role(user_id, role_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Échec de la mise à jour du rôle"))

    return {"message": "Rôle mis à jour avec succès"}

# Cet router permet à un admin de supprimer un utilisateur
@admin_router.delete("/users/{user_id}")
@token_required
@role_required("admin")
async def delete_user(user_id: int, current_user: dict):
    if current_user["user_id"] == user_id:
        raise HTTPException(status_code=403, detail="Impossible de supprimer son propre compte")
    
    # Permet de vérifier que l'utilisateur existe
    user = UserModel.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    success = UserModel.delete(user_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Échec de la suppression (parcours ou sites associés)"))

    return {"message": "Utilisateur supprimé avec succès"}