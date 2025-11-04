from app.models import SiteModel, CommuneModel, UserModel
from app.anonymization import site_to_public_dict, site_to_prestataire_dict

# ===== Service de gestion des sites touristiques =====
class SiteService:

    @staticmethod
    def get_all_sites_public():
        """
        Récupère tous les sites pour affichage public.
        Les données sensibles (GPS, prestataire) sont anonymisées.
        """
        sites = SiteModel.get_all(include_prestataire=False)
        # On anonymise les données sensibles pour chaque site
        return [site_to_public_dict(site) for site in sites]

    @staticmethod
    def get_site_by_id_public(site_id: int):
        """
        Récupère un site spécifique pour affichage public (anonymisé).
        """
        site = SiteModel.get_by_id(site_id, include_prestataire=False)
        if not site:
            return {"success": False, "error": "Site introuvable"}
        
        return {"success": True, "site": site_to_public_dict(site)}

    @staticmethod
    def get_sites_by_prestataire(prestataire_id: int):
        """
        Récupère tous les sites d'un prestataire avec données complètes.
        Vérifie que le prestataire existe.
        """
        prestataire = UserModel.get_by_id(prestataire_id)
        if not prestataire:
            return {"success": False, "error": "Prestataire introuvable ou token invalide"}

        sites = SiteModel.get_by_prestataire(prestataire_id)
        return {"success": True, "sites": [site_to_prestataire_dict(site) for site in sites]}

    @staticmethod
    def create_site(nom_site: str, commune_id: int, prestataire_id: int = None, **kwargs):
        """
        Crée un nouveau site touristique.
        Vérifie la commune et le prestataire.
        Les champs est_activite et est_lieu remplacent type_site.
        """
        if not nom_site or not nom_site.strip():
            return {"success": False, "error": "Le nom du site est requis"}

        # Vérifie que la commune existe
        communes = CommuneModel.get_all()
        if not any(c["commune_id"] == commune_id for c in communes):
            return {"success": False, "error": "Commune introuvable"}

        # Vérifie prestataire si fourni
        if prestataire_id and not UserModel.get_by_id(prestataire_id):
            return {"success": False, "error": "Prestataire introuvable ou token invalide"}

        try:
            site = SiteModel.create(
                nom_site=nom_site.strip(),
                commune_id=commune_id,
                prestataire_id=prestataire_id,
                est_activite=kwargs.get("est_activite", False),
                est_lieu=kwargs.get("est_lieu", False),
                description=kwargs.get("description"),
                latitude=kwargs.get("latitude"),
                longitude=kwargs.get("longitude")
            )
            return {"success": True, "site": site}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la création: {str(e)}"}

    @staticmethod
    def update_site(site_id: int, prestataire_id: int, **kwargs):
        """
        Modifie un site touristique.
        Vérifie que le site appartient au prestataire.
        """
        site = SiteModel.get_by_id(site_id, include_prestataire=True)
        if not site:
            return {"success": False, "error": "Site introuvable"}

        if site.get("prestataire_id") != prestataire_id:
            return {"success": False, "error": "Accès refusé - Ce site ne vous appartient pas"}

        # Mise à jour des champs autorisés
        allowed_fields = ["nom_site", "description", "est_activite", "est_lieu", "latitude", "longitude"]
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        success = SiteModel.update(site_id, **updates)
        return {"success": success, "error": None if success else "Échec de la mise à jour"}

    @staticmethod
    def delete_site(site_id: int, prestataire_id: int):
        """
        Marque un site comme supprimé.
        Vérifie que le site appartient au prestataire.
        """
        site = SiteModel.get_by_id(site_id, include_prestataire=True)
        if not site:
            return {"success": False, "error": "Site introuvable"}

        if site.get("prestataire_id") != prestataire_id:
            return {"success": False, "error": "Accès refusé - Ce site ne vous appartient pas"}

        success = SiteModel.delete(site_id)
        return {"success": success, "error": None if success else "Échec de la suppression"}
