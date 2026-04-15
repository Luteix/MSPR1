"""Service pour les mesures - Couche Domaine"""

from datetime import datetime
from models import Alerte, TypeAlerte, StatutAlerte
from repositories.mesure_repository import MesureRepository
from repositories.alerte_repository import AlerteRepository

class MesureService:
    """Logique métier pour les mesures"""
    
    @staticmethod
    def validate_mesure_data(data):
        """Valide les données d'une mesure"""
        errors = []
        
        # Champs requis
        required_fields = ['idEntrepot', 'temperature', 'humidite']
        for field in required_fields:
            if field not in data:
                errors.append(f'Champ requis: {field}')
        
        # Validation des valeurs
        try:
            temperature = float(data['temperature'])
            if not (-50 <= temperature <= 100):
                errors.append('Température hors plage valide (-50°C à 100°C)')
        except ValueError:
            errors.append('Température doit être un nombre')
        
        try:
            humidite = float(data['humidite'])
            if not (0 <= humidite <= 100):
                errors.append('Humidité hors plage valide (0% à 100%)')
        except ValueError:
            errors.append('Humidité doit être un nombre')
        
        # Validation de la date si fournie
        if 'datMesure' in data:
            try:
                datetime.fromisoformat(data['datMesure'].replace('Z', '+00:00'))
            except ValueError:
                errors.append('Format de date invalide. Utilisez ISO 8601')
        
        return errors
    
    @staticmethod
    def create_mesure(data):
        """Crée une mesure et génère les alertes si nécessaire"""
        # Validation
        errors = MesureService.validate_mesure_data(data)
        if errors:
            raise ValueError('; '.join(errors))
        
        # Préparation des données
        mesure_data = {
            'idEntrepot': data['idEntrepot'],
            'temperature': float(data['temperature']),
            'humidite': float(data['humidite']),
            'datMesure': datetime.fromisoformat(data['datMesure'].replace('Z', '+00:00')) if 'datMesure' in data else datetime.utcnow()
        }
        
        # Création de la mesure
        mesure = MesureRepository.create(mesure_data)
        
        # Génération des alertes
        MesureService._generer_alertes(mesure)
        
        return mesure
    
    @staticmethod
    def _generer_alertes(mesure):
        """Génère les alertes pour une mesure"""
        seuils = MesureRepository.get_seuils_entrepot(mesure.idEntrepot)
        
        if seuils:
            # Alerte température
            if mesure.temperature < seuils.temperatureMin or mesure.temperature > seuils.temperatureMax:
                alerte_data = {
                    'idMesure': mesure.idMesure
                }
                AlerteRepository.create(alerte_data)
            
            # Alerte humidité
            if mesure.humidite < seuils.humiditeMin or mesure.humidite > seuils.humiditeMax:
                alerte_data = {
                    'idMesure': mesure.idMesure
                }
                AlerteRepository.create(alerte_data)
    
    @staticmethod
    def get_mesures_by_entrepot(entrepot_id, limit=100, from_date=None):
        """Récupère les mesures d'un entrepôt"""
        # Validation des paramètres
        try:
            limit = int(limit)
            if limit <= 0 or limit > 1000:
                raise ValueError('Limite doit être entre 1 et 1000')
        except ValueError:
            raise ValueError('Limite doit être un entier valide')
        
        # Validation de la date si fournie
        from_date_dt = None
        if from_date:
            try:
                from_date_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Format de date invalide. Utilisez ISO 8601')
        
        return MesureRepository.get_by_entrepot(entrepot_id, limit, from_date_dt)
    
    @staticmethod
    def get_mesure_by_id(mesure_id):
        """Récupère une mesure par son ID"""
        try:
            mesure_id_int = int(mesure_id)
        except ValueError:
            raise ValueError('ID de mesure invalide')
        
        mesure = MesureRepository.get_by_id(mesure_id_int)
        if not mesure:
            raise ValueError('Mesure non trouvée')
        
        return mesure
