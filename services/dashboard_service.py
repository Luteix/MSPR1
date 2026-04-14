from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from sqlalchemy import func, and_, or_
from models import Pays, Exploitation, Entrepot, LotGrains, Alerte, StatutLot
from database import get_db, commit_session, rollback_session

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

class AlerteService:
    
    @staticmethod
    def get_recent_alertes(limit=5):
        """
        Récupère les dernières alertes déclenchées
        """
        session = get_db()
        try:
            alertes = session.query(Alerte).options(
                joinedload(Alerte.entrepot)
            ).order_by(Alerte.dateAlerte.desc()).limit(limit).all()
            
            result = []
            for alerte in alertes:
                alerte_dict = alerte.to_dict()
                if alerte.entrepot:
                    alerte_dict['nomEntrepot'] = alerte.entrepot.nom
                result.append(alerte_dict)
            
            return result
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_all_alertes(pays_id=None, type_alerte=None, date_from=None, date_to=None):
        """
        Récupère toutes les alertes avec filtres
        """
        session = get_db()
        try:
            query = session.query(Alerte).options(
                joinedload(Alerte.entrepot)
                .joinedload(Entrepot.exploitation)
                .joinedload(Exploitation.pays)
            )
            
            # Appliquer les filtres
            if pays_id:
                query = query.join(Entrepot).join(Exploitation).filter(
                    Exploitation.idPays == pays_id
                )
            
            if type_alerte:
                query = query.filter(Alerte.type == type_alerte)
            
            if date_from:
                date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00')) if isinstance(date_from, str) else date_from
                query = query.filter(Alerte.dateAlerte >= date_from_dt)
            
            if date_to:
                date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00')) if isinstance(date_to, str) else date_to
                query = query.filter(Alerte.dateAlerte <= date_to_dt)
            
            alertes = query.order_by(Alerte.dateAlerte.desc()).all()
            
            return [alerte.to_dict(include_details=True) for alerte in alertes]
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def create_alerte(data):
        """
        Crée une nouvelle alerte
        """
        session = get_db()
        try:
            alerte = Alerte(
                idEntrepot=data['idEntrepot'],
                idMesure=data.get('idMesure'),
                idLotGrains=data.get('idLotGrains'),
                type=data['type'],
                valeurMesuree=data.get('valeurMesuree'),
                dateAlerte=datetime.utcnow(),
                statut=data.get('statut', 'en cours')
            )
            
            session.add(alerte)
            commit_session()
            return alerte.to_dict()
        except Exception as e:
            rollback_session()
            raise e
        finally:
            session.close()
    
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
