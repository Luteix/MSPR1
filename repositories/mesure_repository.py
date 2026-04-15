"""Repository pour les mesures - Couche BDD"""

from database import get_db, commit_session, rollback_session
from models import Mesure
from sqlalchemy import text
from datetime import datetime

class MesureRepository:
    """Gestion des opérations BDD pour les mesures"""
    
    @staticmethod
    def create(mesure_data):
        """Crée une nouvelle mesure"""
        session = get_db()
        try:
            # Gestion de l'auto-incrémentation manuelle si la BDD ne l'a pas configurée
            if 'idMesure' not in mesure_data:
                # Récupérer le dernier ID et incrémenter
                last_mesure = session.query(Mesure).order_by(Mesure.idMesure.desc()).first()
                next_id = (last_mesure.idMesure + 1) if last_mesure else 1
                mesure_data['idMesure'] = next_id
            
            mesure = Mesure(**mesure_data)
            session.add(mesure)
            session.flush()
            session.commit()
            # Rafraîchir l'objet pour éviter les problèmes de session
            session.refresh(mesure)
            # Détacher l'objet de la session avant de la fermer
            session.expunge(mesure)
            return mesure
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_by_entrepot(entrepot_id, limit=100, from_date=None):
        """Récupère les mesures d'un entrepôt"""
        session = get_db()
        try:
            query = session.query(Mesure).filter(Mesure.idEntrepot == entrepot_id)
            
            if from_date:
                query = query.filter(Mesure.datMesure >= from_date)
            
            return query.order_by(Mesure.datMesure.desc()).limit(limit).all()
        finally:
            session.close()
    
    @staticmethod
    def get_by_id(mesure_id):
        """Récupère une mesure par son ID"""
        session = get_db()
        try:
            return session.query(Mesure).filter(Mesure.idMesure == mesure_id).first()
        finally:
            session.close()
    
    @staticmethod
    def get_seuils_entrepot(entrepot_id):
        """Récupère les seuils de température/humidité pour un entrepôt"""
        session = get_db()
        try:
            result = session.execute(text("""
                SELECT p.temperatureMin, p.temperatureMax, p.humiditeMin, p.humiditeMax
                FROM entrepot e
                JOIN exploitation ex ON e.idExploitation = ex.idExploitation
                JOIN pays p ON ex.idPays = p.idPays
                WHERE e.idEntrepot = :idEntrepot
            """), {"idEntrepot": entrepot_id}).fetchone()
            return result
        finally:
            session.close()
