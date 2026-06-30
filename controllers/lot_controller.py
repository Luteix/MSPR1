"""Contrôleur des lots"""

from flask import Blueprint, request, jsonify
from services.lot_service import LotService

lot_bp = Blueprint('lot', __name__, url_prefix='/api/lots')

@lot_bp.route('', methods=['GET'])
def get_all_lots():
    """
    Liste les lots.
    ---
    tags:
      - Lots
    responses:
      200:
        description: Liste des lots
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
    Récupère un lot.
    ---
    tags:
      - Lots
    parameters:
      - name: lot_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Lot trouvé
        schema:
          type: object
      404:
        description: Lot introuvable
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
    Retourne les mesures d'un lot.
    ---
    tags:
      - Lots
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
      404:
        description: Lot introuvable
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
    Liste les alertes d'un lot.
    ---
    tags:
      - Lots
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
      404:
        description: Lot introuvable
    """
    try:
        alertes = LotService.get_alertes_by_lot(lot_id)
        return jsonify(alertes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lot_bp.route('/<string:lot_id>', methods=['PUT'])
def update_lot(lot_id):
    """
    Met à jour un lot.
    ---
    tags:
      - Lots
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
      404:
        description: Lot introuvable
    """
    try:
        data = request.get_json()
        lot = LotService.update_lot(lot_id, data)
        
        if not lot:
            return jsonify({'error': 'Lot non trouvé'}), 404
            
        return jsonify(lot), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
