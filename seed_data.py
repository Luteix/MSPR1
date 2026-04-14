"""
Script d'initialisation des données de test pour l'API FutureKawa

Ce script insère des données exemples dans la base de données MySQL
pour tester les fonctionnalités de l'API.
"""

from database import DatabaseTransaction
from models import Pays, Exploitation, Utilisateur, Entrepot, LotGrains, Mesure, Alerte, StatutLot, TypeAlerte, StatutAlerte
from datetime import datetime, timedelta
import uuid

def create_test_data():
    """
    Crée des données de test dans la base de données
    """
    with DatabaseTransaction() as session:
        # Création des pays
        pays1 = Pays(
            idPays=str(uuid.uuid4()),
            nom="Colombie",
            temperatureMin=18.0,
            temperatureMax=22.0,
            humiditeMin=60.0,
            humiditeMax=70.0
        )
        
        pays2 = Pays(
            idPays=str(uuid.uuid4()),
            nom="Éthiopie",
            temperatureMin=15.0,
            temperatureMax=20.0,
            humiditeMin=55.0,
            humiditeMax=65.0
        )
        
        pays3 = Pays(
            idPays=str(uuid.uuid4()),
            nom="Brésil",
            temperatureMin=20.0,
            temperatureMax=25.0,
            humiditeMin=65.0,
            humiditeMax=75.0
        )
        
        session.add_all([pays1, pays2, pays3])
        session.flush()  # Pour obtenir les IDs
        
        # Création des exploitations
        exploitation1 = Exploitation(
            idExploitation=str(uuid.uuid4()),
            idPays=pays1.idPays,
            nom="Finca La Esperanza"
        )
        
        exploitation2 = Exploitation(
            idExploitation=str(uuid.uuid4()),
            idPays=pays2.idPays,
            nom="Kilimanjaro Plantation"
        )
        
        exploitation3 = Exploitation(
            idExploitation=str(uuid.uuid4()),
            idPays=pays3.idPays,
            nom="Fazenda São Paulo"
        )
        
        session.add_all([exploitation1, exploitation2, exploitation3])
        session.flush()
        
        # Création des utilisateurs
        utilisateur1 = Utilisateur(
            idUtilisateur=str(uuid.uuid4()),
            idExploitation=exploitation1.idExploitation,
            nom="Rodriguez",
            prenom="Carlos",
            mail="carlos.rodriguez@futurekawa.com"
        )
        
        utilisateur2 = Utilisateur(
            idUtilisateur=str(uuid.uuid4()),
            idExploitation=exploitation2.idExploitation,
            nom="Mekonnen",
            prenom="Lemma",
            mail="lemma.mekonnen@futurekawa.com"
        )
        
        utilisateur3 = Utilisateur(
            idUtilisateur=str(uuid.uuid4()),
            idExploitation=exploitation3.idExploitation,
            nom="Silva",
            prenom="Maria",
            mail="maria.silva@futurekawa.com"
        )
        
        session.add_all([utilisateur1, utilisateur2, utilisateur3])
        session.flush()
        
        # Création des entrepôts
        entrepot1 = Entrepot(
            idEntrepot=str(uuid.uuid4()),
            idExploitation=exploitation1.idExploitation,
            nom="Entrepot Bogotá",
            adresse="Calle 123, Bogotá, Colombie",
            limiteQte=50000
        )
        
        entrepot2 = Entrepot(
            idEntrepot=str(uuid.uuid4()),
            idExploitation=exploitation2.idExploitation,
            nom="Entrepot Addis-Abeba",
            adresse="Bole Road, Addis-Abeba, Éthiopie",
            limiteQte=35000
        )
        
        entrepot3 = Entrepot(
            idEntrepot=str(uuid.uuid4()),
            idExploitation=exploitation3.idExploitation,
            nom="Entrepot São Paulo",
            adresse="Avenida Paulista, São Paulo, Brésil",
            limiteQte=75000
        )
        
        session.add_all([entrepot1, entrepot2, entrepot3])
        session.flush()
        
        # Création des lots de grains
        lot1 = LotGrains(
            idLotGrains=str(uuid.uuid4()),
            idEntrepot=entrepot1.idEntrepot,
            datSto=datetime.utcnow() - timedelta(days=30),
            statut=StatutLot.CONFORME
        )
        
        lot2 = LotGrains(
            idLotGrains=str(uuid.uuid4()),
            idEntrepot=entrepot2.idEntrepot,
            datSto=datetime.utcnow() - timedelta(days=15),
            statut=StatutLot.EN_ALERTE
        )
        
        lot3 = LotGrains(
            idLotGrains=str(uuid.uuid4()),
            idEntrepot=entrepot3.idEntrepot,
            datSto=datetime.utcnow() - timedelta(days=60),
            statut=StatutLot.CONFORME,
            datSortie=datetime.utcnow() - timedelta(days=5)
        )
        
        session.add_all([lot1, lot2, lot3])
        session.flush()
        
        # Création des mesures (température et humidité)
        maintenant = datetime.utcnow()
        
        # Mesures pour entrepôt 1 (température normale)
        for i in range(10):
            mesure = Mesure(
                idMesure=str(uuid.uuid4()),
                idEntrepot=entrepot1.idEntrepot,
                temperature=20.5 + (i % 3) * 0.5,  # 20.5, 21.0, 21.5
                humidite=65.0 + (i % 2) * 2.0,     # 65.0, 67.0
                datMesure=maintenant - timedelta(hours=i*6)
            )
            session.add(mesure)
        
        # Mesures pour entrepôt 2 (température hors plage - alerte)
        for i in range(8):
            mesure = Mesure(
                idMesure=str(uuid.uuid4()),
                idEntrepot=entrepot2.idEntrepot,
                temperature=25.5 + (i % 3) * 0.3,  # Trop élevé pour l'Éthiopie
                humidite=70.0 + (i % 2) * 3.0,     # Un peu élevé
                datMesure=maintenant - timedelta(hours=i*8)
            )
            session.add(mesure)
        
        # Mesures pour entrepôt 3 (normales)
        for i in range(12):
            mesure = Mesure(
                idMesure=str(uuid.uuid4()),
                idEntrepot=entrepot3.idEntrepot,
                temperature=22.0 + (i % 4) * 0.5,  # 22.0, 22.5, 23.0, 23.5
                humidite=68.0 + (i % 3) * 1.5,     # 68.0, 69.5, 71.0
                datMesure=maintenant - timedelta(hours=i*4)
            )
            session.add(mesure)
        
        session.flush()
        
        # Création des alertes
        alerte1 = Alerte(
            idAlerte=str(uuid.uuid4()),
            idEntrepot=entrepot2.idEntrepot,
            type=TypeAlerte.TEMPERATURE_HORS_PLAGE,
            valeurMesuree=25.8,
            statut=StatutAlerte.EN_COURS
        )
        
        alerte2 = Alerte(
            idAlerte=str(uuid.uuid4()),
            idEntrepot=entrepot2.idEntrepot,
            type=TypeAlerte.HUMIDITE_HORS_PLAGE,
            valeurMesuree=73.0,
            statut=StatutAlerte.EN_COURS
        )
        
        alerte3 = Alerte(
            idAlerte=str(uuid.uuid4()),
            idEntrepot=entrepot1.idEntrepot,
            type=TypeAlerte.LOT_PROCHE_PEREMPTION,
            idLotGrains=lot1.idLotGrains,
            statut=StatutAlerte.TRAITEE
        )
        
        session.add_all([alerte1, alerte2, alerte3])
        
        print("Données de test créées avec succès !")
        print(f"- {3} pays créés")
        print(f"- {3} exploitations créées")
        print(f"- {3} utilisateurs créés")
        print(f"- {3} entrepôts créés")
        print(f"- {3} lots de grains créés")
        print(f"- {30} mesures créées")
        print(f"- {3} alertes créées")

if __name__ == "__main__":
    create_test_data()
