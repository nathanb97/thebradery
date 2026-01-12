# Product Intelligence Platform - Rapport Technique

## 🎯 Vue d'ensemble du projet

La Product Intelligence Platform est un système complet développé pour TheBradery permettant d'enrichir automatiquement les descriptions de produits via IA et de proposer une API de recherche avancée. Le projet combine une interface Streamlit pour l'enrichissement et une API FastAPI pour l'interrogation des données.

## 🚀 Démarrage rapide avec Docker

### Prérequis
- Docker et Docker Compose installés
- 8 GB de RAM minimum (pour les modèles Ollama)
- Ports 5432, 8000, 8501 disponibles

### Lancement complet du système

```bash
# 1. Cloner le repository
git clone <repository-url>
cd thebradery

# 2. Créer le fichier d'environnement
cp .env.example .env.docker

# 3. Lancer tous les services
docker-compose up -d

# 4. Vérifier que tous les services sont démarrés
docker-compose ps
```

### Accès aux services

- **API FastAPI** : http://localhost:8000
  - Documentation interactive : http://localhost:8000/docs
  - Health check : http://localhost:8000/health

- **Interface Streamlit** : http://localhost:8501
  - Dashboard d'enrichissement des produits

- **Base de données PostgreSQL** : localhost:5432
  - Base : `thebradery_db`
  - Utilisateur : `user` 
  - Mot de passe : `password`

## 📁 Architecture du projet

```
thebradery/
├── api/                          # API FastAPI
│   ├── main.py                  # Point d'entrée FastAPI
│   ├── routes.py                # Endpoints API
│   ├── services.py              # Logique métier
│   ├── schemas.py               # Modèles Pydantic
│   ├── dependencies.py         # Dépendances DI
│   └── Dockerfile              # Container API
├── front_streamlit/             # Interface Streamlit
│   ├── app.py                  # Application principale
│   ├── pages/                  # Pages Streamlit
│   ├── components/             # Composants réutilisables
│   └── Dockerfile              # Container Streamlit
├── database/                    # Configuration BDD
│   ├── models.py               # Modèles SQLAlchemy
│   ├── database.py             # Configuration DB
│   ├── init_db.py              # Script d'initialisation
│   └── Dockerfile.init         # Container d'initialisation
├── tests/                       # Tests unitaires
│   ├── test_api/               # Tests API
│   └── test_streamlit/         # Tests Streamlit
├── docker-compose.yml          # Orchestration des services
├── requirements.txt            # Dépendances Python
└── README_rapport.md           # Ce fichier
```

## 🛠️ Choix techniques et justifications

### Stack technologique

| Composant | Technologie | Justification |
|-----------|------------|---------------|
| **Backend API** | FastAPI + Uvicorn | Performance élevée, documentation automatique, validation Pydantic |
| **Frontend** | Streamlit | Développement rapide d'interfaces data, parfait pour le prototypage |
| **Base de données** | PostgreSQL | Robustesse, support JSON, index full-text pour la recherche |
| **ORM** | SQLAlchemy | Maturité, migrations, requêtes complexes |
| **Validation** | Pydantic | Validation automatique, sérialisation, documentation |
| **IA/LLM** | Ollama | Modèles locaux gratuits, pas de coûts d'API |
| **Containerisation** | Docker Compose | Isolation, reproductibilité, déploiement simplifié |

### Architecture modulaire

- **Séparation des responsabilités** : API, Frontend et BDD dans des containers séparés
- **Inversion de dépendances** : Services injectés via FastAPI Depends
- **Modèles de données** : Schemas Pydantic pour la validation et documentation
- **Tests unitaires** : Couverture complète avec mocks et fixtures

### Patterns implémentés

1. **Repository Pattern** : Services pour l'accès aux données
2. **DTO Pattern** : Schemas Pydantic pour les transferts
3. **Dependency Injection** : FastAPI Depends pour les dépendances
4. **Error Handling** : HTTPException centralisée
5. **Configuration Management** : Variables d'environnement

## 🔌 Documentation de l'API

### Endpoints disponibles

#### 🏥 Health & Monitoring

- **GET** `/health` - Vérification de l'état du système
- **GET** `/api/v1/stats` - Statistiques du catalogue

#### 🔍 Recherche de produits

