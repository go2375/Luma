from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.routes.admin_routes import router as admin_router
from app.routes.public_routes import router as public_router
from app.routes.auth_routes import router as auth_router
from app.auth import AuthService
from app.config import Config

app = FastAPI(title="Luméa", version="1.0.0", description="Luméa : pour faciliter la découverte de la Bretagne !")

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
    public_paths = [
        "/",  # accueil sans token
        "/api/auth/login",
        "/api/auth/register",
        "/api/public",
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
    if not decoded["success"]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": decoded.get("error", "Token invalide")}
        )

    request.state.user = decoded["data"]
    return await call_next(request)

# ===== Page d'accueil =====
@app.get("/", tags=["Accueil"])
async def welcome():
    return {"message": "Bienvenue sur l'API Luméa ! Découvrez la Bretagne facilement."}

# ===== Inclusion des routers =====
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(public_router)

# ===== OpenAPI JWT Bearer =====
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Ajouter Bearer JWT
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT à inclure : Bearer <token>"
        }
    }

    # Appliquer sécurité uniquement aux routes non publiques
    for path_item in openapi_schema["paths"].values():
        for method_item in path_item.values():
            tags = method_item.get("tags", [])
            if any(tag in ["Public", "Authentification", "Accueil"] for tag in tags):
                continue
            method_item["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
