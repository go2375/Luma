from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth_routes import router as auth_router
from app.routes.admin_routes import router as admin_router
from app.routes.prestataire_routes import router as prestataire_router
from app.routes.public_routes import router as public_router
from app.anonymization import check_and_fix_all_usernames
from app.config import Config

# On vérifie RGPD avant lancement
check_and_fix_all_usernames()

# On crée l’application FastAPI
app = FastAPI(
    title="API Luméa",
    description="API REST pour la gestion des sites touristiques et des utilisateurs",
    version="1.0.0"
)

# On gère middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Permet d'inclure des routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(prestataire_router)
app.include_router(public_router)

# On gère Health Check
@app.get("/api/health", tags=["Default"])
def health_check():
    return {"status": "ok", "message": "API Luméa fonctionne correctement"}