"""Debug auth issues"""
from app import create_app
import json
import traceback

app = create_app()
app.config['SQLALCHEMY_ECHO'] = False

with app.test_client() as client:
    print("="*50)
    print("DEBUG AUTHENTIFICATION")
    print("="*50)
    
    # Test 1: Direct DB check
    print("\n1. Check utilisateur en BDD...")
    with app.app_context():
        from database import get_db
        from models import Utilisateur
        db = get_db()
        user = db.query(Utilisateur).filter_by(mail='jean@kawa.com').first()
        if user:
            print(f"   User trouve: ID={user.idUtilisateur}, Email={user.mail}")
            print(f"   MDP stocke: {user.mdp[:20]}..." if user.mdp else "   MDP: None")
        else:
            print("   User PAS trouve!")
    
    # Test 2: Login
    print("\n2. Test POST /api/login...")
    try:
        resp = client.post('/api/login',
            data=json.dumps({'email': 'jean@kawa.com', 'password': 'hash123'}),
            content_type='application/json'
        )
        print(f"   Status: {resp.status_code}")
        data = resp.get_json()
        print(f"   Response: {data}")
        
        if resp.status_code == 200:
            print("   [OK] Login fonctionne!")
        else:
            print(f"   [ERREUR] {data.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"   [EXCEPTION] {e}")
        traceback.print_exc()
    
    print("\n" + "="*50)
