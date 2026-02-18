**Data Scientist & Développeur d’application en Intelligence Artificielle**  
**RNCP 37827**

**Projet : Flashcards AI**

**Bloc de compétences 1 — E1**  
**Réaliser la collecte, le stockage et la mise à disposition des données d’un projet en intelligence artificielle**

**Auteur : KHRIBECH Bouchaib**  
**Cohorte : 2023–2025**  
**Localisation : Marseille — Nice**

[[À AJOUTER : date de remise + organisme/centre + intitulé exact de la session (ex : Avril 2025)]]

---

## Remerciements

Je tiens à remercier [[À AJOUTER : personne(s) / équipe / formateur(s) / structure d’accueil]] pour [[À AJOUTER : 2–3 lignes : accompagnement, retours, mise à disposition de ressources, etc.]].

[[TOC]]

## Compétences

### A1. Collecte de Données

**C1.** Automatiser l’extraction de données depuis un service web, une page web (scraping), un fichier de données, une base de données et un système big data en programmant le script adapté afin de pérenniser la collecte des données nécessaires au projet.

**C2.** Développer des requêtes de type SQL d’extraction des données depuis un système de gestion de base de données et un système big data en appliquant le langage de requête propre au système afin de préparer la collecte des données.

**C3.** Développer des règles d'agrégation de données issues de différentes sources en programmant, sous forme de script, la suppression des entrées corrompues et en programmant l’homogénéisation des formats des données afin de préparer le stockage du jeu de données final.

### A2. Mise à disposition des Données

**C4.** Créer une base de données dans le respect du RGPD en élaborant les modèles conceptuels et physiques des données à partir des données préparées et en programmant leur import afin de stocker le jeu de données du projet.

**C5.** Développer une API mettant à disposition le jeu de données en utilisant l’architecture REST afin de permettre l’exploitation du jeu de données par les autres composants du projet.

---

## Introduction

### Contexte du projet

Le projet **Flashcards AI** est une application “de bout en bout” destinée à faciliter l’apprentissage : l’utilisateur dépose un document, le texte est extrait, puis des *flashcards* sont générées et organisées en *decks* afin de réviser via une interface web.

Dans le cadre du livrable **E1**, l’objectif n’est pas de détailler tout le projet IA (OCR/LLM), mais de démontrer une chaîne **complète et reproductible** de **collecte**, **stockage**, **préparation** et **mise à disposition** de données.

[[À AJOUTER : 5–8 lignes (contexte personnel : période, rôle, objectifs, lien avec l’IA et l’apprentissage)]]

### Périmètre et organisation du travail

Afin de ne pas perturber l’application principale, le travail E1 est **isolé** dans le dossier `e1/` (pipeline, tests, documentation). Le projet principal est néanmoins utilisé comme preuve “réaliste” pour la partie **API REST** et pour illustrer l’exploitation d’une base relationnelle.

Points clés :

- Aucun changement dans les services existants (backend API, OCR, LLM, base de production).
- Le pipeline E1 est exécutable en une commande : `python e1/run_all.py`.
- Les paramètres (sources, limites, chemins) sont centralisés dans `e1/config/config.json`.

### Architecture applicative (vue d’ensemble)

L’application est dockerisée (voir `docker-compose.yml`) et s’articule autour de :

- **Frontend** : application web (Vue).
- **Backend** : API REST (FastAPI) exposée sur `http://localhost:8002`.
- **Services OCR / LLM** : traitement de document et génération de flashcards (contexte projet).
- **Redis** : support au *rate limiting*.

[[À AJOUTER : capture de `docker-compose.yml` (liste des services + ports)]]

### Bases de données utilisées

Pour ce livrable, trois bases SQLite sont à distinguer (avec des objectifs différents) :

1) **Base principale du projet** : `data/flashcards.db`  
   - utilisée par l’API FastAPI (via `DATABASE_URL=sqlite:///./data/flashcards.db`).
   - schéma documenté dans `docs/database_schema.md`, `docs/database_mcd.md`, `docs/database_mpd.md`.

2) **Base “externe / staging” E1** : `e1/data/wikipedia_external.db`  
   - dédiée au stockage *brut* de données publiques Wikipedia (collecte API et/ou dump).  
   - elle sert de source SQL “intermédiaire” pour l’ETL vers le dataset final.

