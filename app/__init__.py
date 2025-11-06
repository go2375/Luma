# J'importe FastAPI et les modules nécessaires pour créer l'application,
# gérer les requêtes, les réponses JSON et le middleware CORS.
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import Config
from app.routes.auth_routes import router as auth_router
from app.routes.admin_routes import router as admin_router
from app.routes.public_routes import router as public_router
from app.auth import AuthService  # service JWT

def create_app() -> FastAPI:
    """
    Je crée l'application FastAPI Luméa.
    Ici, je configure les middleware, la sécurité JWT, 
    l'inclusion des routes et la gestion globale des erreurs.
    """
    app = FastAPI(title="API Luméa", version="1.0.0")

    # Je configure CORS pour permettre aux clients web
    # d'accéder à l'API depuis les domaines autorisés.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=Config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def decode_jwt_middleware(request: Request, call_next):
        """
        Middleware pour décoder le JWT et stocker l'utilisateur dans request.state.user.
        Je laisse passer les routes publiques et je vérifie le token pour les routes sécurisées.
        """
        # Liste des chemins publics qui n'ont pas besoin de JWT
        public_paths = [
            "/api/health",
            "/api/auth/login",
            "/api/auth/register",
            "/api/sites",
            "/api/parcours",
            "/api/communes",
            "/api/departments",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/swagger-ui"
        ]
        if any(request.url.path.startswith(p) for p in public_paths):
            return await call_next(request)

        # Je récupère le token dans le header Authorization
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token manquant ou invalide"}
            )

        token = auth_header.split(" ")[1]
        decoded = AuthService.decode_token(token)
        if not decoded.get("success"):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": decoded.get("error", "Token invalide")}
            )

        # Si tout est correct, je stocke l'utilisateur décodé dans request.state
        request.state.user = decoded["data"]

        return await call_next(request)

    # Je regroupe les routes par domaine pour la modularité
    app.include_router(auth_router)    # Routes d'authentification : login / register
    app.include_router(admin_router)   # Routes admin pour gérer les parcours
    app.include_router(public_router)  # Routes publiques : parcours et sites

    # Page d'accueil
    @app.get("/", tags=["Accueil"])
    async def home():
        """
        Je définis une route d'accueil qui renvoie un message de bienvenue.
        Cette route ne nécessite pas de token.
        """
        return {"message": "Bienvenue sur l'API Luméa, découvrez la Bretagne !"}

    # Gestion globale des erreurs
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Je capture toutes les exceptions non gérées pour renvoyer
        un JSON propre à l'utilisateur.
        """
        status_code = getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR)
        detail = getattr(exc, "detail", str(exc))
        return JSONResponse(status_code=status_code, content={"detail": detail})

    return app


# Je crée l'application pour qu'elle soit directement exécutable
app = create_app()
