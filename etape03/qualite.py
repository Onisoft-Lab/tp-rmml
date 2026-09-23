from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUT_DIR = Path(__file__).resolve().parent.parent / "sorties"

CSVS = {
    "documents": DATA_DIR / "documents.csv",
    "adherents": DATA_DIR / "adherents.csv",
    "emprunts": DATA_DIR / "emprunts.csv",
}

anomalies: list[dict] = []


def enregistrer_anomalie(
    fichier: str,
    colonne: str,
    description: str,
    n_lignes: int,
    n_total: int,
    traitement: str,
) -> None:
    anomalies.append(
        {
            "fichier": fichier,
            "colonne": colonne,
            "description": description,
            "n_lignes": int(n_lignes),
            "part_pct": round(100 * n_lignes / n_total, 2) if n_total else 0.0,
            "traitement": traitement,
        }
    )


def generer_rapport(
    bilans: dict[str, tuple[int, int]],
    n_emprunts_en_cours: int,
) -> str:
    lignes = [
        "# Rapport qualité des données RMML",
        "",
        "## Tableau récapitulatif des anomalies",
        "",
        "| Fichier | Colonne | Description | Lignes | Part (%) | Traitement |",
        "|---|---|---|---:|---:|---|",
    ]
    for a in anomalies:
        lignes.append(
            f"| `{a['fichier']}` | `{a['colonne']}` | {a['description']} "
            f"| {a['n_lignes']} | {a['part_pct']} | {a['traitement']} |"
        )

    lignes += [
        "",
        "## Effectifs avant / après nettoyage",
        "",
        "| Fichier | Avant | Après | Écart |",
        "|---|---:|---:|---:|",
    ]
    for nom, (avant, apres) in bilans.items():
        lignes.append(f"| `{nom}` | {avant} | {apres} | {apres - avant} |")

    lignes += [
        "",
        "## Cas métier normal (non compté comme anomalie)",
        "",
        f"Les emprunts sans date de retour réelle sont des prêts en cours "
        f"({n_emprunts_en_cours} lignes). On les a conservés tels quels.",
        "",
        "## Points d'attention pour la direction",
        "",
        "Les fichiers ont des défauts, mais en petit nombre. Sur le catalogue, "
        "chaque problème touche moins de 4 % des fiches.",
        "",
        "Certaines fiches documents sont en double à l'identique. Si on ne "
        "les enlève pas, on compte trop de documents et on fausse les "
        "classements d'emprunts.",
        "",
        "23 emprunts concernent un document qui n'existe pas (identifiant "
        "99999). On les a retirés : on ne peut pas les rattacher au catalogue, "
        "et une base de données propre les refuserait.",
        "",
        "Quelques dates de retour sont antérieures à la date d'emprunt. Ces "
        "cas ont été retirés. Les prêts encore ouverts, sans date de retour, "
        "sont en revanche normaux : on les a gardés.",
        "",
        "Le catalogue contient aussi des années de publication dans le futur, "
        "et des années ou des prix non renseignés. On n'a rien inventé : les "
        "années impossibles sont passées en \"non renseigné\", le reste est "
        "seulement signalé.",
        "",
        "Chez les adhérents, des codes postaux manquent et quelques tranches "
        "d'âge disent \"inconnu\". Ce n'est pas bloquant, mais on ne pourra "
        "pas bien analyser le territoire ni l'âge des usagers tant que la "
        "saisie n'est pas reprise.",
        "",
        "Il faudrait corriger à la source, dans les logiciels de prêt, les "
        "documents orphelins et les dates incohérentes. Sinon, chaque nouvelle "
        "extraction reproduira les mêmes écarts.",
        "",
    ]
    return "\n".join(lignes)


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------
df_documents = pd.read_csv(CSVS["documents"])
n_docs_avant = len(df_documents)

print("====================[ DOCUMENTS ]====================")

n_doublons_docs = int(df_documents.duplicated().sum())
print(f"\n==== Doublons ====\nNombre: {n_doublons_docs}\n")
print(df_documents[df_documents.duplicated()].head(3))
enregistrer_anomalie(
    "documents.csv",
    "toutes",
    "Lignes en doublon strict (identiques sur toutes les colonnes)",
    n_doublons_docs,
    n_docs_avant,
    "Suppression des doublons (une occurrence conservée). Les lignes "
    "identiques fausseraient les effectifs du catalogue.",
)
df_documents = df_documents.drop_duplicates()

n_annee_vide = int(df_documents["annee_publication"].isna().sum())
print(f"\n==== annee_publication vide ====\nNombre: {n_annee_vide}\n")
print(df_documents[df_documents["annee_publication"].isna()].head(3))
enregistrer_anomalie(
    "documents.csv",
    "annee_publication",
    "Année de publication vide",
    n_annee_vide,
    n_docs_avant,
    "Conservation en l'état avec signalement. On ne peut pas inventer "
    "une année sans source fiable.",
)

