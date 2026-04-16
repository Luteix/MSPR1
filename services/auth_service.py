"""
FICHIER: services/auth_service.py
UTILITÉ: Logique métier d'authentification (Couche Domaine)

Gère:
- Hashage MDP avec bcrypt (hash_password)
- Génération et vérification JWT (generate_token, verify_token)
- Inscription et connexion (register, login)
- Récupération utilisateur par token (get_current_user)

Utilise UtilisateurRepository pour accéder à la BDD.
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from config import Config
from repositories.utilisateur_repository import UtilisateurRepository

class AuthService:
    """Gestion de l'authentification et des tokens JWT"""
    
    @staticmethod
    def hash_password(password):
        """
        Hash un mot de passe avec bcrypt
        Args:
            password: Mot de passe en clair
        Returns:
            Hash du mot de passe (string)
        """
        # Génère un salt et hash le mot de passe
        salt = bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password, stored_password):
        """
        Vérifie un mot de passe contre celui stocké en BDD
        Gère les MDP en clair (compatibilité) et les MDP hashés (sécurité)
        
        Args:
            password: Mot de passe en clair saisi par l'utilisateur
            stored_password: Mot de passe tel que stocké en BDD (clair ou hashé)
        Returns:
            True si correspond, False sinon
        """
        # Si c'est un hash bcrypt (commence par $2b$, $2a$, $2y$)
        if stored_password and stored_password.startswith('$2'):
            try:
                # Vérification bcrypt standard
                return bcrypt.checkpw(
                    password.encode('utf-8'),
                    stored_password.encode('utf-8')
                )
            except ValueError:
                # Si le hash est invalide, on traite comme clair
                return password == stored_password
        else:
            # Comparaison en clair (pour compatibilité BDD existante)
            return password == stored_password
    
    @staticmethod
    def generate_token(user_id):
        """
        Génère un token JWT pour un utilisateur
        Args:
            user_id: ID de l'utilisateur
        Returns:
            Token JWT (string)
        """
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=Config.JWT_ACCESS_TOKEN_EXPIRES),
            'iat': datetime.utcnow(),  # Issued at
            'type': 'access'
        }
        
        token = jwt.encode(
            payload,
            Config.JWT_SECRET_KEY,
            algorithm=Config.JWT_ALGORITHM
        )
        return token
    
    @staticmethod
    def verify_token(token):
        """
        Vérifie et décode un token JWT
        Args:
            token: Token JWT à vérifier
        Returns:
            Payload du token si valide
        Raises:
            jwt.ExpiredSignatureError: Si le token est expiré
            jwt.InvalidTokenError: Si le token est invalide
        """
        payload = jwt.decode(
            token,
            Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return payload
    
    @staticmethod
    def register(nom, prenom, email, password, id_exploitation, id_poste=1):
        """
        Inscrit un nouvel utilisateur
        Args:
            nom: Nom de famille
            prenom: Prénom
            email: Adresse email (unique)
            password: Mot de passe en clair
            id_exploitation: ID de l'exploitation
            id_poste: ID du poste (défaut: 1 = Employé)
        Returns:
            Dictionnaire avec user et token
        Raises:
            ValueError: Si l'email existe déjà
        """
        # Vérifie si l'email existe déjà
        existing = UtilisateurRepository.get_by_email(email)
        if existing:
            raise ValueError("Cet email est déjà utilisé")
        
        # Hash le mot de passe
        password_hash = AuthService.hash_password(password)
        
        # Crée l'utilisateur (sans idPoste car pas de colonne dans la BDD)
        user_data = {
            'nom': nom,
            'prenom': prenom,
            'mail': email,
            'mdp': password_hash,
            'idExploitation': id_exploitation
        }
        
        user = UtilisateurRepository.create(user_data)
        
        # Génère le token
        token = AuthService.generate_token(user.idUtilisateur)
        
        return {
            'user': {
                'id': user.idUtilisateur,
                'nom': user.nom,
                'prenom': user.prenom,
                'email': user.mail
            },
            'token': token
        }
    
    @staticmethod
    def login(email, password):
        """
        Authentifie un utilisateur
        Args:
            email: Adresse email
            password: Mot de passe en clair
        Returns:
            Dictionnaire avec user et token
        Raises:
            ValueError: Si identifiants invalides
        """
        # Récupère l'utilisateur
        user = UtilisateurRepository.get_by_email(email)
        if not user:
            raise ValueError("Email ou mot de passe incorrect")
        
        # Vérifie le mot de passe
        if not AuthService.verify_password(password, user.mdp):
            raise ValueError("Email ou mot de passe incorrect")
        
        # Génère le token
        token = AuthService.generate_token(user.idUtilisateur)
        
        return {
            'user': {
                'id': user.idUtilisateur,
                'nom': user.nom,
                'prenom': user.prenom,
                'email': user.mail,
                'idExploitation': user.idExploitation
            },
            'token': token
        }
    
    @staticmethod
    def get_current_user(token):
        """
        Récupère l'utilisateur courant depuis un token
        Args:
            token: Token JWT
        Returns:
            Utilisateur ou None
        """
        try:
            payload = AuthService.verify_token(token)
            user_id = payload.get('user_id')
            if user_id:
                return UtilisateurRepository.get_by_id(user_id)
            return None
        except jwt.InvalidTokenError:
            return None
