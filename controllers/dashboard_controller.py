"""
Contrôleur dashboard et alertes
"""

from flask import Blueprint, request, jsonify
from services.dashboard_service import DashboardService, AlerteService

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')
alerte_bp = Blueprint('alerte', __name__, url_prefix='/api/alertes')

@dashboard_bp.route('/summary', methods=['GET'])
def get_dashboard_summary():
    """Récupère le résumé global du dashboard"""
    try:
        summary = DashboardService.get_dashboard_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

alerte_bp = Blueprint('alerte', __name__, url_prefix='/api/alertes')

@alerte_bp.route('/recent', methods=['GET'])
def get_recent_alertes():
    """Récupère les dernières alertes"""
    try:
        limit = request.args.get('limit', 5, type=int)
        alertes = AlerteService.get_recent_alertes(limit)
        return jsonify(alertes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alerte_bp.route('', methods=['GET'])
def get_all_alertes():
    """Récupère toutes les alertes avec filtres"""
    try:
        pays_id = request.args.get('pays')
        type_alerte = request.args.get('type')
        date_from = request.args.get('from')
        date_to = request.args.get('to')
        
        alertes = AlerteService.get_all_alertes(pays_id, type_alerte, date_from, date_to)
        return jsonify(alertes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alerte_bp.route('', methods=['POST'])
def create_alerte():
    """Crée une nouvelle alerte manuellement"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        if 'idEntrepot' not in data or 'type' not in data:
            return jsonify({'error': 'Champs requis: idEntrepot, type'}), 400
        
        alerte = AlerteService.create_alerte(data)
        return jsonify(alerte), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alerte_bp.route('/<string:alerte_id>/statut', methods=['PUT'])
def update_alerte_statut(alerte_id):
    """Met à jour le statut d'une alerte"""
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