3) **Base dataset E1 (isolée)** : `e1/data/flashcards2.db`  
   - utilisée pour unifier les sources, nettoyer, tracer les exécutions et exporter un dataset.
   - ce choix permet de **ne pas modifier** la base principale du projet.

[[À AJOUTER : 1 capture d’une table de `flashcards.db` (ex : `users` ou `documents`) + 1 capture de `wikipedia_external.db`]]

### Vue d’ensemble du flux E1

Le flux suit une logique *collecte → staging → ETL → nettoyage → export* :

1. Collecte (service web, scraping, fichiers, option Big Data via Spark)
2. Staging Wikipedia (`wikipedia_external.db`)
3. ETL vers `flashcards2.db.raw_items`
4. Nettoyage vers `flashcards2.db.clean_items`
5. Exports CSV et JSONL (`e1/data/exports/`)

```mermaid
flowchart LR
  A[Sources publiques] -->|Wikipedia API| B[(wikipedia_external.db)]
  A -->|Dump titles (Spark)| B
  A -->|CSV/JSON/XML| C[(flashcards2.db)]
  A -->|Web scraping| C
  B -->|ETL| C
  C -->|Cleaning| D[clean_items]
  D -->|Export| E[CSV + JSONL]
```

[[À AJOUTER : image du dataflow (export Mermaid en PNG ou capture d’écran)]]

---

## A1. Collecte de Données

### C1. Extraction de Données

#### Identifier les contraintes techniques des sources de données cibles

**Service web (Wikipedia API, HTTP/JSON)**

- **Qualité/variabilité du contenu** : certaines pages peuvent retourner un contenu court ou non pertinent (ex. pages d’homonymie).
- **Contraintes réseau** : timeouts, erreurs transitoires, encodage.
- **Bonnes pratiques** : identification via `User-Agent` et paramétrage des délais (voir `wikipedia_api.user_agent` et `timeout_seconds` dans `e1/config/config.json`).

**Web scraping (HTML non structuré)**

- **Bruit HTML** : exclusion des balises non textuelles (script/style/noscript) et extraction du texte utile (voir `e1/src/e1_pipeline/web_scraping.py`).
- **Risque de fragments** : application d’un seuil minimal de longueur avant insertion dans la base finale.

**Fichiers (CSV/JSON/XML)**

- **Hétérogénéité** : schémas différents selon les formats ; standardisation vers un schéma commun (table `raw_items`).
- **Encodage** : lecture en UTF‑8 et normalisation des retours à la ligne.

**Big Data (dump Wikimedia)**

- **Volumétrie** : traitement via Spark (API DataFrame), exécutable en local.

- **Prérequis/temps** : étape activable selon le contexte ; par défaut, le téléchargement automatique est désactivé pour conserver une exécution reproductible hors-ligne.


#### Définir les spécifications techniques du processus d'extraction

L’implémentation E1 vise à couvrir plusieurs modalités d’extraction (service web, scraping, fichiers, option Big Data), tout en conservant un pipeline **simple**, **traçable** et **reproductible**.

L’exécution est pilotée par :

- Script d’orchestration : `e1/run_all.py`
- Configuration centralisée : `e1/config/config.json`

Spécifications de stockage (cible E1) :

- **Standard de stockage E1** : toutes les sources convergent vers `flashcards2.db.raw_items` avec les champs `source`, `external_id`, `raw_text`, `raw_meta_json`, `fetched_at`, `content_hash`.
- **Déduplication & idempotence** : `content_hash` est unique (SHA256) ; une relance du pipeline n’insère pas de doublons.
- **Traçabilité** : chaque étape enregistre une exécution dans `flashcards2.db.runs` (horodatage, statut, paramètres, message d’erreur le cas échéant).


#### Extraction des données

##### Construire des requêtes HTTP pour l'accès aux données web

- Source : MediaWiki API (`https://en.wikipedia.org/w/api.php`)
- Objectif : extraire rapidement des contenus textuels publics sur des thèmes utiles pour générer des flashcards.
- Paramètres (config) :
  - `keywords` (ex : *machine learning*, *neural network*)
  - `search_limit` (limite de résultats par mot-clé)
  - `user_agent`, `timeout_seconds`
- Implémentation : `e1/src/e1_pipeline/wikipedia_api.py`

