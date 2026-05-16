**Data Scientist & Développeur d'application en Intelligence Artificielle**
**RNCP 37827**

**Projet : FlashCards AI**

**Bloc de compétences 2 — E2**
**Développer un système d'intelligence artificielle répondant à un besoin fonctionnel**

**Auteur : KHRIBECH Bouchaib**
**Cohorte : 2023–2025**
**Localisation : Marseille — Nice**

[[À AJOUTER : date de remise + organisme + session (ex : Mai 2026)]]

---

## Remerciements

Je remercie [[À AJOUTER : formateur(s), équipe, structure d'accueil]] pour leur accompagnement tout au long de ce projet.

---

## Sommaire

1. Introduction et contexte
2. Architecture technique
3. Conteneurisation et déploiement
4. Intégration continue et livraison continue (CI/CD)
5. Monitoring et observabilité
6. Gestion de la configuration et des secrets
7. Runbook — démarrage, vérification, arrêt
8. Risques identifiés et mesures prises
9. Conclusion

---

## 1. Introduction et contexte

Le projet **FlashCards AI** est une application web complète qui permet à un utilisateur de déposer un document (PDF ou image) et d'obtenir automatiquement des fiches de révision. Le texte est d'abord extrait par un service OCR, puis un modèle de langage génère des paires question/réponse organisées en decks consultables depuis l'interface.

J'ai conçu ce projet pour couvrir l'ensemble du cycle d'un système IA en production : développement, déploiement, surveillance, et maintenance. Ce rapport E2 décrit comment l'application est construite, packagée, déployée et opérée.

[[À AJOUTER : 4–5 lignes sur votre contexte personnel (période, rôle, objectif pédagogique)]]

---

## 2. Architecture technique

L'application est décomposée en **7 services indépendants** qui communiquent entre eux via HTTP (REST) et via Redis pour la gestion du rate limiting.

| Service | Port | Rôle |
|---|---|---|
| `ocr-service` | 8000 | Extraction de texte (PDF + images) via PyMuPDF / Tesseract |
| `llm-service` | 8001 | Génération de flashcards via un LLM (Qwen 2.5 0.5B Instruct) |
| `backend-service` | 8002 | API REST principale (FastAPI) : auth, documents, decks, flashcards |
| `frontend-service` | 8080 | Interface Vue.js servie par Nginx |
| `db-service` | — | Module SQLite partagé (SQLAlchemy) |
| `redis` | 6379 | Rate limiting + cache |
| `mlflow-ocr` / `mlflow-llm` | 5000 / 5001 | Suivi des expériences ML |

Le flux principal est le suivant :

1. L'utilisateur upload un document depuis le frontend (port 8080).
2. Le backend (8002) reçoit le fichier, l'enregistre dans la base SQLite et lance un traitement en arrière-plan.
3. Le backend appelle `ocr-service` (8000) pour extraire le texte.
4. Le backend appelle `llm-service` (8001) pour générer les flashcards.
5. Les flashcards sont stockées en base et visibles immédiatement dans l'interface.

[[À AJOUTER : capture d'écran du schéma d'architecture ou diagramme de flux]]

Chaque service est **isolé** : il peut être redémarré ou mis à jour indépendamment sans couper les autres.

---

## 3. Conteneurisation et déploiement

### 3.1 Dockerfiles

Chaque service possède son propre `Dockerfile`. Voici les grandes lignes de chaque image :

- **`ocr-service/Dockerfile`** : image Python 3.10, installe PyMuPDF, Pillow, Tesseract OCR, FastAPI/Uvicorn. Le point d'entrée est `uvicorn src.main:app`.
- **`llm-service/Dockerfile`** : image Python 3.10, installe transformers, torch (CPU), FastAPI. Le modèle est téléchargé au premier démarrage et mis en cache dans un volume Docker (`llm_models`).
- **`backend-service/Dockerfile`** : image Python 3.10, installe FastAPI, SQLAlchemy, httpx, Alembic. Montage du dossier `db_module` pour partager les modèles de données.
- **`frontend-service/Dockerfile`** : build multi-stage — Node 16 compile le projet Vue.js (`npm run build`), puis l'image finale Nginx copie le résultat dans `/usr/share/nginx/html`.
- **`db-service/Dockerfile`** : image légère qui maintient la base SQLite en vie via un volume persistant.

### 3.2 Docker Compose

Le fichier `docker-compose.yml` à la racine du projet orchestre tous les services. Points importants :

- Les services **dépendent** les uns des autres via `depends_on` (ex : `backend-service` attend `ocr-service`, `llm-service`, `db-service` et `redis`).
- Un **healthcheck** est configuré sur chaque service pour détecter les démarrages lents (notamment le LLM qui peut prendre 1–2 minutes à charger le modèle).
- Les logs de chaque service sont stockés dans des **volumes nommés** (`ocr_logs`, `llm_logs`, `backend_logs`, etc.) pour survivre aux redémarrages.
- La base de données est dans le volume `db_data` monté à la fois par `db-service` et `backend-service`.
- Les uploads utilisateur sont dans `./uploads` monté directement dans `backend-service`.

```yaml
# Extrait docker-compose.yml — healthcheck backend
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

### 3.3 Monitoring complémentaire (docker-compose.monitoring.yml)

Un deuxième fichier `docker-compose.monitoring.yml` démarre la stack d'observabilité :

- `prometheus` : collecte les métriques de chaque service
- `grafana` : dashboards visuels (tableaux de bord pré-chargés)
- `redis-exporter` : expose les métriques Redis pour Prometheus

[[À AJOUTER : capture d'écran `docker compose ps` montrant tous les containers "healthy"]]

---

## 4. Intégration continue et livraison continue (CI/CD)

### 4.1 Pipeline GitHub Actions

J'ai mis en place un pipeline CI/CD sur la branche `dev` via GitHub Actions (fichier `.github/workflows/ci.yml`). À chaque push ou pull request, le pipeline exécute automatiquement :

1. **Lint Python** : `flake8` sur les fichiers backend pour détecter les erreurs de style ou les imports inutiles.
2. **Tests backend** : `pytest` sur `backend_service/tests/` et `db_module/tests/`.
3. **Build frontend** : `npm install && npm run build` pour vérifier que le projet Vue.js compile sans erreur.
4. **Lint frontend** : `npm run lint` via ESLint pour détecter les erreurs JavaScript/Vue.

Le pipeline est pensé comme un filet de sécurité : si un test casse ou si le build frontend échoue, le push est signalé comme en erreur et je peux corriger avant que le problème arrive en production.

[[À AJOUTER : capture d'écran GitHub Actions — run "green" sur la branche dev]]

### 4.2 Stratégie de branches

Tout le développement se fait sur la branche `dev`. Les commits sont atomiques : chaque correction ou fonctionnalité fait l'objet d'un commit séparé avec un message explicite (ex : `Fix flashcard generation pipeline`, `Auto-scale flashcards per document; UI polish + stats`).

Les tags de version ou les merges vers `main` sont utilisés pour marquer les jalons importants (livrable, démonstration).

---

## 5. Monitoring et observabilité

### 5.1 Métriques Prometheus

Chaque service expose un endpoint `/metrics` au format Prometheus. Les métriques collectées incluent :

- **OCR service** : nombre de requêtes, durée de traitement, taux d'erreur.
- **LLM service** : nombre de générations, latence par requête (`llm_generation_duration`), compteur de requêtes par statut (`llm_generation_requests_total`).
- **Backend service** : métriques FastAPI standard (requêtes, durées, codes HTTP).
- **Redis** : métriques mémoire, connexions actives (via `redis-exporter`).

La configuration de scraping est dans `monitoring/prometheus.yml` :

```yaml
# Extrait monitoring/prometheus.yml
scrape_configs:
  - job_name: 'ocr-service'
    static_configs:
      - targets: ['ocr-service:8000']
  - job_name: 'llm-service'
    static_configs:
      - targets: ['llm-service:8001']
  - job_name: 'backend-service'
    static_configs:
      - targets: ['backend-service:8002']
```

### 5.2 Dashboards Grafana

Quatre dashboards Grafana sont pré-chargés automatiquement depuis `monitoring/grafana/dashboards/` :

- **`flashcards-overview.json`** : vue globale de l'application (requêtes totales, taux d'erreur, état des services).
- **`backend-service.json`** : performances API (temps de réponse par endpoint, authentifications, uploads).
- **`llm-service.json`** : métriques IA (latence de génération, nombre de flashcards générées, cold start).
- **`ocr-service.json`** : métriques OCR (taille des documents traités, durée d'extraction).

[[À AJOUTER : capture d'écran du dashboard Grafana "flashcards-overview" avec données réelles]]

Les dashboards sont provisionnés via `monitoring/grafana/provisioning/dashboards/` et `monitoring/grafana/provisioning/datasources/`. Grafana démarre directement connecté à Prometheus, sans configuration manuelle.

### 5.3 MLflow — suivi des expériences IA

MLflow est utilisé pour tracer les expériences liées aux services OCR et LLM :

- `mlflow-ocr` (port 5000) : trace chaque appel OCR (durée, nombre de caractères extraits, type de fichier).
- `mlflow-llm` (port 5001) : trace chaque génération de flashcards (modèle utilisé, nombre de cartes, latence).

Cela permet de comparer les performances entre différents modèles et de garder une trace historique des runs pour les livrables RNCP.

[[À AJOUTER : capture d'écran interface MLflow avec une liste de runs (llm-service)]]

### 5.4 Alerting

Des règles d'alerte sont définies dans `monitoring/alert_rules.yml` et `monitoring/alertmanager.yml`. Elles couvrent par exemple :
- Service indisponible (health check en échec)
- Temps de réponse du LLM supérieur à un seuil
- Taux d'erreur élevé sur le backend

---

## 6. Gestion de la configuration et des secrets

Toute la configuration de l'application passe par des **variables d'environnement** définies dans `docker-compose.yml`. Cela permet de changer le comportement sans modifier le code.

Exemples importants :

| Variable | Valeur par défaut | Rôle |
|---|---|---|
| `LLM_MODEL_NAME` | `Qwen/Qwen2.5-0.5B-Instruct` | Modèle LLM utilisé |
| `JWT_SECRET_KEY` | `supersecretkey` (à remplacer) | Signature des tokens JWT |
| `DATABASE_URL` | `sqlite:///./data/flashcards.db` | Base de données |
| `DEFAULT_NUM_CARDS_PER_DOCUMENT` | `5` (minimum) | Nombre minimal de flashcards |
| `INITIAL_ADMIN_USERNAME` | *(vide)* | Bootstrap admin au démarrage |

Les secrets sensibles (JWT, mot de passe admin initial) ne sont **pas commités en clair** dans le dépôt git. Ils doivent être définis dans un fichier `.env` local (ignoré par `.gitignore`).

Pour changer de modèle LLM sans recompiler l'image :

```powershell
$env:LLM_MODEL_NAME='Qwen/Qwen2.5-0.5B-Instruct'
docker compose up -d --force-recreate llm-service
```

---

## 7. Runbook — démarrage, vérification, arrêt

### Démarrer l'application

```bash
# Démarrer tous les services principaux
docker compose up -d

# Démarrer aussi le monitoring (Prometheus + Grafana)
docker compose -f docker-compose.monitoring.yml up -d
```

### Vérifier l'état des services

```bash
# Voir l'état de tous les containers
docker compose ps

# Voir les logs en temps réel
docker compose logs -f backend-service
docker compose logs -f llm-service

# Tester les endpoints de santé
curl http://localhost:8002/health   # backend
curl http://localhost:8000/health   # OCR
curl http://localhost:8001/health   # LLM
```

Le LLM démarre de façon **non bloquante** : le service répond `/health` immédiatement mais le modèle se charge en arrière-plan. L'endpoint `/ready` indique si le modèle est prêt à générer.

### Relancer un service après mise à jour

```bash
docker compose build backend-service
docker compose up -d --force-recreate backend-service
```

### Arrêter proprement

```bash
docker compose down
```

Les volumes (base de données, modèles LLM, logs) sont conservés. Pour tout supprimer :

```bash
docker compose down -v
```

[[À AJOUTER : capture d'écran terminal montrant `docker compose ps` avec services "healthy"]]

---

## 8. Risques identifiés et mesures prises

| Risque | Impact | Mesure |
|---|---|---|
| Cold start du LLM (1–2 min) | Premières requêtes lentes | Startup non bloquant + healthcheck avec `start_period: 120s` |
| Out of memory (modèle trop grand) | Container tué (exit 137) | Limite mémoire Docker à 4G + choix d'un modèle léger (0.5B) |
| Fichiers trop grands uploadés | Saturation disque/RAM | Limite à 10 MB enforced en streaming côté backend (HTTP 413) |
| Clé JWT trop faible | Compromission des tokens | Variable d'environnement + warning dans le code |
| Perte des données si volume supprimé | Perte de la base SQLite | Volume `db_data` nommé + backup manuel recommandé |
| Rate limiting LLM dépassé | Erreur 429 | Redis-based limiter (5 req/min par IP) sur l'endpoint `/generate` |

---

## 9. Conclusion

Ce projet m'a permis de mettre en pratique toutes les étapes du cycle de vie d'une application IA : du développement des microservices individuels à leur déploiement via Docker Compose, en passant par la mise en place d'une CI/CD fonctionnelle et d'un système de monitoring complet.

Le choix d'une architecture microservices m'a obligé à réfléchir aux contrats entre services (API REST bien définies, healthchecks, gestion des timeouts), à la gestion des configurations par environnement, et à l'observabilité du système en production.

Les points que j'améliorerais avec plus de temps : migration de SQLite vers PostgreSQL pour un vrai environnement de production, mise en place d'un HTTPS/TLS, et ajout d'alertes Alertmanager avec notification par email ou Slack.

[[À AJOUTER : 3–4 lignes personnelles sur ce que ce projet vous a appris, les difficultés rencontrées]]

---

*Fin du rapport E2 — KHRIBECH Bouchaib*

