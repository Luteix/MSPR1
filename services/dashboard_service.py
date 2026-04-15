from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from sqlalchemy import func, and_, or_
from models import Pays, Exploitation, Entrepot, LotGrains, Mesure, Alerte, StatutLot, TypeAlerte, StatutAlerte
from database import get_db, commit_session, rollback_session
from repositories.dashboard_repository import DashboardRepository

class DashboardService:
    
    @staticmethod
    def get_dashboard_summary():
        """
        Récupère les métriques globales et le résumé par pays
        """
        session = get_db()
        try:
            # Métriques globales
            lots_stockes = session.query(LotGrains).count()
            lots_alerte = session.query(LotGrains).filter(
                LotGrains.statut == StatutLot.EN_ALERTE
            ).count()
            lots_perimes = session.query(LotGrains).filter(
                LotGrains.statut == StatutLot.PERIME
            ).count()
            entrepots_actifs = session.query(Entrepot).count()
            
            metrics = {
                'lotsStockes': lots_stockes,
                'lotsAlerte': lots_alerte,
                'lotsPerimes': lots_perimes,
                'entrepotsActifs': entrepots_actifs
            }
            
            # Résumé par pays
            pays_list = session.query(Pays).all()
            summary_by_country = []
            
            for pays in pays_list:
                # Nombre d'exploitations
                nb_exploitations = session.query(Exploitation).filter(
                    Exploitation.idPays == pays.idPays
                ).count()
                
                # Nombre d'entrepôts
                nb_entrepots = session.query(Entrepot).join(Exploitation).filter(
                    Exploitation.idPays == pays.idPays
                ).count()
                
                # Nombre de lots
                nb_lots = session.query(LotGrains).join(Entrepot).join(Exploitation).filter(
                    Exploitation.idPays == pays.idPays
                ).count()
                
                # Lots en alerte
                lots_en_alerte = session.query(LotGrains).join(Entrepot).join(Exploitation).filter(
                    and_(
                        Exploitation.idPays == pays.idPays,
                        LotGrains.statut == StatutLot.EN_ALERTE
                    )
                ).count()
                
                # Dernière mesure
                derniere_mesure = session.query(func.max(Mesure.datMesure)).join(Entrepot).join(Exploitation).filter(
                    Exploitation.idPays == pays.idPays
                ).scalar()
                
                summary_by_country.append({
                    'pays': {
                        'idPays': pays.idPays,
                        'nom': pays.nom
                    },
                    'nbExploitations': nb_exploitations,
                    'nbEntrepots': nb_entrepots,
                    'nbLots': nb_lots,
                    'lotsEnAlerte': lots_en_alerte,
                    'derniereMesure': derniere_mesure.isoformat() if derniere_mesure else None
                })
            
            return {
                'metrics': metrics,
                'summaryByCountry': summary_by_country
            }
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()

    @staticmethod
    def get_all_alertes():
        """Récupère toutes les alertes"""
        try:
            alertes = DashboardRepository.get_alertes_with_hierarchy()
            return alertes
        except Exception as e:
            raise e
    
    @staticmethod
    def get_recent_alertes(limit=5):
        """Récupère les alertes récentes"""
        try:
            alertes = DashboardRepository.get_alertes_with_hierarchy()
            return alertes[:limit]
        except Exception as e:
            raise e
    
    @staticmethod
    def create_alerte(data):
        """Crée une nouvelle alerte"""
        # Validation des données requises
        required_fields = ['idMesure']
        for field in required_fields:
            if field not in data:
                raise ValueError(f'Champ requis: {field}')
        
        # Filtrer les données pour ne garder que les champs du modèle
        filtered_data = {'idMesure': data['idMesure']}
        
        try:
            alerte = DashboardRepository.create_alerte(filtered_data)
            if isinstance(alerte, dict):
                return alerte
            return alerte.to_dict() if hasattr(alerte, 'to_dict') else alerte
        except Exception as e:
            raise e
    
    @staticmethod
    def get_all_alertes(pays_id=None, type_alerte=None, date_from=None, date_to=None):
        """
        Récupère toutes les alertes avec filtres
        Note: Les filtres sont désactivés car la table alertes n'a que idAlerte et idMesure
        """
        return DashboardRepository.get_alertes_with_hierarchy()
    
    @staticmethod
    def update_alerte_statut(alerte_id, statut):
        """
        Met à jour le statut d'une alerte
        """
        session = get_db()
        try:
            alerte = session.query(Alerte).filter(
                Alerte.idAlerte == alerte_id
            ).first()
            
            if not alerte:
                return None
            
            alerte.statut = statut
            commit_session()
            return alerte.to_dict()
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
