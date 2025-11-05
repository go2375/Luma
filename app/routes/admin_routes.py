from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
from app.services.parcours_service import ParcoursService
from app.auth import AuthService

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# ===== Schemas =====
class SiteSchema(BaseModel):
    site_id: int
    ordre_visite: int

class ParcoursSchema(BaseModel):
    nom_parcours: str
    createur_id: int
    sites: Optional[List[SiteSchema]] = []

class ParcoursUpdateSchema(BaseModel):
    nom_parcours: Optional[str] = None
    sites: Optional[List[SiteSchema]] = None

# ===== Dépendance JWT pour Admin =====
def get_current_admin(request: Request):
    token_header = request.headers.get("Authorization")
    if not token_header or not token_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant ou invalide")

    token = token_header.split(" ")[1]
    decoded = AuthService.decode_token(token)
    if not decoded["success"]:
        raise HTTPException(status_code=401, detail=decoded["error"])

    user = decoded["data"]
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé : Admin uniquement")

    return user

# ===== Routes Admin =====
@router.get("/parcours", response_model=List[dict])
def get_all_parcours(current_user: dict = Depends(get_current_admin)):
    return ParcoursService.get_all()

@router.get("/parcours/{parcours_id}", response_model=dict)
def get_parcours(parcours_id: int, current_user: dict = Depends(get_current_admin)):
    parcours = ParcoursService.get_by_id(parcours_id)
    if not parcours:
        raise HTTPException(status_code=404, detail="Parcours non trouvé")
    return parcours

@router.post("/parcours", response_model=dict)
def create_parcours(data: ParcoursSchema, current_user: dict = Depends(get_current_admin)):
    parcours = ParcoursService.create(
        nom_parcours=data.nom_parcours,
        createur_id=data.createur_id,
        sites=[s.dict() for s in data.sites] if data.sites else []
    )
    return parcours

@router.put("/parcours/{parcours_id}", response_model=dict)
def update_parcours(parcours_id: int, data: ParcoursUpdateSchema, current_user: dict = Depends(get_current_admin)):
    updated = ParcoursService.update(parcours_id, **data.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Parcours non trouvé ou rien à mettre à jour")
    return {"message": "Parcours mis à jour avec succès"}

@router.delete("/parcours/{parcours_id}", response_model=dict)
def delete_parcours(parcours_id: int, current_user: dict = Depends(get_current_admin)):
    deleted = ParcoursService.delete(parcours_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Parcours non trouvé")
    return {"message": "Parcours supprimé avec succès"}
