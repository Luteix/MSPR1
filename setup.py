"""
FICHIER: setup.py
UTILITÉ: Script d'installation automatique pour nouveaux environnements

- Vérifie si config.py existe, sinon le crée depuis config.example.py
- Génère une clé JWT unique si nécessaire
- Vérifie les dépendances Python
- Doit être exécuté avant le premier lancement: python setup.py
"""

import os
import sys
import secrets
import shutil

def generate_jwt_secret():
    """Génère une clé JWT sécurisée de 64 caractères hexadécimaux"""
    return secrets.token_hex(32)

def setup_config():
    """
    Configure le fichier config.py pour l'environnement local.
    Crée config.py depuis config.example.py s'il n'existe pas.
    """
    print("=== SETUP FUTUREKAWA API ===\n")
    
    # Vérifie si config.py existe déjà
    if os.path.exists('config.py'):
        print("[OK] config.py existe déjà")
        return True
    
    # Vérifie si config.example.py existe
    if not os.path.exists('config.example.py'):
        print("[ERREUR] config.example.py manquant!")
        print("   Le fichier template est nécessaire pour créer config.py")
        return False
    
    print("[INFO] config.py manquant - Création depuis le template...")
    
    # Lit le template
    with open('config.example.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Génère une nouvelle clé JWT
    new_secret = generate_jwt_secret()
    print(f"[INFO] Nouvelle clé JWT générée: {new_secret[:16]}...")
    
    # Remplace la clé par défaut
    content = content.replace(
        "JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'votre-cle-super-secrete-a-changer')",
        f'JWT_SECRET_KEY = "{new_secret}"'
    )
    
    # Écrit config.py
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[OK] config.py créé avec succès!")
    print("   ⚠️  Ce fichier contient votre clé JWT privée")
    print("   ⚠️  Ne le partagez pas et ne le commitez pas (déjà dans .gitignore)")
    
    return True

def check_dependencies():
    """Vérifie si les dépendances principales sont installées"""
    print("\n=== VÉRIFICATION DÉPENDANCES ===")
    
    required_modules = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('flasgger', 'Flasgger'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('pymysql', 'PyMySQL'),
        ('jwt', 'PyJWT'),
        ('bcrypt', 'bcrypt'),
        ('dotenv', 'python-dotenv'),
    ]
    
    missing = []
    
    for module_name, package_name in required_modules:
        try:
            __import__(module_name)
            print(f"  [OK] {package_name}")
        except ImportError:
            print(f"  [MANQUANT] {package_name}")
            missing.append(package_name)
    
    if missing:
        print(f"\n[ERREUR] Dépendances manquantes: {', '.join(missing)}")
        print("   Installez-les avec: pip install -r requirements.txt")
        return False
    else:
        print("\n[OK] Toutes les dépendances sont installées")
        return True

def main():
    """Fonction principale de setup"""
    print("FutureKawa API - Installation\n")
    
    # Setup config
    if not setup_config():
        print("\n[ECHEC] Impossible de créer config.py")
        sys.exit(1)
    
    # Vérifie dépendances
    if not check_dependencies():
        print("\n[ECHEC] Dépendances manquantes")
        sys.exit(1)
    
    print("\n" + "="*40)
    print("[OK] SETUP TERMINÉ AVEC SUCCÈS!")
    print("="*40)
    print("\nProchaines étapes:")
    print("  1. Configurer .env avec vos paramètres BDD")
    print("  2. Lancer l'API: python app.py")
    print("\nDocumentation:")
    print("  - Swagger UI: http://localhost:5000/docs")
    print("  - README.md pour plus d'infos")

if __name__ == "__main__":
    main()
