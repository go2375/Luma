from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.user_service import UserService
from app.auth import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentification"])

# ===== Schemas =====
class RegisterSchema(BaseModel):
    username: str
    password: str
    # On supprime role_id envoyé par l'utilisateur pour éviter qu'il s'attribue un rôle admin

class LoginSchema(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ===== Routes =====
@router.post("/register", response_model=dict)
def register(data: RegisterSchema):
    # Vérifie si le username existe déjà
    if UserService.get_by_username(data.username):
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")

    # Création de l'utilisateur avec rôle "visiteur" forcé
    user = UserService.create(
        username=data.username,
        password=data.password,
        role_id=2  # rôle visiteur
    )

    return {
        "message": f"Utilisateur {user['username']} créé avec rôle visiteur",
        "user_id": user["user_id"]
    }

@router.post("/login", response_model=TokenResponse)
def login(data: LoginSchema):
    user = UserService.get_by_username(data.username)
    if not user or not AuthService.verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Nom d'utilisateur ou mot de passe incorrect")

    # Génère le token avec le rôle exact de l'utilisateur
    token = AuthService.generate_token(
        user_id=user["user_id"],
        username=user["username"],
        role=user["nom_role"]  # doit correspondre à "visiteur" ou autre
    )

    return {"access_token": token}
