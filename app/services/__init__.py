# Permet de créer à partir du dossier un package services qui ensuite va permettre importer directement les classes depuis ce package.
# Ca permet de centraliser les imports pour simplifier leur utilisation et aussi mieux contrôler ce qui sera exposé via __all__. 
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.services.site_service import SiteService
from app.services.parcours_service import ParcoursService

__all__ = ['UserService', 'RoleService', 'SiteService', 'ParcoursService']