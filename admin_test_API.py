from app.services.user_service import UserService
from app.models import RoleModel

roles = RoleModel.get_all()
admin_role = next((r for r in roles if r["nom_role"] == "admin"), None)

if not admin_role:
    raise Exception("Rôle admin introuvable — crée-le d'abord.")

user = UserService.create_user(
    username="admin",
    password="Admin123!",
    role_id=admin_role["role_id"]
)

print(" Utilisateur admin créé :", user)