from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.decorators import token_required, role_required
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.services.parcours_service import ParcoursService
from app.services.site_service import SiteService

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# ===== Schemas =====
class CreateUserSchema(BaseModel):
    username: str
    password: str
    role_id: int

class UpdateUserSchema(BaseModel):
    username: Optional[str] = None
    role_id: Optional[int] = None

class CreateRoleSchema(BaseModel):
    nom_role: str

class UpdateRoleSchema(BaseModel):
    nom_role: str

# ===== Utilisateurs =====
@router.get("/users")
@token_required
@role_required("admin")
def get_users(current_user: dict = None):
    return UserService.get_all()

@router.get("/users/{user_id}")
@token_required
@role_required("admin")
def get_user(user_id: int, current_user: dict = None):
    user = UserService.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

@router.post("/users")
@token_required
@role_required("admin")
def create_user(data: CreateUserSchema, current_user: dict = None):
    return UserService.create(data.username, data.password, data.role_id)

@router.put("/users/{user_id}")
@token_required
@role_required("admin")
def update_user(user_id: int, data: UpdateUserSchema, current_user: dict = None):
    success = UserService.update(user_id, username=data.username, role_id=data.role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé ou rien à mettre à jour")
    return {"message": "Utilisateur mis à jour avec succès"}

@router.delete("/users/{user_id}")
@token_required
@role_required("admin")
def delete_user(user_id: int, current_user: dict = None):
    success = UserService.delete(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"message": "Utilisateur supprimé avec succès"}

# ===== Rôles =====
@router.get("/roles")
@token_required
@role_required("admin")
def get_roles(current_user: dict = None):
    return RoleService.get_all()

@router.post("/roles")
@token_required
@role_required("admin")
def create_role(data: CreateRoleSchema, current_user: dict = None):
    return RoleService.create(data.nom_role)

@router.put("/roles/{role_id}")
@token_required
@role_required("admin")
def update_role(role_id: int, data: UpdateRoleSchema, current_user: dict = None):
    success = RoleService.update(role_id, data.nom_role)
    if not success:
        raise HTTPException(status_code=404, detail="Rôle non trouvé")
    return {"message": "Rôle mis à jour avec succès"}

@router.delete("/roles/{role_id}")
@token_required
@role_required("admin")
def delete_role(role_id: int, current_user: dict = None):
    success = RoleService.delete(role_id)
    if not success:
        raise HTTPException(status_code=400, detail="Impossible de supprimer le rôle")
    return {"message": "Rôle supprimé avec succès"}

# ===== Parcours =====
@router.get("/parcours")
@token_required
@role_required("admin")
def get_all_parcours(current_user: dict = None):
    return ParcoursService.get_all()

@router.get("/parcours/{parcours_id}")
@token_required
@role_required("admin")
def get_parcours(parcours_id: int, current_user: dict = None):
    parcours = ParcoursService.get_by_id(parcours_id)
    if not parcours:
        raise HTTPException(status_code=404, detail="Parcours non trouvé")
    return parcours

# ===== Sites =====
@router.get("/sites")
@token_required
@role_required("admin")
def get_all_sites(current_user: dict = None):
    return SiteService.get_all()

@router.get("/sites/{site_id}")
@token_required
@role_required("admin")
def get_site(site_id: int, current_user: dict = None):
    site = SiteService.get_by_id(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site non trouvé")
    return site