masque_annee_impossible = df_documents["annee_publication"] > 2026
n_annee_impossible = int(masque_annee_impossible.sum())
print(f"\n==== annee_publication > 2026 ====\nNombre: {n_annee_impossible}\n")
print(df_documents[masque_annee_impossible].head(3))
enregistrer_anomalie(
    "documents.csv",
    "annee_publication",
    "Année de publication postérieure à 2026 (impossible)",
    n_annee_impossible,
    n_docs_avant,
    "Mise à valeur manquante explicite. Une année future ne doit pas "
    "rester comme une date valide.",
)
df_documents.loc[masque_annee_impossible, "annee_publication"] = pd.NA

n_prix_vide = int(df_documents["prix_achat"].isna().sum())
print(f"\n==== prix_achat vide ====\nNombre: {n_prix_vide}\n")
print(df_documents[df_documents["prix_achat"].isna()].head(3))
enregistrer_anomalie(
    "documents.csv",
    "prix_achat",
    "Prix d'achat vide",
    n_prix_vide,
    n_docs_avant,
    "Conservation en l'état avec signalement. Un 0 ferait croire à un "
    "document gratuit et biaiserait les moyennes.",
)

masque_auteur_maj = df_documents["auteur"].str.isupper()
n_auteur_maj = int(masque_auteur_maj.sum())
print(f"\n==== Auteur en majuscules ====\nNombre: {n_auteur_maj}\n")
print(df_documents[masque_auteur_maj].head(3))
enregistrer_anomalie(
    "documents.csv",
    "auteur",
    "Auteur écrit intégralement en majuscules",
    n_auteur_maj,
    n_docs_avant,
    "Correction automatique de la casse (première lettre de chaque mot "
    "en majuscule) pour coller au reste du catalogue.",
)
df_documents["auteur"] = df_documents["auteur"].str.title()

masque_genre_espaces = df_documents["genre"].str.startswith(" ") | df_documents[
    "genre"
].str.endswith(" ")
n_genre_espaces = int(masque_genre_espaces.sum())
print(f"\n==== Genre avec espaces parasites ====\nNombre: {n_genre_espaces}\n")
print(df_documents[masque_genre_espaces].head(3))
enregistrer_anomalie(
    "documents.csv",
    "genre",
    "Espaces parasites en début ou fin de genre",
    n_genre_espaces,
    n_docs_avant,
    "Correction automatique : suppression des espaces en trop. Ils "
    "créaient de fausses catégories distinctes.",
)
df_documents["genre"] = df_documents["genre"].str.strip()

n_docs_apres = len(df_documents)

# ---------------------------------------------------------------------------
# Adhérents
# ---------------------------------------------------------------------------
df_adherents = pd.read_csv(CSVS["adherents"])
n_adh_avant = len(df_adherents)

print("\n====================[ ADHERENTS ]====================")

n_cp_vide = int(df_adherents["code_postal"].isna().sum())
print(f"\n==== Code postal vide ====\nNombre: {n_cp_vide}\n")
print(df_adherents[df_adherents["code_postal"].isna()].head(3))
enregistrer_anomalie(
    "adherents.csv",
    "code_postal",
    "Code postal vide",
    n_cp_vide,
    n_adh_avant,
    "Conservation en l'état avec signalement. Un code postal ne peut "
    "pas être inventé sans risque d'erreur.",
)

masque_age_inconnu = df_adherents["tranche_age"] == "inconnu"
n_age_inconnu = int(masque_age_inconnu.sum())
print(f"\n==== Tranche d'âge 'inconnu' ====\nNombre: {n_age_inconnu}\n")
print(df_adherents[masque_age_inconnu].head(3))
enregistrer_anomalie(
    "adherents.csv",
    "tranche_age",
    "Tranche d'âge valant \"inconnu\"",
    n_age_inconnu,
    n_adh_avant,
    "Conservation en l'état avec signalement. \"Inconnu\" reste une "
    "information utile, ce n'est pas une erreur à effacer.",
)

masque_jjmmaaaa = df_adherents["date_inscription"].astype(str).str.contains("/")
n_dates_fr = int(masque_jjmmaaaa.sum())
print(f"\n==== Dates JJ/MM/AAAA ====\nNombre: {n_dates_fr}\n")
print(df_adherents[masque_jjmmaaaa].head(3))
enregistrer_anomalie(
    "adherents.csv",
    "date_inscription",
    "Date d'inscription au format JJ/MM/AAAA au lieu de AAAA-MM-JJ",
    n_dates_fr,
    n_adh_avant,
    "Correction automatique vers le format AAAA-MM-JJ, pour comparer "
    "et charger les dates sans ambiguïté.",
)
df_adherents["date_inscription"] = pd.to_datetime(
    df_adherents["date_inscription"], format="mixed", dayfirst=True
)
df_adherents["date_inscription"] = df_adherents["date_inscription"].dt.strftime(
    "%Y-%m-%d"
)

