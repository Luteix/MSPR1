from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from sqlalchemy import func, and_, or_
from models import LotGrains, Entrepot, Exploitation, Pays, Mesure, Alerte, StatutLot, TypeAlerte
from database import get_db, commit_session, rollback_session

class LotService:
    
    @staticmethod
    def get_lot_by_id(lot_id):
        """
        Récupère les infos d'un lot avec entrepôt, exploitation et pays
        """
        session = get_db()
        try:
            lot = session.query(LotGrains).options(
                joinedload(LotGrains.entrepot)
                .joinedload(Entrepot.exploitation)
                .joinedload(Exploitation.pays)
            ).filter(LotGrains.idLotGrains == lot_id).first()
            
            if not lot:
                return None
            
            return lot.to_dict(include_hierarchy=True)
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_mesures_by_lot(entrepot_id, date_debut):
        """
        Récupère les mesures température/humidité depuis la date de stockage du lot
        """
        session = get_db()
        try:
            date_from = datetime.fromisoformat(date_debut.replace('Z', '+00:00')) if isinstance(date_debut, str) else date_debut
            
            mesures = session.query(Mesure).filter(
                and_(
                    Mesure.idEntrepot == entrepot_id,
                    Mesure.datMesure >= date_from
                )
            ).order_by(Mesure.datMesure.desc()).all()
            
            return [mesure.to_dict() for mesure in mesures]
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_alertes_by_lot(lot_id):
        """
        Récupère l'historique des alertes liées à un lot
        """
        session = get_db()
        try:
            alertes = session.query(Alerte).filter(
                Alerte.idLotGrains == lot_id
            ).order_by(Alerte.dateAlerte.desc()).all()
            
            return [alerte.to_dict() for alerte in alertes]
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def update_lot(lot_id, data):
        """
        Met à jour un lot (principalement pour datSortie)
        """
        session = get_db()
        try:
            lot = session.query(LotGrains).filter(
                LotGrains.idLotGrains == lot_id
            ).first()
            
            if not lot:
                return None
            
            if 'datSortie' in data:
                if data['datSortie']:
                    lot.datSortie = datetime.fromisoformat(data['datSortie'].replace('Z', '+00:00')) if isinstance(data['datSortie'], str) else data['datSortie']
                else:
                    lot.datSortie = None
            
            commit_session()
            return lot.to_dict()
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def update_lot_status():
        """
        Met à jour le statut de tous les lots (calcul automatique)
        """
        session = get_db()
        try:
            lots = session.query(LotGrains).options(
                joinedload(LotGrains.entrepot)
                .joinedload(Entrepot.exploitation)
                .joinedload(Exploitation.pays)
            ).all()
            
            for lot in lots:
                ancien_statut = lot.statut
                nouveau_statut = LotService._calculer_statut_lot(lot)
                
                if ancien_statut != nouveau_statut:
                    lot.statut = nouveau_statut
                    
                    # Créer une alerte si le lot devient périmé
                    if nouveau_statut == StatutLot.PERIME:
                        alerte = Alerte(
                            idEntrepot=lot.idEntrepot,
                            idLotGrains=lot.idLotGrains,
                            type=TypeAlerte.LOT_PERIME,
                            dateAlerte=datetime.utcnow(),
                            statut="en cours"
                        )
                        session.add(alerte)
            
            commit_session()
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def _calculer_statut_lot(lot):
        """
        Calcule le statut d'un lot selon les règles métier
        """
        # Vérifier si le lot est périmé (> 365 jours)
        if lot.datSto:
            age_jours = (datetime.utcnow() - lot.datSto).days
            if age_jours > 365:
                return StatutLot.PERIME
            
            # Vérifier si le lot est proche de la péremption (> 300 jours)
            if age_jours > 300:
                return StatutLot.EN_ALERTE
        
        # Vérifier les conditions environnementales
        if lot.entrepot and lot.entrepot.exploitation and lot.entrepot.exploitation.pays:
            pays = lot.entrepot.exploitation.pays
            
            # Récupérer la dernière mesure
            derniere_mesure = session.query(Mesure).filter(
                Mesure.idEntrepot == lot.idEntrepot
            ).order_by(Mesure.datMesure.desc()).first()
            
            if derniere_mesure:
                if (derniere_mesure.temperature < pays.temperatureMin or 
                    derniere_mesure.temperature > pays.temperatureMax or
                    derniere_mesure.humidite < pays.humiditeMin or 
                    derniere_mesure.humidite > pays.humiditeMax):
                    return StatutLot.EN_ALERTE
        
        return StatutLot.CONFORME
