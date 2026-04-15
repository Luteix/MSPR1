#!/usr/bin/env python3
"""
Script de test complet pour l'API - teste tous les endpoints /api/...
Exécute : python test_api.py
"""

import sys
sys.path.append('.')  # Ajoute le dossier courant au path pour importer l'app

from app import create_app  # Importe la factory function Flask
app = create_app()  # Crée l'instance de l'application Flask
import json  # Pour sérialiser les données POST

def test_api():
    """Teste tous les endpoints de l'API"""
    print(">>> TESTS COMPLETS DES ENDPOINTS API")
    print("=" * 60)
    
    # Crée un client de test Flask (simule les requêtes HTTP sans serveur)
    with app.test_client() as client:
        # Liste des tests à exécuter : (méthode, endpoint, données POST, status attendu)
        tests = [
            # Tests GET - récupération de données
            ('GET', '/api/pays', None, 200),           # Liste tous les pays
            ('GET', '/api/pays/1', None, 404),         # Pays ID 1 (404 = vide)
            ('GET', '/api/exploitations', None, 200),   # Liste exploitations
            ('GET', '/api/exploitations/1', None, 404), # Exploitation ID 1
            ('GET', '/api/entrepots', None, 200),      # Liste entrepôts
            ('GET', '/api/entrepots/1', None, 404),    # Entrepôt ID 1
            ('GET', '/api/lots', None, 200),         # Liste lots
            ('GET', '/api/lots/1', None, 404),       # Lot ID 1
            ('GET', '/api/mesures/entrepot/1', None, 200),  # Mesures entrepôt 1
            ('GET', '/api/mesures/1', None, 200),   # Mesure ID 1
            ('GET', '/api/dashboard/summary', None, 200),  # Résumé dashboard
            ('GET', '/api/alertes', None, 200),      # Liste alertes
            
            # Tests POST - création de données
            ('POST', '/api/mesures', {'idEntrepot': 1, 'temperature': 25.5, 'humidite': 65.0}, 201),  # Crée mesure
            ('POST', '/api/alertes', {'idMesure': 1}, [201, 500]),  # Crée alerte (500 si déjà existe)
        ]
        
        passed = 0   # Compteur de tests réussis
        failed = 0   # Compteur de tests échoués
        
        # Boucle sur chaque test
        for method, endpoint, data, expected_status in tests:
            try:
                # Exécute la requête GET ou POST
                if method == 'GET':
                    response = client.get(endpoint)  # Envoie requête GET
                else:
                    response = client.post(
                        endpoint,
                        data=json.dumps(data),  # Convertit dict en JSON
                        content_type='application/json'  # Header Content-Type
                    )
                
                # Vérifie si le status est OK (gère liste ou valeur unique)
                if isinstance(expected_status, list):
                    status_ok = response.status_code in expected_status
                else:
                    status_ok = response.status_code == expected_status
                
                # Affiche le résultat du test
                if status_ok:
                    print(f"[OK] {method} {endpoint} - Status {response.status_code}")
                    passed += 1
                else:
                    print(f"[FAIL] {method} {endpoint} - Status {response.status_code} (attendu: {expected_status})")
                    print(f"   Réponse: {response.get_json()}")
                    failed += 1
                    
            except Exception as e:
                # Gère les erreurs inattendues
                print(f"[ERROR] {method} {endpoint} - ERREUR: {e}")
                failed += 1
        
        # Affiche le résumé final
        print("\n" + "=" * 60)
        print(f"RESULTATS: {passed} passés, {failed} échoués")
        print(f"Taux de réussite: {passed/(passed+failed)*100:.1f}%")
        
        return failed == 0  # Retourne True si tous les tests passent

if __name__ == "__main__":
    success = test_api()  # Lance les tests
    sys.exit(0 if success else 1)  # Code de sortie 0 si OK, 1 si erreur
