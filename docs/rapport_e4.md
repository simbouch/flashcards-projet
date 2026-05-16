**Data Scientist & Développeur d'application en Intelligence Artificielle**
**RNCP 37827**

**Projet : FlashCards AI**

**Bloc de compétences 4 — E4**
**Gérer un projet en intelligence artificielle**

**Auteur : KHRIBECH Bouchaib**
**Cohorte : 2023–2025**
**Localisation : Marseille — Nice**

[[À AJOUTER : date de remise + organisme + session (ex : Mai 2026)]]

---

## Remerciements

Je remercie [[À AJOUTER : formateur(s), équipe, structure d'accueil]].

---

## Sommaire

1. Introduction — contexte et objectifs
2. Méthode de travail adoptée
3. Organisation du backlog et des user stories
4. Déroulement des itérations
5. Suivi des risques et décisions clés
6. Rétrospective
7. Conclusion

---

## 1. Introduction — contexte et objectifs

[[À AJOUTER : 5–8 lignes sur le contexte personnel du projet : quand il a démarré, dans quel cadre (formation Simplon, alternance, projet personnel ?), quelle était votre mission principale, et quel était l'objectif final du projet.]]

Le projet **FlashCards AI** avait pour ambition de construire une application complète de génération automatique de fiches de révision. Contrairement à un projet "tutoriel", tous les composants — OCR, LLM, API, interface, monitoring — devaient fonctionner ensemble en production, ce qui a impliqué une vraie gestion de projet avec des priorités, des itérations, et des corrections chemin faisant.

---

## 2. Méthode de travail adoptée

J'ai travaillé en mode **itératif** : plutôt que de tout planifier d'avance, j'ai défini des objectifs à court terme (1–2 semaines) et j'ai ajusté le plan à chaque fin de cycle selon ce qui avait été livré ou bloqué.

La méthode ressemble à une approche Agile légère :
- **Backlog** : liste de fonctionnalités et corrections à faire, priorisées par valeur utilisateur.
- **Itérations** : chaque itération produit quelque chose de fonctionnel et testable.
- **Revues** : après chaque itération, je fais le point sur ce qui marche, ce qui est en retard, et ce qui a changé dans les exigences.

Je n'ai pas utilisé d'outil de gestion de projet externe (Jira, Trello) car le projet était individuel. Le suivi s'est fait via les commits git (chaque commit = une tâche terminée) et via un document de notes personnelles.

[[À AJOUTER : si vous avez utilisé un tableau Kanban, une capture d'écran Trello/Notion/autre]]

---

## 3. Organisation du backlog et des user stories

Le backlog est organisé en **épics** (grandes fonctionnalités) avec des user stories associées. Voici les principaux épics du projet :

### Épic 1 : Pipeline de base (P0 — bloquant)
- En tant qu'utilisateur, je peux uploader un PDF ou une image.
- En tant que système, le texte est extrait automatiquement par OCR.
- En tant que système, des flashcards sont générées par un LLM.
- En tant qu'utilisateur, je vois les flashcards dans mon interface.

### Épic 2 : Authentification et rôles
- En tant qu'utilisateur, je peux m'inscrire et me connecter.
- En tant qu'administrateur, j'ai accès à un tableau de bord de gestion des utilisateurs.
- En tant que système, un compte administrateur initial est créé automatiquement au démarrage.

### Épic 3 : Qualité et tests
- En tant que développeur, j'ai des tests unitaires pour chaque service.
- En tant que développeur, j'ai des tests E2E qui valident le pipeline complet.
- En tant que développeur, le lint et le build s'exécutent automatiquement en CI.

### Épic 4 : Monitoring et observabilité
- En tant qu'opérateur, je peux voir l'état des services en temps réel (Prometheus/Grafana).
- En tant que data scientist, je peux comparer les performances des modèles LLM (MLflow).

### Épic 5 : UX et polish
- En tant qu'utilisateur, les boutons sont bien espacés et lisibles.
- En tant qu'utilisateur, mon profil affiche le bon nombre de flashcards.
- En tant qu'utilisateur, un grand PDF génère plus de 5 flashcards.

[[À AJOUTER : tableau ou capture d'écran de votre backlog réel si vous en avez un]]

---

## 4. Déroulement des itérations

### Itération 1 — Mise en place de l'architecture
**Objectif** : avoir tous les services qui démarrent et communiquent.
**Livré** : `docker-compose.yml` fonctionnel, healthchecks, pipeline OCR → LLM → backend de bout en bout.
**Difficultés** : le LLM bloquait le démarrage du service (startup synchrone). Résolu en passant à un démarrage non bloquant avec un endpoint `/ready`.

[[À AJOUTER : date ou semaine de cette itération]]

### Itération 2 — Authentification et administration
**Objectif** : sécuriser l'application avec des comptes utilisateurs et un rôle administrateur.
**Livré** : inscription, connexion, JWT, endpoints admin (gestion des utilisateurs, désactivation, suppression), protection de l'utilisateur `system`.
**Difficultés** : s'assurer que l'administrateur ne peut pas se supprimer lui-même ni supprimer le dernier admin. Résolu via des gardes dans les endpoints admin.

### Itération 3 — Tests et CI/CD
**Objectif** : couvrir le code avec des tests et automatiser les vérifications.
**Livré** : 70 tests backend, 13 tests LLM, 8 tests E2E, pipeline GitHub Actions.
**Difficultés** : isolation des tests (sessions DB partagées, imports circulaires). Résolu avec des fixtures pytest propres et des mocks.

### Itération 4 — Qualité et monitoring
**Objectif** : rendre l'application observable et améliorer l'expérience utilisateur.
**Livré** : dashboards Grafana, métriques Prometheus, benchmarking LLM, choix du modèle Qwen 2.5.
**Difficultés** : le benchmarking sur CPU prend des heures. Résolu en limitant les runs à 2 par modèle et en archivant les résultats dans des fichiers JSON.

### Itération 5 — Polish UI et fonctionnalités finales
**Objectif** : rendre l'interface propre et les fonctionnalités complètes.
**Livré** : boutons unifiés, page d'accueil animée, auto-scaling du nombre de cartes, titre de deck personnalisable, option "deck public".
**Difficultés** : erreurs ESLint liées aux tabulations dans les fichiers Vue.js. Résolu avec un script de normalisation.

---

## 5. Suivi des risques et décisions clés

| Risque identifié | Impact | Décision prise |
|---|---|---|
| LLM trop lent sur CPU | Expérience dégradée | Startup non bloquant + benchmark pour choisir le modèle le plus rapide |
| Modèle trop lourd (OOM) | Crash du container | Limite mémoire Docker à 4G + tests avec plusieurs modèles |
| Pipeline fragile si OCR renvoie du texte vide | Aucune flashcard générée | Génération quand même avec le minimum de cartes (pas d'erreur bloquante) |
| Sécurité : JWT avec clé par défaut faible | Tokens falsifiables | Variable d'environnement + avertissement dans le code |
| Tests trop couplés aux services réels | CI difficile | Mocks systématiques dans les tests unitaires, E2E optionnels |

---

## 6. Rétrospective

**Ce qui a bien fonctionné :**
- L'architecture microservices a facilité le travail en parallèle sur plusieurs services sans tout casser.
- Le versioning git avec des commits atomiques m'a permis de revenir en arrière facilement quand quelque chose cassait.
- Le benchmarking structuré du LLM a évité de choisir un modèle "au hasard" — les données objectives ont guidé la décision.

**Ce qui a été difficile :**
- La gestion des tests E2E sur un système avec un LLM lent : chaque run de test prend 3–4 minutes. Il faut de la patience.
- Les erreurs ESLint sur les tabulations/espaces : un problème mineur en apparence, mais bloquant pour le build Docker.
- La configuration des dashboards Grafana : la provisioning automatique fonctionne bien, mais le débogage d'un dashboard qui ne s'affiche pas est fastidieux.

**Ce que je ferais différemment :**
- [[À AJOUTER : votre ressenti personnel sur ce que vous changeriez dans l'organisation du projet]]
- Définir des critères d'acceptation clairs dès le début pour chaque user story.
- Mettre en place la CI dès l'itération 1 plutôt qu'à l'itération 3.

---

## 7. Conclusion

Gérer ce projet en solo m'a appris que la rigueur dans l'organisation compense l'absence d'équipe. Les commits git comme trace de progression, les tests comme filet de sécurité, et le monitoring comme outil de feedback : ce sont ces pratiques qui ont permis de livrer un projet fonctionnel et maintenable.

[[À AJOUTER : 4–5 lignes personnelles sur ce que ce projet vous a apporté du point de vue gestion de projet]]

---

*Fin du rapport E4 — KHRIBECH Bouchaib*
