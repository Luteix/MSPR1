"""
Configuration JWT chargée depuis les variables d'environnement et le fichier .env.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration JWT"""

    # Clé secrète pour signer les tokens (garder SECRET !)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-change-me')

    # Durée de validité du token en heures
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '24'))

    # Algorithme de signature
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

    # Complexité du hash bcrypt (12 = bon équilibre)
    BCRYPT_ROUNDS = int(os.getenv('BCRYPT_ROUNDS', '12'))
