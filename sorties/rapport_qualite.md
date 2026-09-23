# Rapport qualité des données RMML

## Tableau récapitulatif des anomalies

| Fichier | Colonne | Description | Lignes | Part (%) | Traitement |
|---|---|---|---:|---:|---|
| `documents.csv` | `toutes` | Lignes en doublon strict (identiques sur toutes les colonnes) | 6 | 1.41 | Suppression des doublons (une occurrence conservée). Les lignes identiques fausseraient les effectifs du catalogue. |
| `documents.csv` | `annee_publication` | Année de publication vide | 14 | 3.29 | Conservation en l'état avec signalement. On ne peut pas inventer une année sans source fiable. |
| `documents.csv` | `annee_publication` | Année de publication postérieure à 2026 (impossible) | 4 | 0.94 | Mise à valeur manquante explicite. Une année future ne doit pas rester comme une date valide. |
| `documents.csv` | `prix_achat` | Prix d'achat vide | 9 | 2.11 | Conservation en l'état avec signalement. Un 0 ferait croire à un document gratuit et biaiserait les moyennes. |
| `documents.csv` | `auteur` | Auteur écrit intégralement en majuscules | 7 | 1.64 | Correction automatique de la casse (première lettre de chaque mot en majuscule) pour coller au reste du catalogue. |
| `documents.csv` | `genre` | Espaces parasites en début ou fin de genre | 5 | 1.17 | Correction automatique : suppression des espaces en trop. Ils créaient de fausses catégories distinctes. |
| `adherents.csv` | `code_postal` | Code postal vide | 11 | 4.58 | Conservation en l'état avec signalement. Un code postal ne peut pas être inventé sans risque d'erreur. |
| `adherents.csv` | `tranche_age` | Tranche d'âge valant "inconnu" | 6 | 2.5 | Conservation en l'état avec signalement. "Inconnu" reste une information utile, ce n'est pas une erreur à effacer. |
| `adherents.csv` | `date_inscription` | Date d'inscription au format JJ/MM/AAAA au lieu de AAAA-MM-JJ | 5 | 2.08 | Correction automatique vers le format AAAA-MM-JJ, pour comparer et charger les dates sans ambiguïté. |
| `emprunts.csv` | `toutes` | Lignes en doublon strict | 15 | 0.29 | Suppression des doublons (une occurrence conservée). |
| `emprunts.csv` | `id_document` | Emprunt pointant vers un document absent du catalogue | 23 | 0.44 | Suppression de la ligne. Ces emprunts ne pourraient pas être reliés au catalogue en base de données. |
| `emprunts.csv` | `date_retour_reelle / date_emprunt` | Date de retour réelle antérieure à la date d'emprunt | 12 | 0.23 | Suppression de la ligne (chronologie impossible). Les emprunts en cours, sans date de retour, sont conservés. |

## Effectifs avant / après nettoyage

| Fichier | Avant | Après | Écart |
|---|---:|---:|---:|
| `documents.csv` | 426 | 420 | -6 |
| `adherents.csv` | 240 | 240 | 0 |
| `emprunts.csv` | 5215 | 5165 | -50 |

## Cas métier normal (non compté comme anomalie)

Les emprunts sans date de retour réelle sont des prêts en cours (179 lignes). On les a conservés tels quels.

## Points d'attention pour la direction

Les fichiers ont des défauts, mais en petit nombre. Sur le catalogue, chaque problème touche moins de 4 % des fiches.

Certaines fiches documents sont en double à l'identique. Si on ne les enlève pas, on compte trop de documents et on fausse les classements d'emprunts.

23 emprunts concernent un document qui n'existe pas (identifiant 99999). On les a retirés : on ne peut pas les rattacher au catalogue, et une base de données propre les refuserait.

Quelques dates de retour sont antérieures à la date d'emprunt. Ces cas ont été retirés. Les prêts encore ouverts, sans date de retour, sont en revanche normaux : on les a gardés.

Le catalogue contient aussi des années de publication dans le futur, et des années ou des prix non renseignés. On n'a rien inventé : les années impossibles sont passées en "non renseigné", le reste est seulement signalé.

Chez les adhérents, des codes postaux manquent et quelques tranches d'âge disent "inconnu". Ce n'est pas bloquant, mais on ne pourra pas bien analyser le territoire ni l'âge des usagers tant que la saisie n'est pas reprise.

Il faudrait corriger à la source, dans les logiciels de prêt, les documents orphelins et les dates incohérentes. Sinon, chaque nouvelle extraction reproduira les mêmes écarts.
