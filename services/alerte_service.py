"""Service pour les alertes - Couche Domaine"""

from repositories.alerte_repository import AlerteRepository

class AlerteService:
    """Logique métier pour les alertes"""
    
    @staticmethod
    def get_all_alertes():
        """Récupère toutes les alertes"""
        return AlerteRepository.get_all()
    
    @staticmethod
    def get_alerte_by_id(alerte_id):
        """Récupère une alerte par son ID"""
        alerte = AlerteRepository.get_by_id(alerte_id)
        if not alerte:
            raise ValueError('Alerte non trouvée')
        return alerte
    
    @staticmethod
    def create_alerte(data):
        """Crée une nouvelle alerte"""
        # Validation des données requises
        required_fields = ['idEntrepot', 'type']
        for field in required_fields:
            if field not in data:
                raise ValueError(f'Champ requis: {field}')
        
        return AlerteRepository.create(data)
