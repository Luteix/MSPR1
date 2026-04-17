"""
FICHIER: app.py
UTILITÉ: Point d'entrée principal de l'API Flask

- Crée et configure l'application Flask (factory pattern)
- Enregistre tous les blueprints (routes API)
- Configure CORS, Swagger (documentation), et le middleware d'auth
- Démarre le serveur sur http://localhost:5000

Pour lancer: python app.py
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
from database import init_db, test_connection

# Import des blueprints pour l'organisation modulaire de l'API
from controllers.pays_controller import pays_bp
from controllers.exploitation_controller import exploitation_bp
from controllers.entrepot_controller import entrepot_bp
from controllers.lot_controller import lot_bp
from controllers.dashboard_controller import dashboard_bp, alerte_bp
from controllers.mesure_controller import mesure_bp
from controllers.auth_controller import auth_bp  # Blueprint d'authentification

def create_app():
    """Factory function pour créer et configurer l'application Flask"""
    app = Flask(__name__)
    
    # Configuration de l'application
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Configuration CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Configuration Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
                "title": "API Futurekawa",
                "description": "API REST pour la gestion de la chaîne d'approvisionnement du café",
                "version": "1.0.0"
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }
    Swagger(app, config=swagger_config)
    
    # Enregistrement des blueprints
    app.register_blueprint(pays_bp)
    app.register_blueprint(exploitation_bp)
    app.register_blueprint(entrepot_bp)
    app.register_blueprint(lot_bp)
    app.register_blueprint(mesure_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(alerte_bp)
    app.register_blueprint(auth_bp)  # Routes d'authentification (/api/login, /api/register)
    
    # Middleware d'authentification
    @app.before_request
    def validate_token():
        # Routes publiques qui ne nécessitent pas d'authentification
        public_routes = [
            '/docs', 
            '/static/swagger.json', 
            '/api/verify',
            '/api/login',      # Connexion - doit être publique
            '/api/register'    # Inscription - doit être publique
        ]
        
        if request.path in public_routes:
            return None
        
        # Pour l'instant, on skippe la validation (développement)
        # TODO: Implémenter la validation avec l'API d'authentification externe
        return None
    
    @app.route('/api/auth/validate', methods=['GET'])
    def validate_auth():
        # TODO: Implémenter la validation réelle des tokens JWT
        return jsonify({'valid': True}), 200
    
    # Gestion des erreurs
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Ressource non trouvée'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Erreur interne du serveur'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Requête invalide'}), 400
    
    # Route de santé
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'Futurekawa API'})
    
    return app

def setup_database_auto():
    """Crée la BDD et les tables automatiquement si elles n'existent pas"""
    import pymysql
    from dotenv import load_dotenv
    
    load_dotenv()
    
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', '3306'))
    db_name = os.getenv('DB_NAME', 'futurekawa')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    
    try:
        # Essaie de se connecter SANS spécifier de base
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        
        # Crée la base si elle n'existe pas
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"[OK] Base de données '{db_name}' prête")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERREUR] Impossible de créer la base de données: {e}")
        return False


if __name__ == '__main__':
    """Point d'entrée principal de l'application"""
    print("Initialisation de l'API Futurekawa...")
    
    # Vérifie/crée la base de données automatiquement
    if not test_connection():
        print("[INFO] Base de données inexistante, création automatique...")
        if not setup_database_auto():
            print("[ERREUR] Échec de la création de la base de données")
            exit(1)
    
    # Maintenant la connexion doit fonctionner
    if test_connection():
        print("[OK] Connexion à la base de données réussie")
        
        # Initialisation des tables (les crée si elles n'existent pas)
        init_db()
        print("[OK] Tables initialisées")
        
        # Lancement de l'application
        app = create_app()
        
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5000))
        
        print(f"[OK] API démarrée sur http://{host}:{port}")
        print(f"[OK] Documentation sur http://{host}:{port}/docs")
        
        app.run(host=host, port=port, debug=app.config['DEBUG'])
    else:
        print("[ERREUR] Connexion à la base de données impossible")
        exit(1)
