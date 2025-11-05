from fastapi import APIRouter, HTTPException
from app.services.site_service import SiteService
from app.services.parcours_service import ParcoursService
from app.services.referentiel_service import ReferentielService

router = APIRouter(prefix="/api/public", tags=["Public"])

@router.get("/sites", tags=["Sites"])
def get_all_sites():
    return SiteService.get_all_public()

@router.get("/sites/{site_id}", tags=["Sites"])
def get_site(site_id: int):
    site = SiteService.get_by_id_public(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site non trouvé")
    return site

@router.get("/parcours", tags=["Parcours"])
def get_all_parcours():
    return ParcoursService.get_all_public()

@router.get("/parcours/{parcours_id}", tags=["Parcours"])
def get_parcours(parcours_id: int):
    parcours = ParcoursService.get_by_id_public(parcours_id)
    if not parcours:
        raise HTTPException(status_code=404, detail="Parcours non trouvé")
    return parcours

@router.get("/departments", tags=["Referentiels"])
def get_departments():
    return ReferentielService.get_all_departments()

@router.get("/communes", tags=["Referentiels"])
def get_communes():
    return ReferentielService.get_all_communes()
