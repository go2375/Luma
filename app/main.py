from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import APIKey, APIKeyIn, SecuritySchemeType
from fastapi.openapi.utils import get_openapi
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
    """Vérifie l’état de santé de l’API."""
    return {"status": "ok", "message": "API Luméa fonctionne correctement"}

# Permet de  configurer avec bearer token
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # On Ajoute le schéma d’authentification Bearer
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT à inclure dans le header Authorization : Bearer <token>",
        }
    }

    # On applique automatiquement la sécurité aux routes protégées
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# On applique notre configuration personnalisée
app.openapi = custom_openapi