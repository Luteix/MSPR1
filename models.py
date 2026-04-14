from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class StatutLot(Enum):
    CONFORME = "conforme"
    EN_ALERTE = "en alerte"
    PERIME = "périmé"

class TypeAlerte(Enum):
    TEMPERATURE_HORS_PLAGE = "Température hors plage"
    HUMIDITE_HORS_PLAGE = "Humidité hors plage"
    LOT_PERIME = "Lot périmé"
    LOT_PROCHE_PEREMPTION = "Lot proche péremption"

class StatutAlerte(Enum):
    EN_COURS = "en cours"
    TRAITEE = "traitée"

class Pays(Base):
    __tablename__ = 'pays'
    
    idPays = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nom = Column(String(100), nullable=False)
    temperatureMin = Column(Float(1), nullable=False)
    temperatureMax = Column(Float(1), nullable=False)
    humiditeMin = Column(Float(1), nullable=False)
    humiditeMax = Column(Float(1), nullable=False)
    
    exploitations = relationship("Exploitation", back_populates="pays")
    
    def to_dict(self):
        return {
            'idPays': self.idPays,
            'nom': self.nom,
            'temperatureMin': self.temperatureMin,
            'temperatureMax': self.temperatureMax,
            'humiditeMin': self.humiditeMin,
            'humiditeMax': self.humiditeMax
        }

class Exploitation(Base):
    __tablename__ = 'exploitation'
    
    idExploitation = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    idPays = Column(String(36), ForeignKey('pays.idPays'), nullable=False)
    nom = Column(String(150), nullable=False)
    
    pays = relationship("Pays", back_populates="exploitations")
    entrepots = relationship("Entrepot", back_populates="exploitation")
    utilisateurs = relationship("Utilisateur", back_populates="exploitation")
    
    def to_dict(self, include_pays=False):
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

class Utilisateur(Base):
    __tablename__ = 'utilisateur'
    
    idUtilisateur = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    idExploitation = Column(String(36), ForeignKey('exploitation.idExploitation'), nullable=False)
    nom = Column(String(50), nullable=False)
    prenom = Column(String(50), nullable=False)
    mail = Column(String(255), nullable=False, unique=True)
    
    exploitation = relationship("Exploitation", back_populates="utilisateurs")
    
    def to_dict(self):
        return {
            'idUtilisateur': self.idUtilisateur,
            'idExploitation': self.idExploitation,
            'nom': self.nom,
            'prenom': self.prenom,
            'mail': self.mail
        }

class Entrepot(Base):
    __tablename__ = 'entrepot'
    
    idEntrepot = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    idExploitation = Column(String(36), ForeignKey('exploitation.idExploitation'), nullable=False)
    nom = Column(String(100), nullable=False)
    adresse = Column(String(255), nullable=False)
    limiteQte = Column(Integer, nullable=False)
    
    exploitation = relationship("Exploitation", back_populates="entrepots")
    lots = relationship("LotGrains", back_populates="entrepot")
    mesures = relationship("Mesure", back_populates="entrepot")
    alertes = relationship("Alerte", back_populates="entrepot")
    
    def to_dict(self, include_details=False):
        result = {
            'idEntrepot': self.idEntrepot,
            'idExploitation': self.idExploitation,
            'nom': self.nom,
            'adresse': self.adresse,
            'limiteQte': self.limiteQte
        }
        
        if include_details:
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

class LotGrains(Base):
    __tablename__ = 'lot_grains'
    
    idLotGrains = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    idEntrepot = Column(String(36), ForeignKey('entrepot.idEntrepot'), nullable=False)
    datSto = Column(DateTime, nullable=False, default=datetime.utcnow)
    statut = Column(SQLEnum(StatutLot), nullable=False, default=StatutLot.CONFORME)
    datSortie = Column(DateTime, nullable=True)
    
    entrepot = relationship("Entrepot", back_populates="lots")
    alertes = relationship("Alerte", back_populates="lot_grains")
    
    def to_dict(self, include_hierarchy=False):
        result = {
            'idLotGrains': self.idLotGrains,
            'idEntrepot': self.idEntrepot,
            'datSto': self.datSto.isoformat() if self.datSto else None,
            'statut': self.statut.value if self.statut else None,
            'datSortie': self.datSortie.isoformat() if self.datSortie else None
        }
        
        if include_hierarchy and self.entrepot:
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

class Mesure(Base):
    __tablename__ = 'mesure'
    
    idMesure = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    idEntrepot = Column(String(36), ForeignKey('entrepot.idEntrepot'), nullable=False)
    temperature = Column(Float(1), nullable=False)
    humidite = Column(Float(1), nullable=False)
    datMesure = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    entrepot = relationship("Entrepot", back_populates="mesures")
    alertes = relationship("Alerte", back_populates="mesure")
    
    def to_dict(self):
        return {
            'idMesure': self.idMesure,
            'idEntrepot': self.idEntrepot,
            'temperature': self.temperature,
            'humidite': self.humidite,
            'datMesure': self.datMesure.isoformat() if self.datMesure else None
        }

class Alerte(Base):
    __tablename__ = 'alerte'
    
    idAlerte = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    idMesure = Column(String(36), ForeignKey('mesure.idMesure'), nullable=True)
    idLotGrains = Column(String(36), ForeignKey('lot_grains.idLotGrains'), nullable=True)
    idEntrepot = Column(String(36), ForeignKey('entrepot.idEntrepot'), nullable=False)
    type = Column(SQLEnum(TypeAlerte), nullable=False)
    valeurMesuree = Column(Float, nullable=True)
    dateAlerte = Column(DateTime, nullable=False, default=datetime.utcnow)
    statut = Column(SQLEnum(StatutAlerte), nullable=False, default=StatutAlerte.EN_COURS)
    
    entrepot = relationship("Entrepot", back_populates="alertes")
    mesure = relationship("Mesure", back_populates="alertes")
    lot_grains = relationship("LotGrains", back_populates="alertes")
    
    def to_dict(self, include_details=False):
        result = {
            'idAlerte': self.idAlerte,
            'idEntrepot': self.idEntrepot,
            'type': self.type.value if self.type else None,
            'valeurMesuree': self.valeurMesuree,
            'dateAlerte': self.dateAlerte.isoformat() if self.dateAlerte else None,
            'statut': self.statut.value if self.statut else None
        }
        
        if include_details and self.entrepot:
            result['nomEntrepot'] = self.entrepot.nom
            if self.entrepot.exploitation:
                result['nomExploitation'] = self.entrepot.exploitation.nom
                result['idExploitation'] = self.entrepot.exploitation.idExploitation
                if self.entrepot.exploitation.pays:
                    result['nomPays'] = self.entrepot.exploitation.pays.nom
                    result['idPays'] = self.entrepot.exploitation.pays.idPays
                    
        return result
