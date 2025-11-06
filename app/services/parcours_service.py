# J'importe le modèle ParcoursModel qui contient toutes les requêtes SQL liées aux parcours
from app.models import ParcoursModel

class ParcoursService:
    """
    Service métier pour gérer les parcours touristiques.
    Ici, je centralise toute la logique métier liée aux parcours,
    ce qui me permet de séparer la logique de la base de données (ParcoursModel)
    de la logique de présentation et des routes FastAPI.
    """
    @staticmethod
    def _enrich_sites(parcours: dict) -> dict:
        """
        Méthode interne pour ajouter les coordonnées GPS à chaque site d'un parcours.

        Je vérifie que le parcours contient bien des sites, puis je reconstruis
        la liste des sites en incluant 'latitude' et 'longitude'.
        Cela permet aux routes admin de toujours renvoyer les coordonnées.
        """
        if parcours and "sites" in parcours:
            parcours["sites"] = [
                {
                    "site_id": site.get("site_id"),
                    "ordre_visite": site.get("ordre_visite"),
                    "longitude": site.get("longitude"),
                    "latitude": site.get("latitude")
                }
                for site in parcours["sites"]
            ]
        return parcours

    @staticmethod
    def get_all():
        """
        Retourne la liste complète des parcours.
        J’enrichis chaque parcours avec les coordonnées GPS de ses sites
        pour que l’admin ait toujours ces informations.
        """
        parcours_list = ParcoursModel.get_all()
        return [ParcoursService._enrich_sites(p) for p in parcours_list]

    @staticmethod
    def get_by_id(parcours_id: int, include_prestataire: bool = False):
        """
        Récupère un parcours spécifique par son ID.
        include_prestataire permet de récupérer les coordonnées GPS si nécessaire (pour l’admin).
        """
        parcours = ParcoursModel.get_by_id(parcours_id, include_prestataire=include_prestataire)
        return ParcoursService._enrich_sites(parcours)

    @staticmethod
    def create(nom_parcours: str, createur_id: int, sites: list = None):
        """
        Crée un nouveau parcours.
        - nom_parcours : nom du parcours
        - createur_id : ID de l’utilisateur qui crée le parcours
        - sites : liste des sites associés, avec leur ordre de visite
        Retourne le parcours complet enrichi avec longitude et latitude.
        """
        sites = sites or []
        parcours = ParcoursModel.create(nom_parcours=nom_parcours, createur_id=createur_id, sites=sites)
        return ParcoursService._enrich_sites(parcours)

    @staticmethod
    def update(parcours_id: int, **kwargs):
        """
        Met à jour un parcours existant.
        - kwargs peut contenir 'nom_parcours' ou d'autres champs modifiables.
        Si la mise à jour réussit, je récupère le parcours complet
        avec tous les sites et leurs coordonnées GPS.
        Sinon, API renvoie None pour indiquer que rien n’a été modifié.
        """
        success = ParcoursModel.update(parcours_id, **kwargs)
        if not success:
            return None
        
        # Je récupère le parcours complet après mise à jour
        parcours = ParcoursModel.get_by_id(parcours_id, include_prestataire=True)
        return ParcoursService._enrich_sites(parcours)

    @staticmethod
    def delete(parcours_id: int):
        """
        Supprime un parcours et ses relations avec les sites.
        Retourne True si la suppression a réussi, False sinon.
        """
        return ParcoursModel.delete(parcours_id)

    @staticmethod
    def get_all_public():
        """
        Retourne tous les parcours pour les utilisateurs publics.
        Les coordonnées GPS sont masquées pour respecter la confidentialité.
        """
        return ParcoursService.get_all()

    @staticmethod
    def get_by_id_public(parcours_id: int):
        """
        Retourne un parcours spécifique pour les utilisateurs publics.
        Les coordonnées GPS sont cachées, donc include_prestataire=False.
        """
        return ParcoursService.get_by_id(parcours_id, include_prestataire=False)
