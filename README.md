# 📚 Registre des Élèves — Projet Final P8

Application web complète de gestion et suivi des données scolaires, développée avec un backend Python/FastAPI, une base de données PostgreSQL (SQL écrit manuellement, sans ORM), et un frontend HTML/CSS/JavaScript vanilla avec tableau de bord Chart.js.

> Projet final intégrateur — exploitation de données Python dans une application web.

---

## ✨ Fonctionnalités

- **Registre d'élèves** avec pagination intelligente (5 lignes par défaut, personnalisable)
- **Fusion de deux sources de données** : PostgreSQL (modifiable) et fichier JSON source (lecture seule), avec indication claire de l'origine de chaque ligne
- **Recherche et filtrage** par numéro, code, nom, prénom, classe
- **Import sélectif** des données JSON vers la base, avec détection automatique des doublons (par numéro d'élève)
- **Validation robuste des notes** : toute note hors de la plage 0–20 est rejetée individuellement et signalée, sans bloquer l'import de l'élève ni faire planter l'application
- **Ajout manuel** d'élèves via formulaire, avec validation complète (Pydantic côté API)
- **Édition en ligne** : modification cellule par cellule (double-clic) et par ligne complète — réservée aux données en base de données
- **Archivage / restauration** (suppression douce) : les élèves archivés sont masqués sans être supprimés physiquement, et restaurables à tout moment
- **Tableau de bord statistique** avec Chart.js :
  - Indicateurs globaux (total, part en base, part à importer, archivés)
  - Répartition des élèves par classe
  - Répartition par source (base de données / JSON)
  - Moyenne générale par classe (combinant base et données restantes)
  - Top 10 des meilleures moyennes générales
  - Liste des élèves archivés

---

## 🛠️ Stack technique

| Couche | Technologies |
|---|---|
| **Backend** | Python, FastAPI, Pydantic |
| **Base de données** | PostgreSQL, `psycopg2` (SQL écrit manuellement, sans ORM) |
| **Frontend** | HTML, CSS, JavaScript (vanilla, sans framework) |
| **Visualisation** | Chart.js |
| **Environnement** | Linux, Bash, `venv` |
| **Versionnement** | Git / GitHub |

---

## 🏗️ Architecture générale

projet-final-p8/
├── backend/
│ ├── app/
│ │ ├── main.py # Point d'entrée FastAPI
│ │ ├── database.py # Connexion PostgreSQL (psycopg2)
│ │ ├── config.py # Lecture des variables .env
│ │ ├── models.py # Requêtes SQL et logique métier
│ │ ├── schemas.py # Validation Pydantic (entrées/sorties API)
│ │ └── routes/
│ │ ├── health.py
│ │ ├── etudiants.py
│ │ └── stats.py
│ └── requirements.txt
├── database/
│ └── init.sql # Schéma SQL : tables, contraintes, index
├── data/
│ └── valides.json # Données source (issues du projet Python précédent)
├── frontend/
│ ├── index.html # Registre principal
│ ├── dashboard.html # Tableau de bord statistique
│ ├── css/style.css
│ └── js/
│ ├── api.js # Communication avec l'API
│ ├── main.js # Logique du registre
│ ├── dashboard.js # Logique des graphiques
│ └── chart.umd.min.js # Chart.js (hébergé en local)
└── README.md



Le projet suit une architecture en couches strictement séparées : le frontend ne communique jamais directement avec la base de données, il passe exclusivement par l'API REST, elle-même organisée en routes → schémas de validation → logique métier → connexion base de données.

---

## 🗄️ Modèle de données

Trois tables PostgreSQL, reliées par clés étrangères :

- **`etudiants`** — identité et scolarité de chaque élève (numéro unique, classe, statut d'archivage)
- **`matieres`** — référentiel des matières enseignées
- **`notes`** — notes par élève et par matière (devoirs, examen, moyenne), liée aux deux tables précédentes, avec `ON DELETE CASCADE`

8 index sont en place pour optimiser les recherches fréquentes (par classe, par nom, par statut d'archivage, jointures notes/élèves).

La moyenne générale d'un élève n'est jamais stockée : elle est recalculée à la volée à partir des moyennes par matière, pour garantir la cohérence des données à tout moment.

---

## 🔌 API — Endpoints principaux

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/health` | Vérifie l'état de l'API et de la connexion base de données |
| `GET` | `/etudiants` | Liste paginée, fusion base + JSON, recherche et filtres |
| `POST` | `/etudiants` | Ajout manuel d'un élève |
| `POST` | `/etudiants/importer` | Import sélectif d'élèves depuis le JSON |
| `PATCH` | `/etudiants/{id}` | Modification d'un élève |
| `PATCH` | `/etudiants/{id}/notes/{matiere}` | Modification d'une note |
| `PATCH` | `/etudiants/{id}/archiver` | Archivage (suppression douce) |
| `PATCH` | `/etudiants/{id}/restaurer` | Restauration d'un élève archivé |
| `GET` | `/etudiants/archives` | Liste des élèves archivés |
| `GET` | `/stats/kpis` | Indicateurs globaux |
| `GET` | `/stats/repartition-classe` | Répartition par classe |
| `GET` | `/stats/repartition-source` | Répartition par source de données |
| `GET` | `/stats/moyenne-classe-globale` | Moyenne générale par classe |
| `GET` | `/stats/top10` | Top 10 des meilleures moyennes |

Documentation interactive complète disponible via Swagger UI à `/docs` une fois le serveur lancé.

---

## 🚀 Installation et lancement

### Prérequis
- Python 3.12+
- PostgreSQL installé et actif

### 1. Cloner le projet
```bash
git clone https://github.com/<ton-utilisateur>/<nom-du-repo>.git
cd <nom-du-repo>
```

### 2. Créer l'environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r backend/requirements.txt
```

### 4. Configurer la base de données
```bash
sudo -u postgres psql -c "CREATE DATABASE projet_final_p8;"
psql -U postgres -d projet_final_p8 -f database/init.sql
```

### 5. Configurer les variables d'environnement
Copier `.env.example` en `.env` à la racine du projet, et renseigner les identifiants PostgreSQL.

### 6. Lancer le serveur backend
```bash
cd backend
uvicorn app.main:app --reload
```
L'API est accessible sur `http://127.0.0.1:8000`, la documentation interactive sur `http://127.0.0.1:8000/docs`.

### 7. Ouvrir le frontend
Ouvrir `frontend/index.html` dans un navigateur (le serveur backend doit être actif en parallèle).

---

## 📂 Détail des fichiers du projet

### Backend

#### `backend/app/main.py`
**Rôle** : point d'entrée de l'application FastAPI. Assemble toutes les routes du projet en un seul serveur.
**Contenu** : création de l'instance `FastAPI`, configuration du middleware CORS (autorise le frontend à communiquer avec l'API depuis un fichier local), inclusion des trois routeurs (`health`, `etudiants`, `stats`), route racine `/` de bienvenue.

#### `backend/app/config.py`
**Rôle** : centralise la lecture des variables d'environnement (`.env`), pour ne jamais écrire d'identifiants en dur dans le code.
**Contenu** : classe `Settings` (Pydantic `BaseSettings`) qui valide automatiquement les variables `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` ; résolution du chemin absolu vers `.env` via `Path(__file__).resolve().parent.parent.parent`, pour que la configuration se charge correctement peu importe le dossier depuis lequel le serveur est lancé.

#### `backend/app/database.py`
**Rôle** : gère la connexion brute à PostgreSQL avec `psycopg2` (aucun ORM, conformément au cahier des charges).
**Contenu** : `get_connection()` ouvre une connexion PostgreSQL à partir des paramètres de `config.py` ; `get_cursor(commit=False)` est un gestionnaire de contexte (`with ... as cur:`) qui fournit un curseur en mode dictionnaire (`RealDictCursor`), avec fermeture automatique de la connexion et `rollback` en cas d'erreur, `commit` explicite pour les écritures.

#### `backend/app/schemas.py`
**Rôle** : définit la forme des données acceptées et validées par l'API (Pydantic), côté entrée.
**Contenu** : `NoteMatiere` (structure d'une note avec validation 0–20), `EtudiantCreate` (champs obligatoires pour créer un élève), `EtudiantUpdate` (mêmes champs, tous optionnels, pour l'édition partielle), `NoteUpdate` (édition partielle d'une note, avec la même validation 0–20).

#### `backend/app/models.py`
**Rôle** : toute la logique métier et les requêtes SQL du projet — le fichier central qui parle réellement à la base de données et au fichier JSON.
**Fonctions principales** :
- `charger_valides_json()` — lit `data/valides.json`
- `get_numeros_existants()` — renvoie l'ensemble des numéros déjà en base (détection de doublons)
- `get_matieres_id()` — associe chaque nom de matière à son identifiant SQL
- `_convertir_date()` — convertit une date `JJ/MM/AAAA` (JSON) en `AAAA-MM-JJ` (PostgreSQL)
- `_note_valide()` — vérifie qu'une note est comprise entre 0 et 20
- `importer_etudiants(numeros)` — importe les élèves sélectionnés du JSON vers PostgreSQL, ignore les doublons, rejette individuellement les notes invalides et les signale dans un rapport d'anomalies
- `rechercher_etudiants_db(...)` / `rechercher_etudiants_json(...)` — recherche filtrée dans chaque source séparément
- `obtenir_etudiants(...)` — fusionne les deux sources, applique la pagination
- `ajouter_etudiant(...)` — insertion manuelle d'un nouvel élève
- `modifier_etudiant(...)` / `modifier_note(...)` — mise à jour partielle (`UPDATE` dynamique selon les champs fournis)
- `archiver_etudiant(...)` / `restaurer_etudiant(...)` / `get_etudiants_archives()` — gestion de l'archivage (suppression douce)
- `get_kpis()` — indicateurs globaux (total, source, validité, archivage)
- `get_repartition_par_classe()` / `get_repartition_par_source()` — statistiques de répartition
- `get_moyenne_par_classe()` / `get_moyenne_par_classe_globale()` — moyennes par classe (base seule, puis base + JSON combinés)
- `get_top10_meilleures_moyennes()` — classement des meilleures moyennes

#### `backend/app/routes/health.py`
**Rôle** : route de vérification technique. `GET /health` teste que l'API répond et que la connexion à PostgreSQL fonctionne.

#### `backend/app/routes/etudiants.py`
**Rôle** : toutes les routes HTTP liées à la gestion des élèves. Fait uniquement le lien entre les requêtes web et les fonctions de `models.py` — aucune logique métier écrite directement ici.
**Routes** : `GET /etudiants`, `POST /etudiants`, `POST /etudiants/importer`, `PATCH /etudiants/{id}`, `PATCH /etudiants/{id}/notes/{matiere}`, `PATCH /etudiants/{id}/archiver`, `PATCH /etudiants/{id}/restaurer`, `GET /etudiants/archives`.

#### `backend/app/routes/stats.py`
**Rôle** : routes statistiques pour alimenter le tableau de bord. Chaque route appelle la fonction correspondante de `models.py`.

#### `backend/requirements.txt`
**Rôle** : liste des dépendances Python du projet (`fastapi`, `uvicorn`, `psycopg2-binary`, `pydantic`, `pydantic-settings`, `python-dotenv`).

#### `database/init.sql`
**Rôle** : script SQL de création du schéma de base de données — sert aussi de documentation exécutable de la structure des données. Contient les 3 tables, leurs contraintes (clés étrangères, `UNIQUE`, `ON DELETE CASCADE`), et les 8 index de performance.

### Frontend

#### `frontend/index.html`
**Rôle** : page principale — le registre des élèves. En-tête avec statistiques rapides, onglets (Registre / Archives), zone de filtres, tableau paginé avec cases à cocher pour l'import, modale d'ajout d'élève.

#### `frontend/dashboard.html`
**Rôle** : page du tableau de bord statistique. Bandeau de résumé en langage naturel, grille de 6 indicateurs clés (KPIs), 4 zones de graphiques, section des élèves archivés.

#### `frontend/css/style.css`
**Rôle** : système de design complet du projet — variables de couleurs/typographie centralisées (`:root`), styles du header, cartes, tableau, boutons, badges "tampon" (origine des données), modale, dashboard, responsive mobile.

#### `frontend/js/api.js`
**Rôle** : unique point de communication entre le frontend et l'API backend. Aucun autre fichier JS n'appelle `fetch()` directement. Contient l'objet `api` regroupant une fonction par endpoint, et une fonction utilitaire `apiFetch` qui gère les en-têtes et les erreurs de façon uniforme.

#### `frontend/js/main.js`
**Rôle** : logique interactive de la page `index.html`.
**Fonctions principales** : `chargerListe()` (récupère et affiche la page courante), `ligneHTML(e)` (génère le HTML d'une ligne selon son origine), `chargerStatsRapides()` / `chargerClasses()` (alimentent l'en-tête et les filtres), `attacherEvenementsLignes()` (branche cases à cocher, archivage, édition), `activerEditionCellule(cell)` (édition au double-clic), `chargerArchives()` et fonctions associées (gestion de l'onglet Archives), `debounce()` (limite la fréquence des appels API pendant la frappe), gestion complète de la modale d'ajout.

#### `frontend/js/dashboard.js`
**Rôle** : logique du tableau de bord — récupère les statistiques et construit les graphiques Chart.js.
**Fonctions principales** : `chargerResume()` (phrase de synthèse), `chargerKpis()` (6 cartes d'indicateurs), `chargerGraphClasse()` / `chargerGraphSource()` / `chargerGraphMoyenne()` (graphiques Chart.js avec titres d'axes et info-bulles personnalisées), `chargerTop10()` (classement des meilleures moyennes), `chargerArchivesDashboard()` (tableau des élèves archivés).

#### `frontend/js/chart.umd.min.js`
**Rôle** : librairie Chart.js hébergée en local dans le projet plutôt qu'un CDN externe, pour garantir que le tableau de bord fonctionne même sans dépendre d'une connexion internet fiable au moment de la démonstration.

---

## 📌 Notes de conception

- **Pas d'ORM** : toutes les requêtes SQL sont écrites manuellement avec `psycopg2`, conformément aux exigences du projet — choix pédagogique pour maîtriser le SQL sous-jacent plutôt que de le masquer derrière une abstraction.
- **Validation à deux niveaux** : les données sont validées côté API (Pydantic, avant toute écriture) et lors de l'import JSON (les notes hors plage 0–20 sont détectées et rapportées sans bloquer l'import).
- **Séparation stricte des responsabilités** : chaque fichier backend a un rôle unique (connexion, validation, logique métier, routes), suivant un principe de responsabilité unique appliqué de bout en bout — le frontend ne parle jamais directement à la base de données, uniquement à l'API.

---

## 



