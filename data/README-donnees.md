# Jeu de données — Réseau des Médiathèques de la Métropole Lilloise

> Document remis aux apprenants avec l'énoncé du TP.
> Ces fichiers sont des exports du système de gestion du réseau. Ils vous
> sont livrés tels qu'ils ont été produits, sans retraitement.

## Les quatre fichiers

| Fichier | Lignes | Contenu |
|---|---|---|
| `mediatheques.csv` | 6 | Les sites du réseau |
| `documents.csv` | 426 | Le catalogue : livres, DVD, CD, numérique |
| `adherents.csv` | 240 | Les adhérents inscrits |
| `emprunts.csv` | 5 215 | Les emprunts de septembre 2025 à septembre 2026 |

Encodage : UTF-8. Séparateur : virgule. Première ligne : en-têtes.

## mediatheques.csv

| Colonne | Type | Description |
|---|---|---|
| `code_site` | texte | Identifiant du site, par exemple `MED-LIL` |
| `nom` | texte | Nom de la médiathèque |
| `commune` | texte | Commune d'implantation |
| `annee_ouverture` | entier | Année d'ouverture au public |
| `surface_m2` | entier | Surface en mètres carrés |

## documents.csv

| Colonne | Type | Description |
|---|---|---|
| `id_document` | entier | Identifiant du document |
| `isbn` | texte | Code ISBN |
| `titre` | texte | Titre du document |
| `auteur` | texte | Auteur ou autrice |
| `genre` | texte | Roman, Policier, BD, Documentaire, Jeunesse, Poesie, Manga, Essai |
| `support` | texte | Livre, DVD, CD, Livre numerique |
| `annee_publication` | entier | Année de publication |
| `code_site` | texte | Site de rattachement du document |
| `prix_achat` | décimal | Prix d'acquisition en euros |

## adherents.csv

| Colonne | Type | Description |
|---|---|---|
| `id_adherent` | entier | Identifiant de l'adhérent |
| `nom`, `prenom` | texte | Identité |
| `code_postal` | texte | Code postal de résidence |
| `tranche_age` | texte | Moins de 14 ans, 14-25 ans, 26-59 ans, 60 ans et plus |
| `date_inscription` | date | Date de première inscription |
| `code_site` | texte | Site d'inscription |
| `abonnement_actif` | texte | `oui` ou `non` |

## emprunts.csv

| Colonne | Type | Description |
|---|---|---|
| `id_emprunt` | texte | Identifiant de l'emprunt, préfixé `E` |
| `id_document` | entier | Document emprunté |
| `id_adherent` | entier | Adhérent emprunteur |
| `code_site` | texte | Site où l'emprunt a été effectué |
| `date_emprunt` | date | Date de l'emprunt |
| `date_retour_prevue` | date | Date de retour prévue |
| `date_retour_reelle` | date | Date de retour effective |

## Avertissement du service informatique du réseau

Ces exports proviennent de trois logiciels différents, utilisés
successivement depuis 2011. La reprise des données lors des changements
d'outil n'a jamais été auditée. Le service ne garantit donc ni
l'exhaustivité, ni l'homogénéité des formats, ni l'absence de doublons.

Une partie de votre travail consiste précisément à établir cet état des
lieux avant toute analyse.
