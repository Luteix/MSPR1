"""Contrôleur des mesures - Couche HTTP"""

from flask import Blueprint, request, jsonify
from services.mesure_service import MesureService

mesure_bp = Blueprint('mesure', __name__, url_prefix='/api/mesures')

@mesure_bp.route('', methods=['POST'])
def create_mesure():
    """
    Crée une mesure.
    ---
    tags:
      - Mesures
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - idEntrepot
            - temperature
            - humidite
            - datMesure
    responses:
      201:
        description: Mesure créée
      400:
        description: Données invalides
    """
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
    """
    Liste les mesures d'un entrepôt.
    ---
    tags:
      - Mesures
    parameters:
      - name: entrepot_id
        in: path
        required: true
        type: string
      - name: limit
        in: query
        type: integer
        default: 100
      - name: from_date
        in: query
        type: string
    responses:
      200:
        description: Liste des mesures
        schema:
          type: array
    """
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
    """
    Récupère une mesure.
    ---
    tags:
      - Mesures
    parameters:
      - name: mesure_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Mesure trouvée
        schema:
          type: object
      404:
        description: Mesure introuvable
    """
    try:
        mesure = MesureService.get_mesure_by_id(mesure_id)
        return jsonify(mesure.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
