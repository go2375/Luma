from app.models import ParcoursModel, SiteModel, UserModel

class ParcoursService:
    @staticmethod
    def get_user_parcours(user_id: int):
        # Vérifie si l'utilisateur existe
        user = UserModel.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Utilisateur introuvable ou token invalide"}

        parcours_list = ParcoursModel.get_by_user(user_id)

        # Masquage GPS et exposition est_activite / est_lieu
        for parcours in parcours_list:
            for site in parcours.get("sites", []):
                site["latitude"] = None
                site["longitude"] = None
                site["est_activite"] = bool(site.get("est_activite", False))
                site["est_lieu"] = bool(site.get("est_lieu", False))

        return {"success": True, "parcours": parcours_list}

    @staticmethod
    def get_parcours_by_id(parcours_id: int, user_id: int):
        # Vérifie l'existence de l'utilisateur
        user = UserModel.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Utilisateur introuvable ou token invalide"}

        parcours = ParcoursModel.get_by_id(parcours_id)
        if not parcours:
            return {"success": False, "error": "Parcours introuvable"}

        if parcours["createur_id"] != user_id:
            return {"success": False, "error": "Accès refusé - Ce parcours ne vous appartient pas"}

        # Masquage GPS et exposition est_activite / est_lieu
        for site in parcours.get("sites", []):
            site["latitude"] = None
            site["longitude"] = None
            site["est_activite"] = bool(site.get("est_activite", False))
            site["est_lieu"] = bool(site.get("est_lieu", False))

        return {"success": True, "parcours": parcours}

    @staticmethod
    def create_parcours(nom_parcours: str, createur_id: int, sites: list = None):
        user = UserModel.get_by_id(createur_id)
        if not user:
            return {"success": False, "error": "Utilisateur introuvable ou token invalide"}

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
    def update_parcours(parcours_id: int, user_id: int, nom_parcours: str):
        user = UserModel.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Utilisateur introuvable ou token invalide"}

        parcours = ParcoursModel.get_by_id(parcours_id)
        if not parcours:
            return {"success": False, "error": "Parcours introuvable"}

        if parcours["createur_id"] != user_id:
            return {"success": False, "error": "Accès refusé"}

        if not nom_parcours or not nom_parcours.strip():
            return {"success": False, "error": "Le nom du parcours est requis"}

        success = ParcoursModel.update(parcours_id, nom_parcours=nom_parcours.strip())
        return {"success": success, "error": None if success else "Échec de la mise à jour"}

    @staticmethod
    def delete_parcours(parcours_id: int, user_id: int):
        user = UserModel.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Utilisateur introuvable ou token invalide"}

        parcours = ParcoursModel.get_by_id(parcours_id)
        if not parcours:
            return {"success": False, "error": "Parcours introuvable"}

        if parcours["createur_id"] != user_id:
            return {"success": False, "error": "Accès refusé"}

        success = ParcoursModel.delete(parcours_id)
        return {"success": success, "error": None if success else "Échec de la suppression"}

    @staticmethod
    def remove_site_from_parcours(parcours_id: int, user_id: int, site_id: int):
        user = UserModel.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "Utilisateur introuvable ou token invalide"}

        parcours = ParcoursModel.get_by_id(parcours_id)
        if not parcours:
            return {"success": False, "error": "Parcours introuvable"}

        if parcours["createur_id"] != user_id:
            return {"success": False, "error": "Accès refusé"}

        success = ParcoursModel.remove_site(parcours_id, site_id)
        if success:
            # Met à jour la timestamp du parcours après suppression
            ParcoursModel.update(parcours_id)
            return {"success": True}

        return {"success": False, "error": "Site non trouvé dans ce parcours"}
