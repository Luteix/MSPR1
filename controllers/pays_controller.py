"""
Contrôleur pour la gestion des pays
"""

from flask import Blueprint, request, jsonify
from services.pays_service import PaysService

# Blueprint pour les routes /api/pays/*
pays_bp = Blueprint('pays', __name__, url_prefix='/api/pays')

@pays_bp.route('', methods=['GET'])
def get_all_pays():
    """Récupère la liste de tous les pays"""
    try:
        pays = PaysService.get_all_pays()
        return jsonify(pays), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pays_bp.route('/<string:pays_id>', methods=['GET'])
def get_pays(pays_id):
    """Récupère les détails d'un pays spécifique"""
    try:
        pays = PaysService.get_pays_by_id(pays_id)
        if not pays:
            return jsonify({'error': 'Pays non trouvé'}), 404
        return jsonify(pays), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pays_bp.route('/<string:pays_id>/exploitations', methods=['GET'])
def get_exploitations_by_pays(pays_id):
    """Récupère les exploitations d'un pays avec statistiques"""
    try:
        exploitations = PaysService.get_exploitations_by_pays(pays_id)
        return jsonify(exploitations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pays_bp.route('/<string:pays_id>/mesures/history', methods=['GET'])
def get_mesures_history(pays_id):
    """Récupère l'historique des températures moyennes"""
    try:
        days = request.args.get('days', 7, type=int)
        history = PaysService.get_mesures_history(pays_id, days)
        return jsonify(history), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pays_bp.route('', methods=['POST'])
def create_pays():
    """Crée un nouveau pays"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['nom', 'temperatureMin', 'temperatureMax', 'humiditeMin', 'humiditeMax']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ requis: {field}'}), 400
        
        pays = PaysService.create_pays(data)
        return jsonify(pays), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pays_bp.route('/<string:pays_id>', methods=['PUT'])
def update_pays(pays_id):
    """Met à jour un pays existant"""
    try:
        data = request.get_json()
        pays = PaysService.update_pays(pays_id, data)
        
        if not pays:
            return jsonify({'error': 'Pays non trouvé'}), 404
            
        return jsonify(pays), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pays_bp.route('/<string:pays_id>', methods=['DELETE'])
def delete_pays(pays_id):
    """Supprime un pays"""
    try:
        success = PaysService.delete_pays(pays_id)
        if not success:
            return jsonify({'error': 'Pays non trouvé'}), 404
            
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
