import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

# Configuration de la base de données
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///futurekawa.db'  # Base SQLite par défaut pour le développement
)

# Configuration pour MySQL
MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '3306'),
    'database': os.getenv('DB_NAME', 'futurekawa'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '')
}

def get_database_url():
    """
    Retourne l'URL de la base de données en fonction de la configuration
    """
    db_type = os.getenv('DB_TYPE', 'sqlite').lower()
    
    if db_type == 'mysql':
        return f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}"
    else:
        # SQLite par défaut
        return DATABASE_URL

# Création du moteur de base de données
engine = create_engine(
    get_database_url(),
    echo=os.getenv('DB_ECHO', 'False').lower() == 'true',  # Log des requêtes SQL
    pool_pre_ping=True,  # Vérification des connexions
    pool_size=10,
    max_overflow=20,
    # Configuration spécifique pour SQLite
    connect_args={'check_same_thread': False} if 'sqlite' in get_database_url() else {}
)

# Création de la factory de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Session scoped pour les requêtes
db_session = scoped_session(SessionLocal)

def get_db():
    """
    Retourne une session de base de données
    """
    return db_session()

def init_db():
    """
    Initialise la base de données en créant toutes les tables
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("Base de données initialisée avec succès")

def drop_db():
    """
    Supprime toutes les tables (attention: perte de données!)
    """
    from models import Base
    Base.metadata.drop_all(bind=engine)
    print("Toutes les tables ont été supprimées")

def reset_db():
    """
    Réinitialise la base de données (supprime et recrée les tables)
    """
    drop_db()
    init_db()
    print("Base de données réinitialisée")

# Configuration du logging SQL
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO if os.getenv('DB_ECHO', 'False').lower() == 'true' else logging.WARNING)

# Variable globale pour la session
Session = SessionLocal

# Fonctions utilitaires pour la gestion des transactions
def commit_session():
    """
    Commit la transaction en cours
    """
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e

def rollback_session():
    """
    Rollback la transaction en cours
    """
    db_session.rollback()

def close_session():
    """
    Ferme la session en cours
    """
    db_session.remove()

# Context manager pour les transactions
class DatabaseTransaction:
    """
    Context manager pour gérer les transactions de base de données
    """
    def __enter__(self):
        return get_db()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            rollback_session()
        else:
            commit_session()
        close_session()

# Fonction pour tester la connexion
def test_connection():
    """
    Teste la connexion à la base de données
    """
    try:
        with DatabaseTransaction() as session:
            session.execute(text("SELECT 1"))
        print("Connexion à la base de données réussie")
        return True
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return False

if __name__ == "__main__":
    # Test de connexion et initialisation
    if test_connection():
        init_db()
    else:
        print("Impossible de se connecter à la base de données")
