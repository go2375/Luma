from app.models import SiteModel, CommuneModel
from app.anonymization import site_to_public_dict, site_to_prestataire_dict

# Permet de créer un service de gestion des sites touristiques
class SiteService:
    @staticmethod
    # Permet de récupérer tous les sites pour affichage public (anonymisés)
    def get_all_sites_public():
        sites = SiteModel.get_all(include_prestataire=False)
        # On anonymise les données sensibles
        return [site_to_public_dict(site) for site in sites]
    
    @staticmethod
    # Permet de récupérer un site par ID pour affichage public (anonymisé)
    def get_site_by_id_public(site_id: int):
        site = SiteModel.get_by_id(site_id, include_prestataire=False)
        if not site:
            return None
        
        return site_to_public_dict(site)
    
    @staticmethod
    # Permet de récupérer tous les sites d'un prestataire, incluant ses données complètes
    def get_sites_by_prestataire(prestataire_id: int):
        sites = SiteModel.get_by_prestataire(prestataire_id)
        return [site_to_prestataire_dict(site) for site in sites]
    
    @staticmethod
    # Permet de créer un nouveau site touristique
    def create_site(nom_site: str, commune_id: int, prestataire_id: int = None, **kwargs):
        # On valide la présence du nom du site
        if not nom_site.strip():
            return {"success": False, "error": "Le nom du site est requis"}
        
        # On vérifie que la commune existe
        communes = CommuneModel.get_all()
        if not any(c["commune_id"] == commune_id for c in communes):
            return {'success': False, 'error': 'Commune introuvable'}
        
        try:
            site = SiteModel.create(
                nom_site=nom_site.strip(),
                commune_id=commune_id,
                prestataire_id=prestataire_id,
                type_site=kwargs.get("type_site"),
                description=kwargs.get("description"),
                latitude=kwargs.get("latitude"),
                longitude=kwargs.get("longitude")
            )
            return {"success": True, "site": site}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    # Permet de modifier un site touristique appartenant à un prestataire
    def update_site(site_id: int, prestataire_id: int, **kwargs):
        # On vérifie que le site existe et appartient au prestataire
        site = SiteModel.get_by_id(site_id, include_prestataire=True)
        if not site:
            return {"success": False, "error": "Site introuvable"}
        
        if site.get("prestataire_id") != prestataire_id:
            return {"success": False, "error": "Accès refusé - Ce site ne vous appartient pas"}
        
        # On effectue une mise à jour
        success = SiteModel.update(site_id, **kwargs)
        
        return {"success": success, "error": None if success else "Échec de la mise à jour"}
    
    @staticmethod
    # Permet de marquer un site touristique comme supprimé
    def delete_site(site_id: int, prestataire_id: int):
        # On vérifie que le site existe et appartient au prestataire
        site = SiteModel.get_by_id(site_id, include_prestataire=True)
        if not site:
            return {"success": False, "error": "Site introuvable"}
        
        if site.get('prestataire_id') != prestataire_id:
            return {"success": False, "error": "Accès refusé - Ce site ne vous appartient pas"}
        
        # On marque un site comme supprimé
        success = SiteModel.delete(site_id)
        
        success = SiteModel.delete(site_id)
        return {"success": success, "error": None if success else "Échec de la suppression"}