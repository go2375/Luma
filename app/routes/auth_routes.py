from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.services.user_service import UserService
from app.auth import AuthService

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
    # Vérifie si l'utilisateur existe déjà
    existing_users = UserService.get_all()
    if any(u["username"] == data.username for u in existing_users):
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")

    user = UserService.create(data.username, data.password, data.role_id)
    return {"message": f"Utilisateur {user['username']} créé avec succès", "user_id": user["user_id"]}

# ===== Login =====
@router.post("/login", response_model=TokenResponse)
def login(data: LoginSchema):
    users = UserService.get_all()
    user = next((u for u in users if u["username"] == data.username), None)

    if not user or not AuthService.verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Nom d'utilisateur ou mot de passe incorrect")

    token = AuthService.generate_token(user["user_id"], user["username"], user["role"])
    return {"access_token": token}

# ===== Exemple endpoint sécurisé =====
from app.decorators import token_required, role_required

@router.get("/me", response_model=dict)
@token_required
def get_me(current_user: dict = None):
    return {"user_id": current_user["user_id"], "username": current_user["username"], "role": current_user["role"]}
