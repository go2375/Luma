from app.models import ParcoursModel

class ParcoursService:
    @staticmethod
    def get_all():
        return ParcoursModel.get_all()

    @staticmethod
    def get_by_id(parcours_id: int, include_prestataire: bool = False):
        return ParcoursModel.get_by_id(parcours_id, include_prestataire=include_prestataire)

    @staticmethod
    def create(nom_parcours: str, createur_id: int, sites: list = None):
        sites = sites or []
        return ParcoursModel.create(nom_parcours=nom_parcours, createur_id=createur_id, sites=sites)

    @staticmethod
    def update(parcours_id: int, **kwargs):
        return ParcoursModel.update(parcours_id, **kwargs)

    @staticmethod
    def delete(parcours_id: int):
        return ParcoursModel.delete(parcours_id)

    @staticmethod
    def get_all_public():
        return ParcoursService.get_all()

    @staticmethod
    def get_by_id_public(parcours_id: int):
        return ParcoursService.get_by_id(parcours_id, include_prestataire=False)
