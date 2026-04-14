"""
Contrôleur pour la gestion des pays
"""

from flask import Blueprint, request, jsonify
from services.pays_service import PaysService

# Blueprint pour les routes /api/pays/*
pays_bp = Blueprint('pays', __name__, url_prefix='/api/pays')

@pays_bp.route('', methods=['GET'])
def get_all_pays():
    """
    Liste de tous les pays
    ---
    responses:
      200:
        description: Liste des pays
        schema:
          type: array
    """
    try:
        pays = PaysService.get_all_pays()
        return jsonify(pays), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pays_bp.route('/<string:pays_id>', methods=['GET'])
def get_pays(pays_id):
    """
    Détails d'un pays
    ---
    parameters:
      - name: pays_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Détails du pays
        schema:
          type: object
    """
    try:
        pays = PaysService.get_pays_by_id(pays_id)
        if not pays:
            return jsonify({'error': 'Pays non trouvé'}), 404
        return jsonify(pays), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pays_bp.route('/<string:pays_id>/exploitations', methods=['GET'])
def get_exploitations_by_pays(pays_id):
    """
    Exploitations d'un pays
    ---
    parameters:
      - name: pays_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Liste des exploitations
        schema:
          type: array
    """
    try:
        exploitations = PaysService.get_exploitations_by_pays(pays_id)
        return jsonify(exploitations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pays_bp.route('/<string:pays_id>/mesures', methods=['GET'])
def get_mesures_history(pays_id):
    """
    Historique des températures
    ---
    parameters:
      - name: pays_id
        in: path
        required: true
        type: string
      - name: days
        in: query
        type: integer
        default: 7
    responses:
      200:
        description: Historique des températures
        schema:
          type: array
    """
    try:
        days = request.args.get('days', 7, type=int)
        history = PaysService.get_mesures_history(pays_id, days)
        return jsonify(history), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pays_bp.route('', methods=['POST'])
def create_pays():
    """
    Crée un nouveau pays
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nom
            - temperatureMin
            - temperatureMax
            - humiditeMin
            - humiditeMax
    responses:
      201:
        description: Pays créé
        schema:
          type: object
    """
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
    """
    Met à jour un pays
    ---
    parameters:
      - name: pays_id
        in: path
        required: true
        type: string
      - name: body
        in: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: Pays mis à jour
        schema:
          type: object
    """
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
    """
    Supprime un pays
    ---
    parameters:
      - name: pays_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Pays supprimé
        schema:
          type: object
    """
    try:
        success = PaysService.delete_pays(pays_id)
        if not success:
            return jsonify({'error': 'Pays non trouvé'}), 404
            
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
