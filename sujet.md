# TP de révision — Pilotage de l'activité de prêt du RMML

Cursus PRF Concepteur développeur en science de la donnée (Data Analyst 02)
Titre professionnel RNCP39103 — M2i Villeneuve d'Ascq

---

## Cadre du TP

**Objet.** Ce TP est le travail de révision du cursus. Il mobilise, sur un seul
cas métier continu, l'ensemble des compétences travaillées depuis juillet 2026 :
Python et programmation orientée objet, SQL et PostgreSQL, pandas et qualité
des données, modélisation MCD/MLD, API REST avec FastAPI et SQLAlchemy, front
Streamlit avec requests.

**Durée.** 2 jours : le jour 1 de 09h00 à 18h15, le jour 2 de 09h00 à 17h00.

**Modalité.** Travail **individuel**. Le TP avance en 10 étapes. À la fin de
chaque étape, une **correction collective au tableau** est conduite par le
formateur : vous y présentez vos choix, vous comparez avec les autres solutions
proposées dans la salle, et vous repartez sur une base commune pour l'étape
suivante. Personne ne reste bloqué : si une étape résiste, vous la reprenez
après la correction collective et vous continuez.

**Outils requis.**

| Outil | Version attendue | Usage |
|---|---|---|
| Python | 3.12 | Étapes 1 à 10 |
| PostgreSQL | 14 ou supérieur | Étapes 4 à 10 |
| Un client SQL | pgAdmin, DBeaver ou la CLI `psql` | Étapes 4 à 6 |
| pandas | 2.x | Étapes 2, 3, 5 |
| FastAPI + Uvicorn | récents | Étapes 7 à 10 |
| SQLAlchemy | 2.x | Étapes 5, 7 à 10 |
| Streamlit, requests | récents | Étape 9 |
| Un éditeur | VS Code ou PyCharm | Tout le TP |
| Git | 2.x | Étape 10 |

**Données fournies.** Quatre fichiers CSV, déjà générés, placés dans le dossier
`data/` à la racine du projet. Vous ne les modifiez jamais : vous les lisez, et
vous écrivez vos résultats ailleurs.

| Fichier | Lignes de données | Colonnes |
|---|---|---|
| `data/mediatheques.csv` | 6 | `code_site`, `nom`, `commune`, `annee_ouverture`, `surface_m2` |
| `data/documents.csv` | 426 | `id_document`, `isbn`, `titre`, `auteur`, `genre`, `support`, `annee_publication`, `code_site`, `prix_achat` |
| `data/adherents.csv` | 240 | `id_adherent`, `nom`, `prenom`, `code_postal`, `tranche_age`, `date_inscription`, `code_site`, `abonnement_actif` |
| `data/emprunts.csv` | 5215 | `id_emprunt`, `id_document`, `id_adherent`, `code_site`, `date_emprunt`, `date_retour_prevue`, `date_retour_reelle` |

Tous les chemins que vous écrivez dans votre code sont **relatifs** à la racine
du projet : `data/documents.csv`, et non un chemin absolu de votre machine.

---

## Mise en situation

### Le commanditaire

Le **Réseau des Médiathèques de la Métropole Lilloise (RMML)** regroupe six
équipements publics, de tailles très différentes, ouverts entre 1972 et 2015 :

| Code site | Nom | Commune | Ouverture | Surface |
|---|---|---|---|---|
| `MED-LIL` | Médiathèque Jean-Levy | Lille | 1972 | 4200 m2 |
| `MED-ROU` | Médiathèque La Grand Plage | Roubaix | 2015 | 3100 m2 |
| `MED-TOU` | Médiathèque André Malraux | Tourcoing | 1998 | 2600 m2 |
| `MED-VIL` | Médiathèque Le Temps Libre | Villeneuve-d'Ascq | 2004 | 2200 m2 |
| `MED-ARM` | Médiathèque de l'Abbaye | Armentières | 1989 | 1500 m2 |
| `MED-SEC` | Médiathèque Le Quai | Seclin | 2011 | 1100 m2 |

Le réseau prête des livres, des livres numériques, des CD et des DVD. La carte
d'adhérent est valable sur les six sites. La direction du réseau dispose
aujourd'hui d'un logiciel de prêt par site, mais d'**aucune vision consolidée**
de son activité.

### La demande

Vous intervenez comme développeur data pour la direction du réseau. La commande
tient en une phrase : **donner au réseau un outil de pilotage de son activité de
prêt**, alimenté par les données d'exploitation, capable de répondre à quatre
questions que la direction se pose chaque mois.

1. Comment évolue le volume de prêts, mois par mois, sur l'ensemble du réseau ?
2. Quels documents tournent réellement, et lesquels dorment sur les rayons ?
3. Quels sites sont sous tension, c'est-à-dire où l'activité de prêt est la plus
   forte au regard de la collection et des effectifs disponibles ?
4. Quels adhérents sont actifs, et quelle part des prêts revient en retard ?

### Le brief de la directrice

Extraits de la réunion de cadrage avec Mme Valérie Dehaene, directrice du réseau.

> « Nous avons six logiciels, six manières de saisir, et zéro chiffre commun.
> Quand la Métropole me demande combien de prêts nous avons faits l'an dernier,
> je passe trois jours à recoller des exports Excel, et je ne suis jamais sûre
> du résultat. »

> « Ce que je veux, ce n'est pas un outil de plus. Je veux d'abord un socle
> fiable : une base unique, des chiffres que je peux redemander à tout moment
> par un simple appel, et un catalogue que mes agents consultent sans passer
> par six logiciels. »

> « Je vous préviens tout de suite sur les données. Elles viennent de systèmes
> différents, certaines ont été reprises à la main lors de la fusion des
> catalogues en 2021. Il y a des trous, il y a des doublons, il y a des dates
> qui n'ont pas de sens. Je ne veux pas que vous me sortiez un chiffre propre
> en cachant la poussière sous le tapis : je veux savoir ce que vous avez
> corrigé et ce que vous avez écarté, et pourquoi. »

> « Côté accès : mes agents de terrain doivent pouvoir consulter le catalogue,
> mais les chiffres consolidés du réseau, les indicateurs par site, ce n'est pas
> une information publique. Cela reste entre la direction et moi. »

### Les contraintes

- **Équipe réduite.** Le réseau n'a pas de service informatique. Une seule
  personne, à mi-temps, reprendra la maintenance. Votre code doit être lisible,
  commenté là où c'est utile, et documenté dans un README.
- **Budget.** Aucun achat de licence. Tout repose sur la base PostgreSQL déjà
  disponible et sur des bibliothèques Python libres.
- **Qualité des données inégale.** Les quatre fichiers sont des extractions
  brutes des systèmes d'origine. Ils contiennent des anomalies réelles. Les
  détecter, les quantifier et décider de leur traitement fait partie du travail
  demande, ce n'est pas un incident.
- **Confidentialité.** Les données nominatives des adhérents ne sortent jamais
  des écrans de travail : aucun export nominatif, aucune diffusion.

### Ce que vous construisez sur deux jours

Au terme des 10 étapes, vous livrez une chaîne complète et fonctionnelle :

```
CSV bruts -> nettoyage -> base PostgreSQL -> API FastAPI -> front Streamlit
```

Le jour 1 construit le socle données : lecture Python, manipulation pandas,
qualité, modélisation, chargement en base, requêtes d'analyse. Le jour 2
construit l'application : API REST, endpoints analytiques, front catalogue,
finalisation.

---

## Organisation des deux jours

### Jour 1 — Python, données et base (09h00 - 18h15)

