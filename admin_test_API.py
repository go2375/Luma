from app.services.user_service import UserService
from app.models import RoleModel

# Récupération des rôles
roles = RoleModel.get_all()
roles_dict = {r["nom_role"]: r["role_id"] for r in roles}

# Utilisateurs à créer
users_to_create = [
    {"username": "admin3", "password": "Admin123!", "role": "admin"},
    {"username": "prestataire3", "password": "Presta123!", "role": "prestataire"},
    {"username": "visiteur3", "password": "Visit123!", "role": "visiteur"}
]

# Création des utilisateurs
for user_data in users_to_create:
    role_id = roles_dict.get(user_data["role"])
    if not role_id:
        print(f" Rôle '{user_data['role']}' introuvable")
        continue
    
    try:
        # Utilise .create() au lieu de .create_user()
        user = UserService.create(
            username=user_data["username"],
            password=user_data["password"],
            role_id=role_id
        )
        print(f" Utilisateur {user_data['role']} créé : {user}")
    except Exception as e:
        print(f" Erreur lors de la création de {user_data['username']}: {e}")