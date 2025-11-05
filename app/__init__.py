from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import Config
from app.routes.auth_routes import router as auth_router
from app.routes.admin_routes import router as admin_router
from app.routes.public_routes import router as public_router
from app.auth import AuthService  # service JWT

def create_app() -> FastAPI:
    app = FastAPI(title="API Luméa", version="1.0.0")

    # ===== Middleware CORS =====
    app.add_middleware(
        CORSMiddleware,
        allow_origins=Config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ===== Middleware JWT =====
    @app.middleware("http")
    async def decode_jwt_middleware(request: Request, call_next):
        """
        Middleware pour décoder le JWT et stocker l'utilisateur dans request.state.user.
        Les routes publiques sont ignorées ici.
        """
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

        # Stockage du payload pour accès dans les endpoints
        request.state.user = decoded["data"]

        return await call_next(request)

    # ===== Inclusion des routers =====
    app.include_router(auth_router)    # login / register
    app.include_router(admin_router)   # admin parcours seulement
    # app.include_router(prestataire_router)  # désactivé pour l'instant
    app.include_router(public_router)   # sites et parcours publics

    # ===== Health Check =====
    @app.get("/api/health", tags=["Health"])
    async def health_check():
        return {"status": "ok", "message": "API Luméa fonctionne correctement"}

    # ===== Gestion globale des erreurs =====
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        status_code = getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR)
        detail = getattr(exc, "detail", str(exc))
        return JSONResponse(status_code=status_code, content={"detail": detail})

    return app


# Pour lancer directement
app = create_app()
