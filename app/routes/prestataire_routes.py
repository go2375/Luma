from fastapi import APIRouter, HTTPException, Body, Path
from fastapi.responses import JSONResponse
from app.decorators import token_required, role_required
from app.services.site_service import SiteService

# Cet router permet aux prestataires de gérer leurs sites touristiques
router = APIRouter(
    prefix="/api/prestataire",
    tags=["Prestataire"]
)

# Cet router permet à un prestataire de récupérer tous les sites appartenant à ce prestataire
@router.get("/sites", tags=["Sites du prestataire"])
@token_required
@role_required("prestataire")
async def get_my_sites(current_user: dict):
    """
    Récupère **tous les sites appartenant au prestataire connecté.**
    """
    sites = SiteService.get_sites_by_prestataire(current_user["user_id"])
    return {"success": True, "sites": sites}

# Cet router permet à un prestataire de récupérer un site spécifique choisi
@router.get("/sites/{site_id}", tags=["Sites du prestataire"])
@token_required
@role_required("prestataire")
async def get_site(
    site_id: int = Path(..., description="Identifiant unique du site", example=101),
    current_user: dict = None
):
    """
    Récupère les **détails d’un site spécifique** appartenant au prestataire connecté.
    """
    mes_sites = SiteService.get_sites_by_prestataire(current_user["user_id"])
    
    # Permet de vérifier que le site appartient au prestataire
    site = next((s for s in mes_sites if s["site_id"] == site_id), None)

    if not site:
        raise HTTPException(status_code=404, detail="Site introuvable ou accès refusé")
    return {"success": True, "site": site}

# Cet router permet à un prestataire de créer un nouveau site touristique
@router.post("/sites", tags=["Sites du prestataire"])
@token_required
@role_required("prestataire")
def create_site(
    nom_site: str = Body(..., description="Nom du site à créer", example="Gîte de la Forêt"),
    commune_id: int = Body(..., description="Identifiant de la commune du site", example=12),
    type_site: str = Body(None, description="Type de site (ex: hébergement, musée...)", example="Hébergement"),
    description: str = Body(None, description="Description du site", example="Gîte rural avec vue sur la forêt."),
    latitude: float = Body(None, description="Latitude du site", example=48.8566),
    longitude: float = Body(None, description="Longitude du site", example=2.3522),
    current_user: dict = None
):
    """
    Crée un **nouveau site** pour le prestataire connecté.
    """
    # Permet de créer le site avec le prestataire_id de l'utilisateur connecté
    result = SiteService.create_site(
        nom_site=data["nom_site"],
        commune_id=data["commune_id"],
        prestataire_id=current_user["user_id"],
        type_site=data.get("type_site"),
        description=data.get("description"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude")
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return JSONResponse(status_code=201, content={
        "success": True,
        "message": "Site créé avec succès",
        "site_id": result['site_id']
    })

# Cet router permet à un prestataire de modifier son site touristique
@router.put("/sites/{site_id}", tags=["Sites du prestataire"])
@token_required
@role_required("prestataire")
async def update_site(
    site_id: int = Path(..., description="Identifiant du site à modifier", example=55),
    nom_site: str = Body(None, description="Nouveau nom du site", example="Maison du Lac"),
    type_site: str = Body(None, description="Nouveau type du site", example="Restaurant"),
    description: str = Body(None, description="Nouvelle description du site", example="Restaurant panoramique au bord du lac."),
    latitude: float = Body(None, description="Nouvelle latitude", example=43.6045),
    longitude: float = Body(None, description="Nouvelle longitude", example=1.4442),
    commune_id: int = Body(None, description="Nouvel identifiant de commune", example=29),
    current_user: dict = None
):
    """
    Met à jour les **informations d’un site** appartenant au prestataire connecté.
    """
    data = {
        "nom_site": nom_site,
        "type_site": type_site,
        "description": description,
        "latitude": latitude,
        "longitude": longitude,
        "commune_id": commune_id
    }
    # Permet de filtrer les champs vides
    data = {k: v for k, v in data.items() if v is not None}
    
    if not data:
        raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour fournie.")
    
    result = SiteService.update_site(
        site_id=site_id,
        prestataire_id=current_user["user_id"],
        **data
    )
    
    if not result["success"]:
        status_code = 403 if "Accès refusé" in result["error"] else 400
        raise HTTPException(status_code=status_code, detail=result["error"])
    
    return {"success": True, "message": "Site mis à jour avec succès"}


# Cet router permet à un prestataire de supprimer son site touristique
@router.delete("/sites/{site_id}", tags=["Sites du prestataire"])
@token_required
@role_required("prestataire")
async def delete_site(
    site_id: int = Path(..., description="Identifiant du site à supprimer", example=45),
    current_user: dict = None
):
    """
    Supprime un **site appartenant au prestataire connecté.**
    """
    result = SiteService.delete_site(
        site_id=site_id,
        prestataire_id=current_user["user_id"]
    )

    if not result["success"]:
        status_code = 403 if "Accès refusé" in result["error"] else 400
        raise HTTPException(status_code=status_code, detail=result["error"])
    
    return {"success": True, "message": "Site supprimé avec succès"}