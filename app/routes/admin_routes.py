from fastapi import APIRouter, HTTPException, Body, Path, Depends, Request
from fastapi.responses import JSONResponse
from app.decorators import token_required, role_required
from app.services.role_service import RoleService
from app.services.user_service import UserService
from app.models import RoleModel, UserModel

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# ===== RÔLES =====
@router.get("/roles")
@token_required
@role_required("admin")
async def get_roles(current_user: dict):
    result = RoleService.get_all_roles(user_id=current_user["user_id"])
    if not result["success"]:
        raise HTTPException(status_code=403, detail=result["error"])
    return JSONResponse(content=result)

@router.post("/roles")
@token_required
@role_required("admin")
async def create_role(current_user: dict, nom_role: str = Body(..., description="Nom du rôle à créer")):
    result = RoleService.create_role(nom_role=nom_role, user_id=current_user["user_id"])
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return JSONResponse(status_code=201, content=result)

@router.put("/roles/{role_id}")
@token_required
@role_required("admin")
async def update_role(current_user: dict, role_id: int = Path(...), nom_role: str = Body(...)):
    result = RoleService.update_role(role_id=role_id, nom_role=nom_role, user_id=current_user["user_id"])
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return JSONResponse(content=result)

@router.delete("/roles/{role_id}")
@token_required
@role_required("admin")
async def delete_role(current_user: dict, role_id: int = Path(...)):
    result = RoleService.delete_role(role_id=role_id, user_id=current_user["user_id"])
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return JSONResponse(content=result)

# ===== UTILISATEURS =====
@router.get("/users")
@token_required
@role_required("admin")
async def get_users(current_user: dict):
    users = UserModel.get_all()
    return JSONResponse(content={"success": True, "users": users})

@router.get("/users/{user_id}")
@token_required
@role_required("admin")
async def get_user(current_user: dict, user_id: int = Path(...)):
    user = UserService.get_user_info(user_id)
    if not user or not user["success"]:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return JSONResponse(content=user)

# ===== CREATE USER =====
@router.post("/users")
@token_required
@role_required("admin")
async def create_user(
    request: Request,  # Ajoutez cette ligne
    current_user: dict,
    username: str = Body(..., example="prestataire1"),
    password: str = Body(..., example="Prest123!"),
    role_id: int = Body(..., example=2)
):
    # Vérifier que le rôle existe
    roles = RoleModel.get_all()
    role = next((r for r in roles if r["role_id"] == role_id), None)
    if not role:
        raise HTTPException(status_code=400, detail="Rôle introuvable")

    # Créer l'utilisateur
    result = UserService.create_user(username=username, password=password, role_id=role_id)
    if not result["success"]:
        raise HTTPException(status_code=409, detail=result["error"])

    return JSONResponse(content={
        "success": True,
        "message": "Utilisateur créé",
        "user": {
            "user_id": result["user"]["user_id"],
            "username": result["user"]["username"],
            "role_id": role_id
        }
    })

# ===== AUTRES ROUTES UTILISATEURS =====
@router.put("/users/{user_id}/password")
@token_required
@role_required("admin")
async def update_user_password(current_user: dict, user_id: int = Path(...), new_password: str = Body(...)):
    result = UserService.update_password(user_id, new_password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return JSONResponse(content=result)

@router.put("/users/{user_id}/role")
@token_required
@role_required("admin")
async def update_user_role(current_user: dict, user_id: int = Path(...), role_id: int = Body(...)):
    if current_user["user_id"] == user_id:
        raise HTTPException(status_code=403, detail="Impossible de modifier son propre rôle")

    user = UserModel.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if not RoleModel.get_by_id(role_id):
        raise HTTPException(status_code=400, detail="Rôle invalide")

    success = UserModel.update_role(user_id, role_id)
    if not success:
        raise HTTPException(status_code=400, detail="Échec de la mise à jour du rôle")

    return JSONResponse(content={"success": True, "message": "Rôle utilisateur mis à jour"})

@router.delete("/users/{user_id}")
@token_required
@role_required("admin")
async def delete_user(current_user: dict, user_id: int = Path(...)):
    if current_user["user_id"] == user_id:
        raise HTTPException(status_code=403, detail="Impossible de supprimer son propre compte")

    user = UserModel.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    success = UserModel.delete(user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Échec de la suppression (parcours ou sites associés)")

    return JSONResponse(content={"success": True, "message": "Utilisateur supprimé"})