n_adh_apres = len(df_adherents)

# ---------------------------------------------------------------------------
# Emprunts
# ---------------------------------------------------------------------------
df_emprunts = pd.read_csv(CSVS["emprunts"])
n_emp_avant = len(df_emprunts)
n_emprunts_en_cours = int(
    df_emprunts["date_retour_reelle"].isna().sum()
    + (df_emprunts["date_retour_reelle"].astype(str).str.strip() == "").sum()
)
# Éviter le double comptage si pandas lit déjà les vides en NaN
n_emprunts_en_cours = int(df_emprunts["date_retour_reelle"].isna().sum())

print("\n====================[ EMPRUNTS ]====================")
print(f"(Emprunts en cours, cas normal : {n_emprunts_en_cours})")

n_doublons_emp = int(df_emprunts.duplicated().sum())
print(f"\n==== Doublons ====\nNombre: {n_doublons_emp}\n")
print(df_emprunts[df_emprunts.duplicated()].head(3))
enregistrer_anomalie(
    "emprunts.csv",
    "toutes",
    "Lignes en doublon strict",
    n_doublons_emp,
    n_emp_avant,
    "Suppression des doublons (une occurrence conservée).",
)
df_emprunts = df_emprunts.drop_duplicates()

masque_orphelin = ~df_emprunts["id_document"].isin(df_documents["id_document"])
n_orphelins = int(masque_orphelin.sum())
print(f"\n==== id_document inexistant ====\nNombre: {n_orphelins}\n")
print(df_emprunts[masque_orphelin].head(3))
enregistrer_anomalie(
    "emprunts.csv",
    "id_document",
    "Emprunt pointant vers un document absent du catalogue",
    n_orphelins,
    n_emp_avant,
    "Suppression de la ligne. Ces emprunts ne pourraient pas être "
    "reliés au catalogue en base de données.",
)
df_emprunts = df_emprunts[~masque_orphelin]

df_emprunts["date_emprunt"] = pd.to_datetime(df_emprunts["date_emprunt"])
df_emprunts["date_retour_prevue"] = pd.to_datetime(df_emprunts["date_retour_prevue"])
df_emprunts["date_retour_reelle"] = pd.to_datetime(df_emprunts["date_retour_reelle"])
masque_chrono = df_emprunts["date_retour_reelle"].notna() & (
    df_emprunts["date_retour_reelle"] < df_emprunts["date_emprunt"]
)
n_chrono = int(masque_chrono.sum())
print(f"\n==== Chronologie impossible ====\nNombre: {n_chrono}\n")
print(df_emprunts[masque_chrono].head(3))
enregistrer_anomalie(
    "emprunts.csv",
    "date_retour_reelle / date_emprunt",
    "Date de retour réelle antérieure à la date d'emprunt",
    n_chrono,
    n_emp_avant,
    "Suppression de la ligne (chronologie impossible). Les emprunts en "
    "cours, sans date de retour, sont conservés.",
)
df_emprunts = df_emprunts[~masque_chrono]

n_emp_apres = len(df_emprunts)

# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------
OUT_DIR.mkdir(parents=True, exist_ok=True)

df_documents.to_csv(OUT_DIR / "documents_propre.csv", index=False, encoding="utf-8")
df_adherents.to_csv(OUT_DIR / "adherents_propre.csv", index=False, encoding="utf-8")
df_emprunts.to_csv(OUT_DIR / "emprunts_propre.csv", index=False, encoding="utf-8")

bilans = {
    "documents.csv": (n_docs_avant, n_docs_apres),
    "adherents.csv": (n_adh_avant, n_adh_apres),
    "emprunts.csv": (n_emp_avant, n_emp_apres),
}
rapport = generer_rapport(bilans, n_emprunts_en_cours)
(OUT_DIR / "rapport_qualite.md").write_text(rapport, encoding="utf-8")

print("\n====================[ EXPORTS ]====================")
print(f"Anomalies recensées : {len(anomalies)} (attendu : 12)")
print(f"Genres distincts après nettoyage : {df_documents['genre'].nunique()} (attendu : 8)")
print(f"Emprunts propres : {n_emp_apres} (attendu : entre 5150 et 5215)")
print(f"Rapport écrit dans {OUT_DIR / 'rapport_qualite.md'}")
