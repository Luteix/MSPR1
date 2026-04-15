"""Repository pour les entrepôts - Couche BDD"""

from database import get_db
from models import Entrepot, Exploitation
from sqlalchemy.orm import joinedload

class EntrepotRepository:
    """Gestion des opérations BDD pour les entrepôts"""
    
    @staticmethod
    def get_all():
        """Récupère tous les entrepôts"""
        session = get_db()
        try:
            return session.query(Entrepot).options(
                joinedload(Entrepot.exploitation).joinedload(Exploitation.pays)
            ).all()
        finally:
            session.close()
    
    @staticmethod
    def get_by_id(entrepot_id):
        """Récupère un entrepôt par son ID"""
        session = get_db()
        try:
            return session.query(Entrepot).options(
                joinedload(Entrepot.exploitation).joinedload(Exploitation.pays)
            ).filter(Entrepot.idEntrepot == entrepot_id).first()
        finally:
            session.close()
