# Rapport E1 – Gestion des Données

**Projet :** FlashCards AI  
**Auteur :** Bouchaib Khribech  
**Bloc RNCP :** E1 – Collecte, stockage et mise à disposition des données

---

## 1. Introduction

Le projet FlashCards AI est une application intelligente permettant la génération automatique de fiches de révision (flashcards) à partir de documents utilisateurs (PDF, images, textes) et de données externes issues de Wikipédia. Le système repose sur une architecture data complète intégrant des pipelines d’extraction, de transformation, de nettoyage, d’agrégation et de stockage des données afin d’alimenter les composants d’intelligence artificielle.

Le livrable E1 couvre l’ensemble du cycle de vie de la donnée, depuis sa collecte multi-sources jusqu’à sa mise à disposition structurée, sécurisée et conforme aux exigences réglementaires.

---

## 2. Présentation Générale du Système de Données

L’architecture repose sur les composants suivants :
- Collecte multi-sources (documents utilisateurs, API Wikipedia, web scraping, Big Data)
- Traitement OCR
- Pipeline Big Data avec PySpark
- ETL automatisé
- Base externe de staging
- Base relationnelle principale
- Préparation des données pour IA

---

## 3. Collecte des Données (A1 – C1)

### 3.1 Sources de Données

- Documents utilisateurs : PDF, JPG, PNG, TXT
- API Wikipédia : récupération d’articles encyclopédiques
- Web scraping : extraction ciblée d’informations complémentaires
- Dump Wikimedia : source massive utilisée dans un cadre Big Data

### 3.2 Contraintes Techniques

- Formats multiples
- Volumétrie importante
- Qualité hétérogène
- Encodages variés
- Performance et scalabilité

### 3.3 Technologies Utilisées

- Python
- Tesseract OCR
- Wikipedia API
- Requests + BeautifulSoup
- PySpark
- SQLite / PostgreSQL
- Pandas
- SQLAlchemy

---

## 4. Extraction des Données

### 4.1 API Wikipédia

Utilisation de l’API officielle permettant de récupérer dynamiquement les articles. Les contenus sont nettoyés et stockés dans une base externe dédiée.

### 4.2 Web Scraping

Utilisation de BeautifulSoup afin d’extraire des données non accessibles via API, en respectant les règles d’éthique, de légalité et les conditions d’utilisation.

### 4.3 OCR

Les fichiers PDF et images sont traités via Tesseract OCR afin d’extraire automatiquement le texte, qui est ensuite nettoyé, segmenté et structuré.

---

## 5. Big Data – Pipeline PySpark

### 5.1 Source

Dump Wikimedia officiel : `frwiki-latest-abstract.xml.gz`

### 5.2 Objectif

Mettre en œuvre un traitement massif simulant un environnement Big Data réel afin de démontrer la capacité à traiter de grands volumes de données.

### 5.3 Pipeline

- Lecture du dump XML compressé
- Parsing XML distribué
- Filtrage thématique
- Nettoyage massif
- Structuration tabulaire
- Export CSV / Parquet
- Chargement en base externe

---

## 6. Requêtes SQL & ORM (C2)

Le projet utilise SQLAlchemy ORM pour la manipulation des données relationnelles. Chaque requête est testée, optimisée et documentée.

Les requêtes permettent :
- insertion massive
- jointures multi-tables
- filtrage sémantique
- statistiques d’apprentissage

Chaque requête ORM est fournie avec son équivalent SQL brut pour assurer la traçabilité.

---

## 7. Nettoyage & Agrégation (C3)

Le pipeline de nettoyage comprend :
- suppression des doublons
- correction d’encodage
- normalisation linguistique
- suppression du bruit
- homogénéisation des formats

Les données issues de différentes sources sont agrégées dans un pipeline automatisé assurant cohérence, fiabilité et traçabilité.

---

## 8. Mise à Disposition des Données (A2 – C4)

### 8.1 Base de Données

Le système repose sur deux bases :
- Base externe `wikipedia_external.db`
- Base principale `flashcards.db`

### 8.2 Méthode MERISE

MCD : User, Document, Deck, Flashcard, StudySession  
MLD : tables relationnelles normalisées  
MPD : schéma SQL optimisé

### 8.3 Sécurité & RGPD

- chiffrement des mots de passe
- anonymisation
- journalisation
- suppression des données sur demande
- registre de traitement

---

## 9. Conclusion

Le livrable E1 démontre la mise en œuvre complète d’une architecture data professionnelle intégrant Big Data, ETL, nettoyage, agrégation, stockage et sécurité. Cette architecture garantit une base solide et scalable pour l’ensemble du projet d’intelligence artificielle FlashCards AI.

