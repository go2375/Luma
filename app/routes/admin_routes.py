# J’importe les modules nécessaires de FastAPI :
# HTTPException : pour gérer les erreurs HTTP personnalisées
# Depends et Request : pour la gestion des dépendances et l’accès aux requêtes
from pydantic import BaseModel
from typing import List, Optional
# J’importe mes services métier (logique du parcours) et l’authentification
from app.services.parcours_service import ParcoursService
from app.auth import AuthService
from fastapi import APIRouter, HTTPException, Depends, Request

# Je crée un routeur spécifique à la partie Admin de l’API
# Cela me permet de mieux structurer le projet et d’éviter les conflits de routes
router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Définition des schémas Pydantic
# Ce schéma représente la structure d’un site lié à un parcours
# J’ajoute ici longitude et latitude pour que l’admin puisse les voir
class SiteSchema(BaseModel):
    site_id: int
    ordre_visite: int
    longitude: Optional[float] = None
    latitude: Optional[float] = None

# Ce schéma est utilisé pour la création d’un parcours
# Il contient le nom, l’ID du créateur et la liste des sites associés
class ParcoursSchema(BaseModel):
    nom_parcours: str
    createur_id: int
    sites: Optional[List[SiteSchema]] = []

# Ce schéma est utilisé pour la mise à jour partielle d’un parcours
# Les champs sont optionnels pour permettre une modification flexible
class ParcoursUpdateSchema(BaseModel):
    nom_parcours: Optional[str] = None
    sites: Optional[List[SiteSchema]] = None

# Vérification du rôle ADMIN via JWT
# HTTPException : pour gérer les erreurs HTTP personnalisées
def get_current_admin(request: Request):
    """
    Cette fonction est exécutée avant chaque route Admin.
    Elle vérifie si le token JWT est présent, valide et appartient à un administrateur.
    """
    token = request.headers.get("Authorization")
    # Si aucun token n’est envoyé dans l’en-tête, API envoie une erreur 401
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant ou invalide")

     # Je récupère uniquement la valeur du token (en retirant le mot "Bearer")
    token_value = token.split(" ")[1]

    # Je décode le token avec mon AuthService
    decoded = AuthService.decode_token(token_value)
    if not decoded["success"]:
        raise HTTPException(status_code=401, detail=decoded["error"])
    
    # Je vérifie que l’utilisateur possède bien le rôle admin
    user = decoded["data"]
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé : Admin uniquement")

    # Si tout est correct, API renvoie les infos de l’utilisateur
    return user

# Routes Admin
# oute pour récupérer tous les parcours avec latitude/longitude des sites
# Depends pour la gestion des dépendances
@router.get("/parcours", response_model=List[dict])
def get_all_parcours(current_user: dict = Depends(get_current_admin)):
    """
    Je récupère tous les parcours avec les coordonnées GPS des sites.
    Cette route est réservée aux administrateurs.
    """
    parcours_list = ParcoursService.get_all()
    for parcours in parcours_list:
        sites = parcours.get("sites", [])
        for s in sites:
            # Je m’assure que chaque site contient bien latitude et longitude
            s["latitude"] = s.get("latitude")
            s["longitude"] = s.get("longitude")
    return parcours_list

# Get parcours par id avec latitude/longitude : Route pour récupérer un parcours par ID
@router.get("/parcours/{parcours_id}", response_model=dict)
def get_parcours(parcours_id: int, current_user: dict = Depends(get_current_admin)):
    """
    Je récupère un parcours précis grâce à son ID.
    J’inclus les coordonnées GPS pour permettre à l’admin de visualiser la position des sites.
    """
    parcours = ParcoursService.get_by_id(parcours_id, include_prestataire=True)
    if not parcours:
        raise HTTPException(status_code=404, detail="Parcours non trouvé")
    
    # Je reformate les sites pour inclure leurs coordonnées
    sites_with_coords = []
    for site in parcours.get("sites", []):
        sites_with_coords.append({
            "site_id": site.get("site_id"),
            "ordre_visite": site.get("ordre_visite"),
            "longitude": site.get("longitude"),
            "latitude": site.get("latitude")
        })
    parcours["sites"] = sites_with_coords
    return parcours

# Route pour créer un nouveau parcours
@router.post("/parcours", response_model=dict)
def create_parcours(data: ParcoursSchema, current_user: dict = Depends(get_current_admin)):
    """
    Je crée un nouveau parcours à partir des données reçues dans le corps de la requête.
    J’appelle la méthode 'create' du service métier pour effectuer l’insertion dans ma base des données.
    """
    parcours = ParcoursService.create(
        nom_parcours=data.nom_parcours,
        createur_id=data.createur_id,
        sites=[s.dict() for s in data.sites] if data.sites else []
    )
    return parcours

# Route pour mettre à jour un parcours existant
@router.put("/parcours/{parcours_id}", response_model=dict)
def update_parcours(parcours_id: int, data: ParcoursUpdateSchema, current_user: dict = Depends(get_current_admin)):
    """
    Je mets à jour les informations d’un parcours existant.
    Si le parcours n’existe pas ou qu’aucune donnée n’est modifiée, j’envoie une erreur.
    """
    updated_parcours = ParcoursService.update(parcours_id, **data.dict(exclude_unset=True))
    if not updated_parcours:
        raise HTTPException(status_code=404, detail="Parcours non trouvé ou rien à mettre à jour")
    return updated_parcours

# Route pour supprimer un parcours
@router.delete("/parcours/{parcours_id}", response_model=dict)
def delete_parcours(parcours_id: int, current_user: dict = Depends(get_current_admin)):
    """
    Je supprime un parcours de la base de données.
    Cette action est définitive et réservée aux administrateurs.
    """
    deleted = ParcoursService.delete(parcours_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Parcours non trouvé")
    return {"message": "Parcours supprimé avec succès"}
