from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import uvicorn

from app.routes.auth_routes import router as auth_router
from app.routes.admin_routes import router as admin_router
from app.routes.prestataire_routes import router as prestataire_router
from app.routes.public_routes import router as public_router
from app.config import Config
from app.anonymization import check_and_fix_all_usernames

# ===== Vérification RGPD au démarrage =====
check_and_fix_all_usernames()

# ===== Création de l'application FastAPI =====
app = FastAPI(
    title="API Luméa",
    description="API REST pour la gestion des sites touristiques et des utilisateurs",
    version="1.0.0"
)

# ===== Middleware CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Inclusion des routers =====
app.include_router(auth_router)         # Public : login/register
app.include_router(admin_router)        # Sécurisé : admin only
app.include_router(prestataire_router)  # Sécurisé : prestataire only
app.include_router(public_router)       # Public : sites, parcours, référentiels

# ===== Health Check =====
@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "API Luméa fonctionne correctement"}

# ===== Gestion globale des erreurs =====
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )

# ===== OpenAPI personnalisé avec Bearer JWT =====
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Schéma Bearer JWT
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT à inclure dans le header Authorization : Bearer <token>",
        }
    }

    # Appliquer sécurité aux routes sécurisées automatiquement
    for path_item in openapi_schema["paths"].values():
        for method_item in path_item.values():
            tags = method_item.get("tags", [])
            # Ne sécurise pas les routes publiques ou health/auth
            if any(tag in ["Authentification", "Public", "Health"] for tag in tags):
                continue
            method_item["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ===== Lancement =====
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        debug=True
    )
