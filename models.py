"""
Modèles de données SQLAlchemy pour l'API FutureKawa

Définit toutes les entités de la base de données.
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
    """Modèle pour les pays producteurs de café"""
    __tablename__ = 'pays'
    
    # Clé primaire UUID pour l'unicité et la sécurité
    idPays = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Nom du pays (ex: 'Colombie', 'Éthiopie', 'Brésil')
    nom = Column(String(100), nullable=False)
    
    # Conditions de stockage optimales pour ce pays
    temperatureMin = Column(Float, nullable=False)  # Température minimale acceptable (°C)
    temperatureMax = Column(Float, nullable=False)  # Température maximale acceptable (°C)
    humiditeMin = Column(Float, nullable=False)     # Humidité relative minimale (%)
    humiditeMax = Column(Float, nullable=False)     # Humidité relative maximale (%)
    
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
    Représente une plantation ou une exploitation agricole de café
    
    Une exploitation est rattachée à un pays et peut gérer plusieurs
    entrepôts et utilisateurs.
    """
    __tablename__ = 'exploitation'
    
    # Clé primaire UUID
    idExploitation = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Clé étrangère vers le pays d'origine
    idPays = Column(String(36), ForeignKey('pays.idPays'), nullable=False)
    
    # Nom de l'exploitation (ex: 'Finca La Esperanza', 'Kilimanjaro Plantation')
    nom = Column(String(150), nullable=False)
    
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
    
    # Clé primaire UUID
    idEntrepot = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Clé étrangère vers l'exploitation
    idExploitation = Column(String(36), ForeignKey('exploitation.idExploitation'), nullable=False)
    
    # Informations sur l'entrepôt
    nom = Column(String(100), nullable=False)           # Nom de l'entrepôt
    adresse = Column(String(255), nullable=False)       # Adresse complète
    limiteQte = Column(Integer, nullable=False)         # Capacité maximale (kg)
    
    # Relations avec les autres entités
    exploitation = relationship("Exploitation", back_populates="entrepots")  # Plusieurs-à-un
    lots = relationship("LotGrains", back_populates="entrepot")           # Une-à-plusieurs
    mesures = relationship("Mesure", back_populates="entrepot")             # Une-à-plusieurs
    alertes = relationship("Alerte", back_populates="entrepot")             # Une-à-plusieurs
    
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
    
    # Clé primaire UUID
    idLotGrains = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Clé étrangère vers l'entrepôt de stockage
    idEntrepot = Column(String(36), ForeignKey('entrepot.idEntrepot'), nullable=False)
    
    # Informations sur le lot
    datSto = Column(DateTime, nullable=False, default=datetime.utcnow)  # Date d'entrée en stock
    statut = Column(SQLEnum(StatutLot), nullable=False, default=StatutLot.CONFORME)  # Statut actuel
    datSortie = Column(DateTime, nullable=True)  # Date de sortie du stock (si applicable)
    
    # Relations
    entrepot = relationship("Entrepot", back_populates="lots")      # Plusieurs-à-un
    alertes = relationship("Alerte", back_populates="lot_grains")   # Une-à-plusieurs
    
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
            'statut': self.statut.value if self.statut else None,
            'datSortie': self.datSortie.isoformat() if self.datSortie else None
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
    Représente une mesure environnementale dans un entrepôt
    
    Les mesures sont prises régulièrement par des capteurs pour surveiller
    les conditions de stockage (température et humidité).
    """
    __tablename__ = 'mesures'
    
    # Clé primaire UUID
    idMesure = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Clé étrangère vers l'entrepôt où la mesure a été prise
    idEntrepot = Column(String(36), ForeignKey('entrepot.idEntrepot'), nullable=False)
    
    # Données de la mesure
    temperature = Column(Float(1), nullable=False)  # Température en °C (1 décimale)
    humidite = Column(Float(1), nullable=False)    # Humidité relative en % (1 décimale)
    datMesure = Column(DateTime, nullable=False, default=datetime.utcnow)  # Date/heure de la mesure
    
    # Relations
    entrepot = relationship("Entrepot", back_populates="mesures")  # Plusieurs-à-un
    alertes = relationship("Alerte", back_populates="mesure")       # Une-à-plusieurs
    
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
    __tablename__ = 'alerte'
    
    # Clé primaire UUID
    idAlerte = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Clés étrangères (optionnelles selon le type d'alerte)
    idMesure = Column(String(36), ForeignKey('mesures.idMesure'), nullable=True)        # Pour alertes environnementales
    idLotGrains = Column(String(36), ForeignKey('lotgrains.idLotGrains'), nullable=True)  # Pour alertes sur lots
    idEntrepot = Column(String(36), ForeignKey('entrepot.idEntrepot'), nullable=False)  # Entrepôt concerné
    
    # Informations sur l'alerte
    type = Column(SQLEnum(TypeAlerte), nullable=False)               # Type de l'alerte
    valeurMesuree = Column(Float, nullable=True)                      # Valeur qui a déclenché l'alerte
    dateAlerte = Column(DateTime, nullable=False, default=datetime.utcnow)  # Date/heure de création
    statut = Column(SQLEnum(StatutAlerte), nullable=False, default=StatutAlerte.EN_COURS)  # Statut de traitement
    
    # Relations
    entrepot = relationship("Entrepot", back_populates="alertes")      # Plusieurs-à-un
    mesure = relationship("Mesure", back_populates="alertes")          # Plusieurs-à-un (optionnel)
    lot_grains = relationship("LotGrains", back_populates="alertes")    # Plusieurs-à-un (optionnel)
    
    def to_dict(self, include_details=False):
        """
        Convertit l'objet Alerte en dictionnaire
        
        Args:
            include_details (bool): Si True, inclut les détails hiérarchiques
            
        Returns:
            dict: Représentation JSON de l'alerte
        """
        result = {
            'idAlerte': self.idAlerte,
            'idEntrepot': self.idEntrepot,
            'type': self.type.value if self.type else None,
            'valeurMesuree': self.valeurMesuree,
            'dateAlerte': self.dateAlerte.isoformat() if self.dateAlerte else None,
            'statut': self.statut.value if self.statut else None
        }
        
        if include_details and self.entrepot:
            # Ajout des détails hiérarchiques si demandé
            result['nomEntrepot'] = self.entrepot.nom
            if self.entrepot.exploitation:
                result['nomExploitation'] = self.entrepot.exploitation.nom
                result['idExploitation'] = self.entrepot.exploitation.idExploitation
                if self.entrepot.exploitation.pays:
                    result['nomPays'] = self.entrepot.exploitation.pays.nom
                    result['idPays'] = self.entrepot.exploitation.pays.idPays
                    
        return result
