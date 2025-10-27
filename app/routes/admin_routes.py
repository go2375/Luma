from fastapi import APIRouter, HTTPException, Body, Path
from fastapi.responses import JSONResponse
from app.decorators import token_required, role_required
from app.services.role_service import RoleService
from app.services.user_service import UserService
from app.models import RoleModel, UserModel

### Ce router permet à un admin de gérer des rôles et des comptes des utilisateurs
router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)

## Ces routers permettent à un admin de gérer des rôles des utilisateurs
# Cet router permet à un admin de récupérer tous les rôles
@router.get("/roles")
@token_required
@role_required("admin")
async def get_roles(current_user: dict):
    """
    Récupère la liste complète des rôles disponibles.
    """
    roles = RoleService.get_all_roles()
    return {"roles": roles}

# Cet router permet à un admin de créer un nouveau rôle
@router.post("/roles")
@token_required
@role_required("admin")
async def create_role(
    current_user: dict,
    nom_role: str = Body(..., description="Nom du rôle à créer", example="visiteur")
):
    """
    Crée un nouveau rôle dans le système.
    """
    
    if not data or "nom_role" not in data:
        raise HTTPException(status_code=400, detail="nom_role requis")
    
    result = RoleService.create_role(nom_role)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Échec de la création"))
    
    return JSONResponse(
        status_code=201,
        content={"success": True, "message": "Rôle créé", "role": result["role"]}
    )

# Cet router permet à un admin de modifier un rôle existant
@router.put("/roles/{role_id}")
@token_required
@role_required("admin")
async def update_role(
    current_user: dict,
    role_id: int = Path(..., description="ID du rôle à modifier", example=2),
    nom_role: str = Body(..., description="Nouveau nom du rôle", example="visiteur_pro")
):
    """
    Met à jour le nom d’un rôle existant.
    """
    # Permet de vérifier que le rôle existe
    if not RoleModel.get_by_id(role_id):
        raise HTTPException(status_code=404, detail="Rôle introuvable")
    
    result = RoleService.update_role(role_id, nom_role)
    
    if not result["success"]:
       raise HTTPException(status_code=400, detail=result.get("error", "Échec de la mise à jour"))

    return {"message": "Rôle mis à jour avec succès"}

# Cet router permet à un admin de supprimer un rôle existant
@router.delete("/roles/{role_id}", tags=["Rôles"])
@token_required
@role_required("admin")
async def delete_role(
    current_user: dict,
    role_id: int = Path(..., description="ID du rôle à supprimer", example=2)
):
    """
    Supprime un rôle (à l'exception des rôles clés pour le système).
    """
    result = RoleService.delete_role(role_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Échec de la suppression"))

    return {"success": True, "message": "Rôle supprimé"}

## Ces routers permettent à un admin de gérer des comptes des utilisateurs
# Cet router permet à un admin de récupérer tous les utilisateurs
@router.get("/users")
@token_required
@role_required("admin")
async def get_users(current_user: dict):
    """
    Récupère la liste de tous les utilisateurs actifs.
    """
    users = UserModel.get_all()
    return {"users": users}

# Cet router permet à un admin de récupérer les données d'un utilisateur spécifique
@router.get("/users/{user_id}")
@token_required
@role_required("admin")
async def get_user(
    current_user: dict,
    user_id: int = Path(..., description="ID de l'utilisateur à consulter", example=7)
):
    """
    Récupère les informations détaillées d’un utilisateur par son ID.
    """
    user = UserService.get_user_info(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    return {"success": True, "user": user}

# Cet router permet à un admin de créer un nouvel utilisateur
@router.post("/users", tags=["Utilisateurs"])
@token_required
@role_required("admin")
async def create_user(
    current_user: dict,
    username: str = Body(..., description="Nom d'utilisateur", example="jean123"),
    password: str = Body(..., description="Mot de passe de l'utilisateur", example="Password123!"),
    role_id: int = Body(..., description="ID du rôle attribué", example=2)
):
    """
    Crée un nouvel utilisateur (admin, prestataire ou visiteur).
    """    
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

    return JSONResponse(
        status_code=201,
        content={"success": True, "message": "Utilisateur créé", "user": user}
    )

# Cet router permet à un admin de modifier le mot de passe d'un utilisateur
@router.put("/users/{user_id}/password", tags=["Utilisateurs"])
@token_required
@role_required("admin")
async def update_user_password(
    current_user: dict,
    user_id: int = Path(..., description="ID de l'utilisateur dont le mot de passe doit être changé", example=10),
    new_password: str = Body(..., description="Nouveau mot de passe", example="NouveauPass123!")
):
    """
    Met à jour le mot de passe d’un utilisateur (par un administrateur).
    """
    result = UserService.update_password(user_id, old_password=None, new_password=new_password)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Échec de la mise à jour du mot de passe"))

    return {"success": True, "message": "Mot de passe mis à jour"}

# Cet router permet à un admin de modifier un rôle d'un utilisateur
@router.put("/users/{user_id}/role", tags=["Utilisateurs"])
@token_required
@role_required("admin")
async def update_user_role(
    current_user: dict,
    user_id: int = Path(..., description="ID de l'utilisateur à modifier", example=6),
    role_id: int = Body(..., description="Nouveau rôle ID à attribuer", example=3)
):
    """
     Met à jour le rôle d’un utilisateur (sauf soi-même).
    """
    # Permet d'empêcher un admin de changer son propre rôle (sécurité)
    if current_user["user_id"] == user_id:
        raise HTTPException(status_code=403, detail="Impossible de modifier son propre rôle")
    
    # Permet de vérifier que l'utilisateur existe
    user = UserModel.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    # Permet de vérifier que le rôle existe
    if not RoleModel.get_by_id(role_id):
        raise HTTPException(status_code=400, detail="Rôle invalide")
    
    
    result = UserModel.update_role(user_id, role_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Échec de la mise à jour du rôle"))

    return {"success": True, "message": "Rôle utilisateur mis à jour"}

# Cet router permet à un admin de supprimer un utilisateur
@router.delete("/users/{user_id}")
@token_required
@role_required("admin")
async def delete_user(
    current_user: dict,
    user_id: int = Path(..., description="ID de l'utilisateur à supprimer", example=12)
):
    """
    Supprime un utilisateur (impossible de se supprimer soi-même).
    """
    if current_user["user_id"] == user_id:
        raise HTTPException(status_code=403, detail="Impossible de supprimer son propre compte")
    
    # Permet de vérifier que l'utilisateur existe
    user = UserModel.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    result = UserModel.delete(user_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Échec de la suppression (parcours ou sites associés)"))

    return {"success": True, "message": "Utilisateur supprimé"}