"""
Application Flask principale pour l'API FutureKawa

Cette API REST gère les stocks de grains de café vert pour la société FutureKawa.
Elle fournit des endpoints pour la gestion des exploitations, entrepôts, lots,
et des tableaux de bord de suivi.

Technologies utilisées:
- Flask: Framework web microservice
- SQLAlchemy: ORM pour la base de données
- Flask-CORS: Gestion des requêtes cross-origin
- Flask-Swagger-UI: Documentation API interactive
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from database import init_db, test_connection
import os
from datetime import timedelta

# =============================================================================
# IMPORT DES CONTRÔLEURS (BLUEPRINTS)
# =============================================================================

# Import des blueprints pour l'organisation modulaire de l'API
# Chaque blueprint gère une ressource spécifique de l'application
from controllers.pays_controller import pays_bp          # Gestion des pays
from controllers.exploitation_controller import exploitation_bp  # Gestion des exploitations
from controllers.entrepot_controller import entrepot_bp    # Gestion des entrepôts
from controllers.lot_controller import lot_bp            # Gestion des lots de café
from controllers.dashboard_controller import dashboard_bp, alerte_bp  # Tableaux de bord et alertes

def create_app():
    """
    Factory function pour créer et configurer l'application Flask
    
    Returns:
        Flask: Instance de l'application Flask configurée
        
    Cette fonction suit le pattern factory pour permettre la création
    de multiples instances de l'application (utile pour les tests).
    """
    app = Flask(__name__)
    
    # =====================================================================
    # CONFIGURATION DE L'APPLICATION
    # =====================================================================
    
    # Clé secrète pour la sécurité des sessions et tokens JWT
    # En production, utiliser une clé forte et la stocker dans .env
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Préserver l'ordre des clés dans les réponses JSON (important pour l'API)
    app.config['JSON_SORT_KEYS'] = False
    
    # =====================================================================
    # CONFIGURATION CORS
    # =====================================================================
    
    # Activer CORS pour permettre les requêtes cross-origin
    # Permet aux applications frontend d'accéder à l'API depuis différents domaines
    CORS(app, origins=["*"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # =====================================================================
    # ENREGISTREMENT DES BLUEPRINTS
    # =====================================================================
    
    # Enregistrement de tous les blueprints des contrôleurs
    # Chaque blueprint ajoute ses routes à l'application principale
    app.register_blueprint(pays_bp)          # Routes /api/pays/*
    app.register_blueprint(exploitation_bp)   # Routes /api/exploitations/*
    app.register_blueprint(entrepot_bp)       # Routes /api/entrepots/*
    app.register_blueprint(lot_bp)            # Routes /api/lots/*
    app.register_blueprint(dashboard_bp)      # Routes /api/dashboard/*
    app.register_blueprint(alerte_bp)        # Routes /api/alertes/*
    
    # =====================================================================
    # CONFIGURATION SWAGGER UI
    # =====================================================================
    
    # Configuration de l'interface de documentation API Swagger
    # Permet aux développeurs de tester et documenter les endpoints
    SWAGGER_URL = '/docs'                    # URL d'accès à la documentation
    API_URL = '/static/swagger.json'         # Fichier de configuration Swagger
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "FutureKawa API",      # Nom affiché dans l'interface
            'dom_id': '#swagger-ui',           # ID du conteneur DOM
            'deepLinking': True,               # Permet les liens directs vers les endpoints
            'displayRequestDuration': True,     # Affiche la durée des requêtes
            'docExpansion': "none",             # État initial des sections
            'operationsSorter': "alpha",        # Tri alphabétique des opérations
            'filter': True,                     # Permet de filtrer les endpoints
            'showExtensions': True,             # Affiche les extensions
            'showCommonExtensions': True        # Affiche les extensions communes
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # =====================================================================
    # MIDDLEWARE D'AUTHENTIFICATION
    # =====================================================================
    
    @app.before_request
    def validate_token():
        """
        Middleware pour valider les tokens JWT via API d'authentification externe
        
        Ce middleware s'exécute avant chaque requête pour vérifier que le client
        est authentifié. Pour le développement, la validation est désactivée.
        
        TODO: Implémenter la validation avec l'API d'authentification externe
        """
        # Routes publiques qui ne nécessitent pas d'authentification
        public_routes = ['/docs', '/static/swagger.json', '/api/auth/validate']
        
        if request.path in public_routes:
            return None
        
        # Pour l'instant, on skippe la validation (développement)
        # TODO: Implémenter la validation avec l'API d'authentification externe
        return None
    
    @app.route('/api/auth/validate', methods=['GET'])
    def validate_auth():
        """
        Endpoint de validation des tokens (pour l'API d'authentification externe)
        
        Returns:
            JSON: Réponse indiquant si le token est valide
            
        TODO: Implémenter la validation réelle des tokens JWT
        """
        # TODO: Implémenter la validation réelle des tokens
        return jsonify({'valid': True}), 200
    
    # =====================================================================
    # GESTIONNAIRES D'ERREURS
    # =====================================================================
    
    @app.errorhandler(404)
    def not_found(error):
        """
        Gestionnaire d'erreur 404 - Ressource non trouvée
        
        Args:
            error: Objet erreur Flask
            
        Returns:
            JSON: Message d'erreur formaté
        """
        return jsonify({'error': 'Ressource non trouvée'}), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        """
        Gestionnaire d'erreur 400 - Requête invalide
        
        Args:
            error: Objet erreur Flask
            
        Returns:
            JSON: Message d'erreur formaté
        """
        return jsonify({'error': 'Requête invalide'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """
        Gestionnaire d'erreur 401 - Non authentifié
        
        Args:
            error: Objet erreur Flask
            
        Returns:
            JSON: Message d'erreur formaté
        """
        return jsonify({'error': 'Non authentifié'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """
        Gestionnaire d'erreur 403 - Non autorisé
        
        Args:
            error: Objet erreur Flask
            
        Returns:
            JSON: Message d'erreur formaté
        """
        return jsonify({'error': 'Non autorisé'}), 403
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """
        Gestionnaire d'erreur 422 - Erreur de validation
        
        Args:
            error: Objet erreur Flask
            
        Returns:
            JSON: Message d'erreur formaté
        """
        return jsonify({'error': 'Erreur de validation'}), 422
    
    @app.errorhandler(500)
    def internal_error(error):
        """
        Gestionnaire d'erreur 500 - Erreur serveur interne
        
        Args:
            error: Objet erreur Flask
            
        Returns:
            JSON: Message d'erreur formaté
        """
        return jsonify({'error': 'Erreur serveur interne'}), 500
    
    # =====================================================================
    # ROUTES PRINCIPALES
    # =====================================================================
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Endpoint de santé pour le monitoring de l'API
        
        Permet de vérifier que l'API fonctionne correctement
        et que la connexion à la base de données est active.
        
        Returns:
            JSON: État de santé de l'API et de ses composants
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
    
    @app.route('/', methods=['GET'])
    def root():
        """
        Route racine de l'API
        
        Fournit des informations de base sur l'API et les liens utiles.
        
        Returns:
            JSON: Message de bienvenue et informations sur l'API
        """
        return jsonify({
            'message': 'FutureKawa API - Gestion des stocks de grains de café vert',
            'version': '1.0.0',
            'docs': '/docs'
        }), 200
    
    return app

# =============================================================================
# FONCTIONS D'INITIALISATION
# =============================================================================

def init_database():
    """
    Initialise la base de données au démarrage de l'application
    
    Cette fonction est appelée au démarrage pour s'assurer que
    toutes les tables nécessaires existent dans la base de données.
    
    Raises:
        Exception: En cas d'erreur lors de l'initialisation
    """
    try:
        print("Initialisation de la base de données...")
        init_db()
        print("Base de données initialisée avec succès!")
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise

# =============================================================================
# POINT D'ENTRÉE PRINCIPAL
# =============================================================================

if __name__ == '__main__':
    """
    Point d'entrée principal pour lancer l'application Flask
    
    Cette section s'exécute uniquement lorsque le script est lancé
    directement (pas lors de l'import comme module).
    """
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
    
    # Démarrage du serveur Flask
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        threaded=True  # Permet de gérer plusieurs requêtes simultanément
    )
