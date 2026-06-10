-- ============================================
-- PROJET DEV DATA P8
-- Script de création de la base de données
-- ============================================

-- Supprimer les tables si elles existent déjà
-- (utile pour réinitialiser proprement)
-- L'ordre de suppression est l'INVERSE de la création
-- car les clés étrangères doivent être supprimées en premier

DROP TABLE IF EXISTS devoir CASCADE;
DROP TABLE IF EXISTS resultat_matiere CASCADE;
DROP TABLE IF EXISTS matiere CASCADE;
DROP TABLE IF EXISTS etudiant CASCADE;
DROP TABLE IF EXISTS classe CASCADE;

-- ============================================
-- TABLE CLASSE
-- Première table car aucune dépendance
-- ============================================
CREATE TABLE classe (
    id_classe   SERIAL PRIMARY KEY,
    libelle     VARCHAR(20) NOT NULL UNIQUE
);

-- ============================================
-- TABLE MATIERE
-- Indépendante, aucune clé étrangère
-- ============================================
CREATE TABLE matiere (
    id_matiere  SERIAL PRIMARY KEY,
    libelle     VARCHAR(50) NOT NULL UNIQUE
);

-- ============================================
-- TABLE ETUDIANT
-- Dépend de CLASSE via id_classe
-- ============================================
CREATE TABLE etudiant (
    id_etudiant     SERIAL PRIMARY KEY,

    -- Code saisie du projet précédent (ex: AAD004)
    code            VARCHAR(6) NOT NULL,

    -- Identifiant métier UNIQUE → détection doublons
    numero          VARCHAR(7) NOT NULL UNIQUE,

    nom             VARCHAR(100) NOT NULL,
    prenom          VARCHAR(100) NOT NULL,
    date_naissance  DATE NOT NULL,

    -- Moyenne calculée à l'import, stockée pour le dashboard
    moyenne_generale NUMERIC(5,2),

    -- Archivage logique : TRUE = archivé, exclu des listes
    est_archive     BOOLEAN NOT NULL DEFAULT FALSE,

    -- Validité : TRUE = valide, FALSE = invalide
    est_valide      BOOLEAN NOT NULL DEFAULT TRUE,

    -- Clé étrangère vers CLASSE
    -- RESTRICT : interdit de supprimer une classe
    -- si elle contient des étudiants
    id_classe       INTEGER NOT NULL
                    REFERENCES classe(id_classe)
                    ON DELETE RESTRICT
);

-- ============================================
-- TABLE RESULTAT_MATIERE
-- Table associative ETUDIANT ↔ MATIERE
-- Contient la note d'examen et la moyenne
-- ============================================
CREATE TABLE resultat_matiere (
    id_resultat     SERIAL PRIMARY KEY,

    note_examen     NUMERIC(5,2) NOT NULL,

    -- Moyenne calculée selon : (moy_devoirs + 2×examen) / 3
    moyenne_matiere NUMERIC(5,2) NOT NULL,

    id_etudiant     INTEGER NOT NULL
                    REFERENCES etudiant(id_etudiant)
                    ON DELETE CASCADE,
                    -- CASCADE : si l'étudiant est supprimé,
                    -- ses résultats sont supprimés aussi

    id_matiere      INTEGER NOT NULL
                    REFERENCES matiere(id_matiere)
                    ON DELETE RESTRICT,

    -- Un étudiant ne peut pas avoir 2 lignes pour la même matière
    CONSTRAINT uq_etudiant_matiere UNIQUE (id_etudiant, id_matiere)
);

-- ============================================
-- TABLE DEVOIR
-- Gère le nombre variable de devoirs
-- ============================================
CREATE TABLE devoir (
    id_devoir   SERIAL PRIMARY KEY,
    note_devoir NUMERIC(5,2) NOT NULL,

    id_resultat INTEGER NOT NULL
                REFERENCES resultat_matiere(id_resultat)
                ON DELETE CASCADE
                -- CASCADE : si le résultat est supprimé,
                -- les devoirs associés le sont aussi
);

-- ============================================
-- DONNÉES INITIALES — Les 6 matières fixes
-- ============================================
INSERT INTO matiere (libelle) VALUES
    ('Math'),
    ('Francais'),
    ('Anglais'),
    ('PC'),
    ('SVT'),
    ('HG');

-- ============================================
-- INDEX pour accélérer les recherches
-- ============================================

-- Recherche fréquente par numéro
CREATE INDEX idx_etudiant_numero
    ON etudiant(numero);

-- Recherche fréquente par nom/prénom
CREATE INDEX idx_etudiant_nom
    ON etudiant(nom, prenom);

-- Filtrage fréquent par classe
CREATE INDEX idx_etudiant_classe
    ON etudiant(id_classe);

-- Filtrage des archives
CREATE INDEX idx_etudiant_archive
    ON etudiant(est_archive);