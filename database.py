"""
Module de configuration de la base de données pour l'API FutureKawa

Ce module gère la connexion à la base de données et fournit des utilitaires
pour la gestion des transactions et des sessions SQLAlchemy.

Supporte:
- MySQL (production)
- SQLite (développement)
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

# =============================================================================
# CONFIGURATION DE LA BASE DE DONNÉES
# =============================================================================

# URL de la base de données par défaut (SQLite pour le développement local)
# Peut être surchargée par la variable d'environnement DATABASE_URL
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///futurekawa.db'  # Base SQLite par défaut pour le développement
)

# Configuration pour MySQL (base de données principale pour la production)
# Les paramètres peuvent être configurés via des variables d'environnement
MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),      # Hôte du serveur MySQL
    'port': os.getenv('DB_PORT', '3306'),          # Port MySQL par défaut
    'database': os.getenv('DB_NAME', 'futurekawa'), # Nom de la base de données
    'user': os.getenv('DB_USER', 'root'),          # Utilisateur MySQL
    'password': os.getenv('DB_PASSWORD', '')       # Mot de passe MySQL
}

def get_database_url():
    """
    Construit et retourne l'URL de connexion à la base de données
    
    Returns:
        str: URL de connexion SQLAlchemy formatée selon le type de base de données
        
    La fonction utilise la variable d'environnement DB_TYPE pour déterminer
    quel type de base de données utiliser:
    - 'mysql': Base de données MySQL pour la production
    - 'sqlite' ou autre: Base de données SQLite pour le développement
    """
    db_type = os.getenv('DB_TYPE', 'sqlite').lower()
    
    if db_type == 'mysql':
        # Format MySQL: mysql+pymysql://user:password@host:port/database
        return f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}"
    else:
        # SQLite par défaut pour le développement
        return DATABASE_URL

# =============================================================================
# MOTEUR ET SESSIONS DE BASE DE DONNÉES
# =============================================================================

# Création du moteur de base de données SQLAlchemy
# Le moteur gère les connexions et le pool de connexions
engine = create_engine(
    get_database_url(),
    echo=os.getenv('DB_ECHO', 'False').lower() == 'true',  # Log des requêtes SQL si True
    pool_pre_ping=True,  # Vérifie la validité des connexions avant utilisation
    pool_size=10,        # Taille du pool de connexions
    max_overflow=20,     # Nombre max de connexions supplémentaires en cas de pic
    # Configuration spécifique pour SQLite (thread-safe)
    connect_args={'check_same_thread': False} if 'sqlite' in get_database_url() else {}
)

# Factory de sessions SQLAlchemy
# autocommit=False: Gestion manuelle des transactions
# autoflush=False: Pas de flush automatique avant chaque requête
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Session scoped pour les requêtes web
# Assure une session par thread/request
db_session = scoped_session(SessionLocal)

# =============================================================================
# FONCTIONS PRINCIPALES DE GESTION DE BASE DE DONNÉES
# =============================================================================

def get_db():
    """
    Retourne une session de base de données active
    
    Returns:
        Session: Session SQLAlchemy active pour le thread courant
        
    Cette fonction est utilisée par les contrôleurs pour obtenir une session
    de base de données et effectuer des opérations CRUD.
    """
    return db_session()

def init_db():
    """
    Initialise la base de données en créant toutes les tables définies dans les modèles
    
    Cette fonction lit les modèles SQLAlchemy définis dans models.py et crée
    les tables correspondantes dans la base de données si elles n'existent pas.
    
    Raises:
        Exception: En cas d'erreur lors de la création des tables
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("Base de données initialisée avec succès")

def drop_db():
    """
    Supprime toutes les tables de la base de données
    
    ⚠️  ATTENTION: Cette opération entraîne une perte complète de données!
    À utiliser uniquement pour le développement ou les tests.
    
    Raises:
        Exception: En cas d'erreur lors de la suppression des tables
    """
    from models import Base
    Base.metadata.drop_all(bind=engine)
    print("Toutes les tables ont été supprimées")

def reset_db():
    """
    Réinitialise complètement la base de données
    
    Cette fonction supprime toutes les tables existantes puis les recrée
    avec une structure vide. Utile pour le développement et les tests.
    
    ⚠️  ATTENTION: Perte complète de données!
    """
    drop_db()
    init_db()
    print("Base de données réinitialisée")

# =============================================================================
# CONFIGURATION DU LOGGING
# =============================================================================

# Configuration du logging pour SQLAlchemy
# Affiche les requêtes SQL si DB_ECHO=True
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(
    logging.INFO if os.getenv('DB_ECHO', 'False').lower() == 'true' else logging.WARNING
)

# =============================================================================
# VARIABLES GLOBALES
# =============================================================================

# Variable globale pour la session (compatibilité)
Session = SessionLocal

# =============================================================================
# UTILITAIRES DE GESTION DES TRANSACTIONS
# =============================================================================

def commit_session():
    """
    Valide (commit) la transaction en cours
    
    Cette fonction effectue un commit de la transaction SQLAlchemy active.
    En cas d'erreur, un rollback automatique est effectué.
    
    Raises:
        Exception: L'erreur originale est propagée après le rollback
    """
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e

def rollback_session():
    """
    Annule (rollback) la transaction en cours
    
    Cette fonction annule toutes les modifications non validées dans la
    transaction SQLAlchemy active.
    """
    db_session.rollback()

def close_session():
    """
    Ferme la session de base de données en cours
    
    Cette fonction ferme la session SQLAlchemy et la retire du registry
    des sessions scoped. Essentiel pour éviter les fuites de mémoire.
    """
    db_session.remove()

# =============================================================================
# CONTEXT MANAGER POUR LES TRANSACTIONS
# =============================================================================

class DatabaseTransaction:
    """
    Context manager pour la gestion automatique des transactions de base de données
    
    Ce context manager simplifie la gestion des transactions en gérant
    automatiquement le commit/rollback et la fermeture de session.
    
    Usage:
        with DatabaseTransaction() as session:
            # Opérations sur la base de données
            session.add(obj)
            # Si une exception survient, rollback automatique
        # Sinon, commit automatique et fermeture de session
    """
    def __enter__(self):
        """
        Entrée dans le context manager
        
        Returns:
            Session: Session SQLAlchemy active
        """
        return get_db()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Sortie du context manager
        
        Args:
            exc_type: Type d'exception (None si pas d'erreur)
            exc_val: Valeur de l'exception
            exc_tb: Traceback de l'exception
            
        Si une exception a été levée, effectue un rollback.
        Sinon, effectue un commit. Dans tous les cas, ferme la session.
        """
        if exc_type is not None:
            rollback_session()
        else:
            commit_session()
        close_session()

# =============================================================================
# FONCTIONS DE TEST ET UTILITAIRES
# =============================================================================

def test_connection():
    """
    Teste la connexion à la base de données
    
    Cette fonction vérifie que la connexion à la base de données fonctionne
    correctement en exécutant une requête simple.
    
    Returns:
        bool: True si la connexion réussit, False sinon
        
    Affiche un message dans la console indiquant le résultat du test.
    """
    try:
        with DatabaseTransaction() as session:
            session.execute(text("SELECT 1"))
        print("Connexion à la base de données réussie")
        return True
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return False

# =============================================================================
# POINT D'ENTRÉE PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    """
    Point d'entrée principal pour le module database.py
    
    Lorsqu'exécuté directement, ce script teste la connexion à la base de données
    et l'initialise si la connexion réussit.
    """
    # Test de connexion et initialisation
    if test_connection():
        init_db()
    else:
        print("Impossible de se connecter à la base de données")