| Créneau | Étape | Durée | Niveau |
|---|---|---|---|
| 09h00 - 09h45 | Étape 1 — Python de base | 45 min | Facile |
| 09h45 - 10h00 | Correction collective étape 1 | 15 min | |
| 10h00 - 10h45 | Étape 2 — pandas | 45 min | Facile à moyen |
| 10h45 - 11h00 | Correction collective étape 2 | 15 min | |
| 11h00 - 12h15 | Étape 3 — Qualité des données | 1 h 15 | Moyen |
| 12h15 - 13h15 | Pause déjeuner | | |
| 13h15 - 13h30 | Correction collective étape 3 | 15 min | |
| 13h30 - 14h45 | Étape 4 — Modélisation et DDL | 1 h 15 | Moyen |
| 14h45 - 15h00 | Correction collective étape 4 | 15 min | |
| 15h00 - 16h30 | Étape 5 — Chargement en base | 1 h 30 | Moyen à difficile |
| 16h30 - 16h45 | Correction collective étape 5 | 15 min | |
| 16h45 - 18h00 | Étape 6 — SQL d'analyse | 1 h 15 | Difficile |
| 18h00 - 18h15 | Correction collective étape 6 et bilan du jour 1 | 15 min | |

### Jour 2 — API et front (09h00 - 17h00)

| Créneau | Étape | Durée | Niveau |
|---|---|---|---|
| 09h00 - 10h45 | Étape 7 — API FastAPI | 1 h 45 | Moyen |
| 10h45 - 11h00 | Correction collective étape 7 | 15 min | |
| 11h00 - 12h45 | Étape 8 — Endpoints d'analyse | 1 h 45 | Moyen à difficile |
| 12h45 - 13h00 | Correction collective étape 8 | 15 min | |
| 13h00 - 14h00 | Pause déjeuner | | |
| 14h00 - 16h00 | Étape 9 — Front Streamlit catalogue | 2 h | Moyen à difficile |
| 16h00 - 16h15 | Correction collective étape 9 | 15 min | |
| 16h15 - 17h00 | Étape 10 — Finalisation et restitutions | 45 min | Synthèse |

Le jour 2 est volontairement plus court que le jour 1 : les étapes 8 et 9 y
disposent de plus de temps que la stricte addition des durées ne le laisse
croire, et la fin de journée est dégagée pour que les restitutions orales se
tiennent sans être bousculées.

**Comment se déroule une correction collective.** Le formateur reprend l'étape
au tableau, interroge deux ou trois solutions différentes de la salle, et
dégage la version de référence. Vous notez les écarts avec votre propre
solution. Cette référence est celle sur laquelle l'étape suivante s'appuie :
si votre étape n'est pas terminée, vous la reprenez après la correction sans
prendre de retard sur la suite.

### Arborescence de travail

Créez cette arborescence dès le début du jour 1 et respectez-la : les noms de
fichiers attendus à chaque étape en dépendent.

```
tp-rmml/
  data/                 (les 4 CSV fournis, jamais modifies)
  etape01/
  etape02/
  etape03/
  etape04/
  etape05/
  etape06/
  api/
  front/
  sorties/              (tous les fichiers produits : CSV, JSON, rapports)
  README.md
```

---

## Étape 1 — Python de base : lire les données sans pandas

**Durée : 45 min — Niveau : facile**

### Objectif

Réviser les fondamentaux Python : lecture de fichiers, module `csv`,
structures de données (listes, dictionnaires, ensembles), fonctions,
comptages avec `collections.Counter`, et une classe simple. Aucun import de
pandas n'est autorisé à cette étape.

### Consignes

1. Créez le fichier `etape01/exploration.py`.
2. Écrivez une fonction `lire_csv(chemin)` qui ouvre un fichier CSV en UTF-8,
   le lit avec `csv.DictReader` et renvoie une **liste de dictionnaires**.
   Elle doit fonctionner pour les quatre fichiers sans modification.
3. Écrivez une fonction `compter_par(lignes, colonne)` qui renvoie un
   dictionnaire associant chaque valeur distincte de `colonne` à son nombre
   d'occurrences. Vous pouvez utiliser `collections.Counter`.
4. Écrivez une classe `Mediatheque` avec les attributs `code_site`, `nom`,
   `commune`, `annee_ouverture`, `surface_m2`. Ajoutez-lui :
   - une méthode `anciennete(annee_reference)` qui renvoie le nombre d'années
     écoulées depuis l'ouverture ;
   - une méthode `__str__` qui renvoie une ligne lisible, par exemple
     `MED-LIL — Mediatheque Jean-Levy (Lille), 4200 m2`.
5. Dans un bloc `if __name__ == "__main__":`, affichez dans cet ordre :
   - le nombre de lignes de chacun des quatre fichiers ;
   - la liste des six objets `Mediatheque` construits depuis
     `data/mediatheques.csv`, avec leur ancienneté calculée pour 2026 ;
   - le nombre d'emprunts par `code_site`, triés du plus grand au plus petit ;
   - le nombre de documents par `support` ;
   - le nombre d'adhérents par `tranche_age`.
6. Écrivez enfin une fonction `emprunts_en_cours(emprunts)` qui renvoie la
   liste des emprunts dont `date_retour_reelle` est vide, et affichez leur
   nombre. Un emprunt sans date de retour réelle est un prêt **en cours**, ce
   n'est pas une erreur.
7. Aucune valeur en dur dans les fonctions : les chemins de fichiers sont des
   paramètres ou des constantes déclarées en haut du module.

### Livrable

`etape01/exploration.py`

### Vérifiez vous-même

- Le comptage des lignes doit donner exactement : 6 médiathèques,
  426 documents, 240 adhérents, 5215 emprunts.
- Les emprunts par site doivent être, dans l'ordre décroissant :
  `MED-TOU` 1103, `MED-ARM` 1023, `MED-LIL` 977, `MED-ROU` 812,
  `MED-SEC` 711, `MED-VIL` 589. Le total de ces six nombres vaut 5215.
- Les supports doivent donner : `Livre` 233, `CD` 68, `DVD` 64,
  `Livre numerique` 61.
- `emprunts_en_cours` doit renvoyer 179 emprunts.

<details><summary>Indice 1</summary>

`csv.DictReader` renvoie un itérateur : pour obtenir une liste, enveloppez-le
avec `list(...)`. Ouvrez le fichier avec `open(chemin, encoding="utf-8",
newline="")` pour éviter les lignes vides parasites sous Windows.

</details>

<details><summary>Indice 2</summary>

Pour trier un dictionnaire de comptages du plus grand au plus petit, deux
pistes : `Counter.most_common()` qui renvoie directement une liste de couples
triée, ou `sorted(d.items(), key=lambda couple: couple[1], reverse=True)`.

</details>

<details><summary>Indice 3</summary>

Une chaîne vide est fausse en contexte booléen. Pour tester qu'une date de
retour est absente, `if not ligne["date_retour_reelle"].strip():` couvre à la
fois la chaîne vide et la chaîne faite d'espaces.

</details>

---

## Étape 2 — pandas : chargement, typage, agrégats et fusion

**Durée : 45 min — Niveau : facile à moyen**

### Objectif

Réviser la mécanique de pandas : chargement, typage des dates, exploration
d'un DataFrame, sélection de lignes et de colonnes, tri, `groupby`, fusion de
tables avec `merge`, et export CSV. L'étape porte sur la maîtrise de l'outil,
pas sur l'analyse des résultats : l'analyse exploratoire fait l'objet d'un
module dédié plus loin dans le cursus.

### Consignes

