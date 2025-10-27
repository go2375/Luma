from fastapi import APIRouter, HTTPException, Request, Body, Path
from fastapi.responses import JSONResponse
from app.decorators import token_required
from app.services.site_service import SiteService
from app.services.user_service import UserService
from app.services.parcours_service import ParcoursService
from app.models import CommuneModel, DepartmentModel

# On crée le router
router = APIRouter(
    prefix="/api",
    tags=["Public"]
)

## Permet de créer des routers publiques qui ne nécessitent pas d'authentification et permettent de récupérer les données anonymisées sur les sites touristiques
@router.get("/sites", tags=["Sites publics"])
# Permet de récupérer les données anonymisées sur tous les sites touristiques
async def get_all_sites():
    """
    Récupère **la liste de tous les sites disponibles publiquement.**
    """
    sites = SiteService.get_all_sites_public()
    return {"success": True, "sites": sites}


@router.get("/sites/{site_id}", tags=["Sites publics"])
# Permet de récupérer les données anonymisées sur un site spécifique
async def get_site(
    site_id: int = Path(..., description="Identifiant unique du site", example=12)
):
    """
    Récupère les **détails d’un site public** à partir de son ID.
    """
    site = SiteService.get_site_by_id_public(site_id)
    
    if not site:
        raise HTTPException(status_code=404, detail="Site introuvable")
    
    return {"success": True, "site": site}

@router.get("/communes", tags=["Référentiels"])
# Permet de récupérer toutes les communes
async def get_all_communes():
    """
    Récupère **toutes les communes** disponibles.
    """
    communes = CommuneModel.get_all()
    return {"success": True, "communes": communes}


@router.get("/departments", tags=["Référentiels"])
# Permet de récupérer tous les départements
async def get_all_departments():
    """
    Récupère **tous les départements** disponibles.
    """
    departments = DepartmentModel.get_all()
    return {"success": True, "departments": departments}


# Permet de gérer des parcours qui nécessitent une authentification et permet aux utilisateurs authentifiés d'accéder à leurs parcours
@router.get("/parcours", tags=["Parcours"])
@token_required
# Permet de récupérer tous les parcours d'un utilisateur authentifié
async def get_my_parcours(current_user: dict):
    """
    Récupère **tous les parcours créés par l’utilisateur connecté.**
    """
    parcours_list = ParcoursService.get_user_parcours(current_user["user_id"])
    return {"success": True, "parcours": parcours_list}


@router.get("/parcours/{parcours_id}", tags=["Parcours"])
@token_required
# Permet à un utilisateur authentifié de récupérer un parcours avec tous les sites
def get_parcours_detail(
    parcours_id: int = Path(..., description="ID du parcours à consulter", example=42),
    current_user: dict = None
):
    """
    Récupère les **détails d’un parcours** spécifique de l’utilisateur connecté.
    """
    result = ParcoursService.get_parcours_by_id(parcours_id, current_user["user_id"])
    
    if not result["success"]:
        status_code = 403 if "Accès refusé" in result["error"] else 404
        raise HTTPException(status_code=status_code, detail=result["error"])
    return {"success": True, "parcours": result["parcours"]}

