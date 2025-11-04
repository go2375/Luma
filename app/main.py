from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.routes.auth_routes import router as auth_router
from app.routes.admin_routes import router as admin_router
from app.routes.prestataire_routes import router as prestataire_router
from app.routes.public_routes import router as public_router
from app.anonymization import check_and_fix_all_usernames
import uvicorn


# Vérification RGPD au démarrage
check_and_fix_all_usernames()

# Création de l'application
app = FastAPI(
    title="API Luméa",
    description="API REST pour la gestion des sites touristiques et des utilisateurs",
    version="1.0.0",
)

# --- Configuration CORS ---
origins = [
    "http://localhost:3000",  # ton frontend React ou autre
    "http://localhost:8081"  # Swagger UI local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Inclusion des routers ---
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(prestataire_router)
app.include_router(public_router)

# --- Health Check ---
@app.get("/api/health", tags=["Default"])
def health_check():
    """Vérifie l’état de santé de l’API."""
    return {"status": "ok", "message": "API Luméa fonctionne correctement"}


# --- Configuration OpenAPI avec Bearer Token ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT à inclure dans le header Authorization : Bearer <token>",
        }
    }

    # Applique le schéma JWT à toutes les routes par défaut
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# On remplace le générateur OpenAPI par le nôtre
app.openapi = custom_openapi

# --- Point d'entrée ---
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        log_level="info"
    )
