"""Repository pour le dashboard - Couche BDD"""

from database import get_db, commit_session, rollback_session
from models import Alerte
from sqlalchemy.orm import joinedload

class DashboardRepository:
    """Gestion des opérations BDD pour le dashboard"""
    
    @staticmethod
    def get_alertes_with_hierarchy():
        """Récupère les alertes"""
        session = get_db()
        try:
            alertes = session.query(Alerte).order_by(Alerte.idAlerte.desc()).all()
            return [alerte.to_dict() for alerte in alertes]
        finally:
            session.close()
    
    @staticmethod
    def create_alerte(alerte_data):
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
