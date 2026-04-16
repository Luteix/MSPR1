"""
FICHIER: models.py
UTILITÉ: Définition des modèles SQLAlchemy (ORM)

- Définit toutes les tables de la BDD comme classes Python
- Configure les colonnes, types, clés primaires/étrangères
- Établit les relations entre tables (OneToMany, ManyToOne)
- Fournit to_dict() pour sérialiser les objets en JSON

Modèles: Pays, Exploitation, Entrepot, LotGrains, Mesure, Alerte, Utilisateur
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

# Base déclarative pour tous les modèles SQLAlchemy
Base = declarative_base()

# =============================================================================
# ÉNUMÉRATIONS
# =============================================================================

class StatutLot(Enum):
    """
    Énumération des statuts possibles pour un lot de grains de café
    """
    CONFORME = "conforme"           # Lot dans les normes de stockage
    EN_ALERTE = "en alerte"         # Lot avec anomalies mineures
    PERIME = "périmé"               # Lot périmé, à détruire

class TypeAlerte(Enum):
    """
    Énumération des types d'alertes possibles
    """
    TEMPERATURE_HORS_PLAGE = "Température hors plage"     # Température hors limites acceptables
    HUMIDITE_HORS_PLAGE = "Humidité hors plage"         # Humidité hors limites acceptables
    LOT_PERIME = "Lot périmé"                           # Lot dépassant sa durée de vie
    LOT_PROCHE_PEREMPTION = "Lot proche péremption"      # Lot proche de sa date de péremption

class StatutAlerte(Enum):
    """
    Énumération des statuts de traitement des alertes
    """
    EN_COURS = "en cours"         # Alerte active, non traitée
    TRAITEE = "traitée"           # Alerte résolue et close

# =============================================================================
# MODÈLE: PAYS
# =============================================================================

class Pays(Base):
    """
    Représente un pays où sont situées les exploitations
    
    Chaque pays définit des seuils de température et d'humidité
    acceptables pour le stockage du café.
    """
    __tablename__ = 'pays'
    
    # Clé primaire (adaptée à la BDD : int(11))
    idPays = Column(Integer, primary_key=True, autoincrement=True)
    
    # Informations sur le pays
    nom = Column(String(50), nullable=True)  # Nom du pays (nullable dans la BDD)
    temperatureMin = Column(Float, nullable=True)      # Température minimale acceptable (°C) (nullable dans la BDD)
    temperatureMax = Column(Float, nullable=True)      # Température maximale acceptable (°C) (nullable dans la BDD)
    humiditeMin = Column(Float, nullable=True)         # Humidité minimale acceptable (%) (nullable dans la BDD)
    humiditeMax = Column(Float, nullable=True)         # Humidité maximale acceptable (%) (nullable dans la BDD)
    
    # Relations avec les autres entités
    exploitations = relationship("Exploitation", back_populates="pays")  # Une-à-plusieurs
    
    def to_dict(self):
        """Convertit le modèle en dictionnaire"""
        return {
            'idPays': self.idPays,
            'nom': self.nom,
            'temperatureMin': self.temperatureMin,
            'temperatureMax': self.temperatureMax,
            'humiditeMin': self.humiditeMin,
            'humiditeMax': self.humiditeMax
        }

# =============================================================================
# MODÈLE: EXPLOITATION
# =============================================================================

class Exploitation(Base):
    """
    Représente une exploitation agricole
    
    Une exploitation est rattachée à un pays et peut gérer
    plusieurs entrepôts de stockage.
    """
    __tablename__ = 'exploitation'
    
    # Clé primaire (adaptée à la BDD : int(11))
    idExploitation = Column(Integer, primary_key=True, autoincrement=True)
    
    # Clé étrangère vers le pays (adaptée à la BDD : int(11))
    idPays = Column(Integer, ForeignKey('pays.idPays'), nullable=False)
    
    # Informations sur l'exploitation
    nom = Column(String(150), nullable=False)  # Nom de l'exploitation
    
    # Relations avec les autres entités
    pays = relationship("Pays", back_populates="exploitations")      # Plusieurs-à-un
    entrepots = relationship("Entrepot", back_populates="exploitation")  # Une-à-plusieurs
    utilisateurs = relationship("Utilisateur", back_populates="exploitation") # Une-à-plusieurs
    
    def to_dict(self, include_pays=False):
        """
        Convertit l'objet Exploitation en dictionnaire
        
        Args:
            include_pays (bool): Si True, inclut les informations du pays
            
        Returns:
            dict: Représentation JSON de l'exploitation
        """
        result = {
            'idExploitation': self.idExploitation,
            'idPays': self.idPays,
            'nom': self.nom
        }
        if include_pays and self.pays:
            result['pays'] = {
                'idPays': self.pays.idPays,
                'nom': self.pays.nom
            }
        return result

# =============================================================================
# MODÈLE: UTILISATEUR
# =============================================================================

class Utilisateur(Base):
    """
    Représente un utilisateur/gestionnaire d'une exploitation
    
    Chaque utilisateur est rattaché à une exploitation et peut
    gérer les stocks et les alertes de celle-ci.
    """
    __tablename__ = 'utilisateur'
    
    # Clé primaire UUID
    idUtilisateur = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Clé étrangère vers l'exploitation
    idExploitation = Column(String(36), ForeignKey('exploitation.idExploitation'), nullable=False)
    
    # Informations personnelles
    nom = Column(String(50), nullable=False)       # Nom de famille
    prenom = Column(String(50), nullable=False)   # Prénom
    mail = Column(String(255), nullable=False, unique=True)  # Email unique
    mdp = Column(String(255), nullable=False)    # Mot de passe (hashé ou en clair)
    
    # Clés étrangères
    idPoste = Column(Integer, ForeignKey('poste.idPoste'), nullable=True)
    
    # Relations
    exploitation = relationship("Exploitation", back_populates="utilisateurs")  # Plusieurs-à-un
    
    def to_dict(self):
        """
        Convertit l'objet Utilisateur en dictionnaire
        
        Returns:
            dict: Représentation JSON de l'utilisateur
        """
        return {
            'idUtilisateur': self.idUtilisateur,
            'idExploitation': self.idExploitation,
            'nom': self.nom,
            'prenom': self.prenom,
            'mail': self.mail
        }

# =============================================================================
# MODÈLE: ENTREPOT
# =============================================================================

class Entrepot(Base):
    """
    Représente un entrepôt de stockage pour les grains de café
    
    Un entrepôt est rattaché à une exploitation et peut contenir
    plusieurs lots de grains. Il dispose de capteurs pour la surveillance
    de la température et de l'humidité.
    """
    __tablename__ = 'entrepot'
    
    # Clé primaire (adaptée à la BDD : int(11))
    idEntrepot = Column(Integer, primary_key=True, autoincrement=True)
    
    # Clé étrangère vers l'exploitation (adaptée à la BDD : int(11))
    idExploitation = Column(Integer, ForeignKey('exploitation.idExploitation'), nullable=False)
    
    # Informations sur l'entrepôt
    nom = Column(String(50), nullable=True)           # Nom de l'entrepôt (nullable dans la BDD)
    adresse = Column(String(100), nullable=True)       # Adresse complète (nullable dans la BDD)
    limiteQte = Column(Integer, nullable=True)         # Capacité maximale (kg) (nullable dans la BDD)
    
    # Relations avec les autres entités
    exploitation = relationship("Exploitation", back_populates="entrepots")  # Plusieurs-à-un
    lots = relationship("LotGrains", back_populates="entrepot")           # Une-à-plusieurs
    mesures = relationship("Mesure", back_populates="entrepot")             # Une-à-plusieurs
    # Note: relation alertes supprimée car la table alertes n'a pas de clé étrangère idEntrepot
    
    def to_dict(self, include_details=False):
        """
        Convertit l'objet Entrepot en dictionnaire
        
        Args:
            include_details (bool): Si True, inclut les détails hiérarchiques
            
        Returns:
            dict: Représentation JSON de l'entrepôt
        """
        result = {
            'idEntrepot': self.idEntrepot,
            'idExploitation': self.idExploitation,
            'nom': self.nom,
            'adresse': self.adresse,
            'limiteQte': self.limiteQte
        }
        
        if include_details:
            # Ajout des informations hiérarchiques si demandé
            if self.exploitation:
                result['nomExploitation'] = self.exploitation.nom
            if self.exploitation and self.exploitation.pays:
                result['nomPays'] = self.exploitation.pays.nom
                result['pays'] = {
                    'idPays': self.exploitation.pays.idPays,
                    'nom': self.exploitation.pays.nom,
                    'temperatureMin': self.exploitation.pays.temperatureMin,
                    'temperatureMax': self.exploitation.pays.temperatureMax,
                    'humiditeMin': self.exploitation.pays.humiditeMin,
                    'humiditeMax': self.exploitation.pays.humiditeMax
                }
                
        return result

# =============================================================================
# MODÈLE: LOT DE GRAINS
# =============================================================================

class LotGrains(Base):
    """
    Représente un lot de grains de café stocké dans un entrepôt
    
    Un lot est caractérisé par sa date d'entrée en stock,
    son statut de conformité et sa date de sortie éventuelle.
    """
    __tablename__ = 'lotgrains'
    
    # Clé primaire (adaptée à la BDD : int(11))
    idLotGrains = Column(Integer, primary_key=True, autoincrement=True)
    
    # Clé étrangère vers l'entrepôt de stockage (adaptée à la BDD : int(11))
    idEntrepot = Column(Integer, ForeignKey('entrepot.idEntrepot'), nullable=True)
    
    # Informations sur le lot
    datSto = Column(DateTime, nullable=True)  # Date d'entrée en stock (nullable dans la BDD)
    statut = Column(String(10), nullable=True)  # Statut actuel (nullable dans la BDD)
    datSortie = Column(DateTime, nullable=True)  # Date de sortie du stock (nullable dans la BDD)
    
    # Relations
    entrepot = relationship("Entrepot", back_populates="lots")      # Plusieurs-à-un
    # Note: relation alertes supprimée car la table alertes n'a pas de clé étrangère idLotGrains
    
    def to_dict(self, include_hierarchy=False):
        """
        Convertit l'objet LotGrains en dictionnaire
        
        Args:
            include_hierarchy (bool): Si True, inclut la hiérarchie complète
            
        Returns:
            dict: Représentation JSON du lot de grains
        """
        result = {
            'idLotGrains': self.idLotGrains,
            'idEntrepot': self.idEntrepot,
            'datSto': self.datSto.isoformat() if self.datSto else None,
            'statut': self.statut,            'datSortie': self.datSortie.isoformat() if self.datSortie else None
        }
        
        if include_hierarchy and self.entrepot:
            # Ajout de la hiérarchie complète si demandé
            result['entrepot'] = {
                'idEntrepot': self.entrepot.idEntrepot,
                'nom': self.entrepot.nom
            }
            if self.entrepot.exploitation:
                result['exploitation'] = {
                    'idExploitation': self.entrepot.exploitation.idExploitation,
                    'nom': self.entrepot.exploitation.nom
                }
                if self.entrepot.exploitation.pays:
                    result['pays'] = {
                        'idPays': self.entrepot.exploitation.pays.idPays,
                        'nom': self.entrepot.exploitation.pays.nom,
                        'temperatureMin': self.entrepot.exploitation.pays.temperatureMin,
                        'temperatureMax': self.entrepot.exploitation.pays.temperatureMax,
                        'humiditeMin': self.entrepot.exploitation.pays.humiditeMin,
                        'humiditeMax': self.entrepot.exploitation.pays.humiditeMax
                    }
                    
        return result

# =============================================================================
# MODÈLE: MESURE
# =============================================================================

class Mesure(Base):
    """
    Représente une mesure de température et d'humidité
    
    Les mesures sont prises régulièrement dans les entrepôts
    pour surveiller les conditions de stockage.
    """
    __tablename__ = 'mesures'
    
    # Clé primaire
    idMesure = Column(Integer, primary_key=True, autoincrement=True)
    
    # Clé étrangère vers l'entrepôt où la mesure a été prise (adaptée à la BDD : int(11))
    idEntrepot = Column(Integer, ForeignKey('entrepot.idEntrepot'), nullable=False)
    
    # Données de la mesure
    temperature = Column(Float, nullable=True)  # Température en °C (nullable dans la BDD)
    humidite = Column(Float, nullable=True)    # Humidité relative en % (nullable dans la BDD)
    datMesure = Column(DateTime, nullable=True)  # Date/heure de la mesure (nullable dans la BDD)
    
    # Relations
    entrepot = relationship("Entrepot", back_populates="mesures")  # Plusieurs-à-un
    
    def to_dict(self):
        """
        Convertit l'objet Mesure en dictionnaire
        
        Returns:
            dict: Représentation JSON de la mesure
        """
        return {
            'idMesure': self.idMesure,
            'idEntrepot': self.idEntrepot,
            'temperature': self.temperature,
            'humidite': self.humidite,
            'datMesure': self.datMesure.isoformat() if self.datMesure else None
        }

# =============================================================================
# MODÈLE: ALERTE
# =============================================================================

class Alerte(Base):
    """
    Représente une alerte générée automatiquement
    
    Les alertes sont créées lorsque les conditions de stockage
    dépassent les seuils acceptables ou lorsqu'un lot approche
    de sa date de péremption.
    """
    __tablename__ = 'alertes'
    
    # Clé primaire (adaptée à la BDD : INT AUTO_INCREMENT)
    idAlerte = Column(Integer, primary_key=True, autoincrement=True)
    
    # Clé étrangère vers la mesure (seule colonne existante dans la BDD)
    idMesure = Column(Integer, ForeignKey('mesures.idMesure'), nullable=False, unique=True)
    
    def to_dict(self):
        """Convertit l'objet Alerte en dictionnaire"""
        return {
            'idAlerte': self.idAlerte,
            'idMesure': self.idMesure
        }
