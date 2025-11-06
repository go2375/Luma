from app.models import ParcoursModel

class ParcoursService:

    @staticmethod
    def _enrich_sites(parcours: dict) -> dict:
        """Ajoute longitude et latitude à chaque site d'un parcours."""
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
        parcours_list = ParcoursModel.get_all()
        return [ParcoursService._enrich_sites(p) for p in parcours_list]

    @staticmethod
    def get_by_id(parcours_id: int, include_prestataire: bool = False):
        parcours = ParcoursModel.get_by_id(parcours_id, include_prestataire=include_prestataire)
        return ParcoursService._enrich_sites(parcours)

    @staticmethod
    def create(nom_parcours: str, createur_id: int, sites: list = None):
        sites = sites or []
        parcours = ParcoursModel.create(nom_parcours=nom_parcours, createur_id=createur_id, sites=sites)
        return ParcoursService._enrich_sites(parcours)

    @staticmethod
    def update(parcours_id: int, **kwargs):
        """
        Met à jour un parcours et renvoie le parcours complet mis à jour avec sites,
        longitude et latitude.
        """
        success = ParcoursModel.update(parcours_id, **kwargs)
        if not success:
            return None  # parcours non trouvé ou rien à mettre à jour
        
        # Récupère le parcours complet après mise à jour
        parcours = ParcoursModel.get_by_id(parcours_id, include_prestataire=True)
        return ParcoursService._enrich_sites(parcours)

    @staticmethod
    def delete(parcours_id: int):
        return ParcoursModel.delete(parcours_id)

    @staticmethod
    def get_all_public():
        return ParcoursService.get_all()

    @staticmethod
    def get_by_id_public(parcours_id: int):
        return ParcoursService.get_by_id(parcours_id, include_prestataire=False)
