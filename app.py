from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from database import init_db, test_connection
import os
from datetime import timedelta

# Import des contrôleurs
from controllers.pays_controller import pays_bp
from controllers.exploitation_controller import exploitation_bp
from controllers.entrepot_controller import entrepot_bp
from controllers.lot_controller import lot_bp
from controllers.dashboard_controller import dashboard_bp, alerte_bp

def create_app():
    """
    Crée et configure l'application Flask
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JSON_SORT_KEYS'] = False  # Préserver l'ordre des clés dans les réponses JSON
    
    # Activer CORS pour toutes les routes
    CORS(app, origins=["*"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Enregistrement des blueprints
    app.register_blueprint(pays_bp)
    app.register_blueprint(exploitation_bp)
    app.register_blueprint(entrepot_bp)
    app.register_blueprint(lot_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(alerte_bp)
    
    # Configuration Swagger
    SWAGGER_URL = '/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "FutureKawa API",
            'dom_id': '#swagger-ui',
            'deepLinking': True,
            'displayRequestDuration': True,
            'docExpansion': "none",
            'operationsSorter': "alpha",
            'filter': True,
            'showExtensions': True,
            'showCommonExtensions': True
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Middleware pour validation des tokens (à implémenter avec API d'authentification externe)
    @app.before_request
    def validate_token():
        """
        Middleware pour valider les tokens JWT via API d'authentification externe
        """
        # Routes qui ne nécessitent pas d'authentification
        public_routes = ['/docs', '/static/swagger.json', '/api/auth/validate']
        
        if request.path in public_routes:
            return None
        
        # Pour l'instant, on skippe la validation (à implémenter)
        # TODO: Implémenter la validation avec l'API d'authentification externe
        return None
    
    @app.route('/api/auth/validate', methods=['GET'])
    def validate_auth():
        """
        Endpoint de validation des tokens (pour l'API d'authentification externe)
        """
        # TODO: Implémenter la validation réelle des tokens
        return jsonify({'valid': True}), 200
    
    # Gestion des erreurs
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Ressource non trouvée'}), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Requête invalide'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Non authentifié'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Non autorisé'}), 403
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({'error': 'Erreur de validation'}), 422
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Erreur serveur interne'}), 500
    
    # Route de santé
    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Vérifie l'état de santé de l'API
        """
        try:
            # Test de connexion à la base de données
            db_status = "OK" if test_connection() else "ERREUR"
            
            return jsonify({
                'status': 'OK',
                'database': db_status,
                'version': '1.0.0'
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'ERREUR',
                'error': str(e)
            }), 500
    
    # Route racine
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'FutureKawa API - Gestion des stocks de grains de café vert',
            'version': '1.0.0',
            'docs': '/docs'
        }), 200
    
    return app

def init_database():
    """
    Initialise la base de données
    """
    try:
        print("Initialisation de la base de données...")
        init_db()
        print("Base de données initialisée avec succès!")
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise

if __name__ == '__main__':
    # Création de l'application
    app = create_app()
    
    # Initialisation de la base de données
    try:
        init_database()
    except Exception as e:
        print(f"Impossible d'initialiser la base de données: {e}")
    
    # Configuration du serveur de développement
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"Démarrage de l'API FutureKawa sur http://{host}:{port}")
    print(f"Documentation disponible sur: http://{host}:{port}/docs")
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        threaded=True
    )