1. Créez le fichier `etape02/analyse_pandas.py`.
2. Chargez les quatre CSV dans quatre DataFrames : `df_sites`, `df_documents`,
   `df_adherents`, `df_emprunts`. Pour les emprunts, convertissez
   `date_emprunt`, `date_retour_prevue` et `date_retour_reelle` en dates avec
   `pd.to_datetime`.
3. Affichez pour `df_documents` et `df_emprunts` : la forme (`shape`), le
   résultat de `info()`, et le nombre de valeurs manquantes par colonne.
4. Produisez par du code les deux résultats suivants et affichez chacun avec
   un libellé clair. Aucun commentaire ni aucune interprétation ne sont
   demandés : seul le code qui produit le résultat est évalué.
   - a. Les 10 documents les plus chers (`titre`, `auteur`, `support`,
     `prix_achat`), triés par prix décroissant.
   - b. Le nombre de documents par `genre`, trié du plus fréquent au moins
     fréquent.
5. Construisez un DataFrame `df_complet` en fusionnant `df_emprunts` avec
   `df_documents` sur `id_document`, puis avec `df_adherents` sur
   `id_adherent`. Utilisez une jointure `left` depuis les emprunts. Affichez
   combien de lignes de `df_complet` n'ont pas trouvé de document
   correspondant.
