"""
Contrôleur pour la gestion des entrepôts
"""

from flask import Blueprint, request, jsonify
from services.entrepot_service import EntrepotService

# Blueprint pour les routes /api/entrepots/*
entrepot_bp = Blueprint('entrepot', __name__, url_prefix='/api/entrepots')

@entrepot_bp.route('', methods=['GET'])
def get_all_entrepots():
    """Récupère la liste de tous les entrepôts"""
    try:
        entrepots = EntrepotService.get_all_entrepots()
        return jsonify(entrepots), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@entrepot_bp.route('/<string:entrepot_id>', methods=['GET'])
def get_entrepot(entrepot_id):
    """Récupère les détails d'un entrepôt spécifique"""
    try:
        entrepot = EntrepotService.get_entrepot_by_id(entrepot_id)
        if not entrepot:
            return jsonify({'error': 'Entrepôt non trouvé'}), 404
        return jsonify(entrepot), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@entrepot_bp.route('/<string:entrepot_id>/mesures', methods=['GET'])
def get_mesures_by_entrepot(entrepot_id):
    """Récupère les mesures température/humidité d'un entrepôt"""
    try:
        periode = request.args.get('periode', 30, type=int)
        mesures = EntrepotService.get_mesures_by_entrepot(entrepot_id, periode)
        return jsonify(mesures), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@entrepot_bp.route('/<string:entrepot_id>/lots', methods=['GET'])
def get_lots_by_entrepot(entrepot_id):
    """Récupère les lots stockés dans un entrepôt"""
    try:
        lots = EntrepotService.get_lots_by_entrepot(entrepot_id)
        return jsonify(lots), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@entrepot_bp.route('/<string:entrepot_id>/lots', methods=['POST'])
def create_lot_in_entrepot(entrepot_id):
    """Crée un nouveau lot dans un entrepôt spécifique"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        if 'datSto' not in data:
            return jsonify({'error': 'Champ requis: datSto'}), 400
        
        lot = EntrepotService.create_lot_in_entrepot(entrepot_id, data)
        if not lot:
            return jsonify({'error': 'Entrepôt non trouvé'}), 404
            
        return jsonify(lot), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@entrepot_bp.route('', methods=['POST'])
def create_entrepot():
    """Crée un nouvel entrepôt"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['nom', 'adresse', 'limiteQte', 'idExploitation']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ requis: {field}'}), 400
        
        entrepot = EntrepotService.create_entrepot(data)
        return jsonify(entrepot), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@entrepot_bp.route('/<string:entrepot_id>', methods=['PUT'])
def update_entrepot(entrepot_id):
    """Met à jour un entrepôt existant"""
    try:
        data = request.get_json()
        entrepot = EntrepotService.update_entrepot(entrepot_id, data)
        
        if not entrepot:
            return jsonify({'error': 'Entrepôt non trouvé'}), 404
            
        return jsonify(entrepot), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@entrepot_bp.route('/<string:entrepot_id>', methods=['DELETE'])
def delete_entrepot(entrepot_id):
    """Supprime un entrepôt"""
    try:
        success = EntrepotService.delete_entrepot(entrepot_id)
        if not success:
            return jsonify({'error': 'Entrepôt non trouvé'}), 404
            
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
