workspace "Système Web avec Nginx, Flask et FastAPI" "Architecture d'un système web complet avec reverse proxy, frontend Flask, backend FastAPI et base de données MySQL" {

    model {
        # Personnes
        user = person "Utilisateur" "Un utilisateur accédant au site web via un navigateur" "External"

        # Système principal
        webSystem = softwareSystem "Système Web" "Système complet de gestion web" "Internal" {
            # Conteneurs
            nginx = container "Reverse Proxy Nginx" "Serveur web et reverse proxy" "Nginx" "Web Server" {
                routing = component "Routing" "Gestion du routage des requêtes" "Nginx Configuration"
                ssl = component "SSL Termination" "Gestion du chiffrement HTTPS" "OpenSSL"
            }

            flaskApp = container "Site Web Flask" "Application frontend" "Python/Flask" "Web Application" {
                views = component "Vues" "Pages web et templates Jinja2" "Jinja2"
                static = component "Fichiers Statiques" "CSS, JS, images" "Static Files"
                auth = component "Authentification" "Gestion des sessions utilisateurs" "Flask-Login"
            }

            fastApi = container "API FastAPI" "Application backend" "Python/FastAPI" "API Service" {
                endpoints = component "Endpoints" "Points d'accès de l'API" "FastAPI Routes"
                models = component "Modèles" "Modèles de données Pydantic" "Pydantic"
                services = component "Services" "Logique métier" "Python Services"
            }

            mysql = container "Base de données MySQL" "Stockage des données" "MySQL" "Database" {
                tables = component "Tables" "Structure de la base de données" "SQL Schema"
                procedures = component "Procédures stockées" "Logique métier côté base" "SQL Procedures"
            }
        }

        # Relations
        user -> nginx "Accède au site via HTTPS" "HTTPS"
        nginx -> flaskApp "Route les requêtes vers le frontend" "HTTP"
        nginx -> fastApi "Route les requêtes vers l'API" "HTTP"
        flaskApp -> fastApi "Appelle l'API pour récupérer les données" "HTTP"
        fastApi -> mysql "Lit/écrit les données" "MySQL Protocol"
    }

    views {
        # Vue de contexte (C1)
        systemContext webSystem {
            include *
            autoLayout lr
        }

        # Vue des conteneurs (C2)
        container webSystem {
            include *
            autoLayout lr
        }

        # Vue des composants (C3) pour Nginx
        component nginx {
            include *
            autoLayout tb
        }

        # Vue des composants (C3) pour Flask
        component flaskApp {
            include *
            autoLayout tb
        }

        # Vue des composants (C3) pour FastAPI
        component fastApi {
            include *
            autoLayout tb
        }

        # Vue des composants (C3) pour MySQL
        component mysql {
            include *
            autoLayout tb
        }

        # Vue dynamique
        dynamic webSystem {
            user -> nginx "1. Accède au site"
            nginx -> flaskApp "2. Route vers le frontend"
            flaskApp -> fastApi "3. Appelle l'API"
            fastApi -> mysql "4. Interroge la base de données"
            autoLayout lr
        }

    styles {
        element "Person" {
            shape Person
            background #08427b
            color #ffffff
        }
        element "Software System" {
            background #1168bd
            color #ffffff
        }
        element "Container" {
            background #999999
            color #ffffff
        }
        element "Component" {
            background #cccccc
            color #000000
        }
        relationship "Relationship" {
            color #707070
            thickness 2
        }
        relationship "HTTPS" {
            color #2e86c1
            style dashed
        }
        relationship "HTTP" {
            color #27ae60
        }
        relationship "MySQL Protocol" {
            color #e74c3c
        }
    }
    }
}