@router.post("/parcours", tags=["Parcours"])
@token_required
# Permet de créer un nouveau parcours
def create_parcours(
    nom_parcours: str = Body(..., description="Nom du parcours à créer", example="Parcours nature et patrimoine"),
    sites: list[int] = Body(None, description="Liste des IDs de sites à inclure dans le parcours", example=[1, 2, 3]),
    current_user: dict = None
):
    """
    Crée un **nouveau parcours personnalisé** pour l’utilisateur connecté.
    """
    
    if not data or "nom_parcours" not in data:
        raise HTTPException(status_code=400, detail="nom_parcours requis")
    
    result = ParcoursService.create_parcours(
        nom_parcours=data["nom_parcours"],
        createur_id=current_user["user_id"],
        sites=data.get("site")
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return JSONResponse(status_code=201, content={
        "success": True,
        "message": "Parcours créé avec succès",
        "parcours_id": result["parcours_id"]
    })

@router.put("/parcours/{parcours_id}", tags=["Parcours"])
@token_required
# Permet de modifier le nom d'un parcours
async def update_parcours(
    parcours_id: int = Path(..., description="ID du parcours à modifier", example=7),
    nom_parcours: str = Body(..., description="Nouveau nom du parcours", example="Découverte des sentiers"),
    current_user: dict = None
):
    """
    Met à jour le **nom d’un parcours existant** appartenant à l’utilisateur.
    """
    if not data or "nom_parcours" not in data:
        raise HTTPException(status_code=400, detail="nom_parcours requis")
    
    # On effectue une mise à jour
    result = ParcoursService.update_parcours(
        parcours_id=parcours_id,
        user_id=current_user["user_id"],
        nom_parcours=data["nom_parcours"]
    )
    
    if not result["success"]:
        status_code = 403 if "Accès refusé" in result["error"] else 404
        raise HTTPException(status_code=status_code, detail=result["error"])
    
    return {"success": True, "message": "Parcours mis à jour avec succès"}

@router.delete("/parcours/{parcours_id}", tags=["Parcours"])
@token_required
# Permet de supprimer un parcours
async def delete_parcours(
    parcours_id: int = Path(..., description="ID du parcours à supprimer", example=8),
    current_user: dict = None
):
    """
    Supprime un **parcours appartenant à l’utilisateur connecté.**
    """
    result = ParcoursService.delete_parcours(
        parcours_id=parcours_id,
        user_id=current_user["user_id"]
    )
    
    if not result["success"]:
        status_code = 403 if "Accès refusé" in result["error"] else 404
        raise HTTPException(status_code=status_code, detail=result["error"])
    return {"success": True, "message": "Parcours supprimé avec succès"}

@router.delete("/parcours/{parcours_id}/sites/{site_id}", tags=["Parcours"])
@token_required
# Permet de retirer un site d'un parcours
def remove_site_from_parcours(
    parcours_id: int = Path(..., description="ID du parcours", example=8),
    site_id: int = Path(..., description="ID du site à retirer", example=2),
    current_user: dict = None
):
    """
    Retire un **site spécifique d’un parcours** appartenant à l’utilisateur.
    """
    result = ParcoursService.remove_site_from_parcours(
        parcours_id=parcours_id,
        user_id=current_user["user_id"],
        site_id=site_id
    )
    
    if not result["success"]:
        status_code = 403 if "Accès refusé" in result["error"] else 404
        raise HTTPException(status_code=status_code, detail=result["error"])
    return {"success": True, "message": "Site retiré du parcours avec succès"}

## Permet de gérer les comptes des utilisateurs

@router.get("/me", tags=["Profil utilisateur"])
@token_required
# Permet à un utilisateur de récupérer son profil
async def get_my_profile(current_user: dict):
    """
    Récupère les **informations du profil** de l’utilisateur connecté.
    """
    user = UserService.get_user_info(current_user["user_id"])
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return {"success": True, "user": user}


@router.put("/me/password", tags=["Profil utilisateur"])
@token_required
# Permet à un utilisateur de modifier son mot de passe
async def update_my_password(
    old_password: str = Body(..., description="Ancien mot de passe", example="OldPass123!"),
    new_password: str = Body(..., description="Nouveau mot de passe", example="NewPass456!"),
    current_user: dict = None
):
    """
    Met à jour le **mot de passe** de l’utilisateur connecté.
    """    
    if not data or "old_password" not in data or "new_password" not in data:
        raise HTTPException(status_code=400, detail="old_password et new_password requis")
    
    result = UserService.update_password(
        user_id=current_user["user_id"],
        old_password=data["old_password"],
        new_password=data["new_password"]
    )
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return {"success": True, "message": "Mot de passe mis à jour avec succès"}


@router.delete("/me", tags=["Profil utilisateur"])
@token_required
# Permet d'anonymiser ou marquer comme supprimé un compte par un utilisateur
async def delete_my_account(
    password: str = Body(..., description="Mot de passe pour confirmer la suppression", example="MySecret123!"),
    anonymize: bool = Body(False, description="Anonymiser plutôt que supprimer définitivement le compte", example=False),
    current_user: dict = None
):
    """
    Supprime ou **anonymise le compte** de l’utilisateur connecté.  
    Nécessite la saisie du mot de passe actuel pour confirmation.
    """    
    # On supprime le compte
    result = UserService.delete_account(
        user_id=current_user["user_id"],
        password=data["password"],
        anonymize=anonymize
    )
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    if result.get("method") == "anonymized":
        return {"success": True, "message": "Compte anonymisé avec succès", "info": result["message"]}
    
    return {"success": True, "message": "Compte supprimé avec succès"}