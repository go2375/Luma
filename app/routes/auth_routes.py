from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.user_service import UserService
from app.auth import AuthService
from app.decorators import token_required, role_required

router = APIRouter(prefix="/api/auth", tags=["Authentification"])

# ===== Schemas =====
class RegisterSchema(BaseModel):
    username: str
    password: str
    role_id: int  # rôle par défaut pour un utilisateur

class LoginSchema(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ===== Register =====
@router.post("/register", response_model=dict)
def register(data: RegisterSchema):
    existing_user = UserService.get_by_username(data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")

    user = UserService.create(data.username, data.password, data.role_id)
    return {"message": f"Utilisateur {user['username']} créé avec succès", "user_id": user["user_id"]}

# ===== Login =====
@router.post("/login", response_model=TokenResponse)
def login(data: LoginSchema):
    user = UserService.get_by_username(data.username)
    if not user or not AuthService.verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Nom d'utilisateur ou mot de passe incorrect")

    token = AuthService.generate_token(user["user_id"], user["username"], user["nom_role"])
    return {"access_token": token}