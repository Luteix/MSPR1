"""
FICHIER: controllers/auth_controller.py
UTILITÉ: Routes HTTP pour l'authentification (Couche HTTP)

Définit les endpoints:
- POST /api/register : Inscription nouvel utilisateur
- POST /api/login : Connexion et génération JWT
- GET /api/verify : Vérification validité token

Utilise AuthService pour la logique métier.
"""

from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

# Création du Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Inscription d'un nouvel utilisateur
    Body JSON: {nom, prenom, email, password, idExploitation, idPoste (optionnel)}
    Returns: {user: {id, nom, prenom, email}, token: string}
    """
    try:
        data = request.get_json()
        
        # Validation des champs requis
        required = ['nom', 'prenom', 'email', 'password', 'idExploitation']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Champ requis: {field}'}), 400
        
        # Inscription
        result = AuthService.register(
            nom=data['nom'],
            prenom=data['prenom'],
            email=data['email'],
            password=data['password'],
            id_exploitation=data['idExploitation'],
            id_poste=data.get('idPoste', 1)
        )
        
        return jsonify({
            'message': 'Inscription réussie',
            'user': result['user'],
            'token': result['token']
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Connexion d'un utilisateur
    Body JSON: {email, password}
    Returns: {user: {...}, token: string}
    """
    try:
        data = request.get_json()
        
        # Validation
        if 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        
        # Authentification
        result = AuthService.login(
            email=data['email'],
            password=data['password']
        )
        
        return jsonify({
            'message': 'Connexion réussie',
            'user': result['user'],
            'token': result['token']
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """
    Vérifie si un token est valide (pour le frontend)
    Header: Authorization: Bearer <token>
    Returns: {valid: true, user: {...}} ou 401
    """
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token manquant'}), 401
        
        token = auth_header[7:]  # Enlève "Bearer "
        
        # Vérifie le token
        from services.auth_service import AuthService
        user = AuthService.get_current_user(token)
        
        if not user:
            return jsonify({'error': 'Token invalide'}), 401
        
        return jsonify({
            'valid': True,
            'user': {
                'id': user.idUtilisateur,
                'nom': user.nom,
                'prenom': user.prenom,
                'email': user.mail
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Token invalide'}), 401