**Spécification d’appels (extraits)**

- Recherche : `action=query&list=search&srsearch=<keyword>&srlimit=<limit>&format=json`
- Récupération du texte : `action=query&prop=extracts&explaintext=1&exsectionformat=plain&pageids=<page_id>&format=json`

**Stockage (staging)**

Les résultats sont stockés dans la base de staging `e1/data/wikipedia_external.db`, table `wiki_pages_raw`.

Champs principaux : `run_id`, `title`, `page_id`, `url`, `content_raw`, `fetched_at`, `content_hash`.

La colonne `content_hash` est contrainte en `UNIQUE` afin de garantir la **déduplication** et l’**idempotence** (relancer le pipeline ne duplique pas les données).

[[À AJOUTER : capture de `wiki_pages_raw` (2–3 lignes) + exemple de contenu récupéré]]


##### (Option) Extraire des données depuis un système Big Data

- Source : dump officiel Wikimedia : `enwiki-latest-all-titles-in-ns0.gz`
- Objectif : démontrer la capacité à manipuler une source de grande volumétrie avec un moteur Big Data (Spark), même en environnement local.
- Implémentation : `e1/src/e1_pipeline/wikimedia_spark.py`

**Traitement**

Le pipeline lit le dump de titres, calcule des métadonnées simples (ex : longueur du titre) et stocke le résultat dans `wikipedia_external.db`, table `wiki_titles_raw`.

**Exécution optionnelle**

Par défaut `auto_download=false` (voir `e1/config/config.json`) : l’étape peut être activée selon le contexte de démonstration. Cette approche garde la commande `python e1/run_all.py` exécutable même sans téléchargement.

[[À AJOUTER : (optionnel) capture de l’exécution Spark (logs) + table `wiki_titles_raw` si l’étape est activée]]


##### Mettre en œuvre des techniques de web scraping pour l'extraction de données

- Source : pages web publiques (ex : `https://en.wikipedia.org/wiki/Machine_learning`)
- Objectif : démontrer l’extraction de texte à partir d’un HTML non structuré.
- Paramètres (config) : `seed_urls`, `timeout_seconds`
- Implémentation : `e1/src/e1_pipeline/web_scraping.py`

**Principe** :

1. Téléchargement HTML (stdlib `urllib`)
2. Extraction de texte (stdlib `html.parser`)
3. Insertion dans `flashcards2.db.raw_items` avec `source = web_scrape`

[[À AJOUTER : capture d’une page source + extrait texte avant/après extraction]]


##### Traiter différents formats de fichiers de données (CSV, JSON, XML, etc.)

- Source : répertoire `e1/data/samples/`
- Objectif : ingestion multi-format et standardisation du schéma.
- Implémentation : `e1/src/e1_pipeline/file_ingest.py`

Chaque fichier est parsé (stdlib) et converti vers un modèle unifié dans `flashcards2.db.raw_items`.

[[À AJOUTER : capture du dossier `e1/data/samples/` + 1 exemple d’item ingéré dans `raw_items`]]


##### Se connecter à des bases de données relationnelles et NoSQL

Ce projet met en œuvre :

- **Base relationnelle (SQLite)** :
  - côté application : `data/flashcards.db` (accès via SQLAlchemy et dépendance FastAPI `get_db()` dans `db_module/database.py`).
  - côté E1 : `e1/data/wikipedia_external.db` et `e1/data/flashcards2.db` (accès direct via `sqlite3` pour garder un pipeline autonome).

- **Base NoSQL (Redis)** : utilisée pour le *rate limiting* (SlowAPI) dans l’API backend, configurée via `REDIS_URL` et vérifiée au démarrage (voir `backend_service/src/main.py` et la section Redis dans `docker-compose.yml`).

Les chemins et preuves à capturer (Swagger / OpenAPI, endpoints, auth) sont décrits dans : `e1/docs/c5_api_proof.md`.

[[À AJOUTER : capture Swagger UI + 1 appel login + 1 appel protégé (ex: GET /documents)]]


##### Filtrer et parser les données extraites

Les données brutes sont filtrées et parsées de manière reproductible avant insertion dans le schéma cible :

