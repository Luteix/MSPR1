"""Test simple auth sans emojis"""
from app import create_app
import json

app = create_app()

with app.test_client() as client:
    print("="*50)
    print("TEST AUTHENTIFICATION")
    print("="*50)
    
    # Test Login
    print("\n1. POST /api/login")
    resp = client.post('/api/login',
        data=json.dumps({'email': 'jean@kawa.com', 'password': 'hash123'}),
        content_type='application/json'
    )
    
    print(f"   Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.get_json()
        token = data['token']
        user = data['user']
        print(f"   Token: {token[:40]}...")
        print(f"   User: {user['prenom']} {user['nom']}")
        print("   SUCCES")
        
        # Test Verify
        print("\n2. GET /api/verify")
        resp2 = client.get('/api/verify', headers={'Authorization': f'Bearer {token}'})
        print(f"   Status: {resp2.status_code}")
        if resp2.status_code == 200:
            print("   Token valide")
    else:
        print(f"   ERREUR: {resp.get_json()}")
    
    # Test Register
    print("\n3. POST /api/register")
    resp3 = client.post('/api/register',
        data=json.dumps({
            'nom': 'Test', 'prenom': 'User', 'email': 'test99@test.com',
            'password': 'test123', 'idExploitation': 1
        }),
        content_type='application/json'
    )
    print(f"   Status: {resp3.status_code}")
    data3 = resp3.get_json()
    print(f"   Message: {data3.get('message', 'N/A')}")
    
    print("\n" + "="*50)
    print("TEST TERMINE")
    print("="*50)
