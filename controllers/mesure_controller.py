"""
Contrôleur pour la gestion des mesures environnementales
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from database import get_db, commit_session, rollback_session
from models import Mesure

# Blueprint pour les routes /api/mesures/*
mesure_bp = Blueprint('mesure', __name__, url_prefix='/api/mesures')

@mesure_bp.route('', methods=['POST'])
def create_mesure():
    """
    Crée une nouvelle mesure
    ---
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
    responses:
      201:
        description: Mesure créée
        schema:
          type: object
    """
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['idEntrepot', 'temperature', 'humidite']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ requis: {field}'}), 400
        
        session = get_db()
        
        # Création de la mesure
        mesure = Mesure(
            idEntrepot=data['idEntrepot'],
            temperature=float(data['temperature']),
            humidite=float(data['humidite']),
            datMesure=datetime.fromisoformat(data['datMesure'].replace('Z', '+00:00')) if 'datMesure' in data else datetime.utcnow()
        )
        
        session.add(mesure)
        commit_session()
        
        result = mesure.to_dict()
        session.close()
        
        return jsonify(result), 201
        
    except Exception as e:
        rollback_session()
        return jsonify({'error': str(e)}), 500

@mesure_bp.route('/entrepot/<string:entrepot_id>', methods=['GET'])
def get_mesures_by_entrepot(entrepot_id):
    """
    Mesures d'un entrepôt
    ---
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
        session = get_db()
        
        query = session.query(Mesure).filter(Mesure.idEntrepot == entrepot_id)
        
        # Filtre par date si spécifié
        from_date = request.args.get('from_date')
        if from_date:
            from_date_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
            query = query.filter(Mesure.datMesure >= from_date_dt)
        
        # Limite les résultats
        limit = request.args.get('limit', 100, type=int)
        mesures = query.order_by(Mesure.datMesure.desc()).limit(limit).all()
        
        result = [mesure.to_dict() for mesure in mesures]
        session.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        rollback_session()
        return jsonify({'error': str(e)}), 500

@mesure_bp.route('/<string:mesure_id>', methods=['GET'])
def get_mesure(mesure_id):
    """
    Détails d'une mesure
    ---
    parameters:
      - name: mesure_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Détails de la mesure
        schema:
          type: object
    """
    try:
        session = get_db()
        mesure = session.query(Mesure).filter(Mesure.idMesure == mesure_id).first()
        
        if not mesure:
            session.close()
            return jsonify({'error': 'Mesure non trouvée'}), 404
        
        result = mesure.to_dict()
        session.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        rollback_session()
        return jsonify({'error': str(e)}), 500
