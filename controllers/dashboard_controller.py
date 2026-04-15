"""
Contrôleur dashboard et alertes
"""

from flask import Blueprint, request, jsonify
from services.dashboard_service import DashboardService

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')
alerte_bp = Blueprint('alerte', __name__, url_prefix='/api')

@dashboard_bp.route('/summary', methods=['GET'])
def get_dashboard_summary():
    """
    Résumé global du dashboard
    ---
    responses:
      200:
        description: OK
        schema:
          type: object
    """
    try:
        summary = DashboardService.get_dashboard_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alerte_bp.route('/alertes/recentes', methods=['GET'])
def get_recent_alertes():
    """
    Alertes récentes
    ---
    parameters:
      - name: limit
        in: query
        type: integer
        default: 5
    responses:
      200:
        description: OK
        schema:
          type: array
    """
    try:
        limit = request.args.get('limit', 5, type=int)
        alertes = AlerteService.get_recent_alertes(limit)
        return jsonify(alertes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alerte_bp.route('/alertes', methods=['GET'])
def get_all_alertes():
    """Liste des alertes"""
    try:
        alertes = DashboardService.get_all_alertes()
        # Les alertes sont déjà des dictionnaires retournés par le service
        return jsonify(alertes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alerte_bp.route('/alertes', methods=['POST'])
def create_alerte():
    """Crée une alerte"""
    try:
        data = request.get_json()
        alerte = DashboardService.create_alerte(data)
        # Gérer le cas où alerte est déjà un dict ou un objet
        if isinstance(alerte, dict):
            return jsonify(alerte), 201
        return jsonify(alerte.to_dict() if hasattr(alerte, 'to_dict') else alerte), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/alertes/<string:alerte_id>', methods=['PUT'])
def update_alerte_statut(alerte_id):
    """
    Met à jour le statut d'une alerte
    ---
    parameters:
      - name: alerte_id
        in: path
        required: true
        type: string
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - statut
    responses:
      200:
        description: OK
        schema:
          type: object
    """
    try:
        data = request.get_json()
        
        if 'statut' not in data:
            return jsonify({'error': 'Champ requis: statut'}), 400
        
        alerte = AlerteService.update_alerte_statut(alerte_id, data['statut'])
        
        if not alerte:
            return jsonify({'error': 'Alerte non trouvée'}), 404
            
        return jsonify(alerte), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
