from app.models import ParcoursModel
from app.services.site_service import SiteService


class ParcoursService:
    @staticmethod
    def get_all_public():
        return ParcoursService.get_all(include_prestataire=False)

    @staticmethod
    def get_by_id_public(parcours_id: int):
        return ParcoursService.get_by_id(parcours_id, include_prestataire=False)

    @staticmethod
    def create(nom_parcours: str, createur_id: int, sites: list):
        return ParcoursModel.create(nom_parcours=nom_parcours, createur_id=createur_id, sites=sites)
