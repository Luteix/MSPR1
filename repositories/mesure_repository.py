"""Repository pour les mesures - Couche d'accès aux données"""

from sqlalchemy.orm import joinedload
from models import Mesure, Entrepot, Exploitation, Pays
from database import get_db, commit_session, rollback_session, close_session

class MesureRepository:
    @staticmethod
    def create(data):
        """Crée une nouvelle mesure en base de données."""
        session = get_db()
        try:
            mesure = Mesure(**data)
            session.add(mesure)
            commit_session()
            session.refresh(mesure) # Pour obtenir l'ID auto-généré
            return mesure
        except Exception as e:
            rollback_session()
            raise e
        finally:
            close_session()

    @staticmethod
    def get_seuils_entrepot(entrepot_id):
        """Récupère les seuils (température/humidité) d'un entrepôt via son pays."""
        session = get_db()
        try:
            # Les seuils sont définis au niveau du pays de l'exploitation de l'entrepôt
            entrepot = session.query(Entrepot).options(
                joinedload(Entrepot.exploitation).joinedload(Exploitation.pays)
            ).filter(Entrepot.idEntrepot == entrepot_id).first()
            
            if entrepot and entrepot.exploitation and entrepot.exploitation.pays:
                # Le service s'attend à un objet avec les attributs temperatureMin/Max, etc.
                # Le modèle Pays correspond parfaitement.
                return entrepot.exploitation.pays
            return None
        except Exception as e:
            raise e
        finally:
            close_session()

    @staticmethod
    def get_by_entrepot(entrepot_id, limit=100, from_date=None):
        """Récupère les mesures pour un entrepôt donné."""
        session = get_db()
        try:
            query = session.query(Mesure).filter(Mesure.idEntrepot == entrepot_id)
            
            if from_date:
                query = query.filter(Mesure.datMesure >= from_date)
            
            mesures = query.order_by(Mesure.datMesure.desc()).limit(limit).all()
            return mesures
        except Exception as e:
            raise e
        finally:
            close_session()

    @staticmethod
    def get_by_id(mesure_id):
        """Récupère une mesure par son ID."""
        session = get_db()
        try:
            return session.query(Mesure).filter(Mesure.idMesure == mesure_id).first()
        except Exception as e:
            raise e
        finally:
            close_session()