- **Parsing** : conversion JSON (Wikipedia API), parsing HTML (scraping), parsing CSV/JSON/XML (fichiers) vers un format commun.
- **Filtrage** : suppression des contenus trop courts / non informatifs ; exclusion de balises HTML non textuelles (`script`, `style`, etc.).
- **Déduplication** : calcul d’un `content_hash` (SHA256) et contrainte `UNIQUE` pour rendre la relance idempotente.


#### Consolidation : ETL staging → dataset final

Après la collecte Wikipedia (API et/ou dump), une étape d’ETL copie les données de `wikipedia_external.db` vers la base finale `flashcards2.db` afin d’unifier toutes les sources.

- Module : `e1/src/e1_pipeline/wikipedia_etl.py`
- Cible : `flashcards2.db.raw_items` (schéma commun multi-sources)
- Principe :
  - transformation vers un format commun (`source`, `external_id`, `raw_text`, `raw_meta_json`, `content_hash`)
  - déduplication par contrainte `content_hash UNIQUE`

---

### C2. Requêtes SQL

#### Concevoir et développer des requêtes SQL performantes pour extraire des données de bases de données relationnelles

Deux contextes sont complémentaires :

1) **Projet principal** : l’API manipule `data/flashcards.db` via l’ORM SQLAlchemy (couche `db_module/`).
2) **Pipeline E1** : les bases SQLite E1 sont créées et requêtées directement (stdlib `sqlite3`) pour garder un pipeline autonome.

Exemples de requêtes SQL d’audit/extraction (E1) :

```sql
-- Volume par source dans le dataset brut
SELECT source, COUNT(*) AS n
FROM raw_items
GROUP BY source
ORDER BY n DESC;

-- Vérification de déduplication (doit retourner 0)
SELECT COUNT(*)
FROM (
  SELECT content_hash, COUNT(*) AS c
  FROM raw_items
  GROUP BY content_hash
  HAVING c > 1
);

-- Top éléments par score qualité
SELECT id, quality_score
FROM clean_items
ORDER BY quality_score DESC
LIMIT 10;
```

La déduplication est rendue robuste par la contrainte `content_hash UNIQUE` et l’utilisation d’inserts idempotents (pattern `INSERT OR IGNORE`).

[[À AJOUTER : capture de 2 requêtes SQL exécutées (outil SQLite / console) + résultats (volumétrie, doublons=0)]]

[[À AJOUTER : preuve côté API (capture d’un endpoint CRUD + mention ORM/SQLAlchemy + table concernée dans `flashcards.db`)]]

#### Documenter de manière claire et concise les requêtes SQL développées

Les requêtes SQL sont :

- commentées directement (objectif, tables, hypothèses),
- regroupées dans le rapport (extraits ci-dessus) et/ou dans les annexes,
- reliées à des preuves d’exécution (captures de résultats) afin d’assurer la traçabilité.


---

### C3. Nettoyage et Agrégation de Données

#### Définir les spécifications techniques pour l’agrégation et le nettoyage des données

Spécifications appliquées (toutes sources confondues) :

- **Service web / scraping** : nettoyage du bruit (HTML), normalisation des espaces et contrôle de longueur.
- **Fichiers** : harmonisation des champs vers un schéma unique (mêmes colonnes dans `raw_items`).
- **Base de données** : conservation d’un identifiant externe si disponible (`external_id`) + métadonnées JSON (`raw_meta_json`).
- **Système Big Data** : résultats Spark ramenés à un format tabulaire simple puis stockés en SQLite (staging).

#### Développer un processus automatisé pour l’agrégation des données provenant de différentes sources

L’agrégation est automatisée dans `python e1/run_all.py` : chaque source alimente `raw_items`, puis une étape ETL consolide le staging Wikipedia vers la base dataset finale.

#### Identifier et supprimer les entrées de données corrompues ou erronées

La collecte multi-source produit des données hétérogènes (formats, bruit HTML, longueurs variables). Une étape de nettoyage est donc appliquée pour construire un dataset exploitable.


#### Objectifs

- Normaliser le texte (espaces, caractères parasites)
- Filtrer les entrées peu informatives
- Dédupliquer strictement
- Calculer un score de qualité simple, mesurable et reproductible

#### Homogénéiser les formats de données pour assurer la cohérence

L’homogénéisation est assurée par :

