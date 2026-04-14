from flask import Blueprint, request, jsonify
from services.lot_service import LotService

lot_bp = Blueprint('lot', __name__, url_prefix='/api/lots')

@lot_bp.route('/<string:lot_id>', methods=['GET'])
def get_lot(lot_id):
    """
    Récupère les infos du lot avec entrepôt, exploitation et pays
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
    Mesures température/humidité depuis la date de stockage du lot
    """
    try:
        # D'abord récupérer les infos du lot pour obtenir l'ID de l'entrepôt et la date de stockage
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
    Historique des alertes liées à ce lot
    """
    try:
        alertes = LotService.get_alertes_by_lot(lot_id)
        return jsonify(alertes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lot_bp.route('/<string:lot_id>', methods=['PUT'])
def update_lot(lot_id):
    """
    Mettre à jour le lot (principalement pour datSortie)
    """
    try:
        data = request.get_json()
        lot = LotService.update_lot(lot_id, data)
        
        if not lot:
            return jsonify({'error': 'Lot non trouvé'}), 404
            
        return jsonify(lot), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
