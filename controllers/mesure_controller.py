"""Contrôleur des mesures - Couche HTTP"""

from flask import Blueprint, request, jsonify
from services.mesure_service import MesureService

mesure_bp = Blueprint('mesure', __name__, url_prefix='/api/mesures')

@mesure_bp.route('', methods=['POST'])
def create_mesure():
    """Crée une mesure"""
    try:
        data = request.get_json()
        mesure = MesureService.create_mesure(data)
        return jsonify(mesure.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mesure_bp.route('/entrepot/<string:entrepot_id>', methods=['GET'])
def get_mesures_by_entrepot(entrepot_id):
    """Mesures entrepôt"""
    try:
        limit = request.args.get('limit', 100)
        from_date = request.args.get('from_date')
        
        mesures = MesureService.get_mesures_by_entrepot(entrepot_id, limit, from_date)
        result = [mesure.to_dict() for mesure in mesures]
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mesure_bp.route('/<string:mesure_id>', methods=['GET'])
def get_mesure(mesure_id):
    """Détails mesure"""
    try:
        mesure = MesureService.get_mesure_by_id(mesure_id)
        return jsonify(mesure.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