- un schéma commun (`raw_items` puis `clean_items`),
- un texte nettoyé stocké dans `clean_text`,
- des métadonnées normalisées au format JSON (`raw_meta_json`).

#### Versionner et documenter le code source du processus de nettoyage

Le code du pipeline (dont le nettoyage) est versionné dans le dépôt, isolé sous `e1/`, et documenté par :

- des doc techniques (`e1/docs/`),
- des tests automatisés (`e1/tests/`).


#### Implémentation

- Module : `e1/src/e1_pipeline/cleaning.py`
- Entrée : table `flashcards2.db.raw_items`
- Sortie : table `flashcards2.db.clean_items`

La table `clean_items` contient notamment : `clean_text`, `quality_score`, `language`, `content_hash`.


#### Traçabilité (audit)

Chaque étape du pipeline écrit une trace dans la table `runs` (présente dans les deux bases) :

- `run_id` (UUID), `source`, `started_at`, `ended_at`, `status`
- `params_json` (paramètres de l’étape)

Cette traçabilité facilite :

- l’audit d’une exécution,
- l’explication d’un export,
- la reproductibilité.


#### Tests et validation

La qualité du pipeline a été vérifiée par une suite de tests automatisés Pytest dans `e1/tests/`.

Commande :

```bash
python -m pytest -c e1/pytest.ini -q e1/tests
```

Les tests couvrent : création du schéma, extraction (avec HTTP mocké), ingestion fichiers, étape Spark (skippable), nettoyage et export.

[[À AJOUTER : capture du terminal montrant “8 passed” + date/heure d’exécution]]

### Résumé de la stack technique (collecte & préparation)

- Python (stdlib) : `urllib`, `json`, `csv`, `xml.etree`, `html.parser`, `sqlite3`, `hashlib`, `datetime`
- SQLite : bases `wikipedia_external.db` (staging) et `flashcards2.db` (dataset)
- PySpark : traitement optionnel du dump Wikimedia
- Tests : `pytest` (dossier `e1/tests/`)

---

## A2. Mise à disposition des Données

### C4. Création de la Base de Données

#### Définir les spécifications techniques de la base de données

Les bases de données sont de type relationnel (SQLite) et doivent permettre :

- stockage structuré (contraintes, index, clés uniques),
- traçabilité (table `runs`),
- reproductibilité (création de schéma automatisée),
- export du dataset final.

#### Modéliser la structure des données à l’aide de la méthode Merise

**Description des données utiles** : textes sources (bruts), métadonnées associées, informations de traçabilité d’exécution, dataset exporté.

**Modèle Conceptuel des Données (MCD)**

- *Définition* : représentation conceptuelle (métier) des entités et associations, indépendante du SGBD.
- *MCD (réalisation)* : voir `e1/docs/merise.md`.

**Modèle Logique des Données (MLD)**

- *Définition* : traduction du MCD vers un modèle relationnel (tables, attributs, clés), encore indépendant de l’implémentation physique.
- *Optimisation de la mémoire* : limitation des champs, usage de clés/contraintes utiles, JSON pour métadonnées non strictes.
- *MLD (réalisation)* : voir `e1/docs/merise.md`.

**Modèle Physique des Données (MPD)**

- *Définition* : implémentation effective dans un SGBD (types, index, contraintes, scripts).
- *MPD (réalisation)* : voir `e1/docs/merise.md` et `e1/src/e1_pipeline/db_init.py`.

**Tests**

- validation de la création de schéma et des contraintes (tests automatisés `e1/tests/`).

#### Sélectionner un système de gestion de base de données (SGBD)

Le choix de **SQLite** est adapté au livrable : simple à déployer, portable (fichier), suffisant pour démontrer modélisation, contraintes, requêtes SQL et intégration API.

#### Créer la base de données et implémenter le schéma de données

- Schémas E1 : initialisés par `e1/src/e1_pipeline/db_init.py` (création des tables de staging et du dataset).
- Schéma applicatif : initialisé côté backend via `db_module/database.py:init_db()`.

#### Documenter le processus d’installation et le script d’import des données

- Exécution complète du pipeline : `python e1/run_all.py`.
- Import/chargement : la collecte alimente `wikipedia_external.db`, puis l’ETL alimente `flashcards2.db`, puis export (CSV/JSONL).

#### Mettre en œuvre les mesures nécessaires pour assurer la conformité au RGPD

