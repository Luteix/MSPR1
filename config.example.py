"""
Configuration de l'application - EXEMPLE

1. Copier ce fichier en 'config.py'
2. Générer une clé JWT sécurisée
3. Ne JAMAIS commiter config.py (déjà dans .gitignore)
"""

import secrets
import os

class Config:
    """Configuration de base"""
    
    # Clé secrète pour JWT - GÉNÉRER UNE NOUVELLE CLÉ FORTE !
    # Commande pour générer : python -c "import secrets; print(secrets.token_hex(32))"
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'votre-cle-super-secrete-a-changer')
    
    # Durée de validité du token (en heures)
    JWT_ACCESS_TOKEN_EXPIRES = 24
    
    # Algorithme de chiffrement
    JWT_ALGORITHM = 'HS256'
    
    # Configuration bcrypt (complexité du hash)
    # 12 = bon équilibre sécurité/performance
    BCRYPT_ROUNDS = 12

# Mode développement
class DevelopmentConfig(Config):
    DEBUG = True
    JWT_ACCESS_TOKEN_EXPIRES = 24  # 24h en dev

# Mode production
class ProductionConfig(Config):
    DEBUG = False
    JWT_ACCESS_TOKEN_EXPIRES = 8   # 8h en prod pour plus de sécurité
    # En prod, JWT_SECRET_KEY doit OBLIGATOIREMENT venir des variables d'environnement

# Sélection selon l'environnement
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
