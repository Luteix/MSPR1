from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from sqlalchemy import func, and_
from models import Pays, Exploitation, Entrepot, LotGrains, Mesure, StatutLot
from database import get_db, commit_session, rollback_session

class PaysService:
    
    @staticmethod
    def get_all_pays():
        """
        Récupère tous les pays
        """
        session = get_db()
        try:
            pays = session.query(Pays).all()
            return [p.to_dict() for p in pays]
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_pays_by_id(pays_id):
        """
        Récupère un pays par son ID
        """
        session = get_db()
        try:
            pays = session.query(Pays).filter(Pays.idPays == pays_id).first()
            if not pays:
                return None
            return pays.to_dict()
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_exploitations_by_pays(pays_id):
        """
        Récupère les exploitations d'un pays avec statistiques
        """
        session = get_db()
        try:
            exploitations = session.query(Exploitation).filter(Exploitation.idPays == pays_id).all()
            result = []
            
            for exp in exploitations:
                # Compter les entrepôts
                nb_entrepots = session.query(Entrepot).filter(Entrepot.idExploitation == exp.idExploitation).count()
                
                # Compter les lots
                nb_lots = session.query(LotGrains).join(Entrepot).filter(Entrepot.idExploitation == exp.idExploitation).count()
                
                # Déterminer le statut global
                lots_perimes = session.query(LotGrains).join(Entrepot).filter(
                    and_(
                        Entrepot.idExploitation == exp.idExploitation,
                        LotGrains.statut == StatutLot.PERIME
                    )
                ).count()
                
                lots_alerte = session.query(LotGrains).join(Entrepot).filter(
                    and_(
                        Entrepot.idExploitation == exp.idExploitation,
                        LotGrains.statut == StatutLot.EN_ALERTE
                    )
                ).count()
                
                if lots_perimes > 0:
                    statut_global = "périmé"
                elif lots_alerte > 0:
                    statut_global = "en alerte"
                else:
                    statut_global = "conforme"
                
                result.append({
                    'idExploitation': exp.idExploitation,
                    'idPays': exp.idPays,
                    'nom': exp.nom,
                    'nbEntrepots': nb_entrepots,
                    'nbLots': nb_lots,
                    'statutGlobal': statut_global
                })
            
            return result
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_mesures_history(pays_id, days=7):
        """
        Historique température moyenne des derniers jours
        """
        session = get_db()
        try:
            date_debut = datetime.utcnow() - timedelta(days=days)
            
            # Récupérer les mesures des entrepôts du pays
            mesures = session.query(
                func.date(Mesure.datMesure).label('date'),
                func.avg(Mesure.temperature).label('avgTemp')
            ).join(Entrepot).join(Exploitation).filter(
                and_(
                    Exploitation.idPays == pays_id,
                    Mesure.datMesure >= date_debut
                )
            ).group_by(func.date(Mesure.datMesure)).all()
            
            result = []
            for mesure in mesures:
                result.append({
                    'date': mesure.date.strftime('%Y-%m-%d'),
                    'avgTemp': float(mesure.avgTemp) if mesure.avgTemp else None
                })
            
            return result
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def create_pays(data):
        """
        Crée un nouveau pays
        """
        session = get_db()
        try:
            pays = Pays(
                nom=data['nom'],
                temperatureMin=data['temperatureMin'],
                temperatureMax=data['temperatureMax'],
                humiditeMin=data['humiditeMin'],
                humiditeMax=data['humiditeMax']
            )
            session.add(pays)
            commit_session()
            return pays.to_dict()
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def update_pays(pays_id, data):
        """
        Met à jour un pays
        """
        session = get_db()
        try:
            pays = session.query(Pays).filter(Pays.idPays == pays_id).first()
            if not pays:
                return None
            
            pays.nom = data.get('nom', pays.nom)
            pays.temperatureMin = data.get('temperatureMin', pays.temperatureMin)
            pays.temperatureMax = data.get('temperatureMax', pays.temperatureMax)
            pays.humiditeMin = data.get('humiditeMin', pays.humiditeMin)
            pays.humiditeMax = data.get('humiditeMax', pays.humiditeMax)
            
            commit_session()
            return pays.to_dict()
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def delete_pays(pays_id):
        """
        Supprime un pays
        """
        session = get_db()
        try:
            pays = session.query(Pays).filter(Pays.idPays == pays_id).first()
            if not pays:
                return False
            
            session.delete(pays)
            commit_session()
            return True
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
