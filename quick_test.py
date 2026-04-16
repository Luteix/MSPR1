"""Test rapide de l'API d'authentification"""
from app import create_app
import json

app = create_app()

with app.test_client() as client:
    print("="*50)
    print("EXEMPLES D'UTILISATION DE L'AUTHENTIFICATION")
    print("="*50)
    
    # EXEMPLE 1: Inscription
    print("\n1. INSCRIPTION (POST /api/register)")
    print("-"*40)
    response = client.post('/api/register',
        data=json.dumps({
            'nom': 'Doe',
            'prenom': 'John',
            'email': 'john.doe@example.com',
            'password': 'monpassword123',
            'idExploitation': 1
        }),
        content_type='application/json'
    )
    print(f"Requête: {{'nom': 'Doe', 'prenom': 'John', 'email': 'john.doe@example.com', 'password': '***', 'idExploitation': 1}}")
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print(f"Réponse: {response.get_json()}")
    else:
        print(f"Erreur: {response.get_json()}")
    
    # EXEMPLE 2: Connexion
    print("\n2. CONNEXION (POST /api/login)")
    print("-"*40)
    response = client.post('/api/login',
        data=json.dumps({
            'email': 'jean@kawa.com',  # Utilisateur du seed
            'password': 'hash123'
        }),
        content_type='application/json'
    )
    print(f"Requête: {{'email': 'jean@kawa.com', 'password': 'hash123'}}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.get_json()
        token = data['token']
        user = data['user']
        print(f"Token: {token[:50]}...")
        print(f"Utilisateur: {user['prenom']} {user['nom']} ({user['mail']})")
        
        # EXEMPLE 3: Vérification du token
        print("\n3. VÉRIFICATION TOKEN (GET /api/verify)")
        print("-"*40)
        response = client.get('/api/verify',
            headers={'Authorization': f'Bearer {token}'}
        )
        print(f"Header: Authorization: Bearer {token[:30]}...")
        print(f"Status: {response.status_code}")
        print(f"Réponse: {response.get_json()}")
        
        # EXEMPLE 4: Accès sans token (doit échouer)
        print("\n4. ACCÈS PROTEGER SANS TOKEN (doit échouer)")
        print("-"*40)
        response = client.get('/api/protected')  # Route fictive ou réelle protégée
        print(f"Requête: GET /api/protected (sans token)")
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("[OK] Accès refusé - Authentification requise")
    else:
        print(f"Erreur: {response.get_json()}")
    
    print("\n" + "="*50)
    print("FIN DES EXEMPLES")
    print("="*50)