6. À partir de `df_complet`, produisez le **top 10 des documents les plus
   empruntés** (`id_document`, `titre`, `auteur`, nombre d'emprunts) et
   exportez-le dans `sorties/top10_documents.csv`, sans index, en UTF-8.
7. Le script ne doit produire aucun avertissement pandas de type
   `SettingWithCopyWarning`.

### Livrable

`etape02/analyse_pandas.py` et `sorties/top10_documents.csv`

### Vérifiez vous-même

- `df_emprunts.shape` doit donner `(5215, 7)` et `df_documents.shape`
  `(426, 9)`.
- Après conversion, les trois colonnes de dates de `df_emprunts` doivent
  apparaître en `datetime64[ns]` dans `info()`, et non en `object`.
- Le comptage des valeurs manquantes de `date_retour_reelle` doit donner 179,
  le même nombre qu'à l'étape 1.
- Le comptage par `genre` doit renvoyer plus de huit libellés distincts.
  Notez-le sans le corriger : vous y reviendrez à l'étape 3.
- Après la fusion, exactement 23 lignes de `df_complet` n'ont pas de document
  correspondant. Notez ce chiffre, vous le réutiliserez à l'étape 3.
- `sorties/top10_documents.csv` contient 10 lignes de données plus l'en-tête,
  et le document en tête du classement totalise 24 emprunts.

<details><summary>Indice 1</summary>

Deux façons équivalentes de typer les dates : `parse_dates=[...]` directement
dans `pd.read_csv`, ou `pd.to_datetime(df["date_emprunt"])` après le
chargement. Vérifiez le résultat avec `df.dtypes` : tant que la colonne est
en `object`, elle est restée du texte.

</details>

<details><summary>Indice 2</summary>

Pour un comptage par modalité, `df["genre"].value_counts()` trie déjà du plus
fréquent au moins fréquent. `groupby("genre").size().sort_values(
ascending=False)` donne le même résultat en passant par `groupby`.

</details>

<details><summary>Indice 3</summary>

Après un `merge(how="left")`, les lignes sans correspondance ont des valeurs
manquantes dans les colonnes venues de la table de droite. Comptez-les avec
`df_complet["titre"].isna().sum()`, en choisissant une colonne qui ne peut pas
être vide dans la table d'origine.

</details>

---

## Étape 3 — Qualité des données : détecter, quantifier, décider

**Durée : 1 h 15 — Niveau : moyen**

### Objectif

Conduire un audit de qualité complet sur les trois tables métier, quantifier
chaque anomalie, décider d'un traitement argumenté, produire des fichiers
nettoyés et un rapport de qualité lisible par la directrice du réseau.

### Contexte

C'est le point dur du jour 1, et c'est la demande explicite de Mme Dehaene :
elle veut savoir ce que vous avez corrigé et ce que vous avez écarté. Un
chiffre juste sans justification ne vaut rien ici.

### Consignes

1. Créez le fichier `etape03/qualite.py`.
2. **Détectez et quantifiez** les catégories d'anomalies suivantes. Pour
   chacune, votre code doit produire un nombre de lignes concernées et un
   échantillon de 3 lignes fautives au maximum.

   Sur `documents.csv` :
   - a. lignes en doublon strict, c'est-à-dire identiques sur toutes les
     colonnes ;
   - b. `annee_publication` vide ;
   - c. `annee_publication` postérieure à l'année courante, donc impossible ;
   - d. `prix_achat` vide ;
   - e. `auteur` écrit intégralement en majuscules alors que la convention du
     catalogue est la casse normale ;
   - f. `genre` comportant des espaces parasites en début ou en fin de chaîne.

   Sur `adherents.csv` :
   - g. `code_postal` vide ;
   - h. `tranche_age` valant `inconnu` ;
   - i. `date_inscription` au format `JJ/MM/AAAA` au lieu du format ISO
     `AAAA-MM-JJ`.

   Sur `emprunts.csv` :
   - j. lignes en doublon strict ;
   - k. `id_document` ne correspondant à aucun document du catalogue ;
   - l. `date_retour_reelle` antérieure à `date_emprunt`, ce qui est
     chronologiquement impossible.

3. **Attention à un piège.** Les lignes dont `date_retour_reelle` est vide ne
   sont **pas** une anomalie : ce sont les emprunts en cours. Votre rapport
   doit les mentionner explicitement comme cas métier normal, avec leur
   nombre, et ne doit pas les compter comme défaut.
4. **Décidez d'un traitement** pour chaque anomalie détectée, parmi :
   suppression de la ligne, correction automatique, mise à valeur manquante
   explicite, ou conservation en l'état avec signalement. Chaque décision doit
   être justifiée en une à deux phrases dans le rapport.
5. **Produisez les fichiers nettoyés** dans `sorties/` :
   `documents_propre.csv`, `adherents_propre.csv`, `emprunts_propre.csv`.
   Ils doivent respecter les règles suivantes :
   - les doublons stricts sont supprimés, en conservant une occurrence ;
   - les `genre` sont débarrassés de leurs espaces parasites ;
   - les `auteur` sont ramenés à une casse homogène avec le reste du
     catalogue ;
   - toutes les `date_inscription` sont au format ISO `AAAA-MM-JJ` ;
   - les années de publication impossibles sont traitées selon votre décision,
     et cette décision est documentée ;
   - les emprunts pointant vers un document inexistant sont écartés, car ils
     casseraient la contrainte de clé étrangère à l'étape 4 ;
   - les emprunts à la chronologie impossible sont écartés.
6. **Rédigez le rapport** `sorties/rapport_qualite.md`. Il contient :
   - un tableau récapitulatif avec, pour chaque anomalie : le fichier, la
     colonne, la description, le nombre de lignes concernées, la part en
     pourcentage du fichier, et le traitement retenu ;
   - une section par fichier avec le nombre de lignes avant et après
     nettoyage ;
   - une section « points d'attention pour la direction » de 5 à 10 lignes,
     rédigée en français courant, sans jargon technique, qui signale les
     risques métier identifiés.
7. Le rapport doit être généré par le script, pas écrit à la main.

### Livrable

`etape03/qualite.py`, `sorties/documents_propre.csv`,
`sorties/adherents_propre.csv`, `sorties/emprunts_propre.csv`,
`sorties/rapport_qualite.md`

### Vérifiez vous-même

- Votre rapport doit recenser **douze** catégories d'anomalies, de a à l. Si
  vous en avez moins, une catégorie vous a échappé ; si vous en avez plus,
  vérifiez que vous n'avez pas compté les emprunts en cours comme défaut.
- Sur `documents.csv`, les six anomalies portent chacune sur **moins de 4 %**
  du fichier : aucun chiffre à deux chiffres de pourcentage n'est attendu. La
  plus fréquente des six touche entre 10 et 20 lignes.
- Sur `emprunts.csv`, le nombre de lignes pointant vers un document inexistant
  doit être **exactement celui que vous avez trouvé à l'étape 2** en comptant
  les lignes sans correspondance après la fusion. Si les deux nombres
  différent, l'une des deux étapes est fausse.
- `sorties/emprunts_propre.csv` doit contenir **moins de 5215 lignes** de
  données et **plus de 5150**. Si vous descendez sous 5000, vous avez
  probablement supprimé les emprunts en cours par erreur.
- Après nettoyage, `sorties/documents_propre.csv` ne doit plus contenir aucun
  `genre` différent de sa version sans espaces : le nombre de genres distincts
  doit tomber à 8.

<details><summary>Indice 1</summary>

Pour les doublons stricts en pandas, `df.duplicated()` sans argument marque
les lignes identiques sur toutes les colonnes, en laissant la première
occurrence à `False`. `df.duplicated().sum()` donne donc le nombre de lignes à
supprimer, et `df.drop_duplicates()` produit la version nettoyée.

</details>

<details><summary>Indice 2</summary>

Pour repérer un auteur tout en majuscules, comparez la chaîne à sa version
majuscule : `s == s.upper()`. Pensez à exclure les chaînes vides, qui
satisferaient le test. Pour les espaces parasites sur `genre`, le test est
`s != s.strip()`.

</details>

<details><summary>Indice 3</summary>

Les dates mélangées se traitent en deux passes : `pd.to_datetime(serie,
format="%Y-%m-%d", errors="coerce")` pour les ISO, puis un second
`pd.to_datetime(..., format="%d/%m/%Y", errors="coerce")` applique uniquement
là où la première passe a produit une valeur manquante. Combinez avec
`Series.fillna`.

</details>

<details><summary>Indice 4</summary>

Pour trouver les emprunts orphelins, construisez l'ensemble des identifiants
de documents valides et utilisez `~df_emprunts["id_document"].isin(ids)`.
Attention au type : si une colonne est lue en entier et l'autre en chaîne, le
test ne trouvera rien. Forcez les deux du même côté avec `astype(str)`.

</details>

---

## Étape 4 — Modélisation : MCD, MLD et script DDL PostgreSQL

**Durée : 1 h 15 — Niveau : moyen**

### Objectif

Réviser la modélisation : passage du besoin métier au MCD, dérivation du MLD,
puis traduction en DDL PostgreSQL avec les types, les clés et les contraintes
adaptées.

### Consignes

1. Créez le fichier `etape04/modelisation.md`.
2. **MCD.** Décrivez le modèle conceptuel du domaine : les quatre entités
   (médiathèque, document, adhérent, emprunt), leurs propriétés, les
   associations entre elles et les cardinalités. Vous pouvez le rendre sous
   forme de schéma textuel, de diagramme Mermaid, ou d'une image exportée d'un
   outil de modélisation placée dans `etape04/`.
3. **MLD.** Dérivez le modèle logique : les quatre relations avec, pour
   chacune, la clé primaire soulignée ou signalée, les clés étrangères, et le
   type retenu pour chaque attribut.
4. **Justifications.** Rédigez une section de 10 à 20 lignes justifiant :
   - le choix du type de la clé primaire de `emprunt`, sachant que les
     identifiants fournis sont de la forme `E102224` et non des entiers ;
   - le type retenu pour `prix_achat`, en expliquant pourquoi un type flottant
     est déconseillé pour une valeur monétaire ;
   - la représentation de `abonnement_actif`, dont les valeurs sources sont
     `oui` et `non` ;
   - le traitement de `date_retour_reelle`, qui doit pouvoir être absente pour
     les emprunts en cours ;
   - la présence de `code_site` à la fois sur `document`, sur `adherent` et
     sur `emprunt` : s'agit-il d'une redondance à supprimer, ou d'une
     information distincte à conserver ? Argumentez.
5. Créez le fichier `etape04/schema.sql`. Il doit :
   - se placer dans la base `rmml`, créée au préalable avec `createdb rmml` ;
   - créer les quatre tables `mediatheque`, `document`, `adherent`, `emprunt`
     dans cet ordre ;
   - déclarer une clé primaire sur chaque table ;
   - déclarer les clés étrangères de `document` et `adherent` vers
     `mediatheque`, et celles de `emprunt` vers `document`, `adherent` et
     `mediatheque` ;
   - déclarer les contraintes `NOT NULL` pertinentes, en autorisant la valeur
     nulle uniquement là où le métier le justifie ;
   - ajouter une contrainte `CHECK` garantissant que
     `date_retour_prevue` est postérieure ou égale à `date_emprunt` ;
   - ajouter au moins deux index sur des colonnes que vous savez devoir
     interroger fréquemment à l'étape 6, avec un commentaire SQL expliquant
     le choix.
6. Le script doit pouvoir être exécuté deux fois de suite sans erreur. Prévoyez
   les instructions de suppression préalable dans le bon ordre, ou l'usage de
   `CREATE TABLE IF NOT EXISTS`.
7. Les clés étrangères et les contraintes `CHECK` doivent être déclarées dans
   les `CREATE TABLE` : PostgreSQL les applique réellement, une insertion
   fautive doit donc échouer.

### Livrable

`etape04/modelisation.md` et `etape04/schema.sql`

### Vérifiez vous-même

- `psql -d rmml -f etape04/schema.sql` s'exécute sans erreur, deux fois
  d'affilée.
- `\dt` dans `psql -d rmml` retourne exactement quatre lignes.
- `SELECT COUNT(*) FROM information_schema.table_constraints WHERE
  constraint_schema = 'public' AND constraint_type = 'FOREIGN KEY';` retourne
  au moins 5.
- Une tentative d'insertion d'un emprunt avec un `code_site` inexistant, par
  exemple `MED-XXX`, doit être **refusée** par PostgreSQL avec une erreur de
  contrainte de clé étrangère.

<details><summary>Indice 1</summary>

Une clé primaire de la forme `E102224` est une chaîne de longueur fixe :
`CHAR(7)` convient et occupe moins de place qu'un `VARCHAR`. Si vous préférez
un entier engendré par la base (`GENERATED ALWAYS AS IDENTITY`, ou `SERIAL`),
conservez alors l'identifiant source dans une colonne `UNIQUE` : vous en aurez
besoin pour la reprise des données.

</details>

<details><summary>Indice 2</summary>

Pour une valeur monétaire, `NUMERIC(7,2)` stocke la valeur exacte. Un `REAL`
ou un `DOUBLE PRECISION` introduit des erreurs d'arrondi qui se voient dès la
première somme sur plusieurs centaines de lignes.

</details>

<details><summary>Indice 3</summary>

Les clés étrangères imposent un ordre de création et un ordre de suppression
opposés. Créez `mediatheque` en premier et `emprunt` en dernier ; supprimez
`emprunt` en premier et `mediatheque` en dernier.

</details>

---

## Étape 5 — Chargement : des CSV nettoyés vers PostgreSQL

**Durée : 1 h 30 — Niveau : moyen à difficile**

### Objectif

Écrire un script d'import robuste : connexion à la base, insertion par lots,
respect de l'ordre des dépendances, gestion des erreurs, journalisation, et
idempotence.

### Consignes

1. Créez le fichier `etape05/chargement.py`.
2. Le script lit **les fichiers nettoyés produits à l'étape 3**, dans
   `sorties/`, et non les CSV bruts. Seul `data/mediatheques.csv` est lu
   directement, puisqu'il ne comporte pas d'anomalie.
3. La connexion à la base ne doit jamais contenir de mot de passe écrit en dur
   dans le code. Utilisez des variables d'environnement, avec des valeurs par
   défaut raisonnables pour l'hôte, le port et le nom de base. Documentez les
   variables attendues en tête de fichier.
4. Utilisez SQLAlchemy 2 : créez un `Engine` avec `create_engine`, et exécutez
   vos instructions dans un bloc `with engine.begin() as conn:` pour disposer
   d'une transaction.
5. Chargez les quatre tables **dans l'ordre des dépendances** : médiathèques,
   puis documents et adhérents, puis emprunts.
6. **Idempotence.** Le script doit pouvoir être relancé autant de fois que
   nécessaire sans créer de doublon et sans échouer. Choisissez et documentez
   votre stratégie : vidage préalable des tables dans l'ordre inverse des
   dépendances, ou insertion avec gestion du conflit sur la clé primaire.
7. **Gestion des erreurs.** Une ligne refusée par la base ne doit pas
   interrompre le chargement des autres. Capturez les erreurs, comptez-les par
   table, et écrivez les lignes rejetées dans `sorties/rejets_chargement.csv`
   avec une colonne supplémentaire `motif_rejet`.
8. **Journalisation.** Utilisez le module `logging`, pas `print`. Le script
   affiche, pour chaque table : le nombre de lignes lues, le nombre inséré, le
   nombre rejeté, et la durée en secondes. Il affiche en fin d'exécution un
   récapitulatif.
9. Les insertions se font par lots d'au moins 500 lignes, pas ligne par ligne.
10. Le code est organisé en fonctions : une fonction par table plus une
    fonction `main()`, avec des annotations de type sur les signatures.

### Livrable

`etape05/chargement.py` et, s'il y a des rejets,
`sorties/rejets_chargement.csv`

### Vérifiez vous-même

- Après exécution, `SELECT COUNT(*) FROM mediatheque;` retourne 6 et
  `SELECT COUNT(*) FROM adherent;` retourne 240.
- Le nombre de lignes de `document` et de `emprunt` correspond exactement au
  nombre de lignes de vos fichiers nettoyés de l'étape 3. Vérifiez-le par
  comparaison directe, pas de mémoire.
- **Relancez le script une seconde fois** : les comptages doivent être
  strictement identiques, et le script ne doit produire aucune erreur.
- `SELECT COUNT(*) FROM emprunt e LEFT JOIN document d ON e.id_document =
  d.id_document WHERE d.id_document IS NULL;` retourne 0. Aucun emprunt
  orphelin ne doit avoir survécu au nettoyage.

<details><summary>Indice 1</summary>

Avec SQLAlchemy 2, une insertion par lots s'écrit
`conn.execute(text("INSERT INTO ... VALUES (:col1, :col2)"), liste_de_dicts)`
ou `liste_de_dicts` est une liste de dictionnaires dont les clés correspondent
aux paramètres nommés. SQLAlchemy regroupe les lignes automatiquement.

</details>

<details><summary>Indice 2</summary>

Pour vider des tables liées par des clés étrangères, `TRUNCATE` échouera.
Utilisez `DELETE FROM` dans l'ordre inverse des dépendances : emprunt, puis
document et adhérent, puis médiathèque.

</details>

<details><summary>Indice 3</summary>

Une chaîne vide lue dans un CSV n'est pas une valeur nulle SQL. Convertissez
explicitement les chaînes vides en `None` avant l'insertion, sinon PostgreSQL
tentera d'insérer une chaîne vide dans une colonne `DATE` et rejettera la
ligne. Même vigilance sur les booléens : une colonne `BOOLEAN` n'accepte pas
un entier 0 ou 1 depuis Python, il faut lui passer `True` ou `False`.

</details>

---

## Étape 6 — SQL d'analyse : répondre aux questions métier

**Durée : 1 h 15 — Niveau : difficile**

### Objectif

Réviser le SQL d'analyse : jointures multiples, agrégats, `GROUP BY`, `HAVING`,
sous-requêtes, expressions de table communes et fonctions fenêtres.

### Consignes

1. Créez le fichier `etape06/analyses.sql`. Chaque requête est précédée d'un
   commentaire `-- Question N : <intitule>` et suivie d'un commentaire d'une
   ligne indiquant le nombre de lignes retournées.
2. Écrivez une requête par question. Toutes les requêtes portent sur la base
   `rmml` chargée à l'étape 5.

   **Question 1.** Pour chaque médiathèque : le nom, la commune, le nombre de
   documents du fonds, le nombre d'adhérents rattachés et le nombre
   d'emprunts. Triez par nombre d'emprunts décroissant.

   **Question 2.** Le nombre d'emprunts par mois calendaire, de septembre 2025
   à septembre 2026, dans l'ordre chronologique, avec le mois au format
   `AAAA-MM`.

   **Question 3.** Le top 10 des documents les plus empruntés : titre, auteur,
   genre, support, médiathèque de rattachement et nombre d'emprunts.

   **Question 4.** Le taux de retard par médiathèque. Un emprunt est en retard
   si `date_retour_reelle` est postérieure à `date_retour_prevue`. Les
   emprunts en cours sont exclus du calcul. Affichez le nombre d'emprunts
   clos, le nombre d'emprunts en retard et le taux en pourcentage arrondi à
   une décimale. Triez du taux le plus élevé au plus faible.

   **Question 5.** Les genres dont le nombre total d'emprunts dépasse 400.
   Utilisez `HAVING`.

   **Question 6.** Les adhérents ayant emprunté strictement plus de 30 fois :
   nom, prénom, tranche d'âge, médiathèque de rattachement, nombre d'emprunts.
   Triez par nombre d'emprunts décroissant.

   **Question 7.** Pour chaque médiathèque, le document le plus emprunté de son
   propre fonds, avec son nombre d'emprunts. Utilisez une fonction fenêtre
   (`ROW_NUMBER` ou `RANK`) à l'intérieur d'une expression de table commune
   `WITH`.

   **Question 8.** La durée moyenne de prêt en jours, globalement puis par
   support, calculée sur les seuls emprunts clos. Arrondissez à une décimale
   et triez par durée décroissante.

3. Interdiction d'utiliser `SELECT *` dans les requêtes rendues.
4. Toutes les jointures sont écrites en syntaxe explicite `JOIN ... ON`, pas de
   jointure implicite par virgule dans le `FROM`.
5. Ajoutez en fin de fichier un commentaire de 5 à 10 lignes : parmi ces huit
   requêtes, lesquelles sont les plus coûteuses pour la base et pourquoi
   (volume parcouru, jointures, absence d'index utilisable). Il s'agit d'une
   lecture technique, pas d'une analyse des résultats métier.

### Livrable

`etape06/analyses.sql`

### Vérifiez vous-même

- La question 1 retourne exactement 6 lignes, et `MED-TOU` est en tête du
  classement par nombre d'emprunts.
- La question 2 retourne 13 lignes. Les douze premières valeurs sont comprises
  entre 391 et 444 ; la treizième, septembre 2026, est nettement plus basse car
  le mois est incomplet.
- La question 4 donne un taux de retard global du réseau situé entre 16 % et
  17 %, et aucun site ne dépasse 18 %. Si vous obtenez un taux supérieur à
  20 %, vous avez probablement compté les emprunts en cours comme des retards.
- La question 7 retourne exactement 6 lignes, une par médiathèque. Si vous en
  obtenez davantage, votre partitionnement laisse passer les ex aequo :
  choisissez la fonction fenêtre adaptée ou ajoutez un critère de
  départage.
- La question 8 donne une durée moyenne globale proche de 11 jours.

<details><summary>Indice 1</summary>

Pour formater un mois en `AAAA-MM` sous PostgreSQL :
`to_char(date_emprunt, 'YYYY-MM')`. Ce format se trie correctement en
alphabétique, vous n'avez pas besoin de trier sur une autre expression.

</details>

<details><summary>Indice 2</summary>

Pour un taux en pourcentage, `ROUND(100.0 * COUNT(*) FILTER (WHERE condition)
/ COUNT(*), 1)`. Le `100.0` n'est pas décoratif : entre deux entiers,
PostgreSQL fait une division entière et vous obtiendriez 0. Pensez aussi à
restreindre le dénominateur aux seuls emprunts clos, par un
`WHERE date_retour_reelle IS NOT NULL`.

</details>

<details><summary>Indice 3</summary>

Structure type pour la question 7 :

```sql
WITH classement AS (
  SELECT d.code_site, d.titre, COUNT(*) AS nb,
         ROW_NUMBER() OVER (PARTITION BY d.code_site
                            ORDER BY COUNT(*) DESC) AS rang
  FROM emprunt e
  JOIN document d ON d.id_document = e.id_document
  GROUP BY d.code_site, d.id_document, d.titre
)
SELECT code_site, titre, nb FROM classement WHERE rang = 1;
```

</details>

---

## Étape 7 — API FastAPI : structure, modèles et CRUD documents

**Durée : 1 h 45 — Niveau : moyen**

### Objectif

Réviser la construction d'une API REST : organisation du projet, modèles
SQLAlchemy, schémas Pydantic, injection de la session, routes CRUD,
pagination, filtres et gestion du 404.

### Consignes

1. Créez l'arborescence suivante sous `api/` :

```
api/
  main.py
  database.py
  models.py
  schemas.py
  routers/
    __init__.py
    documents.py
```

2. `database.py` crée l'`Engine` SQLAlchemy vers la base `rmml`, la
   `SessionLocal`, la classe de base déclarative, et une fonction générateur
   `get_db()` utilisable comme dépendance FastAPI. La chaîne de connexion est
   lue depuis l'environnement.
3. `models.py` déclare les quatre modèles SQLAlchemy 2 `Mediatheque`,
   `Document`, `Adherent`, `Emprunt`, alignés sur le schéma de l'étape 4, avec
   les relations entre eux.
4. `schemas.py` déclare les schémas Pydantic. Au minimum :
   - `DocumentBase` avec les champs métier ;
   - `DocumentCreate` pour la création ;
   - `DocumentUpdate` avec tous les champs optionnels, pour la mise à jour
     partielle ;
   - `DocumentOut` incluant `id_document`, configuré pour lire depuis un objet
     SQLAlchemy ;
   - `PageDocuments` contenant `total`, `page`, `taille_page` et
     `resultats`.
5. `routers/documents.py` expose les routes suivantes, préfixées par
   `/documents` :

| Méthode | Chemin | Comportement |
|---|---|---|
| `GET` | `/documents` | Liste paginée et filtrable |
| `GET` | `/documents/{id_document}` | Un document, 404 s'il n'existe pas |
| `POST` | `/documents` | Création, réponse 201 |
| `PUT` | `/documents/{id_document}` | Mise à jour partielle, 404 sinon |
| `DELETE` | `/documents/{id_document}` | Suppression, réponse 204, 404 sinon |

6. La route de liste accepte les paramètres de requête suivants, tous
   optionnels : `page` (entier, défaut 1, minimum 1), `taille_page` (entier,
   défaut 20, maximum 100), `genre`, `support`, `code_site`, et `recherche`
   qui filtre sur le titre ou sur l'auteur en ignorant la casse. Elle renvoie
   un objet conforme à `PageDocuments`.
7. Un identifiant inexistant doit produire une réponse `404` avec un corps
   `{"detail": "Document introuvable"}`.
8. `main.py` crée l'application FastAPI avec un titre et une version, inclut le
   routeur, et expose une route `GET /sante` renvoyant
   `{"statut": "ok"}`.
9. Activez CORS pour l'origine `http://localhost:8501`, qui sera celle du front
   Streamlit du jour 2.

### Livrable

Le dossier `api/` complet et fonctionnel

### Vérifiez vous-même

- `uvicorn api.main:app --reload` démarre sans erreur, et
  `http://127.0.0.1:8000/docs` affiche la documentation interactive avec les
  six routes.
- `GET /documents?page=1&taille_page=5` renvoie 5 résultats et un champ
  `total` égal au nombre de documents chargés en base à l'étape 5.
- `GET /documents?code_site=MED-LIL` renvoie un `total` compris entre 70 et 80.
- `GET /documents/999999` renvoie le code 404 et le corps
  `{"detail": "Document introuvable"}`.
- Un `POST` valide suivi d'un `GET` sur l'identifiant retourne renvoie bien le
  document créé.

<details><summary>Indice 1</summary>

Pour que Pydantic lise directement un objet SQLAlchemy, le schéma de sortie a
besoin de `model_config = ConfigDict(from_attributes=True)` en Pydantic v2.
Sans cette configuration, FastAPI lève une erreur de validation au moment de
sérialiser la réponse.

</details>

<details><summary>Indice 2</summary>

Pagination : `decalage = (page - 1) * taille_page`, puis
`.offset(decalage).limit(taille_page)`. Le `total` se calcule sur la requête
**filtrée mais non paginée**, avant d'appliquer `offset` et `limit`, sinon il
ne vaudra jamais plus que `taille_page`.

</details>

<details><summary>Indice 3</summary>

Pour une mise à jour partielle, `donnees.model_dump(exclude_unset=True)` ne
renvoie que les champs réellement fournis par le client. Parcourez ce
dictionnaire avec `setattr(objet, cle, valeur)` pour n'écraser que ce qui a
été transmis.

</details>

---

## Étape 8 — Endpoints d'analyse : formats JSON imposés

**Durée : 1 h 45 — Niveau : moyen à difficile**

### Objectif

Transformer les analyses SQL de l'étape 6 en endpoints REST exploitables,
avec des formats de réponse strictement imposés.

### Contexte

Ces quatre endpoints sont le contrat d'interface de l'API : ce sont eux qui
rendent les analyses SQL de l'étape 6 consommables par un client.
**Les formats JSON ci-dessous sont imposés** : noms de champs, types, ordre des
éléments. Vous les vérifierez à l'étape 10, via `/docs` ou `curl`. Lisez-les
avant de coder.

### Consignes

1. Créez `api/routers/analyses.py` et incluez-le dans `main.py`. Toutes les
   routes sont préfixées par `/analyses`.
2. Les quatre endpoints interrogent la base via SQLAlchemy. Les agrégats sont
   calculés **en base**, pas en Python après avoir rapatrié toutes les lignes.

#### Endpoint 1 — `GET /analyses/emprunts-par-mois`

Paramètres optionnels : `code_site` (filtre sur le site de l'emprunt),
`date_debut` et `date_fin` au format `AAAA-MM-JJ`.

Les éléments du tableau `donnees` sont triés par `mois` croissant.

```json
{
  "perimetre": {
    "code_site": null,
    "date_debut": "2025-09-01",
    "date_fin": "2026-09-16"
  },
  "total_emprunts": 5192,
  "donnees": [
    { "mois": "2025-09", "nb_emprunts": 421 },
    { "mois": "2025-10", "nb_emprunts": 444 }
  ]
}
```

#### Endpoint 2 — `GET /analyses/top-documents`

Paramètres optionnels : `limite` (entier, défaut 10, maximum 50), `code_site`,
`genre`.

Les éléments sont triés par `nb_emprunts` décroissant, et `rang` démarre à 1.

```json
{
  "limite": 10,
  "donnees": [
    {
      "rang": 1,
      "id_document": 166,
      "titre": "Les corps flottants",
      "auteur": "Nicolas Mathieu",
      "genre": "Roman",
      "support": "Livre",
      "code_site": "MED-LIL",
      "nb_emprunts": 24
    }
  ]
}
```

#### Endpoint 3 — `GET /analyses/activite-par-site`

Aucun paramètre. Un objet par médiathèque, soit six éléments, triés par
`nb_emprunts` décroissant.

```json
{
  "donnees": [
    {
      "code_site": "MED-TOU",
      "nom": "Mediatheque Andre Malraux",
      "commune": "Tourcoing",
      "nb_documents": 73,
      "nb_adherents": 49,
      "nb_emprunts": 1098,
      "emprunts_par_document": 15.04
    }
  ]
}
```

`emprunts_par_document` est le rapport du nombre d'emprunts sur le nombre de
documents du fonds du site, arrondi à deux décimales.

#### Endpoint 4 — `GET /analyses/taux-retard`

Paramètre optionnel : `code_site`.

Les éléments du tableau `par_site` sont triés par `taux_retard` décroissant.
Les emprunts en cours sont exclus des calculs de retard et comptés à part dans
`emprunts_en_cours`.

```json
{
  "global": {
    "emprunts_clos": 5013,
    "emprunts_en_retard": 833,
    "emprunts_en_cours": 179,
    "taux_retard": 16.6
  },
  "par_site": [
    {
      "code_site": "MED-ARM",
      "nom": "Mediatheque de l'Abbaye",
      "emprunts_clos": 984,
      "emprunts_en_retard": 176,
      "taux_retard": 17.89
    }
  ]
}
```

`taux_retard` est exprimé en pourcentage, arrondi à deux décimales dans
`par_site` et à une décimale dans `global`.

3. Déclarez un schéma Pydantic pour chacune de ces quatre réponses et
   utilisez-le comme `response_model`. La documentation `/docs` doit montrer
   la structure exacte attendue.
4. Chaque endpoint doit répondre en moins d'une seconde. Si ce n'est pas le
   cas, revoyez vos requêtes ou ajoutez un index.
5. Un `code_site` inconnu, par exemple `MED-XXX`, doit renvoyer un 404 avec
   `{"detail": "Site introuvable"}`, et non un résultat vide.

**Remarque sur les valeurs.** Les exemples JSON ci-dessus sont des extraits de
structure. Les nombres qu'ils contiennent dépendent des décisions de nettoyage
que vous avez prises à l'étape 3 : vos propres chiffres peuvent différer de
quelques unités. Ce qui est imposé, c'est la **structure**, pas les valeurs.

### Livrable

`api/routers/analyses.py` et les schémas correspondants dans `api/schemas.py`

### Vérifiez vous-même

- Les quatre routes apparaissent dans `/docs` avec leur schéma de réponse
  détaillé, et non un simple objet générique.
- `GET /analyses/emprunts-par-mois` renvoie 13 éléments dans `donnees`, du mois
  `2025-09` au mois `2026-09`.
- `GET /analyses/activite-par-site` renvoie exactement 6 éléments, `MED-TOU` en
  tête, et la somme des `nb_emprunts` égale le `total_emprunts` de l'endpoint 1
  sans filtre.
- Dans `GET /analyses/taux-retard`, la somme de `emprunts_clos` et de
  `emprunts_en_cours` du bloc `global` égale le nombre total d'emprunts
  chargés en base. Attention : `emprunts_en_cours` ne vaut plus 179 comme
  dans le fichier brut de l'étape 2, mais 178 sur la base nettoyée. Si vous
  trouvez encore 179, remontez votre chaîne de nettoyage : l'écart
  s'explique.
- `GET /analyses/top-documents?limite=3` renvoie 3 éléments avec `rang` valant
  1, 2 et 3, et le premier totalise au moins 20 emprunts.

<details><summary>Indice 1</summary>

Pour un agrégat par mois en SQLAlchemy 2 :

```python
mois = func.to_char(Emprunt.date_emprunt, "YYYY-MM").label("mois")
requete = (
    select(mois, func.count().label("nb_emprunts"))
    .group_by(mois)
    .order_by(mois)
)
```

</details>

<details><summary>Indice 2</summary>

Pour compter conditionnellement dans un agrégat, utilisez `func.sum(case(...))`
importé depuis `sqlalchemy`. La forme SQLAlchemy 2 est
`case((condition, 1), else_=0)`, le premier argument étant un tuple.

</details>

<details><summary>Indice 3</summary>

Pour `activite-par-site`, évitez de joindre les trois tables dans une seule
requête : les jointures se multiplieraient entre elles et gonfleraient les
comptages. Calculez chaque compte dans une sous-requête agrégée par
`code_site`, puis joignez ces sous-requêtes à la table `mediatheque`.

</details>

---

## Étape 9 — Front Streamlit : le catalogue

**Durée : 2 h — Niveau : moyen à difficile**

### Objectif

Construire un front Streamlit qui consomme l'API : appels HTTP avec `requests`,
filtres interactifs, pagination, et gestion explicite des états de chargement,
de résultat vide et d'erreur.

### Consignes

1. Créez `front/app.py` et `front/api_client.py`.
2. `front/api_client.py` centralise **tous** les appels HTTP. Aucune page ne
   doit appeler `requests` directement. Ce module contient :
   - une constante `URL_API` lue depuis l'environnement, avec
     `http://127.0.0.1:8000` par défaut ;
   - une fonction `lister_documents(...)` correspondant à
     `GET /documents` avec tous ses filtres ;
   - un `timeout` explicite sur chaque appel, jamais d'appel sans délai
     maximum ;
   - une exception maison `ErreurApi` portant le code HTTP et un message
     lisible en français, levée lorsque l'API répond en erreur ou ne répond
     pas.
3. `front/app.py` construit la page catalogue :
   - un titre et une phrase de contexte identifiant le réseau ;
   - dans la barre latérale : un champ de recherche libre sur le titre ou
     l'auteur, une liste déroulante de médiathèque alimentée par les six
     sites, une liste déroulante de genre, une liste déroulante de support, et
     un sélecteur de taille de page ;
   - le nombre total de résultats affiché au-dessus du tableau ;
   - le tableau des documents de la page courante ;
   - des boutons de navigation précédent et suivant, désactivés aux bornes.
4. **Gérez les trois états explicitement** :
   - pendant l'appel, un indicateur de chargement visible ;
   - si la recherche ne retourne aucun résultat, un message explicite invitant
     à élargir les filtres, et non un tableau vide sans explication ;
   - si l'API est injoignable ou répond en erreur, un message d'erreur en
     français indiquant la cause probable, et non une trace technique Python.
5. Mettez en cache les données peu changeantes, comme la liste des sites, avec
   `st.cache_data` et une durée de validité raisonnable.

### Livrable

`front/app.py` et `front/api_client.py`

### Vérifiez vous-même

- `streamlit run front/app.py` ouvre la page sur le port 8501 sans erreur.
- Au premier chargement, le catalogue s'affiche et le nombre total de
  résultats sans filtre correspond au nombre de documents en base.
- En sélectionnant la médiathèque de Lille, le total tombe entre 70 et 80.
- **Arrêtez l'API** puis rechargez la page : un message d'erreur lisible en
  français doit s'afficher, sans trace d'exception Python à l'écran.
- Une recherche sur une chaîne absurde comme `zzzzz` affiche le message de
  résultat vide, pas un tableau vide muet.

<details><summary>Indice 1</summary>

Pour conserver la page courante entre deux interactions, utilisez
`st.session_state`. Initialisez `st.session_state.setdefault("page", 1)` en
tête de script, et remettez la page à 1 dès qu'un filtre change, sinon vous
resterez bloqué sur une page inexistante.

</details>

<details><summary>Indice 2</summary>

Enveloppez chaque appel dans `try/except` en capturant
`requests.exceptions.RequestException`, qui couvre aussi bien le timeout que
le refus de connexion. Convertissez-la en `ErreurApi` avec un message métier,
et affichez ce message avec `st.error`.

</details>

<details><summary>Indice 3</summary>

`with st.spinner("Chargement du catalogue..."):` autour de l'appel suffit à
produire l'indicateur de chargement. Pour désactiver un bouton de pagination,
`st.button("Suivant", disabled=page >= nb_pages)`.

</details>

---

## Étape 10 — Finalisation, documentation et restitution

**Durée : 45 min — Niveau : synthèse**

### Objectif

Rendre le travail exploitable par la personne qui reprendra la maintenance :
structurer le dépôt, écrire un README qui permet à un tiers de tout relancer,
faire le point sur son propre travail, et préparer la restitution orale.

### Consignes

1. **Rangez le dépôt** conformément à l'arborescence donnée en fin de document.
   Supprimez les fichiers de travail inutiles, les caches `__pycache__` et les
   environnements virtuels. Ajoutez un `.gitignore` adapté à un projet Python.
2. **Écrivez `README.md`** à la racine. Il contient, dans cet ordre :
   - le contexte du projet en cinq lignes : qui est le RMML, quelle est la
     demande ;
   - les prérequis : versions de Python et de PostgreSQL, bibliothèques ;
   - l'installation pas à pas, du clonage au lancement ;
   - la liste complète des variables d'environnement attendues, avec un
     exemple de valeur non sensible pour chacune ;
   - la procédure de chargement des données, de l'étape 3 à l'étape 5, dans
     l'ordre ;
   - la commande de lancement de l'API et celle du front ;
   - un tableau des routes de l'API avec leur méthode, leur chemin et une
     description d'une ligne ;
   - une section « limites connues » de 5 à 10 lignes : ce qui n'est pas
     traité, ce qui reste fragile, ce qu'il faudrait faire ensuite.
3. **Créez `requirements.txt`** avec les dépendances et leurs versions.
4. **Vérifiez que tout repart de zéro.** Depuis un environnement virtuel neuf,
   suivez votre propre README ligne à ligne. Toute commande qui manque ou qui
   échoue doit être corrigée dans le README.
5. **Vérifiez les quatre endpoints d'analyse de l'étape 8.** Démarrez l'API et
   interrogez chacun d'eux, depuis `/docs` ou avec `curl`. Reportez leurs
   chiffres clés dans le README : total d'emprunts, taux de retard global,
   site le plus actif. Ces chiffres doivent coïncider avec ceux de l'étape 6.
6. **Rédigez `auto-evaluation.md`** à la racine. Pour chacune des 10 étapes,
   une à trois lignes : ce que vous avez terminé, ce que vous avez laissé de
   côté, et le point précis qui vous a demandé le plus de temps. Ce document
   vous sert de base pour la restitution et pour identifier ce que vous avez
   intérêt à retravailler.
7. **Préparez la restitution orale de 3 minutes.** Vous la présentez devant le
   groupe, écran partagé, sans diaporama. Elle suit ce plan :
   - 30 secondes : la demande du RMML, reformulée avec vos mots ;
   - 60 secondes : une démonstration en direct, du catalogue à la réponse
     d'un endpoint d'analyse ;
   - 60 secondes : la décision technique dont vous êtes le plus satisfait, et
     pourquoi ;
   - 30 secondes : ce que vous feriez différemment avec une journée de plus.
8. Préparez une réponse à la question suivante, qui vous sera posée :
   **quelle anomalie des données sources aurait le plus faussé les chiffres
   renvoyés par vos endpoints d'analyse si vous ne l'aviez pas traitée, et de
   combien ?**

### Livrable

`README.md`, `requirements.txt`, `.gitignore`, `auto-evaluation.md`, et le
dépôt rangé

### Vérifiez vous-même

- Un binôme de la salle suit votre README sur sa propre machine et parvient à
  lancer l'API. Si ce n'est pas le cas, votre README est incomplet.
- `pip install -r requirements.txt` fonctionne dans un environnement virtuel
  neuf.
- `git status` ne fait apparaître ni `__pycache__`, ni dossier d'environnement
  virtuel, ni fichier contenant un mot de passe.
- Les quatre endpoints d'analyse répondent : `/analyses/taux-retard` annonce
  un taux global compris entre 16 % et 17 %, cohérent avec la question 4 de
  l'étape 6.
- Votre restitution, chronométrée, tient en 3 minutes. Répétez-la une fois.

<details><summary>Indice 1</summary>

Pour générer la liste des dépendances sans y inclure tout votre environnement
de travail, préférez `pip freeze` dans un environnement virtuel dédié au
projet, ou écrivez le fichier à la main en ne listant que les bibliothèques
que vous importez réellement.

</details>

<details><summary>Indice 2</summary>

Pour la question sur l'anomalie la plus impactante, comparez deux résultats :
le chiffre obtenu avec les données brutes et celui obtenu avec les données
nettoyées, sur un indicateur précis renvoyé par un endpoint d'analyse.
L'écart chiffré est la réponse.

</details>

---

## Ce qui est attendu à la fin des deux jours

### Le dépôt rendu

Vous remettez un dépôt Git respectant exactement cette arborescence :

```
tp-rmml/
  README.md
  requirements.txt
  auto-evaluation.md
  .gitignore
  data/
    mediatheques.csv
    documents.csv
    adherents.csv
    emprunts.csv
  etape01/
    exploration.py
  etape02/
    analyse_pandas.py
  etape03/
    qualite.py
  etape04/
    modelisation.md
    schema.sql
  etape05/
    chargement.py
  etape06/
    analyses.sql
  api/
    main.py
    database.py
    models.py
    schemas.py
    routers/
      __init__.py
      documents.py
      analyses.py
  front/
    app.py
    api_client.py
  sorties/
    top10_documents.csv
    documents_propre.csv
    adherents_propre.csv
    emprunts_propre.csv
    rapport_qualite.md
```

Le dépôt doit être propre : pas de fichier temporaire, pas de cache Python, pas
d'environnement virtuel, et **aucun mot de passe en clair** dans l'historique
des commits.

### La chaîne fonctionnelle

Depuis un environnement neuf et en suivant votre README, un tiers doit pouvoir :

1. créer la base et les tables à partir de `etape04/schema.sql` ;
2. produire les fichiers nettoyés avec `etape03/qualite.py` ;
3. charger la base avec `etape05/chargement.py` ;
4. démarrer l'API et obtenir une réponse sur `/sante` ;
5. interroger les quatre endpoints d'analyse et retrouver les chiffres de
   l'étape 6 ;
6. démarrer le front et parcourir le catalogue.

### La restitution orale

Trois minutes, en direct, écran partagé, devant le groupe. Le plan est celui
donné à l'étape 10. Vous serez ensuite interrogé sur l'anomalie de données la
plus impactante et son effet chiffré sur les indicateurs.

Une restitution réussie, c'est une démonstration qui fonctionne du premier coup
et une décision technique que vous savez défendre. Préparez votre
environnement avant de passer : API démarrée, `/docs` ouvert et front ouvert
sur le catalogue.
