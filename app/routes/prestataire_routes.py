from fastapi import APIRouter, HTTPException, Request
from app.services.site_service import SiteService
from app.services.parcours_service import ParcoursService
from app.decorators import token_required, role_required

router = APIRouter(prefix="/api/prestataire", tags=["Prestataire"])

# ===== Sites pour prestataires =====
@router.get("/sites")
@token_required
@role_required("prestataire")
def get_all_sites(current_user: dict = None):
    return SiteService.get_all(include_prestataire=True)

@router.get("/sites/{site_id}")
@token_required
@role_required("prestataire")
def get_site(site_id: int, current_user: dict = None):
    site = SiteService.get_by_id(site_id, include_prestataire=True)
    if not site:
        raise HTTPException(status_code=404, detail="Site non trouvé")
    return site
