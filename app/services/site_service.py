# J'importe le modèle SiteModel pour interagir directement avec la base de données.
from app.models import SiteModel
# J'importe également les fonctions d'anonymisation pour adapter la sortie
# selon qu'il s'agit d'un accès public ou prestataire.
from app.anonymization import site_to_public_dict, site_to_prestataire_dict

class SiteService:
    """
    Service métier pour gérer les sites touristiques.
    Je centralise ici toute la logique métier concernant les sites,
    en séparant l'accès à la base (SiteModel) de l'API.
    """
    @staticmethod
    def get_all(include_prestataire: bool = False):
        """
        Retourne la liste complète des sites.
        - include_prestataire : si True, retourne toutes les données,
          y compris les coordonnées sensibles et infos spécifiques prestataire.
        - sinon, anonymise certaines informations pour un accès public.
        """
        sites = SiteModel.get_all(include_prestataire=include_prestataire)
        if include_prestataire:
            # Je transforme les sites pour un usage interne prestataire
            return [site_to_prestataire_dict(s) for s in sites]
        # Pour le public, je masque les informations sensibles (latitude/longitude)
        return [site_to_public_dict(s) for s in sites]

    @staticmethod
    def get_by_id(site_id: int, include_prestataire: bool = False):
        """
        Retourne un site spécifique selon son ID.
        - site_id : identifiant du site
        - include_prestataire : contrôle le niveau d'information retourné
        """
        site = SiteModel.get_by_id(site_id, include_prestataire=include_prestataire)
        if not site:
            return None # Aucun site trouvé
        if include_prestataire:
            return site_to_prestataire_dict(site)
        return site_to_public_dict(site)

    @staticmethod
    def create(**kwargs):
        """
        Crée un nouveau site touristique.
        - kwargs : dictionnaire contenant toutes les informations du site
        Je renvoie directement le site créé via le modèle.
        """
        return SiteModel.create(**kwargs)

    @staticmethod
    def update(site_id: int, **kwargs):
        """
        Met à jour un site existant.
        - site_id : identifiant du site à mettre à jour
        - kwargs : champs à modifier
        Retourne True si la mise à jour a réussi, False sinon.
        """
        return SiteModel.update(site_id, **kwargs)

    @staticmethod
    def delete(site_id: int):
        """
        Supprime un site de la base.
        - site_id : identifiant du site à supprimer
        Retourne True si la suppression a réussi.
        """
        return SiteModel.delete(site_id)

    @staticmethod
    def get_all_public():
        """
        Shortcut pour récupérer tous les sites en mode public.
        Equivalent à get_all(include_prestataire=False)
        """
        return SiteService.get_all(include_prestataire=False)

    @staticmethod
    def get_by_id_public(site_id: int):
        """
        Shortcut pour récupérer un site par ID en mode public.
        Equivalent à get_by_id(site_id, include_prestataire=False)
        """
        return SiteService.get_by_id(site_id, include_prestataire=False)
