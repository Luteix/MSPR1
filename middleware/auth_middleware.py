"""
FICHIER: middleware/auth_middleware.py
UTILITÉ: Protection des routes par JWT (Middleware)

Fournit:
- @require_auth : Décorateur pour protéger une route
- Vérifie le header "Authorization: Bearer <token>"
- Retourne 401 si token manquant, invalide ou expiré

Usage:
    @app.route('/admin')
    @require_auth
    def admin_route():
        return jsonify({'message': 'Accès autorisé'})
"""

from functools import wraps
from flask import request, jsonify
from services.auth_service import AuthService
import jwt

def require_auth(f):
    """
    Décorateur qui protège une route par authentification JWT
    Vérifie le header Authorization: Bearer <token>
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            return jsonify({'message': 'Accès autorisé'})
    
    Le décorateur ajoute automatiquement:
        - request.user_id: ID de l'utilisateur connecté
        - request.user: Objet utilisateur complet (si disponible)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Récupère le header Authorization
        auth_header = request.headers.get('Authorization', '')
        
        # Vérifie le format
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Authentification requise',
                'message': 'Header Authorization manquant ou invalide. Format attendu: Bearer <token>'
            }), 401
        
        # Extrait le token
        token = auth_header[7:]  # Enlève "Bearer "
        
        if not token:
            return jsonify({
                'error': 'Token manquant',
                'message': 'Aucun token fourni'
            }), 401
        
        try:
            # Vérifie et décode le token
            payload = AuthService.verify_token(token)
            user_id = payload.get('user_id')
            
            if not user_id:
                return jsonify({
                    'error': 'Token invalide',
                    'message': 'Token ne contient pas d\'ID utilisateur'
                }), 401
            
            # Ajoute l'user_id à la requête pour les controllers
            request.user_id = user_id
            
            # Récupère l'utilisateur complet (optionnel)
            user = AuthService.get_current_user(token)
            if user:
                request.user = user
            
            # Appelle la fonction originale
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'error': 'Token expiré',
                'message': 'Votre session a expiré. Veuillez vous reconnecter.'
            }), 401
            
        except jwt.InvalidTokenError as e:
            return jsonify({
                'error': 'Token invalide',
                'message': f'Token non valide: {str(e)}'
            }), 401
            
        except Exception as e:
            return jsonify({
                'error': 'Erreur d\'authentification',
                'message': str(e)
            }), 401
    
    return decorated_function


# Décorateurs pour les rôles (optionnel, pour plus tard)
def require_role(role_id):
    """
    Décorateur qui vérifie que l'utilisateur a un rôle spécifique
    Usage: @require_role(2) pour exiger le rôle Responsable
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # D'abord authentification
            auth_result = _check_auth()
            if auth_result:
                return auth_result
            
            # Puis vérification du rôle
            if not hasattr(request, 'user') or request.user.idPoste != role_id:
                return jsonify({
                    'error': 'Accès refusé',
                    'message': f'Rôle insuffisant. Requis: {role_id}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def _check_auth():
    """Fonction helper pour vérifier l'authentification"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authentification requise'}), 401
    
    token = auth_header[7:]
    
    try:
        payload = AuthService.verify_token(token)
        user_id = payload.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Token invalide'}), 401
        
        request.user_id = user_id
        user = AuthService.get_current_user(token)
        if user:
            request.user = user
        
        return None  # Pas d'erreur
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expiré'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token invalide'}), 401
