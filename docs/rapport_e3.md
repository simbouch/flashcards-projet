**Data Scientist & Développeur d'application en Intelligence Artificielle**
**RNCP 37827**

**Projet : FlashCards AI**

**Bloc de compétences 3 — E3**
**Tester un système d'intelligence artificielle**

**Auteur : KHRIBECH Bouchaib**
**Cohorte : 2023–2025**
**Localisation : Marseille — Nice**

[[À AJOUTER : date de remise + organisme + session (ex : Mai 2026)]]

---

## Remerciements

Je remercie [[À AJOUTER : formateur(s), équipe, structure d'accueil]] pour leur soutien tout au long de ce projet.

[[TOC]]

## 1. Introduction

Quand on développe une application qui repose sur un modèle de langage (LLM), les tests classiques ne suffisent pas. En plus de vérifier que l'API répond correctement, il faut aussi s'assurer que le pipeline OCR → LLM → flashcards produit des résultats cohérents, que le modèle ne s'emballe pas sur des documents vides, et que les cas limites (fichier trop grand, texte mal formaté, réponse partielle du LLM) sont gérés proprement.

Ce rapport E3 décrit comment j'ai structuré les tests du projet FlashCards AI, les outils utilisés, et les résultats obtenus.

[[À AJOUTER : 3–4 lignes sur votre approche personnelle des tests (ce qui vous a guidé dans les choix)]]

---

## 2. Stratégie de tests

J'ai organisé les tests en trois niveaux :

1. **Tests unitaires par service** : chaque microservice a ses propres tests dans son dossier (`backend_service/tests/`, `db_module/tests/`, `llm_service/tests/`, `ocr_service/tests/`). Ces tests tournent de façon isolée, sans appeler les autres services — les dépendances externes sont remplacées par des mocks.

2. **Tests d'intégration (E2E)** : dans `tests/integration/`, ces tests parlent aux vraies instances Docker qui tournent. Ils vérifient le pipeline complet : upload d'un document → extraction OCR → génération LLM → création du deck → présence des flashcards.

3. **Lint et vérification statique** : côté frontend (ESLint) et backend (flake8 en CI), pour s'assurer que le code reste propre et lisible.

Le framework utilisé est **pytest** pour tous les tests Python. La configuration centrale est dans `pytest.ini` à la racine du projet, avec des markers pour distinguer les tests unitaires des tests E2E (skippés par défaut si `RUN_E2E` n'est pas défini).

```ini
# pytest.ini
[pytest]
markers =
    e2e: mark a test as end-to-end (skipped unless RUN_E2E=1)
```

---

## 3. Tests unitaires — backend et base de données

### 3.1 Structure des tests backend

Les tests backend se trouvent dans `backend_service/tests/` et couvrent les endpoints principaux de l'API FastAPI. Ils utilisent `TestClient` de Starlette (sans démarrer un vrai serveur) et une base SQLite en mémoire créée pour chaque test via le fixture `client` dans `conftest.py`.

Les tests sont répartis en plusieurs fichiers :

| Fichier | Ce qui est testé |
|---|---|
| `test_auth.py` | Inscription, connexion, tokens JWT, refresh token |
| `test_users.py` | Profil utilisateur, statistiques, suppression de compte |
| `test_documents.py` | Upload de fichier, limites de taille, passage des paramètres au traitement en arrière-plan, auto-scaling du nombre de cartes |
| `test_admin.py` | Endpoints d'administration (création, modification, désactivation, suppression d'utilisateurs) |
| `test_flashcard_count.py` | Fonction de calcul automatique du nombre de flashcards |

### 3.2 Exemple : test de l'upload et du traitement

Un des points critiques du backend est le traitement en arrière-plan (`process_document`). Pour éviter d'appeler les vrais services OCR et LLM dans les tests unitaires, j'utilise `monkeypatch` pour remplacer la fonction par un stub :

```python
# backend_service/tests/test_documents.py
async def _noop_process_document(document_id, file_path, deck_title=None, deck_is_public=False):
    return None

monkeypatch.setattr(documents_module, "process_document", _noop_process_document)
```

Cela me permet de tester que l'upload accepte ou refuse les fichiers selon leur taille, leur extension, et que les paramètres (`title`, `is_public`) sont bien transmis — sans déclencher une vraie extraction OCR.

### 3.3 Test du calcul automatique du nombre de cartes

Avec l'implémentation de l'auto-scaling (Option C), j'ai ajouté un module dédié `backend_service/src/services/flashcard_count.py` et ses tests dans `backend_service/tests/test_flashcard_count.py` :

```python
def test_estimate_num_cards_respects_min_and_max():
    # Texte vide => minimum
    assert estimate_num_cards_for_text("", min_cards=5, max_cards=20) == 5
    # Texte énorme => plafonné à 20
    big = "word " * 100_000
    assert estimate_num_cards_for_text(big, min_cards=5, max_cards=20) == 20

def test_estimate_num_cards_scales_with_words():
    # 750 mots / 250 mots par carte = 3 cartes
    text = "word " * 750
    assert estimate_num_cards_for_text(text, min_cards=1, max_cards=20, words_per_card=250) == 3
```

### 3.4 Tests de la base de données (db_module)

Le module `db_module/tests/` teste les opérations CRUD directement sur une base SQLite temporaire :
- Création d'utilisateur, de document, de deck, de flashcard, de session d'étude
- Suppression en cascade (supprimer un deck supprime ses flashcards)
- Contraintes d'unicité (email, username)

### 3.5 Résultats

```
backend_service/tests + db_module/tests : 70 passed en ~1m53s
```

[[À AJOUTER : capture d'écran du terminal montrant "70 passed"]]

---

## 4. Tests unitaires — service LLM

### 4.1 Ce qui est testé

Les tests LLM sont dans `llm_service/tests/`. Ils se focalisent sur deux choses :

1. **Le parsing des réponses du modèle** : la fonction `parse_qa_pairs` dans `llm_service/src/model.py` doit extraire des paires question/réponse valides même si le modèle renvoie du texte avec du formatage Markdown (blocs de code, tirets, astérisques).

2. **La robustesse aux cas limites** : texte vide, réponse sans aucune paire valide, caractères spéciaux dans les réponses.

### 4.2 Nettoyage des réponses LLM

Un problème classique avec les modèles de génération : ils renvoient parfois leurs réponses entourées de backticks ou de balises de code Markdown. J'ai implémenté et testé un nettoyage automatique :

```python
# llm_service/src/model.py
def _strip_code_fences(text: str) -> str:
    """Supprime les blocs de code Markdown (``` et ```lang) des réponses."""
    ...
```

Le test correspondant vérifie que des réponses comme `` ```python\nQ: ...\nA: ...\n``` `` sont correctement nettoyées avant le parsing.

### 4.3 Exécution dans Docker

Les tests LLM sont exécutés **dans le container** pour avoir accès aux mêmes dépendances que le service en production :

```bash
docker compose exec llm-service pytest -q
# => 13 passed, 2 skipped
```

Les 2 tests skippés sont des tests qui nécessitent un vrai accès GPU ou un modèle plus grand — ils sont marqués comme optionnels.

[[À AJOUTER : capture d'écran "13 passed, 2 skipped" depuis le terminal Docker]]

### 4.4 Startup non bloquant

Un point important à tester : le service LLM peut mettre 1 à 2 minutes à charger le modèle. J'ai vérifié que le service répond à `/health` immédiatement (même si le modèle n'est pas encore prêt) et que `/ready` retourne `false` pendant le chargement, puis `true` une fois terminé. Cela évite que le healthcheck Docker tue le service prématurément.

---

## 5. Tests unitaires — service OCR

Les tests OCR sont dans `ocr_service/tests/`. Ils couvrent :

- L'extraction de texte depuis des images PNG avec du texte simple (mocked ou avec de vraies images de test dans `ocr_service/demo_images/`).
- La gestion des types MIME (PDF vs image) lors de l'envoi au service.
- Le comportement en cas de fichier vide ou illisible.

Le service OCR utilise **PyMuPDF** pour les PDFs (extraction directe du texte vectoriel) et **Tesseract** pour les images (reconnaissance de caractères). Les tests vérifient que les deux chemins renvoient bien un champ `text` dans la réponse JSON.

---

## 6. Tests d'intégration end-to-end

### 6.1 Principe

Les tests d'intégration dans `tests/integration/` sont des tests **contre les vrais services Docker en fonctionnement**. Ils simulent exactement ce que ferait un utilisateur :

1. Inscription d'un utilisateur de test via `POST /api/v1/auth/register`
2. Connexion et récupération d'un token JWT
3. Upload d'un vrai fichier (image PNG ou PDF) via `POST /api/v1/documents`
4. Attente du traitement (polling du statut)
5. Vérification que le deck et les flashcards ont bien été créés

Ces tests sont **skippés par défaut** et ne s'exécutent que si la variable d'environnement `RUN_E2E=1` est définie. Cela évite de casser le pipeline CI si les services Docker ne sont pas démarrés.

```powershell
# Lancer les tests E2E sur la machine locale
$env:RUN_E2E='1'
python -m pytest -c tests/integration/pytest.ini -q
```

### 6.2 Ce qui est vérifié

| Test | Ce qui est prouvé |
|---|---|
| `test_ocr_service` | Le service OCR extrait bien du texte d'une image |
| `test_llm_service` | Le service LLM génère bien des paires Q/R valides |
| `test_full_pipeline_image` | Pipeline complet image → deck → flashcards |
| `test_full_pipeline_pdf` | Pipeline complet PDF → deck → flashcards |
| `test_backend_admin_*` | Endpoints admin (si credentials admin fournis) |

### 6.3 Résultats

```
tests/integration/ : 8 passed en ~3–4 minutes (avec RUN_E2E=1)
```

Le temps est long car le LLM génère les flashcards en conditions réelles (modèle CPU, pas de GPU). C'est volontaire : on teste exactement ce que l'utilisateur final vit.

[[À AJOUTER : capture d'écran du terminal "8 passed" avec RUN_E2E=1]]

---

## 7. Qualité du code — lint et formatage

### 7.1 Frontend (ESLint)

Le projet Vue.js utilise ESLint avec la configuration `@vue/cli-plugin-eslint`. Les règles incluent notamment `no-mixed-spaces-and-tabs` (interdit de mélanger espaces et tabulations) et des règles Vue.js standard.

Le lint est lancé avec :

```bash
npm --prefix frontend_service run lint
# => DONE  No lint errors found!
```

Et intégré dans la CI GitHub Actions pour bloquer les merges si des erreurs sont présentes.

### 7.2 Backend (flake8)

Le backend Python est vérifié avec `flake8` dans la CI. Les règles couvrent :
- Longueur des lignes (limite souple)
- Imports non utilisés
- Variables définies mais non utilisées

Un `.flake8` ou une configuration dans `setup.cfg` permet d'exclure certains patterns (migrations Alembic, fichiers générés).

### 7.3 Tests dans la CI

La CI exécute automatiquement `pytest` sur le backend à chaque push. Si un test casse, le pipeline s'arrête et le push est marqué en rouge. Cela garantit qu'on ne livre jamais de régression non détectée.

[[À AJOUTER : capture d'écran GitHub Actions avec toutes les étapes vertes (lint + test + build)]]

---

## 8. Validation spécifique au modèle IA

### 8.1 Problématique

Valider un LLM est plus complexe que valider une fonction classique. La sortie du modèle est variable : même avec le même texte en entrée, le modèle peut produire des formulations différentes. J'ai donc défini des critères de **qualité minimale** plutôt que de comparer des sorties exactes.

### 8.2 Benchmark des modèles candidats

Pour choisir le modèle LLM par défaut, j'ai réalisé un benchmark structuré comparant plusieurs modèles sur CPU. Le script est `llm_service/src/benchmark_flashcards.py` et les résultats sont archivés dans `llm_service/src/benchmarks_evidence/`.

Critères évalués :
- **Cold start** : temps de chargement du modèle au démarrage
- **Latence** : temps de génération par requête (moyenne et P95)
- **Qualité** : nombre de paires Q/R valides générées, taux de duplicates

Résumé des résultats (modèles testés sur CPU, 5 flashcards demandées) :

| Modèle | Cold start | Latence moy. | Cartes valides | Verdict |
|---|---|---|---|---|
| `Qwen/Qwen2.5-0.5B-Instruct` | ~12s | ~39–55s | 3–5 / 5 | **Choisi** — meilleur ratio qualité/vitesse |
| `bigscience/bloom-560m` | ~13s | ~103–159s | 1–2 / 5 | Trop lent, sous-génère |
| `distilgpt2` | ~196s | ~4–19s | 1 / 5 | Rapide mais ne suit pas le format Q/R |
| `gpt2` | ~134s | ~57–76s | 1 / 5 | Même problème que distilgpt2 |
| `TinyLlama-1.1B` (float16) | ~1275s | ~223–364s | 1 / 5 | Extrêmement lent sur CPU |
| `TinyLlama-1.1B` (float32) | — | — | — | OOM (exit 137) |

Le modèle **Qwen 2.5 0.5B Instruct** a été retenu comme valeur par défaut (`MODEL_NAME` dans `docker-compose.yml`). C'est un modèle "instruct" : il suit les instructions données dans le prompt, ce qui donne des paires Q/R cohérentes et bien formatées.

[[À AJOUTER : capture d'écran d'un fichier JSON de benchmark ou de l'interface MLflow avec les runs]]

### 8.3 Robustesse du parsing

Le LLM ne renvoie pas toujours du texte proprement formaté. J'ai implémenté un parser robuste (`parse_qa_pairs` dans `llm_service/src/model.py`) qui :

- Détecte plusieurs formats possibles (`Q:` / `R:`, `Question:` / `Réponse:`, numérotation, tirets)
- Supprime les blocs de code Markdown (`` ``` ``) qui peuvent entourer les réponses
- Filtre les paires trop courtes ou incohérentes
- Déduplique les questions similaires

Des tests unitaires couvrent chacun de ces cas (`llm_service/tests/test_model_parsing.py`).

### 8.4 Auto-scaling du nombre de cartes

Un autre aspect de la validation IA : vérifier que le nombre de cartes générées est **adapté à la taille du document**. J'ai implémenté une fonction de calcul automatique basée sur le nombre de mots extraits par l'OCR :

```
num_cards = clamp(ceil(nb_mots / 250), min=DEFAULT, max=20)
```

Cette valeur est calculée et loguée avant chaque appel au LLM, ce qui permet de tracer dans les logs combien de cartes ont été demandées pour chaque document.

---

## 9. Résultats globaux

| Suite de tests | Résultat | Contexte |
|---|---|---|
| `backend_service/tests/` | ✅ 70 passed | Dans le container backend-service |
| `db_module/tests/` | ✅ inclus dans les 70 | Base SQLite en mémoire |
| `llm_service/tests/` | ✅ 13 passed, 2 skipped | Dans le container llm-service |
| `tests/integration/` (E2E) | ✅ 8 passed | Avec RUN_E2E=1, services Docker actifs |
| Frontend ESLint | ✅ No lint errors | npm run lint |
| Frontend build | ✅ Build complet | npm run build |

---

## 10. Limitations connues et axes d'amélioration

**Ce qui n'est pas encore testé :**

- La performance sous charge (pas de tests de stress type locust ou k6). Le LLM est limité à 5 requêtes/minute par Redis, mais on n'a pas mesuré le comportement au-delà.
- La qualité des flashcards générées sur des documents très spécialisés (médecine, droit, code source). Le modèle Qwen 0.5B peut produire des questions vagues sur des textes très techniques.
- L'interface utilisateur : pas de tests automatisés Playwright ou Cypress. Les tests frontend se limitent au lint et au build.

**Ce que j'améliorerais :**

- Ajouter des tests de mutation pour vérifier que les tests testent vraiment quelque chose (et pas juste qu'aucune exception n'est levée).
- Mettre en place une mesure de couverture de code (`pytest-cov`) et un seuil minimum dans la CI.
- Tester le comportement avec un vrai GPU pour avoir des benchmarks comparables à une situation de production.

---

## 11. Conclusion

La mise en place des tests sur ce projet a été un travail itératif. Au début, beaucoup de tests échouaient à cause de problèmes d'isolation (session de base de données partagée entre tests, imports circulaires, tabs/espaces mélangés dans les fichiers Vue.js). Ces problèmes ont été résolus un par un.

Ce qui m'a le plus appris : la différence entre "tester une fonction" et "tester un système IA". Pour le LLM, il m'a fallu définir ce qu'est une sortie "acceptable" (au moins 1 paire Q/R valide sur 5 demandées) plutôt que de vérifier une sortie exacte. C'est une approche différente qui m'a forcé à réfléchir à ce que le modèle doit garantir en toutes circonstances.

[[À AJOUTER : 3–5 lignes personnelles sur votre expérience des tests dans ce projet]]

---

*Fin du rapport E3 — KHRIBECH Bouchaib*
