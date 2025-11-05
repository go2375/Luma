from app.models import ParcoursModel
from app.services.site_service import SiteService

class ParcoursService:
    @staticmethod
    def get_all(include_prestataire: bool = False):
        parcours_list = ParcoursModel.get_all()
        for parcours in parcours_list:
            parcours['sites'] = [
                SiteService.get_by_id(site['site_id'], include_prestataire=include_prestataire)
                for site in parcours.get('sites', [])
            ]
        return parcours_list

    @staticmethod
    def get_by_id(parcours_id: int, include_prestataire: bool = False):
        parcours = ParcoursModel.get_by_id(parcours_id)
        if not parcours:
            return None
        parcours['sites'] = [
            SiteService.get_by_id(site['site_id'], include_prestataire=include_prestataire)
            for site in parcours.get('sites', [])
        ]
        return parcours

    @staticmethod
    def get_all_public():
        return ParcoursService.get_all(include_prestataire=False)

    @staticmethod
    def get_by_id_public(parcours_id: int):
        return ParcoursService.get_by_id(parcours_id, include_prestataire=False)
