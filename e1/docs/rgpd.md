## RGPD (C4) — Note de conformité (E1)

Périmètre : pipeline E1 isolé dans `e1/` (collecte + nettoyage + export) basé sur **données publiques**.

### 1) Nature des données traitées

- Sources :
  - Wikipedia API (contenus publics)
  - Dump Wikimedia (titres publics)
  - Web scraping (pages publiques, ici principalement Wikipedia)
  - Fichiers samples CSV/JSON/XML (démonstration)

Type de données : **texte** (contenu encyclopédique / titres / extraits), métadonnées techniques (URL, id).

### 2) Données personnelles

- Objectif : **éviter** tout traitement de données personnelles.
- Risque résiduel : une page web publique peut contenir des noms propres.
- Mesure :
  - collecte limitée à un petit volume (paramètres `search_limit`, `max_titles`, etc.)
  - stockage local uniquement (pas de publication)

### 3) Finalité et base légale

- Finalité : démonstration pédagogique RNCP (collecte, préparation, mise à disposition d’un dataset).
- Base : intérêt légitime / exercice pédagogique (contexte scolaire), données publiques.

### 4) Minimisation & proportionnalité

- Minimisation :
  - champs strictement nécessaires (texte + hash + métadonnées minimales)
  - pas d’identifiants utilisateurs, pas d’email, pas d’IP stockée
- Limitation du volume : paramètres de config (ex: mots-clés, limites de titres/pages).

### 5) Durée de conservation

- Les DB générées sont des **artefacts locaux** :
  - `e1/data/wikipedia_external.db`
  - `e1/data/flashcards2.db`
- Suppression simple : effacer `e1/data/*.db` + `e1/data/exports/*`.
- Les fichiers de données sont ignorés Git via `e1/.gitignore`.

### 6) Sécurité / confidentialité

- Stockage local (poste de dev), pas d’exposition réseau.
- Déduplication par hash (SHA256) : réduit les duplicats, aide à l’audit.
- Traçabilité : table `runs` (horodatage, statut, paramètres).

### 7) Droits des personnes (si concerné)

Si une donnée personnelle apparaissait dans une page publique :

- Droit d’accès / effacement : suppression des lignes concernées (par `content_hash`, URL, etc.) ou suppression de la DB.
- Portabilité : export possible via les fichiers `CSV/JSONL` (répertoire `e1/data/exports/`).

### 8) Mesures organisationnelles (projet)

- Ne pas utiliser de pages ciblant des personnes physiques.
- Garder les volumes faibles.
- Conserver la preuve de sources (URL, page_id) uniquement à des fins d’audit.