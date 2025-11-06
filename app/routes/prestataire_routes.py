# from fastapi import APIRouter, HTTPException
# from app.services.site_service import SiteService
# from app.services.parcours_service import ParcoursService
# from app.decorators import token_required, role_required

# router = APIRouter(prefix="/api/prestataire", tags=["Prestataire"])

# # Sites
# @router.get("/sites")
# @token_required
# @role_required("prestataire")
# def get_all_sites(current_user: dict = None):
#     return SiteService.get_all(include_prestataire=True)

# @router.get("/sites/{site_id}")
# @token_required
# @role_required("prestataire")
# def get_site(site_id: int, current_user: dict = None):
#     site = SiteService.get_by_id(site_id, include_prestataire=True)
#     if not site:
#         raise HTTPException(status_code=404, detail="Site non trouvé")
#     return site

# # Parcours
# @router.get("/parcours")
# @token_required
# @role_required("prestataire")
# def get_all_parcours(current_user: dict = None):
#     return ParcoursService.get_all()

# @router.get("/parcours/{parcours_id}")
# @token_required
# @role_required("prestataire")
# def get_parcours(parcours_id: int, current_user: dict = None):
#     parcours = ParcoursService.get_by_id(parcours_id, include_prestataire=True)
#     if not parcours:
#         raise HTTPException(status_code=404, detail="Parcours non trouvé")
#     return parcours