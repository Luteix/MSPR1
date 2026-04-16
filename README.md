# FutureKawa API

API de gestion des stocks de grains de café vert en architecture 3 couches avec documentation Swagger.

## Architecture

L'API est structurée en 3 couches :

- **Modèles** (`models.py`) : Définition des entités de données avec SQLAlchemy
- **Services** (`services/`) : Logique métier et manipulation des données
- **Contrôleurs** (`controllers/`) : Endpoints HTTP et gestion des requêtes

## Fonctionnalités

- Gestion de la hiérarchie : Pays -> Exploitation -> Entrepôt -> Lot
- Suivi des conditions environnementales (température, humidité)
- Système d'alertes automatiques
- Dashboard avec métriques globales
- Documentation Swagger intégrée

## Installation

### Prérequis

- Python 3.8+
- Base de données (SQLite par défaut, PostgreSQL ou MySQL recommandés pour la production)

### Étapes

1. **Cloner le projet**
   ```bash
   git clone <repository-url>
   cd futurekawa-api
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   ```bash
   # Créer un fichier .env
   cp .env.example .env
   
   # Éditer .env avec votre configuration
   ```

5. **Initialiser la base de données**
   ```bash
   python database.py
   ```

6. **Démarrer l'application**
   ```bash
   python app.py
   ```

## Configuration

### Variables d'environnement

```bash
# Base de données
DB_TYPE=sqlite                    # sqlite, postgresql, mysql
DATABASE_URL=sqlite:///futurekawa.db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=futurekawa
DB_USER=postgres
DB_PASSWORD=password

# Application
SECRET_KEY=votre-secret-key
FLASK_DEBUG=False
PORT=5000
HOST=0.0.0.0

# Logging
DB_ECHO=False
```

### Configuration PostgreSQL (Production)

```bash
DB_TYPE=postgresql
DATABASE_URL=postgresql://user:password@localhost:5432/futurekawa
```

### Configuration MySQL

```bash
DB_TYPE=mysql
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/futurekawa
```

## Documentation

### Swagger UI

Une fois l'application démarrée, accédez à la documentation interactive :

- **URL** : `http://localhost:5000/docs`
- **Format** : OpenAPI 3.0

### Endpoints principaux

#### Dashboard
- `GET /api/dashboard/summary` - Métriques globales et résumé par pays

#### Pays
- `GET /api/pays` - Liste des pays
- `POST /api/pays` - Créer un pays
- `GET /api/pays/{id}` - Détails d'un pays
- `PUT /api/pays/{id}` - Modifier un pays
- `DELETE /api/pays/{id}` - Supprimer un pays

#### Exploitations
- `GET /api/exploitations` - Liste des exploitations
- `POST /api/exploitations` - Créer une exploitation
- `GET /api/exploitations/{id}` - Détails d'une exploitation
- `GET /api/exploitations/{id}/entrepots` - Entrepôts d'une exploitation

#### Entrepôts
- `GET /api/entrepots` - Liste des entrepôts
- `POST /api/entrepots` - Créer un entrepôt
- `GET /api/entrepots/{id}` - Détails d'un entrepôt
- `GET /api/entrepots/{id}/mesures` - Mesures d'un entrepôt
- `POST /api/entrepots/{id}/lots` - Créer un lot dans un entrepôt

#### Lots
- `GET /api/lots/{id}` - Détails d'un lot
- `PUT /api/lots/{id}` - Mettre à jour un lot
- `GET /api/lots/{id}/alertes` - Alertes d'un lot

#### Alertes
- `GET /api/alertes/recent` - Alertes récentes
- `GET /api/alertes` - Toutes les alertes (avec filtres)

## Structure du projet

```
futurekawa-api/
|-- app.py                    # Application Flask principale
|-- models.py                 # Modèles de données SQLAlchemy
|-- database.py               # Configuration de la base de données
|-- requirements.txt          # Dépendances Python
|-- README.md                # Documentation du projet
|-- controllers/             # Couche contrôle
|   |-- __init__.py
|   |-- pays_controller.py
|   |-- exploitation_controller.py
|   |-- entrepot_controller.py
|   |-- lot_controller.py
|   |-- dashboard_controller.py
|-- services/                # Couche service
|   |-- __init__.py
|   |-- pays_service.py
|   |-- exploitation_service.py
|   |-- entrepot_service.py
|   |-- lot_service.py
|   |-- dashboard_service.py
|-- static/                  # Fichiers statiques
|   |-- swagger.json         # Documentation OpenAPI
```

## Développement

### Lancer en mode développement

```bash
export FLASK_DEBUG=True
python app.py
```

### Tests

```bash
# Lancer tous les tests
pytest

# Lancer avec couverture
pytest --cov=.

# Lancer un fichier de test spécifique
pytest tests/test_pays.py
```

### Formatage du code

```bash
# Formatter le code avec Black
black .

# Vérifier le style avec Flake8
flake8 .
```

## Déploiement

### Production avec Gunicorn

```bash
# Installation de Gunicorn
pip install gunicorn

# Lancement en production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Authentification

L'API est conçue pour fonctionner avec une API d'authentification externe :

1. **Token JWT** : Fourni par l'API d'authentification externe
2. **Validation** : Via endpoint `/api/auth/validate`
3. **Headers** : `Authorization: Bearer <token>`

Pour le développement, l'authentification est désactivée.

## Sécurité

- Validation des entrées
- Protection contre les injections SQL
- Gestion des erreurs sécurisée
- CORS configuré
- Rate limiting (à implémenter)

## Monitoring

### Logs

Les logs sont configurés pour afficher les requêtes SQL si `DB_ECHO=True`.

### Health Check

Endpoint de santé : `GET /health`

### Métriques

Intégration avec Sentry possible pour le monitoring en production.

## Support

Pour toute question sur l'implémentation de cette API :

- **Email** : tech@futurekawa.com
- **Documentation** : https://docs.futurekawa.com/api

## Licence

© 2024 FutureKawa - Tous droits réservés.
