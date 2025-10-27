from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Config
from app.routes.auth_routes import router as auth_router
from app.routes.admin_routes import router as admin_router
from app.routes.prestataire_routes import router as prestataire_router
from app.routes.public_routes import router as public_router

# Permet de créer et configurer FastAPI
def create_app() -> FastAPI:
    app = FastAPI(title="API Luméa", version="1.0.0")
    
    # On gère middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=Config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    
    # Permet d'enregistrer les routers    
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(prestataire_router)
    app.include_router(public_router)

    # On gère Health Check
    @app.get("/api/health")
    async def health_check():
        return {
            "status": "ok",
            "message": "API Luméa fonctionne correctement"
        }

    return app