La démarche RGPD (finalité, minimisation, conservation, sécurité) est documentée dans `e1/docs/rgpd.md`.

#### Base relationnelle du projet (exemple principal) : `flashcards.db`

Le projet Flashcards AI s’appuie sur une base relationnelle SQLite : `data/flashcards.db` (configurée côté backend via `DATABASE_URL=sqlite:///./data/flashcards.db`). Cette base illustre un cas d’usage “réaliste” : authentification, gestion de contenus, traçabilité des usages.

Documentation et schémas :

- Diagramme : `docs/database_schema.md`
- Modélisation : `docs/database_mcd.md` et `docs/database_mpd.md`
- Modèles ORM : `db_module/models.py`

Le schéma structure notamment :

- **Utilisateurs & sécurité** : table `users` (mot de passe stocké sous forme `hashed_password`) et `refresh_tokens`.
- **Documents** : `documents` + `extracted_texts` (texte extrait, utilisé ensuite pour générer des flashcards).
- **Flashcards** : `decks` et `flashcards`.
- **Suivi d’apprentissage** : `study_sessions` et `study_records`.

[[À AJOUTER : 1 capture du diagramme + 1 capture d’un extrait de tables (`users`, `documents`, `decks`) dans un outil SQLite]]

#### Bases E1 : staging externe et base dataset isolée

Pour l’E1, j’ai volontairement séparé le traitement dans deux bases dédiées, afin de **ne pas modifier** la base principale `flashcards.db` :

- `e1/data/wikipedia_external.db` : base *externe/staging* contenant la collecte brute Wikipedia (audit et relecture faciles).
- `e1/data/flashcards2.db` : base *dataset* qui unifie les sources, applique le nettoyage et référence les exports.

Le schéma (Merise + MPD) est documenté dans `e1/docs/merise.md` et implémenté dans `e1/src/e1_pipeline/db_init.py`.

[[À AJOUTER : images MCD/MLD/MPD E1 + courte légende]]

#### RGPD : minimisation, conservation et sécurité

Le périmètre E1 manipule majoritairement des textes publics. Une note RGPD (finalité, minimisation, conservation, sécurité) est fournie dans `e1/docs/rgpd.md`.

[[À AJOUTER : encadré “analyse RGPD” (finalité, base légale, durée, droits) + rappel ‘données publiques / pas de données sensibles’]]

Mesures appliquées dans ce livrable :

- volumétrie volontairement limitée (paramètres dans `e1/config/config.json`)
- stockage local (artefacts dans `e1/data/`)
- suppression simple : effacer `e1/data/*.db` et `e1/data/exports/*`
- exclusion Git des artefacts (`e1/.gitignore`)

---

### C5. Développement d'API

#### Définir les spécifications techniques de l’API (technologie, contraintes, architecture et documentation)

L’API du projet principal est développée en **FastAPI** (architecture REST) avec :

- versionnement via préfixe `/api/v1`,
- validation de schémas via **Pydantic** (dans `db_module/schemas.py`),
- documentation automatique **OpenAPI / Swagger**.

#### Configurer les accès aux données de la base de données

L’accès aux données est configuré via :

- la dépendance `get_db()` (session SQLAlchemy) depuis `db_module/database.py`,
- des opérations CRUD centralisées (`db_module/crud.py`),
- des règles d’accès basées sur l’utilisateur courant (JWT) et le rôle (`user` / `admin`).

Exemples de règles :

- endpoints publics : inscription / connexion,
- endpoints protégés : ressources utilisateur (documents, decks, flashcards),
- endpoints administrateur : accès étendu (ex : listing utilisateurs), avec contrôle `is_admin`.

#### Développer les endpoints de l’API (Routes, pydantic, pytest)

L’API REST est apportée par l’application principale Flashcards AI (hors `e1/`). L’objectif E1 est de prouver l’existence d’une API conforme (endpoints, sécurité, doc OpenAPI), sans réimplémenter une seconde API.

Référence des preuves et chemins à capturer : `e1/docs/c5_api_proof.md`.

Éléments visibles :

- FastAPI : `backend_service/src/main.py`
- Routeur : `backend_service/src/api/__init__.py`
- Préfixe : `/api/v1`
- OpenAPI : `http://localhost:8002/api/v1/openapi.json`
- Authentification (JWT) + contrôle d’accès
- Endpoints par domaine : `auth`, `users`, `documents`, `decks`, `flashcards`, `study`

