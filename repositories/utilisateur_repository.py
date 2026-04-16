"""
FICHIER: repositories/utilisateur_repository.py
UTILITÉ: Accès base de données pour les utilisateurs (Couche Database)

Fournit les opérations CRUD:
- get_by_email() : Chercher par email (pour login)
- get_by_id() : Chercher par ID (pour token)
- create() : Créer nouvel utilisateur
- update_password() : Mettre à jour le MDP

Utilise get_db() pour les sessions SQLAlchemy.
"""

from database import get_db
from models import Utilisateur

class UtilisateurRepository:
    """Gestion des opérations BDD pour les utilisateurs"""
    
    @staticmethod
    def get_by_email(email):
        """
        Récupère un utilisateur par son email
        Args:
            email: Adresse email de l'utilisateur
        Returns:
            Utilisateur ou None si non trouvé
        """
        session = get_db()
        try:
            return session.query(Utilisateur).filter(
                Utilisateur.mail == email
            ).first()
        finally:
            session.close()
    
    @staticmethod
    def get_by_id(user_id):
        """
        Récupère un utilisateur par son ID
        Args:
            user_id: ID de l'utilisateur
        Returns:
            Utilisateur ou None si non trouvé
        """
        session = get_db()
        try:
            return session.query(Utilisateur).filter(
                Utilisateur.idUtilisateur == user_id
            ).first()
        finally:
            session.close()
    
    @staticmethod
    def create(user_data):
        """
        Crée un nouvel utilisateur
        Args:
            user_data: Dictionnaire avec nom, prenom, mail, mdp_hash, idExploitation, idPoste
        Returns:
            Utilisateur créé
        """
        session = get_db()
        try:
            utilisateur = Utilisateur(**user_data)
            session.add(utilisateur)
            session.commit()
            session.refresh(utilisateur)
            session.expunge(utilisateur)
            return utilisateur
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def update_password(user_id, new_password_hash):
        """
        Met à jour le mot de passe d'un utilisateur
        Args:
            user_id: ID de l'utilisateur
            new_password_hash: Nouveau hash du mot de passe
        Returns:
            True si mis à jour, False sinon
        """
        session = get_db()
        try:
            user = session.query(Utilisateur).filter(
                Utilisateur.idUtilisateur == user_id
            ).first()
            if user:
                user.mdp = new_password_hash
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
