-- Question 1 : activite par mediatheque (documents, adherents, emprunts)
SELECT
    m.nom,
    m.commune,
    (
        SELECT COUNT(*)
        FROM document d
        WHERE d.code_site = m.code_site
    ) AS nb_documents,
    (
        SELECT COUNT(*)
        FROM adherent a
        WHERE a.code_site = m.code_site
    ) AS nb_adherents,
    (
        SELECT COUNT(*)
        FROM emprunt e
        WHERE e.code_site = m.code_site
    ) AS nb_emprunts
FROM mediatheque m
ORDER BY nb_emprunts DESC;
-- 6 lignes retournees

-- Question 2 : nombre d'emprunts par mois (septembre 2025 a septembre 2026)
SELECT
    to_char(e.date_emprunt, 'YYYY-MM') AS mois,
    COUNT(*) AS nb_emprunts
FROM emprunt e
WHERE e.date_emprunt >= DATE '2025-09-01'
  AND e.date_emprunt < DATE '2026-10-01'
GROUP BY to_char(e.date_emprunt, 'YYYY-MM')
ORDER BY mois;
-- 13 lignes retournees

-- Question 3 : top 10 des documents les plus empruntes
SELECT
    d.titre,
    d.auteur,
    d.genre,
    d.support,
    m.nom AS mediatheque,
    COUNT(*) AS nb_emprunts
FROM emprunt e
JOIN document d ON d.id_document = e.id_document
JOIN mediatheque m ON m.code_site = d.code_site
GROUP BY d.id_document, d.titre, d.auteur, d.genre, d.support, m.nom
ORDER BY nb_emprunts DESC
LIMIT 10;
-- 10 lignes retournees

-- Question 4 : taux de retard par mediatheque (emprunts clos uniquement)
SELECT
    m.nom,
    m.commune,
    COUNT(*) AS nb_emprunts_clos,
    COUNT(*) FILTER (
        WHERE e.date_retour_reelle > e.date_retour_prevue
    ) AS nb_emprunts_en_retard,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE e.date_retour_reelle > e.date_retour_prevue
        ) / COUNT(*),
        1
    ) AS taux_retard_pct
FROM emprunt e
JOIN mediatheque m ON m.code_site = e.code_site
WHERE e.date_retour_reelle IS NOT NULL
GROUP BY m.code_site, m.nom, m.commune
ORDER BY taux_retard_pct DESC;
-- 6 lignes retournees

-- Question 5 : genres avec plus de 400 emprunts
SELECT
    d.genre,
    COUNT(*) AS nb_emprunts
FROM emprunt e
JOIN document d ON d.id_document = e.id_document
GROUP BY d.genre
HAVING COUNT(*) > 400
ORDER BY nb_emprunts DESC;
-- 8 lignes retournees

-- Question 6 : adherents ayant emprunte strictement plus de 30 fois
SELECT
    a.nom,
    a.prenom,
    a.tranche_age,
    m.nom AS mediatheque,
    COUNT(*) AS nb_emprunts
FROM emprunt e
JOIN adherent a ON a.id_adherent = e.id_adherent
JOIN mediatheque m ON m.code_site = a.code_site
GROUP BY a.id_adherent, a.nom, a.prenom, a.tranche_age, m.nom
HAVING COUNT(*) > 30
ORDER BY nb_emprunts DESC;
-- 11 lignes retournees

-- Question 7 : document le plus emprunte du fonds de chaque mediatheque
WITH classement AS (
    SELECT
        d.code_site,
        m.nom AS mediatheque,
        d.titre,
        COUNT(*) AS nb_emprunts,
        ROW_NUMBER() OVER (
            PARTITION BY d.code_site
            ORDER BY COUNT(*) DESC, d.id_document
        ) AS rang
    FROM emprunt e
    JOIN document d ON d.id_document = e.id_document
    JOIN mediatheque m ON m.code_site = d.code_site
    GROUP BY d.code_site, m.nom, d.id_document, d.titre
)
SELECT
    mediatheque,
    titre,
    nb_emprunts
FROM classement
WHERE rang = 1
ORDER BY mediatheque;
-- 6 lignes retournees

-- Question 8 : duree moyenne de pret (globale puis par support), emprunts clos
SELECT
    support,
    duree_moyenne_jours
FROM (
    SELECT
        'Tous supports' AS support,
        ROUND(AVG(e.date_retour_reelle - e.date_emprunt)::numeric, 1) AS duree_moyenne_jours
    FROM emprunt e
    WHERE e.date_retour_reelle IS NOT NULL

    UNION ALL

    SELECT
        d.support,
        ROUND(AVG(e.date_retour_reelle - e.date_emprunt)::numeric, 1) AS duree_moyenne_jours
    FROM emprunt e
    JOIN document d ON d.id_document = e.id_document
    WHERE e.date_retour_reelle IS NOT NULL
    GROUP BY d.support
) AS durees
ORDER BY duree_moyenne_jours DESC;
-- 5 lignes retournees (1 globale + 4 supports)

-- Cout estime :
-- Les requetes 1, 3, 5, 6 et 7 parcourent toute la table emprunt (~5000 lignes)
-- avec des jointures et des agregats : ce sont les plus lourdes.
-- La question 7 ajoute une fenetre PARTITION BY apres le GROUP BY.
-- La question 2 reste plus legere grace a l'index sur date_emprunt et un
-- simple GROUP BY mensuel. La question 4 filtre les emprunts clos puis
-- agrege par site ; l'index sur code_site aide, mais le scan reste large.
-- Sans index sur document.genre ou adherent, les GROUP BY de 5 et 6
-- forcent un parcours + hash/aggregate sur le resultat joint.
