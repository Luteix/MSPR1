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
    Demande interactivement le mot de passe MySQL si non configuré.
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
    
    # Paramètres BDD par défaut
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'futurekawa')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    
    # Si pas de MDP configuré explicitement, demande interactivement
    env_exists = os.path.exists('.env') and os.getenv('DB_PASSWORD') is not None
    
    if db_password == 'votre_mot_de_passe' or (not db_password and not env_exists):
        print("[INFO] Configuration de la connexion MySQL requise")
        print("\nLes paramètres par défaut sont:")
        print(f"  - Hôte: {db_host}")
        print(f"  - Port: {db_port}")
        print(f"  - Utilisateur: {db_user}")
        print(f"  - Base: {db_name}")
        
        db_password_input = input("\nMot de passe MySQL (root) [Entrée pour vide]: ").strip()
        db_password = db_password_input  # Peut être vide
        
        # Sauvegarde dans .env si différent
        save_password_to_env(db_password)
    
    elif not db_password and env_exists:
        print("[INFO] Utilisation du mot de passe vide depuis .env")
    
    print(f"\n[INFO] Connexion à MySQL ({db_host}:{db_port})...")
    
    try:
        import pymysql
        
        # Connexion SANS base pour créer la base si besoin
        conn = pymysql.connect(
            host=db_host,
            port=int(db_port),
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        
        # Vérifie si la base existe déjà
        cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
        db_exists = cursor.fetchone()
        
        if db_exists:
            print(f"[OK] Base de données '{db_name}' existe déjà")
            
            # Vérifie si des tables existent
            cursor.execute(f"USE {db_name}")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print(f"[INFO] {len(tables)} tables trouvées")
                response = input("\nRéinitialiser la base de données? (oui/non): ").lower().strip()
                if response not in ['oui', 'yes', 'o', 'y']:
                    print("[INFO] Conservation de la base existante")
                    conn.close()
                    return True
        else:
            print(f"[INFO] Création de la base '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"[OK] Base '{db_name}' créée")
        
        conn.close()
        
    except Exception as e:
        print(f"[ERREUR] Connexion MySQL échouée: {e}")
        print("   Vérifiez que MySQL est démarré et accessible")
        return False
    
    # Exécute les scripts SQL via Python (pas besoin de commande mysql externe)
    try:
        def execute_sql_file(filepath, db_host, db_port, db_user, db_password, db_name=None):
            """Exécute un fichier SQL via pymysql"""
            with open(filepath, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Connexion
            conn = pymysql.connect(
                host=db_host,
                port=int(db_port),
                user=db_user,
                password=db_password,
                database=db_name if db_name else None,
                charset='utf8mb4'
            )
            cursor = conn.cursor()
            
            # Split les commandes et exécute
            for statement in sql_content.split(';'):
                stmt = statement.strip()
                if stmt and not stmt.startswith('--') and not stmt.startswith('/*'):
                    try:
                        cursor.execute(stmt)
                    except Exception as e:
                        # Ignore les erreurs de commandes qui peuvent échouer silencieusement
                        if 'USE' not in stmt.upper():
                            print(f"   [WARN] Commande ignorée: {str(e)[:60]}")
            
            conn.commit()
            conn.close()
            return True
        
        # futurekawa.sql
        print("\n[INFO] Exécution de futurekawa.sql (structure)...")
        if execute_sql_file('futurekawa.sql', db_host, db_port, db_user, db_password):
            print("[OK] Structure de la base créée")
        else:
            return False
        
        # kawa_seed.sql
        print("\n[INFO] Exécution de kawa_seed.sql (données)...")
        if execute_sql_file('kawa_seed.sql', db_host, db_port, db_user, db_password, db_name):
            print("[OK] Données insérées")
        else:
            return False
        
        print("[OK] Base de données prête!")
        
    except Exception as e:
        print(f"[ERREUR] Impossible d'exécuter les scripts SQL: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def save_password_to_env(password):
    """Sauvegarde le mot de passe dans le fichier .env"""
    env_path = '.env'
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        lines = [
            "# Configuration de la base de données MySQL\n",
            "DB_HOST=localhost\n",
            "DB_PORT=3306\n",
            "DB_NAME=futurekawa\n",
            "DB_USER=root\n",
            "FLASK_DEBUG=True\n"
        ]
    
    # Remplace ou ajoute DB_PASSWORD
    new_lines = []
    password_set = False
    
    for line in lines:
        if line.startswith('DB_PASSWORD='):
            new_lines.append(f'DB_PASSWORD={password}\n')
            password_set = True
        else:
            new_lines.append(line)
    
    if not password_set:
        new_lines.append(f'DB_PASSWORD={password}\n')
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"[OK] Mot de passe sauvegardé dans {env_path}")

def start_api(auto_mode=False):
    """Demande si l'utilisateur veut démarrer l'API"""
    print("\n" + "="*40)
    print("[OK] INSTALLATION TERMINÉE!")
    print("="*40)
    
    if auto_mode:
        # Mode automatique: ne pas demander, juste afficher
        print("\n[INFO] Installation terminée, retour à l'API...")
        return
    
    print("\nVoulez-vous démarrer l'API maintenant?")
    response = input("Démarrer l'API? (oui/non): ").lower().strip()
    
    if response in ['oui', 'yes', 'o', 'y']:
        print("\n[INFO] Démarrage de l'API...")
        print("   Appuyez sur Ctrl+C pour arrêter\n")
        
        try:
            subprocess.run([sys.executable, 'app.py'])
        except KeyboardInterrupt:
            print("\n[INFO] API arrêtée")
    else:
        print("\n[INFO] Pour démarrer manuellement:")
        print("   python app.py")
        print("\nDocumentation Swagger:")
        print("   http://localhost:5000/docs")

def main(auto_mode=False):
    """Fonction principale de setup"""
    if not auto_mode:
        print("FutureKawa API - Installation\n")
    
    # Setup config (JWT)
    if not setup_config():
        print("\n[ECHEC] Impossible de créer config.py")
        return False
    
    # Setup .env (variables BDD)
    if not setup_env():
        print("\n[ECHEC] Impossible de créer .env")
        return False
    
    # Vérifie dépendances
    if not check_dependencies():
        print("\n[ECHEC] Dépendances manquantes")
        return False
    
    # Setup base de données
    if not setup_database():
        print("\n[ECHEC] Problème avec la base de données")
        return False
    
    # Propose de démarrer l'API (ou juste affiche en mode auto)
    start_api(auto_mode)
    return True

if __name__ == "__main__":
    # Détecte si --auto est passé en argument
    auto_mode = '--auto' in sys.argv
    success = main(auto_mode)
    sys.exit(0 if success else 1)
