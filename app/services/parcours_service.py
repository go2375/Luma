from app.models import ParcoursModel, SiteModel

# Permet de créer un service de gestion des parcours
class ParcoursService:
    @staticmethod
    # Permet de récupérer tous les parcours d'un utilisateur
    def get_user_parcours(user_id: int):
        parcours = ParcoursModel.get_by_user(user_id)
        return {"success": True, "parcours": parcours}
    
    @staticmethod
    # Permet de récupérer un parcours avec ses sites seulement pour l'utilisateur propriétaire correspondant
    def get_parcours_by_id(parcours_id: int, user_id: int):
        parcours = ParcoursModel.get_by_id(parcours_id)
        
        if not parcours:
            return {"success": False, "error": "Parcours introuvable"}
        
        # On vérifie que le parcours appartient à l'utilisateur
        if parcours["createur_id"] != user_id:
            return {"success": False, "error": "Accès refusé - Ce parcours ne vous appartient pas"}
        
        return {"success": True, "parcours": parcours}
    
    @staticmethod
    # On créer un nouveau parcours
    def create_parcours(nom_parcours: str, createur_id: int, sites: list = None):
        # On valide la présence du nom du parcours
        if not nom_parcours or not nom_parcours.strip():
            return {"success": False, "error": "Le nom du parcours est requis"}
        
        try:
            parcours = ParcoursModel.create(
                nom_parcours=nom_parcours.strip(),
                createur_id=createur_id,
                sites=sites
            )
            return {"success": True, "parcours": parcours}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la création: {str(e)}"}
    
    @staticmethod
    # Permet de modifier le nom d'un parcours
    def update_parcours(parcours_id: int, user_id: int, nom_parcours: str):
        # On vérifie que le parcours existe et appartient à l'utilisateur
        parcours = ParcoursModel.get_by_id(parcours_id)
        if not parcours:
            return {"success": False, "error": "Parcours introuvable"}
        
        if parcours["createur_id"] != user_id:
            return {"success": False, "error": "Accès refusé"}
        
        # On valide la présence du nom du parcours
        if not nom_parcours or not nom_parcours.strip():
            return {"success": False, "error": "Le nom du parcours est requis"}
        
        # On effectue une mise à jour
        success = ParcoursModel.update(parcours_id, nom_parcours=nom_parcours.strip())
        
        return {"success": success, "error": None if success else "Échec de la mise à jour"}
    
    @staticmethod
    # Permet de supprimer un parcours
    def delete_parcours(parcours_id: int, user_id: int):
        # On vérifie que le parcours existe et appartient à l'utilisateur
        parcours = ParcoursModel.get_by_id(parcours_id)
        if not parcours:
            return {"success": False, "error": "Parcours introuvable"}
        
        if parcours["createur_id"] != user_id:
            return {"success": False, "error": "Accès refusé"}
        
        # On supprime un parcours
        success = ParcoursModel.delete(parcours_id)
        
        return {"success": success, "error": None if success else "Échec de la suppression"}
    
    @staticmethod
    # Permet de retirer un site d'un parcours
    def remove_site_from_parcours(parcours_id: int, user_id: int, site_id: int):
        # On vérifie que le parcours existe et appartient à l'utilisateur
        parcours = ParcoursModel.get_by_id(parcours_id)
        if not parcours:
            return {"success": False, "error": "Parcours introuvable"}
        
        if parcours["createur_id"] != user_id:
            return {"success": False, "error": "Accès refusé"}
        
        # On compte le nombre de sites avant suppression
        nb_sites_precedent = len(parcours.get("sites", []))
        
        # On retire le site
        success = ParcoursModel.remove_site(parcours_id, site_id)
        
        if success:
            # On effectue une mise à jour le timestamp du parcours
            ParcoursModel.update(parcours_id, nb_sites_precedent=nb_sites_precedent)
            return {"success": True}
        
        return {"success": False, "error": "Site non trouvé dans ce parcours"}