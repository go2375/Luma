from app.models import SiteModel
from app.anonymization import site_to_public_dict, site_to_prestataire_dict


class SiteService:
    @staticmethod
    def get_all(include_prestataire: bool = False):
        sites = SiteModel.get_all()
        if include_prestataire:
            return [site_to_prestataire_dict(s) for s in sites]
        return [site_to_public_dict(s) for s in sites]

    @staticmethod
    def get_by_id(site_id: int, include_prestataire: bool = False):
        site = SiteModel.get_by_id(site_id)
        if not site:
            return None
        if include_prestataire:
            return site_to_prestataire_dict(site)
        return site_to_public_dict(site)

    @staticmethod
    def get_all_public():
        sites = SiteModel.get_all()
        return [site_to_public_dict(s) for s in sites]

    @staticmethod
    def get_by_id_public(site_id: int):
        site = SiteModel.get_by_id(site_id)
        if not site:
            return None
        return site_to_public_dict(site)

    @staticmethod
    def create(**site_data):
        return SiteModel.create(**site_data)