[[À AJOUTER : captures Swagger (OpenAPI) + exemple d’auth JWT (header Authorization)]]

#### Mettre en place un système d’authentification et d’autorisation pour sécuriser l’accès à l’API

Le backend met en place :

- authentification via **JWT**,
- contrôle d’accès par dépendance `get_current_active_user` et vérification du rôle (`is_admin`) selon les routes.

[[À AJOUTER : capture d’un token JWT + capture d’un 403 “Not enough permissions” sur une route admin]]

#### Conteneurisation et monitoring de l’API

Le projet est conteneurisé via **Docker / docker-compose** (voir `docker-compose.yml`) et inclut des briques d’observabilité :

- **Redis** (support au rate limiting),
- **Prometheus** (métriques FastAPI via instrumentator, si dépendances présentes),
- **Grafana** (visualisation) / **Uptime Kuma** : [[À AJOUTER : si présent dans ton environnement, préciser service/URL ou capture]].

[[À AJOUTER : capture docker-compose (backend + redis + monitoring) + endpoint /health (redis_status)]]

#### Documenter l’API et les méthodes d’accès aux données

- documentation interactive : Swagger UI (FastAPI),
- documentation machine : `openapi.json`,
- preuves et chemins : `e1/docs/c5_api_proof.md`.

#### Mise à disposition côté E1 : exports dataset

En complément de la preuve C5 via l’API principale, le pipeline E1 met à disposition un dataset directement exploitable via des exports.

- Module : `e1/src/e1_pipeline/export_dataset.py`
- Sortie : `e1/data/exports/` (formats **CSV** et **JSONL**)
- Traçabilité : chaque export est enregistré dans `flashcards2.db.datasets` (chemin, format, nombre de lignes)

[[À AJOUTER : capture des fichiers exportés (CSV/JSONL) + 5 lignes d’exemple]]

#### Résumé de la stack technique (mise à disposition)

- API : FastAPI (`backend_service/src/main.py`, `backend_service/src/api/`)
- Base relationnelle : SQLite `data/flashcards.db` + ORM SQLAlchemy (`db_module/`)
- Auth : JWT + refresh tokens (côté backend)
- Documentation : OpenAPI / Swagger
- Observabilité (contexte projet) : Prometheus / Grafana, MLflow
- Conteneurisation (contexte projet) : Docker / docker-compose

---

## Conclusion

Le livrable E1 met en évidence une chaîne complète et reproductible de traitement de données :

1. **Collecte multi-sources** (API, fichiers, scraping, Big Data via Spark)
2. **Stockage structuré** (staging + base finale)
3. **Nettoyage et déduplication** (normalisation + score qualité)
4. **Mise à disposition** (exports CSV/JSONL)
5. **Traçabilité et qualité** (table `runs`, tests automatisés)

Ce socle permet d’alimenter les prochaines étapes IA (E2) : définition des tâches (génération de cartes), sélection de modèles, évaluation et industrialisation.

---

## Annexes

### A) Commandes utiles

Installer les dépendances E1 (préparation à une dockerisation ultérieure) :

```bash
python -m pip install -r e1/requirements.txt
```

Exécuter le pipeline complet :

```bash
python e1/run_all.py
```

Exécuter les tests :

```bash
python -m pytest -c e1/pytest.ini -q e1/tests
```

### B) Artefacts générés

- Bases :
  - `e1/data/wikipedia_external.db`
  - `e1/data/flashcards2.db`
- Exports : `e1/data/exports/` (CSV + JSONL)

### C) Documentation

- Merise : `e1/docs/merise.md`
- RGPD : `e1/docs/rgpd.md`
- Preuve C5 : `e1/docs/c5_api_proof.md`

Documentation projet principal (base & API) :

- Schéma DB (diagramme) : `docs/database_schema.md`
- Modélisation DB : `docs/database_mcd.md`, `docs/database_mpd.md`
- Modèles & accès DB (ORM) : `db_module/models.py`, `db_module/crud.py`, `db_module/database.py`
- Entrée API : `backend_service/src/main.py`
- Routeur : `backend_service/src/api/__init__.py`

