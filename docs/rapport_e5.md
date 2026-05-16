**Data Scientist & Développeur d'application en Intelligence Artificielle**
**RNCP 37827**

**Projet : FlashCards AI**

**Bloc de compétences 5 — E5**
**Communiquer sur un projet d'intelligence artificielle**

**Auteur : KHRIBECH Bouchaib**
**Cohorte : 2023–2025**
**Localisation : Marseille — Nice**

[[À AJOUTER : date de remise + organisme + session (ex : Mai 2026)]]

---

## Remerciements

Je remercie [[À AJOUTER : formateur(s), équipe, structure d'accueil]].

---

## Sommaire

1. Introduction
2. Documentation technique
3. Guide utilisateur (fonctionnel)
4. Guide opérationnel
5. Index des preuves (captures d'écran à joindre)
6. Conclusion

---

## 1. Introduction

Un projet IA n'existe pas seulement dans le code. Pour qu'il soit utile, il faut qu'on puisse l'expliquer à différents publics : un utilisateur qui veut juste générer ses flashcards, un collègue développeur qui doit maintenir le système, un formateur qui évalue le projet RNCP.

Ce rapport E5 rassemble la documentation produite pour le projet **FlashCards AI** : technique, fonctionnelle, et opérationnelle.

[[À AJOUTER : 3–4 lignes sur votre démarche de documentation (quand vous l'avez faite, comment)]]

---

## 2. Documentation technique

### 2.1 Architecture et base de données

La structure de la base de données est documentée dans `docs/database_schema.md`, `docs/database_mcd.md` et `docs/database_mpd.md`. Elle contient 6 tables principales :

| Table | Rôle |
|---|---|
| `users` | Comptes utilisateurs (email, username, rôle, is_active) |
| `documents` | Fichiers uploadés (chemin, statut de traitement, MIME type) |
| `extracted_texts` | Texte OCR associé à chaque document |
| `decks` | Collections de flashcards (titre, description, is_public) |
| `flashcards` | Paires question/réponse liées à un deck |
| `study_sessions` | Sessions de révision (progression, scores) |

Les relations : un utilisateur possède des documents et des decks. Un document produit un deck. Un deck contient des flashcards. Les suppressions sont en cascade (supprimer un deck supprime ses flashcards).

[[À AJOUTER : capture d'écran ou image du diagramme MCD/MLD]]

### 2.2 Documentation des endpoints API

L'API REST du backend est auto-documentée via Swagger/OpenAPI. L'interface est accessible à `http://localhost:8002/docs` quand l'application tourne.

Principaux groupes d'endpoints :

- `/api/v1/auth/` : inscription, connexion, refresh token
- `/api/v1/users/` : profil, statistiques, suppression de compte
- `/api/v1/documents/` : upload, liste, statut, texte extrait, suppression
- `/api/v1/decks/` : création, liste, modification, suppression
- `/api/v1/flashcards/` : liste par deck, révision
- `/api/v1/study/` : sessions d'étude, progression
- `/api/v1/admin/` : gestion des utilisateurs (réservé aux admins)

[[À AJOUTER : capture d'écran de l'interface Swagger avec la liste des endpoints]]

### 2.3 Documentation de l'administration et du compte système

La documentation `docs/admin_system_users.md` explique :
- Comment créer le premier compte administrateur via les variables d'environnement `INITIAL_ADMIN_USERNAME` / `INITIAL_ADMIN_PASSWORD`
- Les protections en place (l'admin ne peut pas se supprimer lui-même, le dernier admin ne peut pas être supprimé)
- Le compte `system` : réservé, bloqué en login, non modifiable via l'admin

### 2.4 Documentation du benchmarking LLM

`docs/llm_benchmarking.md` documente :
- Comment lancer un benchmark (`python -m src.benchmark_flashcards`)
- Comment changer le modèle LLM sans modifier le code
- Les résultats comparatifs des modèles testés (Qwen, BLOOM, GPT-2, TinyLlama, etc.)
- Comment interpréter les métriques (cold start, latence, cartes valides)

---

## 3. Guide utilisateur (fonctionnel)

### 3.1 Premiers pas

1. Ouvrir l'application dans le navigateur : `http://localhost:8080`
2. Cliquer sur **S'inscrire** et créer un compte (email + mot de passe).
3. Se connecter avec les identifiants créés.

[[À AJOUTER : capture d'écran de la page d'accueil et de la page de connexion]]

### 3.2 Générer des flashcards depuis un document

1. Aller dans **Documents** dans le menu.
2. Cliquer sur **Uploader un document**.
3. Choisir un fichier PDF ou image (PNG, JPG). Taille maximale : 10 MB.
4. (Optionnel) Donner un titre au deck qui sera créé.
5. (Optionnel) Cocher "Deck public" si vous voulez le partager.
6. Cliquer sur **Upload**.
7. Le traitement commence automatiquement. Vous pouvez suivre le statut dans la liste des documents (OCR en cours → Génération → Terminé).
8. Une fois le statut "Terminé", cliquer sur **Voir** pour ouvrir le deck et ses flashcards.

**Note sur le nombre de flashcards** : le système adapte automatiquement le nombre de cartes à la taille du document. Un petit document génère environ 5 cartes, un grand PDF peut en générer jusqu'à 20.

[[À AJOUTER : captures d'écran de l'interface Documents (upload, liste, statut)]]

### 3.3 Réviser avec les flashcards

1. Aller dans **Decks** dans le menu.
2. Cliquer sur **Réviser** sur un deck.
3. Pour chaque carte : lire la question, réfléchir, puis cliquer pour voir la réponse.
4. Choisir si la carte doit être revue ou si vous la maîtrisez.

[[À AJOUTER : capture d'écran du mode révision (StudyView)]]

### 3.4 Décks publics

La section **Decks publics** permet de consulter et d'étudier les decks partagés par d'autres utilisateurs. Vous pouvez les utiliser sans avoir à uploader vos propres documents.

### 3.5 Profil utilisateur

La page **Profil** affiche vos statistiques : nombre de documents, de decks, de flashcards créées, et de sessions de révision.

[[À AJOUTER : capture d'écran de la page Profil avec les statistiques]]

---

## 4. Guide opérationnel

### 4.1 Prérequis

- **Docker Desktop** installé (version 24+ recommandée)
- **4 GB de RAM** disponible pour Docker (8 GB recommandé)
- Connexion internet au premier démarrage (téléchargement du modèle LLM)

### 4.2 Démarrage

```bash
# Cloner le dépôt
git clone <url-du-repo>
cd flashcards-project

# Démarrer tous les services
docker compose up -d

# (Optionnel) Démarrer le monitoring
docker compose -f docker-compose.monitoring.yml up -d

# Vérifier que tout est healthy
docker compose ps
```

La première fois, le service LLM télécharge le modèle Qwen 2.5 (environ 1 GB). Cela peut prendre quelques minutes selon la connexion internet.

### 4.3 Configuration du compte administrateur

Créez un fichier `.env` à la racine (non commité dans git) :

```env
INITIAL_ADMIN_USERNAME=votre_username
INITIAL_ADMIN_PASSWORD=VotreMotDePasseSécurisé
INITIAL_ADMIN_EMAIL=votre@email.com
INITIAL_ADMIN_ALLOW_PROMOTE_EXISTING=true
```

Puis redémarrez le backend : `docker compose up -d --force-recreate backend-service`

### 4.4 Accès aux interfaces de monitoring

| Interface | URL | Credentials par défaut |
|---|---|---|
| Application | http://localhost:8080 | Votre compte utilisateur |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | — |
| MLflow OCR | http://localhost:5000 | — |
| MLflow LLM | http://localhost:5001 | — |

### 4.5 Problèmes courants

**Le LLM ne génère pas de cartes :**
- Vérifier que le service LLM est bien "healthy" : `docker compose ps llm-service`
- Le modèle peut prendre 1–2 minutes à se charger. Attendre et réessayer.
- Consulter les logs : `docker compose logs llm-service`

**Upload refusé (413) :**
- Le fichier dépasse la limite de 10 MB. Compresser le PDF ou réduire la taille de l'image.

**Interface vide après connexion :**
- Faire un hard refresh (Ctrl+F5).
- Vérifier que le backend est accessible : `curl http://localhost:8002/health`

[[À AJOUTER : autres problèmes rencontrés pendant vos tests avec leurs solutions]]

---

## 5. Index des preuves (captures d'écran à joindre)

| # | Description | Section concernée |
|---|---|---|
| 1 | Page d'accueil de l'application | Guide utilisateur 3.1 |
| 2 | Page d'upload d'un document | Guide utilisateur 3.2 |
| 3 | Liste des documents avec statuts | Guide utilisateur 3.2 |
| 4 | Interface de révision (StudyView) | Guide utilisateur 3.3 |
| 5 | Page Profil avec statistiques réelles | Guide utilisateur 3.5 |
| 6 | Interface Admin — liste des utilisateurs | Documentation technique 2.2 |
| 7 | Swagger UI — liste des endpoints | Documentation technique 2.2 |
| 8 | Diagramme MCD/MLD de la base | Documentation technique 2.1 |
| 9 | `docker compose ps` (tous healthy) | Guide opérationnel 4.2 |
| 10 | Dashboard Grafana avec métriques | Guide opérationnel 4.4 |
| 11 | MLflow — liste de runs LLM | Guide opérationnel 4.4 |
| 12 | GitHub Actions — run vert (CI) | [[E3 / preuve qualité]] |

---

## 6. Conclusion

Documenter un projet IA, c'est autant de travail que de le coder. Ce rapport E5 rassemble ce qui est nécessaire pour qu'une autre personne puisse comprendre, installer, utiliser, et maintenir FlashCards AI.

La documentation a été conçue pour trois niveaux de lecture : fonctionnel (utilisateur final), technique (développeur qui reprend le projet), et opérationnel (quelqu'un qui doit le déployer ou le surveiller).

[[À AJOUTER : 4–5 lignes sur votre expérience de la documentation dans ce projet : ce qui a été difficile, ce que vous avez appris]]

---

*Fin du rapport E5 — KHRIBECH Bouchaib*
