from fastapi import APIRouter
from app.services.parcours_service import ParcoursService
from app.services.site_service import SiteService  # Assure-toi d'avoir ce service

router = APIRouter(prefix="/api/public", tags=["Public"])

# ===== Parcours publics =====
@router.get("/parcours", response_model=list)
def get_all_parcours_public():
    """
    Récupère tous les parcours accessibles publiquement.
    Accessible sans token.
    """
    return ParcoursService.get_all()

@router.get("/parcours/{parcours_id}", response_model=dict)
def get_parcours_public(parcours_id: int):
    """
    Récupère un parcours par son ID.
    """
    parcours = ParcoursService.get_by_id(parcours_id)
    if not parcours:
        return {"detail": "Parcours non trouvé"}
    return parcours

# ===== Sites publics =====
@router.get("/sites", response_model=list)
def get_all_sites_public():
    """
    Récupère tous les sites accessibles publiquement.
    Accessible sans token.
    """
    return SiteService.get_all()

@router.get("/sites/{site_id}", response_model=dict)
def get_site_public(site_id: int):
    """
    Récupère un site par son ID.
    """
    site = SiteService.get_by_id(site_id)
    if not site:
        return {"detail": "Site non trouvé"}
    return site
