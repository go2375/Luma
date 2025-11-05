from app.models import SiteModel
from app.anonymization import site_to_public_dict, site_to_prestataire_dict

class SiteService:
    @staticmethod
    def get_all(include_prestataire: bool = False):
        sites = SiteModel.get_all(include_prestataire=include_prestataire)
        if include_prestataire:
            return [site_to_prestataire_dict(s) for s in sites]
        return [site_to_public_dict(s) for s in sites]

    @staticmethod
    def get_by_id(site_id: int, include_prestataire: bool = False):
        site = SiteModel.get_by_id(site_id, include_prestataire=include_prestataire)
        if not site:
            return None
        if include_prestataire:
            return site_to_prestataire_dict(site)
        return site_to_public_dict(site)

    @staticmethod
    def create(**kwargs):
        return SiteModel.create(**kwargs)

    @staticmethod
    def update(site_id: int, **kwargs):
        return SiteModel.update(site_id, **kwargs)

    @staticmethod
    def delete(site_id: int):
        return SiteModel.delete(site_id)

    @staticmethod
    def get_all_public():
        return SiteService.get_all(include_prestataire=False)

    @staticmethod
    def get_by_id_public(site_id: int):
        return SiteService.get_by_id(site_id, include_prestataire=False)
