from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import Config
from app.routes.auth_routes import router as auth_router
from app.routes.admin_routes import router as admin_router
from app.routes.prestataire_routes import router as prestataire_router
from app.routes.public_routes import router as public_router
from app.auth import AuthService  # service de token et login

def create_app() -> FastAPI:
    app = FastAPI(title="API Luméa", version="1.0.0")

    # ===== Middleware CORS =====
    app.add_middleware(
        CORSMiddleware,
        allow_origins=Config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # ===== Middleware Auth / Vérification JWT =====
    @app.middleware("http")
    async def check_jwt_middleware(request: Request, call_next):
        """Vérifie si les routes nécessitent un token valide.
        On ignore les routes publiques et login/signup.
        """
        public_paths = ["/api/health", "/api/login", "/api/register"]
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
        if not decoded["success"]:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": decoded.get("error", "Token invalide")}
            )

        # On peut stocker le payload pour accès dans les endpoints via request.state.user
        request.state.user = decoded["data"]
        return await call_next(request)

    # ===== Inclusion des routers =====
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(prestataire_router)
    app.include_router(public_router)

    # ===== Health Check =====
    @app.get("/api/health")
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

    return app
