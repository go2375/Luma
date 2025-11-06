# J’importe APIRouter depuis FastAPI.
# Cela me permet de regrouper toutes mes routes publiques dans un seul "module".
from fastapi import APIRouter
# J’importe mes services métiers :
# ParcoursService : pour accéder aux parcours touristiques
# SiteService : pour accéder aux sites touristiques
from app.services.parcours_service import ParcoursService
from app.services.site_service import SiteService

# Je crée un routeur spécifique pour les routes publiques
# Celles-ci ne nécessitent pas d’authentification (pas de token requis)
router = APIRouter(prefix="/api/public", tags=["Public"])

# Routes publiques : Parcours touristiques
@router.get("/parcours", response_model=list)
def get_all_parcours_public():
    """
    Cette route permet de récupérer la liste de tous les parcours touristiques.
    Elle est accessible librement, sans connexion ni token JWT.
    Les données sensibles comme la latitude et la longitude sont masquées
    pour respecter la politique de confidentialité (RGPD).
    """
    return ParcoursService.get_all()

@router.get("/parcours/{parcours_id}", response_model=dict)
def get_parcours_public(parcours_id: int):
    """
    Cette route permet de récupérer le détail d’un parcours spécifique à partir de son ID.
    Si le parcours n’existe pas, je renvoie un message d’erreur clair.
    Accessible sans authentification.
    """
    parcours = ParcoursService.get_by_id(parcours_id)
    if not parcours:
        return {"detail": "Parcours non trouvé"}
    return parcours

# Routes publiques : Sites touristiques
@router.get("/sites", response_model=list)
def get_all_sites_public():
    """
    Cette route renvoie la liste complète des sites touristiques disponibles.
    Tout le monde peut y accéder sans être connecté.
    Les coordonnées GPS sont masquées ici aussi pour protéger la vie privée.
    """
    return SiteService.get_all()

@router.get("/sites/{site_id}", response_model=dict)
def get_site_public(site_id: int):
    """
    Cette route permet d’obtenir les informations détaillées d’un site
    en utilisant son identifiant (site_id).
    Si le site n’existe pas, un message explicite est renvoyé.
    """
    site = SiteService.get_by_id(site_id)
    if not site:
        return {"detail": "Site non trouvé"}
    return site
