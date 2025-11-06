from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.routes.admin_routes import router as admin_router
from app.routes.public_routes import router as public_router
from app.routes.auth_routes import router as auth_router
from app.auth import AuthService
from app.config import Config

# Création de l'application
# Je crée l'application FastAPI avec un titre, une version et une description pour Swagger
app = FastAPI(title="Luméa", version="1.0.0", description="Luméa : pour faciliter la découverte de la Bretagne !")

# Je configure CORS pour autoriser les origines définies dans Config
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Je décode le token JWT pour toutes les routes sécurisées
@app.middleware("http")
async def decode_jwt_middleware(request: Request, call_next):
    # Je définis les routes publiques qui n'ont pas besoin de token
    public_paths = [
        "/", # page d'accueil
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

    # Je récupère le token depuis l'en-tête Authorization
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token manquant ou invalide"}
        )

    
    token = auth_header.split(" ")[1]
    # Je décode le token et je vérifie sa validité
    decoded = AuthService.decode_token(token)
    if not decoded["success"]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": decoded.get("error", "Token invalide")}
        )

    # Je stocke les informations de l'utilisateur dans request.state.user
    request.state.user = decoded["data"]
    return await call_next(request)

# Page d'accueil
@app.get("/", tags=["Accueil"])
async def welcome():
    # Je retourne un message de bienvenue pour la page d'accueil
    return {"message": "Bienvenue sur l'API Luméa ! Découvrez la Bretagne facilement."}

# Inclusion des routers
# J'inclus les routers pour organiser mes routes par domaine
app.include_router(auth_router) # routes Authentification
app.include_router(admin_router) # routes Authentification
app.include_router(public_router) # routes Public

# OpenAPI JWT Bearer
def custom_openapi():
    """
    Je personnalise la documentation Swagger pour inclure le JWT Bearer
    et pour ne pas appliquer la sécurité aux routes publiques.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Je définis le schéma de sécurité Bearer
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT à inclure : Bearer <token>"
        }
    }

    # J'applique la sécurité uniquement aux routes non publiques
    for path_item in openapi_schema["paths"].values():
        for method_item in path_item.values():
            tags = method_item.get("tags", [])
            if any(tag in ["Public", "Authentification", "Accueil"] for tag in tags):
                continue
            method_item["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Je surcharge la fonction openapi par ma version personnalisée
app.openapi = custom_openapi
