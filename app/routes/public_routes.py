from fastapi import APIRouter, HTTPException, Body, Path
from fastapi.responses import JSONResponse
from app.decorators import token_required
from app.services.site_service import SiteService
from app.services.user_service import UserService
from app.services.parcours_service import ParcoursService
from app.models import CommuneModel, DepartmentModel

router = APIRouter(
    prefix="/api",
    tags=["Public"]
)

# ------------------- Sites publics -------------------
@router.get("/sites", tags=["Sites publics"])
async def get_all_sites():
    sites = SiteService.get_all_sites_public()
    return {"success": True, "sites": sites}

@router.get("/sites/{site_id}", tags=["Sites publics"])
async def get_site(
    site_id: int = Path(..., description="Identifiant unique du site", example=12)
):
    site = SiteService.get_site_by_id_public(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site introuvable")
    return {"success": True, "site": site}

# ------------------- Référentiels -------------------
@router.get("/communes", tags=["Référentiels"])
async def get_all_communes():
    communes = CommuneModel.get_all()
    return {"success": True, "communes": communes}

@router.get("/departments", tags=["Référentiels"])
async def get_all_departments():
    departments = DepartmentModel.get_all()
    return {"success": True, "departments": departments}

# ------------------- Parcours utilisateur -------------------
@router.get("/parcours", tags=["Parcours"])
@token_required
async def get_my_parcours(current_user: dict):
    parcours_list = ParcoursService.get_user_parcours(current_user["user_id"])
    return {"success": True, "parcours": parcours_list}

@router.get("/parcours/{parcours_id}", tags=["Parcours"])
@token_required
async def get_parcours_detail(
    parcours_id: int = Path(..., description="ID du parcours à consulter", example=42),
    current_user: dict = None
):
    result = ParcoursService.get_parcours_by_id(parcours_id, current_user["user_id"])
    if not result["success"]:
        status_code = 403 if "Accès refusé" in result["error"] else 404
        raise HTTPException(status_code=status_code, detail=result["error"])
    return {"success": True, "parcours": result["parcours"]}

@router.post("/parcours", tags=["Parcours"])
@token_required
async def create_parcours(
    nom_parcours: str = Body(..., description="Nom du parcours", example="Parcours nature"),
    sites: list[int] = Body(default=[], description="Liste des IDs de sites à inclure"),
    current_user: dict = None
):
    if not nom_parcours.strip():
        raise HTTPException(status_code=400, detail="nom_parcours requis")

    result = ParcoursService.create_parcours(
        nom_parcours=nom_parcours,
        createur_id=current_user["user_id"],
        sites=sites
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return JSONResponse(status_code=201, content={
        "success": True,
        "message": "Parcours créé avec succès",
        "parcours_id": result.get("parcours_id")
    })

@router.put("/parcours/{parcours_id}", tags=["Parcours"])
@token_required
async def update_parcours(
    parcours_id: int = Path(..., description="ID du parcours à modifier", example=7),
    nom_parcours: str = Body(..., description="Nouveau nom du parcours", example="Découverte"),
    current_user: dict = None
):
    if not nom_parcours.strip():
        raise HTTPException(status_code=400, detail="nom_parcours requis")

    result = ParcoursService.update_parcours(
        parcours_id=parcours_id,
        user_id=current_user["user_id"],
        nom_parcours=nom_parcours
    )

    if not result["success"]:
        status_code = 403 if "Accès refusé" in result["error"] else 404
        raise HTTPException(status_code=status_code, detail=result["error"])
    return {"success": True, "message": "Parcours mis à jour avec succès"}

@router.delete("/parcours/{parcours_id}", tags=["Parcours"])
@token_required
async def delete_parcours(
    parcours_id: int = Path(..., description="ID du parcours à supprimer", example=8),
    current_user: dict = None
):
    result = ParcoursService.delete_parcours(parcours_id, current_user["user_id"])
    if not result["success"]:
        status_code = 403 if "Accès refusé" in result["error"] else 404
        raise HTTPException(status_code=status_code, detail=result["error"])
    return {"success": True, "message": "Parcours supprimé avec succès"}

@router.delete("/parcours/{parcours_id}/sites/{site_id}", tags=["Parcours"])
@token_required
async def remove_site_from_parcours(
    parcours_id: int = Path(..., description="ID du parcours", example=8),
    site_id: int = Path(..., description="ID du site à retirer", example=2),
    current_user: dict = None
):
    result = ParcoursService.remove_site_from_parcours(
        parcours_id=parcours_id,
        user_id=current_user["user_id"],
        site_id=site_id
    )
    if not result["success"]:
        status_code = 403 if "Accès refusé" in result["error"] else 404
        raise HTTPException(status_code=status_code, detail=result["error"])
    return {"success": True, "message": "Site retiré du parcours avec succès"}

# ------------------- Profil utilisateur -------------------
@router.get("/me", tags=["Profil utilisateur"])
@token_required
async def get_my_profile(current_user: dict):
    user = UserService.get_user_info(current_user["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return {"success": True, "user": user}

@router.put("/me/password", tags=["Profil utilisateur"])
@token_required
async def update_my_password(
    old_password: str = Body(..., description="Ancien mot de passe", example="OldPass123!"),
    new_password: str = Body(..., description="Nouveau mot de passe", example="NewPass456!"),
    current_user: dict = None
):
    auth_check = UserService.authenticate(current_user["username"], old_password)
    if not auth_check["success"]:
        raise HTTPException(status_code=401, detail="Ancien mot de passe incorrect")

    result = UserService.update_password(current_user["user_id"], new_password)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return {"success": True, "message": "Mot de passe mis à jour avec succès"}

@router.delete("/me", tags=["Profil utilisateur"])
@token_required
async def delete_my_account(
    password: str = Body(..., description="Mot de passe pour confirmer", example="MySecret123!"),
    anonymize: bool = Body(False, description="Anonymiser le compte au lieu de le supprimer"),
    current_user: dict = None
):
    auth_check = UserService.authenticate(current_user["username"], password)
    if not auth_check["success"]:
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    result = UserService.delete_account(
        user_id=current_user["user_id"],
        anonymize=anonymize
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    if result.get("method") == "anonymized":
        return {"success": True, "message": "Compte anonymisé avec succès"}
    return {"success": True, "message": "Compte supprimé avec succès"}
