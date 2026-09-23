DROP TABLE IF EXISTS emprunt CASCADE;
DROP TABLE IF EXISTS adherent CASCADE;
DROP TABLE IF EXISTS document CASCADE;
DROP TABLE IF EXISTS mediatheque CASCADE;

CREATE TABLE mediatheque (
    code_site        CHAR(7) PRIMARY KEY,
    nom              VARCHAR(100) NOT NULL,
    commune          VARCHAR(100) NOT NULL,
    annee_ouverture  INTEGER NOT NULL,
    surface_m2       INTEGER NOT NULL
);

CREATE TABLE document (
    id_document        INTEGER PRIMARY KEY,
    isbn               VARCHAR(20),
    titre              VARCHAR(200) NOT NULL,
    auteur             VARCHAR(100) NOT NULL,
    genre              VARCHAR(50) NOT NULL,
    support            VARCHAR(50) NOT NULL,
    annee_publication  INTEGER,
    code_site          CHAR(7) NOT NULL,
    prix_achat         NUMERIC(7, 2),
    CONSTRAINT fk_document_mediatheque
        FOREIGN KEY (code_site) REFERENCES mediatheque (code_site)
);

CREATE TABLE adherent (
    id_adherent        INTEGER PRIMARY KEY,
    nom                VARCHAR(100) NOT NULL,
    prenom             VARCHAR(100) NOT NULL,
    code_postal       VARCHAR(10),
    tranche_age        VARCHAR(30) NOT NULL,
    date_inscription   DATE NOT NULL,
    code_site          CHAR(7) NOT NULL,
    abonnement_actif   BOOLEAN NOT NULL,
    CONSTRAINT fk_adherent_mediatheque
        FOREIGN KEY (code_site) REFERENCES mediatheque (code_site)
);

CREATE TABLE emprunt (
    id_emprunt          CHAR(7) PRIMARY KEY,
    id_document         INTEGER NOT NULL,
    id_adherent         INTEGER NOT NULL,
    code_site           CHAR(7) NOT NULL,
    date_emprunt        DATE NOT NULL,
    date_retour_prevue  DATE NOT NULL,
    date_retour_reelle  DATE,
    CONSTRAINT fk_emprunt_document
        FOREIGN KEY (id_document) REFERENCES document (id_document),
    CONSTRAINT fk_emprunt_adherent
        FOREIGN KEY (id_adherent) REFERENCES adherent (id_adherent),
    CONSTRAINT fk_emprunt_mediatheque
        FOREIGN KEY (code_site) REFERENCES mediatheque (code_site),
    CONSTRAINT chk_emprunt_dates
        CHECK (date_retour_prevue >= date_emprunt)
);

-- Index pour les agrégats mensuels (analyses, question 2).
CREATE INDEX idx_emprunt_date_emprunt ON emprunt (date_emprunt);

-- Index pour les classements et jointures par document (questions 3 et 7).
CREATE INDEX idx_emprunt_id_document ON emprunt (id_document);

-- Index pour les stats par site (questions 1 et 4).
CREATE INDEX idx_emprunt_code_site ON emprunt (code_site);
