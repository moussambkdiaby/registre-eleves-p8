-- Table des étudiants
CREATE TABLE etudiants (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(20) UNIQUE NOT NULL,
    code VARCHAR(20),
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    date_naissance DATE,
    classe VARCHAR(20) NOT NULL,
    archive BOOLEAN DEFAULT FALSE,
    date_creation TIMESTAMP DEFAULT NOW()
);

-- Table des matières
CREATE TABLE matieres (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) UNIQUE NOT NULL
);

-- Table des notes (lien entre étudiants et matières)
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    etudiant_id INTEGER REFERENCES etudiants(id) ON DELETE CASCADE,
    matiere_id INTEGER REFERENCES matieres(id),
    devoirs NUMERIC(4,2)[],
    examen NUMERIC(4,2),
    moyenne NUMERIC(4,2),
    UNIQUE(etudiant_id, matiere_id)
);

-- Matières de base
INSERT INTO matieres (nom) VALUES
('Math'), ('Francais'), ('Anglais'), ('PC'), ('SVT'), ('HG');

-- ===== INDEX =====

-- Recherche par numéro (déjà rapide grâce à UNIQUE, qui crée un index automatiquement)
-- Recherche par code
CREATE INDEX idx_etudiants_code ON etudiants(code);

-- Recherche par nom / prénom (l'utilisateur cherche souvent par nom)
CREATE INDEX idx_etudiants_nom ON etudiants(nom);
CREATE INDEX idx_etudiants_prenom ON etudiants(prenom);

-- Filtrage par classe (utilisé pour pagination ET pour "répartition par classe")
CREATE INDEX idx_etudiants_classe ON etudiants(classe);

-- Filtrage par archive (chaque requête de liste exclut les archivés : WHERE archive = FALSE)
CREATE INDEX idx_etudiants_archive ON etudiants(archive);

-- Index composite : la requête la plus fréquente sera "classe non archivée"
CREATE INDEX idx_etudiants_classe_archive ON etudiants(classe, archive);

-- Accélère les jointures notes <-> etudiants (utilisé pour moyenne générale, top 10)
CREATE INDEX idx_notes_etudiant ON notes(etudiant_id);
CREATE INDEX idx_notes_matiere ON notes(matiere_id);