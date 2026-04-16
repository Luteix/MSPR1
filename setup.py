"""
FICHIER: setup.py
UTILITÉ: Script d'installation automatique pour nouveaux environnements

- Crée config.py (JWT) depuis config.example.py
- Crée .env (variables BDD) s'il n'existe pas
- Vérifie les dépendances Python
- Teste et initialise la base de données (futurekawa.sql + kawa_seed.sql)
- Doit être exécuté avant le premier lancement: python setup.py
"""

import os
import sys
import secrets
import shutil
import subprocess

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

def setup_env():
    """
    Crée le fichier .env avec les paramètres de base de données par défaut.
    L'utilisateur devra éditer ce fichier avec ses vrais credentials.
    """
    if os.path.exists('.env'):
        print("[OK] .env existe déjà")
        return True
    
    print("[INFO] .env manquant - Création du fichier...")
    
    env_content = """# Configuration de la base de données MySQL
# Modifiez ces valeurs avec vos paramètres réels

DB_HOST=localhost
DB_PORT=3306
DB_NAME=futurekawa
DB_USER=root
DB_PASSWORD=votre_mot_de_passe

# Mode debug (True/False)
FLASK_DEBUG=True
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("[OK] .env créé avec les valeurs par défaut")
    print("   ⚠️  Modifiez DB_PASSWORD avec votre vrai mot de passe MySQL")
    return True

def setup_database():
    """
    Initialise la base de données avec les scripts SQL.
    Exécute futurekawa.sql (structure) puis kawa_seed.sql (données).
    """
    print("\n=== BASE DE DONNÉES ===")
    
    # Vérifie si les fichiers SQL existent
    if not os.path.exists('futurekawa.sql'):
        print("[SKIP] futurekawa.sql non trouvé - BDD non initialisée")
        return True
    
    if not os.path.exists('kawa_seed.sql'):
        print("[SKIP] kawa_seed.sql non trouvé - données non insérées")
        return True
    
    # Charge les variables d'environnement
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("[ERREUR] python-dotenv non installé")
        return False
    
    # Récupère les paramètres BDD
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'futurekawa')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    
    if not db_password or db_password == 'votre_mot_de_passe':
        print("[INFO] Mot de passe BDD non configuré dans .env")
        print("   Modifiez DB_PASSWORD dans le fichier .env puis relancez setup.py")
        return True
    
    print(f"[INFO] Connexion à MySQL ({db_host}:{db_port})...")
    
    try:
        import pymysql
        
        # Teste la connexion
        conn = pymysql.connect(
            host=db_host,
            port=int(db_port),
            user=db_user,
            password=db_password
        )
        conn.close()
        print("[OK] Connexion MySQL réussie")
        
    except Exception as e:
        print(f"[ERREUR] Connexion MySQL échouée: {e}")
        print("   Vérifiez vos paramètres dans .env")
        return False
    
    # Demande confirmation avant d'exécuter les scripts SQL
    print("\n[QUESTION] Voulez-vous initialiser la base de données?")
    print("   Cela exécutera:")
    print("   1. futurekawa.sql (création des tables)")
    print("   2. kawa_seed.sql (insertion des données)")
    
    response = input("\nContinuer? (oui/non): ").lower().strip()
    
    if response not in ['oui', 'yes', 'o', 'y']:
        print("[INFO] Initialisation BDD ignorée")
        return True
    
    try:
        # Exécute futurekawa.sql
        print("\n[INFO] Exécution de futurekawa.sql...")
        cmd1 = f'mysql -h {db_host} -P {db_port} -u {db_user} -p{db_password} < futurekawa.sql'
        result1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True)
        
        if result1.returncode != 0:
            print(f"[ERREUR] futurekawa.sql: {result1.stderr}")
            return False
        
        print("[OK] futurekawa.sql exécuté avec succès")
        
        # Exécute kawa_seed.sql
        print("\n[INFO] Exécution de kawa_seed.sql...")
        cmd2 = f'mysql -h {db_host} -P {db_port} -u {db_user} -p{db_password} {db_name} < kawa_seed.sql'
        result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
        
        if result2.returncode != 0:
            print(f"[ERREUR] kawa_seed.sql: {result2.stderr}")
            return False
        
        print("[OK] kawa_seed.sql exécuté avec succès")
        print("[OK] Base de données initialisée avec les données de test!")
        
    except Exception as e:
        print(f"[ERREUR] Impossible d'exécuter les scripts SQL: {e}")
        print("   Assurez-vous que MySQL est installé et accessible")
        return False
    
    return True

def main():
    """Fonction principale de setup"""
    print("FutureKawa API - Installation\n")
    
    # Setup config (JWT)
    if not setup_config():
        print("\n[ECHEC] Impossible de créer config.py")
        sys.exit(1)
    
    # Setup .env (variables BDD)
    if not setup_env():
        print("\n[ECHEC] Impossible de créer .env")
        sys.exit(1)
    
    # Vérifie dépendances
    if not check_dependencies():
        print("\n[ECHEC] Dépendances manquantes")
        sys.exit(1)
    
    # Setup base de données
    if not setup_database():
        print("\n[ECHEC] Problème avec la base de données")
        sys.exit(1)
    
    print("\n" + "="*40)
    print("[OK] SETUP TERMINÉ AVEC SUCCÈS!")
    print("="*40)
    print("\nProchaines étapes:")
    print("  1. Lancer l'API: python app.py")
    print("\nDocumentation:")
    print("  - Swagger UI: http://localhost:5000/docs")
    print("  - README.md pour plus d'infos")

if __name__ == "__main__":
    main()
