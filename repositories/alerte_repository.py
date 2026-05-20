"""Repository pour les alertes - Couche d'accès aux données"""

from models import Alerte
from database import get_db, commit_session, rollback_session, close_session

class AlerteRepository:
    @staticmethod
    def create(data):
        """Crée une nouvelle alerte en base de données."""
        session = get_db()
        try:
            alerte = Alerte(**data)
            session.add(alerte)
            commit_session()
            session.refresh(alerte)  # Pour obtenir l'ID auto-généré
            return alerte
        except Exception as e:
            rollback_session()
            raise e
        finally:
            close_session()