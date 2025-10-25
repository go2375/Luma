from flask import Flask
from flask_cors import CORS
from app.config import Config

# Permet de créer et configurer l'application Flask
def create_app():
    app = Flask(__name__)
    
    # Permet de charger la configuration
    app.config.from_object(Config)
    
    # Permet d'activer CORS pour permettre les requêtes depuis le frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": Config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Permet d'enregistrer les blueprints (routes)
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.prestataire_routes import prestataire_bp
    from app.routes.public_routes import public_bp
    
    # Cela permet de lier auth_bp à mon blueprint défini, 
    # mon ensemble de routes préconfigurées que je peux enregistrer dans mon application principale 
    # à l'aide de la méthode app.register_blueprint() dans app/routes/auth_routes.py. 
    # Par exemple, lorsque nous appelons app.register_blueprint(prestataire_bp), 
    # Flask enregistre toutes les routes et procédures de gestion (méthodes HTTP, erreurs, hooks, filtres, etc.) définies dans le blueprint.
    # En interne, cela ajoute les routes du blueprint à la carte d'URL de notre application principale (app.url_map),
    # applique le préfixe (par exemple url_prefix='/api/prestataire') et relie tous les décorateurs associés (.route(), .errorhandler(), etc.) 
    # au contexte de l'application principale. Chaque blueprint étend donc la carte des routes principales de Flask.
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(prestataire_bp)
    app.register_blueprint(public_bp)
    
    # Permet d'établir la route de vérification de santé de l'API
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {
            'status': 'ok', 
            'message': 'API Luméa fonctionne correctement'
        }, 200
    
    # Permet de gérer des erreurs globales : 
    # si une route inconnue est demandée ca permet de renvoyer un message d’erreur en JSON. 
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Ressource introuvable'}, 404
    
    # Permet de gérer toutes les erreurs non attrapées dans le code, les exceptions en Python.
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Erreur interne du serveur'}, 500
    
    return app