- **GET** `/api/v1/products/search` - Recherche avancée avec filtres
  - **Paramètres** :
    - `query` : Terme de recherche textuelle
    - `vendors` : Filtrage par marques
    - `product_types` : Filtrage par types
    - `price_min/max` : Fourchette de prix
    - `has_description` : Produits avec/sans description
    - `sort_by` : Champ de tri
    - `sort_order` : Ordre (asc/desc)
    - `limit/offset` : Pagination

#### 📦 Détails produits

- **GET** `/api/v1/products/{product_id}` - Détail d'un produit

#### 📊 Métadonnées

- **GET** `/api/v1/vendors` - Liste des marques avec compteurs
- **GET** `/api/v1/product-types` - Types de produits avec compteurs

#### 📚 Documentation

- **GET** `/api/v1/examples/search` - Exemples d'utilisation

### Exemples d'utilisation

#### Recherche simple
```bash
curl \"http://localhost:8000/api/v1/products/search?query=dress\"
```

#### Recherche avec filtres
```bash
curl \"http://localhost:8000/api/v1/products/search?vendors=CHANEL&price_min=100&price_max=500&has_description=true\"
```

#### Recherche avec tri et pagination
```bash
curl \"http://localhost:8000/api/v1/products/search?sort_by=gross_amount_exc_tax_product&sort_order=desc&limit=50&offset=100\"
```

## 🧪 Tests unitaires

### Couverture des tests

Le projet inclut une suite de tests complète couvrant :

- **API Endpoints** : Tests d'intégration avec TestClient
- **Services** : Tests unitaires avec mocks SQLAlchemy  
- **Schemas** : Validation Pydantic et sérialisation
- **Fixtures** : Données de test réutilisables

### Exécution des tests

```bash
# Lancer tous les tests
docker-compose run api python -m pytest tests/ -v

# Tests avec couverture
docker-compose run api python -m pytest tests/ --cov=api --cov-report=html

# Tests spécifiques
docker-compose run api python -m pytest tests/test_api/test_routes.py -v
```

### Structure des tests

```
tests/
├── __init__.py
├── conftest.py                 # Fixtures globales
└── test_api/
    ├── __init__.py
    ├── test_routes.py         # Tests endpoints FastAPI
    ├── test_services.py       # Tests couche service
    └── test_schemas.py        # Tests validation Pydantic
```

## 🔄 Pipeline de développement

### Linting et formatage

```bash
# Vérification du code
flake8 --max-line-length=120 --extend-ignore=E203,W503

# Formatage automatique (si configuré)
black api/ --line-length=120
```

### Workflow de développement

1. **Développement local** avec hot-reload
2. **Tests unitaires** avant commit
3. **Linting** automatique
4. **Documentation** auto-générée via Pydantic

## 📈 Fonctionnalités avancées implémentées

### 1. Interface Streamlit enrichie

- **Dashboard analytique** avec visualisations
- **Filtrage avancé** des produits à enrichir
- **Enrichissement IA** avec Ollama
- **Export des résultats** en différents formats
- **Gestion d'erreurs** et retry automatique

### 2. API de recherche performante

- **Recherche full-text** multi-champs
- **Filtrage complexe** combinable
- **Pagination** optimisée
- **Tri dynamique** sur tous les champs
- **Cache** et optimisations de requêtes

### 3. Améliorations suggérées

#### Performance
- **VLLM** pour parallélisation des appels LLM
- **Elasticsearch** pour recherche avancée
- **Cache Redis** pour les requêtes fréquentes

#### Qualité
- **Système de notation** des descriptions générées
- **Validation humaine** avec interface d'approbation
- **A/B testing** des prompts d'enrichissement

#### Monitoring
- **Logs structurés** avec correlation IDs
- **Métriques** de performance et usage
- **Flyway** pour migrations de base de données

#### ML/IA
- **Vision** pour analyse des images produits
- **Embeddings** pour recherche sémantique
- **Fine-tuning** des modèles sur les données métier



## 🎯 Conclusion

Cette implémentation démontre :

- **Architecture moderne** et scalable
- **Best practices** de développement Python
- **Documentation complète** et maintenable
- **Tests exhaustifs** et automatisés
- **Déploiement simplifié** avec Docker

Le système est prêt pour une utilisation en production avec les améliorations suggérées pour la scalabilité et le monitoring.