"""Démonstration de l'authentification"""
from app import create_app
import json

app = create_app()

with app.test_client() as client:
    print("=" * 50)
    print("EXEMPLES D'AUTHENTIFICATION FUTUREKAWA API")
    print("=" * 50)
    
    # EXEMPLE 1: LOGIN
    print("\n1. CONNEXION (POST /api/login)")
    print("-" * 40)
    print("Requete JSON:")
    print('  {')
    print('    "email": "jean@kawa.com",')
    print('    "password": "hash123"')
    print('  }')
    
    resp = client.post('/api/login',
        data=json.dumps({'email': 'jean@kawa.com', 'password': 'hash123'}),
        content_type='application/json'
    )
    
    print(f"\nReponse: HTTP {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.get_json()
        token = data['token']
        user = data['user']
        print("\n  [OK] Connexion reussie!")
        print(f"  Token JWT: {token[:50]}...")
        print(f"  Utilisateur: {user['prenom']} {user['nom']}")
        print(f"  Email: {user['mail']}")
        print(f"  Role: {user.get('poste', 'N/A')}")
    else:
        print(f"  Erreur: {resp.get_json()}")
    
    # EXEMPLE 2: VERIFY TOKEN
    print("\n2. VERIFICATION TOKEN (GET /api/verify)")
    print("-" * 40)
    print("Header HTTP:")
    print(f'  Authorization: Bearer {token[:30]}...')
    
    resp2 = client.get('/api/verify', 
        headers={'Authorization': f'Bearer {token}'}
    )
    
    print(f"\nReponse: HTTP {resp2.status_code}")
    if resp2.status_code == 200:
        print("  [OK] Token valide et actif!")
    
    # EXEMPLE 3: INSCRIPTION
    print("\n3. INSCRIPTION (POST /api/register)")
    print("-" * 40)
    print("Requete JSON:")
    print('  {')
    print('    "nom": "Martin",')
    print('    "prenom": "Sophie",')
    print('    "email": "sophie.martin@example.com",')
    print('    "password": "monpassword",')
    print('    "idExploitation": 1')
    print('  }')
    
    resp3 = client.post('/api/register',
        data=json.dumps({
            'nom': 'Martin',
            'prenom': 'Sophie',
            'email': 'sophie.martin@example.com',
            'password': 'monpassword',
            'idExploitation': 1
        }),
        content_type='application/json'
    )
    
    print(f"\nReponse: HTTP {resp3.status_code}")
    data3 = resp3.get_json()
    if resp3.status_code == 201:
        print(f"  [OK] {data3.get('message', 'Inscription OK')}")
    else:
        print(f"  Info: {data3.get('message', 'Erreur')}")
    
    print("\n" + "=" * 50)
    print("UTILISATION DANS VOS REQUETES API")
    print("=" * 50)
    print("\nPour acceder aux routes protegees:")
    print("  1. Recuperez le token via /api/login")
    print("  2. Ajoutez le header a toutes vos requetes:")
    print('     Authorization: Bearer <votre_token>')
    print("\nExemple avec curl:")
    print(f'  curl -H "Authorization: Bearer {token[:20]}..." http://localhost:5000/api/mesures')
    
    print("\n" + "=" * 50)
