from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from sqlalchemy import func, and_, or_
from models import Entrepot, Exploitation, Pays, LotGrains, Mesure, StatutLot
from database import get_db, commit_session, rollback_session

class EntrepotService:
    
    @staticmethod
    def get_all_entrepots():
        """
        Récupère tous les entrepôts avec exploitation et pays
        """
        session = get_db()
        try:
            entrepots = session.query(Entrepot).options(
                joinedload(Entrepot.exploitation).joinedload(Exploitation.pays)
            ).all()
            
            return [ent.to_dict(include_details=True) for ent in entrepots]
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_entrepot_by_id(entrepot_id):
        """
        Récupère un entrepôt par son ID avec exploitation et pays
        """
        session = get_db()
        try:
            entrepot = session.query(Entrepot).options(
                joinedload(Entrepot.exploitation).joinedload(Exploitation.pays)
            ).filter(Entrepot.idEntrepot == entrepot_id).first()
            
            if not entrepot:
                return None
            
            return entrepot.to_dict(include_details=True)
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_mesures_by_entrepot(entrepot_id, periode=30):
        """
        Récupère les mesures température/humidité sur une période
        """
        session = get_db()
        try:
            date_debut = datetime.utcnow() - timedelta(days=periode)
            
            mesures = session.query(Mesure).filter(
                and_(
                    Mesure.idEntrepot == entrepot_id,
                    Mesure.datMesure >= date_debut
                )
            ).order_by(Mesure.datMesure.desc()).all()
            
            return [mesure.to_dict() for mesure in mesures]
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_lots_by_entrepot(entrepot_id):
        """
        Récupère les lots stockés triés par date de stockage croissante (FIFO)
        """
        session = get_db()
        try:
            lots = session.query(LotGrains).filter(
                LotGrains.idEntrepot == entrepot_id
            ).order_by(LotGrains.datSto.asc()).all()
            
            return [lot.to_dict() for lot in lots]
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def create_lot_in_entrepot(entrepot_id, data):
        """
        Crée un nouveau lot dans un entrepôt
        """
        session = get_db()
        try:
            # Vérifier que l'entrepot existe
            entrepot = session.query(Entrepot).filter(
                Entrepot.idEntrepot == entrepot_id
            ).first()
            
            if not entrepot:
                return None
            
            # Créer le lot
            lot = LotGrains(
                idEntrepot=entrepot_id,
                datSto=datetime.fromisoformat(data['datSto'].replace('Z', '+00:00')) if isinstance(data['datSto'], str) else data['datSto']
            )
            
            session.add(lot)
            commit_session()
            return lot.to_dict()
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def create_entrepot(data):
        """
        Crée un nouvel entrepôt
        """
        session = get_db()
        try:
            entrepot = Entrepot(
                idExploitation=data['idExploitation'],
                nom=data['nom'],
                adresse=data['adresse'],
                limiteQte=data['limiteQte']
            )
            session.add(entrepot)
            commit_session()
            return entrepot.to_dict()
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def update_entrepot(entrepot_id, data):
        """
        Met à jour un entrepôt
        """
        session = get_db()
        try:
            entrepot = session.query(Entrepot).filter(
                Entrepot.idEntrepot == entrepot_id
            ).first()
            
            if not entrepot:
                return None
            
            entrepot.nom = data.get('nom', entrepot.nom)
            entrepot.adresse = data.get('adresse', entrepot.adresse)
            entrepot.limiteQte = data.get('limiteQte', entrepot.limiteQte)
            entrepot.idExploitation = data.get('idExploitation', entrepot.idExploitation)
            
            commit_session()
            return entrepot.to_dict()
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def delete_entrepot(entrepot_id):
        """
        Supprime un entrepôt
        """
        session = get_db()
        try:
            entrepot = session.query(Entrepot).filter(
                Entrepot.idEntrepot == entrepot_id
            ).first()
            
            if not entrepot:
                return False
            
            session.delete(entrepot)
            commit_session()
            return True
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
