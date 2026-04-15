"""Repository pour les alertes - Couche BDD"""

from database import get_db, commit_session, rollback_session
from models import Alerte

class AlerteRepository:
    """Gestion des opérations BDD pour les alertes"""
    
    @staticmethod
    def create(alerte_data):
        """Crée une nouvelle alerte"""
        session = get_db()
        try:
            alerte = Alerte(**alerte_data)
            session.add(alerte)
            session.commit()
            session.refresh(alerte)
            session.expunge(alerte)
            return alerte
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_all():
        """Récupère toutes les alertes"""
        session = get_db()
        try:
            return session.query(Alerte).order_by(Alerte.idAlerte.desc()).all()
        finally:
            session.close()
    
    @staticmethod
    def get_by_id(alerte_id):
        """Récupère une alerte par son ID"""
        session = get_db()
        try:
            return session.query(Alerte).filter(Alerte.idAlerte == alerte_id).first()
        finally:
            session.close()
