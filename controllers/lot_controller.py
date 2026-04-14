"""Contrôleur des lots"""

from flask import Blueprint, request, jsonify
from services.lot_service import LotService

lot_bp = Blueprint('lot', __name__, url_prefix='/api/lots')

@lot_bp.route('', methods=['GET'])
def get_all_lots():
    """
    Liste des lots
    ---
    responses:
      200:
        description: OK
        schema:
          type: array
    """
    try:
        lots = LotService.get_all_lots()
        return jsonify(lots), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lot_bp.route('/<string:lot_id>', methods=['GET'])
def get_lot(lot_id):
    """
    Détails lot
    ---
    parameters:
      - name: lot_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: OK
        schema:
          type: object
    """
    try:
        lot = LotService.get_lot_by_id(lot_id)
        if not lot:
            return jsonify({'error': 'Lot non trouvé'}), 404
        return jsonify(lot), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lot_bp.route('/<string:lot_id>/mesures', methods=['GET'])
def get_mesures_by_lot(lot_id):
    """
    Mesures température/humidité d'un lot
    ---
    parameters:
      - name: lot_id
        in: path
        required: true
        type: string
      - name: from
        in: query
        type: string
    responses:
      200:
        description: Historique des mesures
        schema:
          type: array
    """
    try:
        # Récupérer d'abord les infos du lot pour obtenir l'ID de l'entrepôt et la date de stockage
        lot = LotService.get_lot_by_id(lot_id)
        if not lot:
            return jsonify({'error': 'Lot non trouvé'}), 404
        
        from_date = request.args.get('from', lot['datSto'])
        mesures = LotService.get_mesures_by_lot(lot['idEntrepot'], from_date)
        return jsonify(mesures), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lot_bp.route('/<string:lot_id>/alertes', methods=['GET'])
def get_alertes_by_lot(lot_id):
    """
    Historique des alertes d'un lot
    ---
    parameters:
      - name: lot_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Liste des alertes
        schema:
          type: array
    """
    try:
        alertes = LotService.get_alertes_by_lot(lot_id)
        return jsonify(alertes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lot_bp.route('/<string:lot_id>', methods=['PUT'])
def update_lot(lot_id):
    """
    Met à jour un lot
    ---
    parameters:
      - name: lot_id
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
        description: Lot mis à jour
        schema:
          type: object
    """
    try:
        data = request.get_json()
        lot = LotService.update_lot(lot_id, data)
        
        if not lot:
            return jsonify({'error': 'Lot non trouvé'}), 404
            
        return jsonify(lot), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
