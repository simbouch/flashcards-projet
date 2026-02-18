## C5 — Preuve “Développement d’une API REST” (hors `e1/`)

But : **ne pas ré-implémenter** une API dans `e1/`, mais **prouver** que le projet principal contient une API REST conforme (C5).

### Où est l’API dans le repo

- App FastAPI : `backend_service/src/main.py`
  - création `FastAPI(...)`
  - inclusion du router : `app.include_router(api_router, prefix=settings.API_V1_STR)`
- Router principal : `backend_service/src/api/__init__.py`
  - routes groupées : `auth`, `users`, `documents`, `decks`, `flashcards`, `study`

### Préfixe d’API et documentation automatique

- Préfixe : `API_V1_STR = "/api/v1"` (voir `backend_service/src/config.py`)
- OpenAPI JSON : `http://localhost:8002/api/v1/openapi.json`

À capturer (preuves) :

- Screenshot de la page **Swagger/OpenAPI** (FastAPI) montrant :
  - endpoints CRUD
  - schémas de réponses (models)
  - auth (token)

### Exemples d’éléments C5 visibles

- **Endpoints REST** regroupés par domaine (users/documents/decks/flashcards/study)
- **Authentification** (router `auth`)
- **Sécurité** : dépendances `get_current_active_user` / contrôle d’accès
- **Gestion d’erreurs** : HTTP status codes, exceptions
- **Healthcheck** : `GET /health` (voir `backend_service/src/main.py`) + healthcheck docker-compose

### Exécution (pour produire les captures)

1) Lancer les services (ex) : `docker compose up -d`.
2) Vérifier la santé : `http://localhost:8002/health`
3) Ouvrir l’OpenAPI : `http://localhost:8002/api/v1/openapi.json`

### Référence docker-compose

- Service backend : `backend-service` exposé sur `8002:8002` (voir `docker-compose.yml`)
- Healthcheck : `curl -f http://localhost:8002/health`