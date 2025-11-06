from app.models import RoleModel, UserModel
from app.services.user_service import UserService
from app.services.site_service import SiteService
from app.services.parcours_service import ParcoursService
import bcrypt

# ===== Roles =====
roles_dict = {}
for r in ["admin", "prestataire", "visiteur"]:
    existing = [x["nom_role"] for x in RoleModel.get_all()]
    if r not in existing:
        role = RoleModel.create(r)
    else:
        role = [x for x in RoleModel.get_all() if x["nom_role"] == r][0]
    roles_dict[r] = role["role_id"]

# ===== Users =====
users = [
    {"username": "admin1", "password": "Admin123!", "role": "admin"},
    {"username": "prestataire1", "password": "Presta123!", "role": "prestataire"},
    {"username": "visiteur1", "password": "Visit123!", "role": "visiteur"},
]

for u in users:
    if not UserModel.get_by_username(u["username"]):
        UserService.create(u["username"], u["password"], roles_dict[u["role"]])

# ===== Sites =====
sites = [
    {"nom_site": "Site A", "commune_id": 1, "prestataire_id": 2, "est_activite": True},
    {"nom_site": "Site B", "commune_id": 2, "prestataire_id": 2, "est_lieu": True},
]

for s in sites:
    SiteService.create(**s)

# ===== Parcours =====
parcours = [
    {"nom_parcours": "Parcours 1", "createur_id": 1, "sites": [{"site_id": 1, "ordre_visite": 1}, {"site_id": 2, "ordre_visite": 2}]},
    {"nom_parcours": "Parcours 2", "createur_id": 1, "sites": [{"site_id": 2, "ordre_visite": 1}]},
]

for p in parcours:
    ParcoursService.create(p["nom_parcours"], p["createur_id"], p["sites"])

# Démo : parcours
# {
#   "nom_parcours": "Parcours Test",
#   "createur_id": 1,
#   "sites": [
#     {"site_id": 1, "ordre_visite": 1},
#     {"site_id": 2, "ordre_visite": 2}
#   ]
# }