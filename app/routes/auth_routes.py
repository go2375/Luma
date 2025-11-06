# J’importe les outils nécessaires depuis FastAPI
# HTTPException : pour envoyer des erreurs HTTP personnalisées
from fastapi import APIRouter, HTTPException
# J’importe Pydantic pour valider les données reçues dans le corps des requêtes
from pydantic import BaseModel

# J’importe mes services métiers : 
# UserService pour interagir avec la base de données utilisateur
# AuthService pour la gestion des tokens JWT et du chiffrement des mots de passe
from app.services.user_service import UserService
from app.auth import AuthService

# Je crée un routeur spécifique à l’authentification
# Cela me permet d’avoir des routes propres et bien séparées des routes Admin et Public
router = APIRouter(prefix="/api/auth", tags=["Authentification"])

# Schémas de validation Pydantic
# Ce schéma définit les données nécessaires à l’inscription d’un utilisateur
# Je ne laisse pas l'utilisateurs choisir son rôle pour des raisons de sécurité
class RegisterSchema(BaseModel):
    username: str
    password: str
    # On supprime role_id envoyé par l'utilisateur pour éviter qu'il s'attribue un rôle admin
     # Je n’inclus pas role_id dans ce schéma : il sera forcé à "visiteur" côté serveur

# Ce schéma définit les données nécessaires à la connexion (login)
class LoginSchema(BaseModel):
    username: str
    password: str

# Ce schéma définit la réponse envoyée après une connexion réussie
# Je retourne un token JWT avec le type "bearer" (standard HTTP)
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Routes d’authentification
# Route pour enregistrer un nouvel utilisateur
@router.post("/register", response_model=dict)
def register(data: RegisterSchema):
    """
    Cette route permet à un utilisateur de s’inscrire.
    Je vérifie d’abord si le nom d’utilisateur existe déjà, puis je crée un compte
    avec le rôle 'visiteur' par défaut (role_id = 2).
    """
    # Vérification si l’utilisateur existe déjà
    if UserService.get_by_username(data.username):
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")

    # Création de l'utilisateur avec rôle "visiteur" forcé
    user = UserService.create(
        username=data.username,
        password=data.password,
        role_id=2  # rôle visiteur
    )

    # API renvoie un message clair pour confirmer la création
    return {
        "message": f"Utilisateur {user['username']} créé avec rôle visiteur",
        "user_id": user["user_id"]
    }

# Route pour se connecter (login)
@router.post("/login", response_model=TokenResponse)
def login(data: LoginSchema):
    """
    Cette route permet à un utilisateur existant de se connecter.
    Si le mot de passe est correct, je lui génère un token JWT valide pendant 24 heures.
    """
    # Je récupère l’utilisateur depuis la base de données
    user = UserService.get_by_username(data.username)
     # Si l’utilisateur n’existe pas ou que le mot de passe est incorrect : erreur 401
    if not user or not AuthService.verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Nom d'utilisateur ou mot de passe incorrect")

    # Si la vérification est réussie, je génère un token JWT
    # Ce token contiendra :
    # - l’ID de l’utilisateur
    # - son nom d’utilisateur
    # - son rôle (ex : visiteur ou admin)
    token = AuthService.generate_token(
        user_id=user["user_id"],
        username=user["username"],
        role=user["nom_role"]
    )

    # API renvoie le token JWT au format standard
    return {"access_token": token}
