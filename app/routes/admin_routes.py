# admin_parcours_sites_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.parcours_service import ParcoursService
from app.services.site_service import SiteService
from app.decorators import token_required, role_required

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# ===== Parcours Schemas =====
class ParcoursCreateSchema(BaseModel):
    nom_parcours: str
    createur_id: int
    sites: Optional[List[dict]] = None  # liste de {'site_id': int, 'ordre_visite': int}

class ParcoursUpdateSchema(BaseModel):
    nom_parcours: Optional[str] = None

# ===== Sites Schemas =====
class SiteCreateSchema(BaseModel):
    nom_site: str
    commune_id: int
    prestataire_id: Optional[int] = None
    est_activite: Optional[bool] = False
    est_lieu: Optional[bool] = False
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class SiteUpdateSchema(BaseModel):
    nom_site: Optional[str] = None
    commune_id: Optional[int] = None
    prestataire_id: Optional[int] = None
    est_activite: Optional[bool] = None
    est_lieu: Optional[bool] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# ===== PARCOURS =====
@router.get("/parcours", response_model=List[dict])
@token_required
@role_required("admin")
def get_all_parcours(current_user: dict = None):
    return ParcoursService.get_all()

@router.get("/parcours/{parcours_id}", response_model=dict)
@token_required
@role_required("admin")
def get_parcours(parcours_id: int, current_user: dict = None):
    parcours = ParcoursService.get_by_id(parcours_id, include_prestataire=True)
    if not parcours:
        raise HTTPException(status_code=404, detail="Parcours non trouvé")
    return parcours

@router.post("/parcours", response_model=dict, status_code=201)
@token_required
@role_required("admin")
def create_parcours(data: ParcoursCreateSchema, current_user: dict = None):
    parcours = ParcoursService.create(data.nom_parcours, data.createur_id, data.sites)
    return {"message": f"Parcours {parcours['parcours_id']} créé", "parcours_id": parcours["parcours_id"]}

@router.put("/parcours/{parcours_id}", response_model=dict)
@token_required
@role_required("admin")
def update_parcours(parcours_id: int, data: ParcoursUpdateSchema, current_user: dict = None):
    update_data = data.dict(exclude_unset=True)
    success = ParcoursService.update(parcours_id, **update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Parcours non trouvé ou aucun champ à mettre à jour")
    return {"message": f"Parcours {parcours_id} mis à jour"}

@router.delete("/parcours/{parcours_id}", response_model=dict)
@token_required
@role_required("admin")
def delete_parcours(parcours_id: int, current_user: dict = None):
    success = ParcoursService.delete(parcours_id)
    if not success:
        raise HTTPException(status_code=404, detail="Parcours non trouvé")
    return {"message": f"Parcours {parcours_id} supprimé"}

# ===== SITES =====
@router.get("/sites", response_model=List[dict])
@token_required
@role_required("admin")
def get_all_sites(current_user: dict = None):
    return SiteService.get_all(include_prestataire=True)

@router.get("/sites/{site_id}", response_model=dict)
@token_required
@role_required("admin")
def get_site(site_id: int, current_user: dict = None):
    site = SiteService.get_by_id(site_id, include_prestataire=True)
    if not site:
        raise HTTPException(status_code=404, detail="Site non trouvé")
    return site

@router.post("/sites", response_model=dict, status_code=201)
@token_required
@role_required("admin")
def create_site(data: SiteCreateSchema, current_user: dict = None):
    site = SiteService.create(**data.dict())
    return {"message": f"Site {site['site_id']} créé", "site_id": site["site_id"]}

@router.put("/sites/{site_id}", response_model=dict)
@token_required
@role_required("admin")
def update_site(site_id: int, data: SiteUpdateSchema, current_user: dict = None):
    update_data = data.dict(exclude_unset=True)
    success = SiteService.update(site_id, **update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Site non trouvé ou aucun champ à mettre à jour")
    return {"message": f"Site {site_id} mis à jour"}

@router.delete("/sites/{site_id}", response_model=dict)
@token_required
@role_required("admin")
def delete_site(site_id: int, current_user: dict = None):
    success = SiteService.delete(site_id)
    if not success:
        raise HTTPException(status_code=404, detail="Site non trouvé")
    return {"message": f"Site {site_id} supprimé"}
