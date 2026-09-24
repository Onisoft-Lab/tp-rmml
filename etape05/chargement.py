from __future__ import annotations

import csv
import logging
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SORTIES_DIR = ROOT / "sorties"
TAILLE_LOT = 500

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

rejets: list[dict[str, Any]] = []


def creer_engine() -> Engine:
    """
    Crée l'engine SQLAlchemy.

    Variables d'environnement : POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB,
    POSTGRES_USER, POSTGRES_PASSWORD (fichier .env ou shell).
    """
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "rmml")
    user = os.getenv("POSTGRES_USER", "rmml")
    password = os.getenv("POSTGRES_PASSWORD", "rmml")
    url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)


def vide_ou_none(valeur: str | None) -> str | None:
    if valeur is None:
        return None
    valeur = valeur.strip()
    return valeur if valeur != "" else None


def vers_int(valeur: str | None) -> int | None:
    texte = vide_ou_none(valeur)
    if texte is None:
        return None
    return int(float(texte))


def vers_float(valeur: str | None) -> float | None:
    texte = vide_ou_none(valeur)
    if texte is None:
        return None
    return float(texte)


def vers_code_postal(valeur: str | None) -> str | None:
    texte = vide_ou_none(valeur)
    if texte is None:
        return None
    return str(int(float(texte)))


def vers_bool_oui_non(valeur: str | None) -> bool:
    texte = (vide_ou_none(valeur) or "").lower()
    return texte == "oui"


def lire_csv(chemin: Path) -> list[dict[str, str]]:
    with chemin.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def lots(lignes: list[dict[str, Any]], taille: int) -> list[list[dict[str, Any]]]:
    return [lignes[i : i + taille] for i in range(0, len(lignes), taille)]


def inserer_par_lots(
    conn: Connection,
    sql: str,
    lignes: list[dict[str, Any]],
    table: str,
) -> tuple[int, int]:
    """Insère par lots de 500 ; si un lot échoue, reprend ligne à ligne."""
    inseres = 0
    rejetes = 0
    stmt = text(sql)

    for lot in lots(lignes, TAILLE_LOT):
        try:
            with conn.begin_nested():
                conn.execute(stmt, lot)
            inseres += len(lot)
        except Exception:
            for ligne in lot:
                try:
                    with conn.begin_nested():
                        conn.execute(stmt, ligne)
                    inseres += 1
                except Exception as exc:
                    rejetes += 1
                    rejets.append({**ligne, "table": table, "motif_rejet": str(exc)})
    return inseres, rejetes


def vider_tables(conn: Connection) -> None:
    """Vide les tables (ordre inverse des FK) pour un rechargement idempotent."""
    conn.execute(text("DELETE FROM emprunt"))
    conn.execute(text("DELETE FROM document"))
    conn.execute(text("DELETE FROM adherent"))
    conn.execute(text("DELETE FROM mediatheque"))


def charger_mediatheques(conn: Connection) -> dict[str, float | int]:
    debut = time.perf_counter()
    brutes = lire_csv(DATA_DIR / "mediatheques.csv")
    lignes = [
        {
            "code_site": vide_ou_none(r["code_site"]),
            "nom": vide_ou_none(r["nom"]),
            "commune": vide_ou_none(r["commune"]),
            "annee_ouverture": vers_int(r["annee_ouverture"]),
            "surface_m2": vers_int(r["surface_m2"]),
        }
        for r in brutes
    ]
    sql = """
        INSERT INTO mediatheque (code_site, nom, commune, annee_ouverture, surface_m2)
        VALUES (:code_site, :nom, :commune, :annee_ouverture, :surface_m2)
    """
    inseres, rejetes = inserer_par_lots(conn, sql, lignes, "mediatheque")
    duree = time.perf_counter() - debut
    logger.info(
        "mediatheque : lues=%s insérées=%s rejetées=%s durée=%.2fs",
        len(lignes),
        inseres,
        rejetes,
        duree,
    )
    return {"lues": len(lignes), "inserees": inseres, "rejetees": rejetes, "duree": duree}


def charger_documents(conn: Connection) -> dict[str, float | int]:
    debut = time.perf_counter()
    brutes = lire_csv(SORTIES_DIR / "documents_propre.csv")
    lignes = [
        {
            "id_document": vers_int(r["id_document"]),
            "isbn": vide_ou_none(r["isbn"]),
            "titre": vide_ou_none(r["titre"]),
            "auteur": vide_ou_none(r["auteur"]),
            "genre": vide_ou_none(r["genre"]),
            "support": vide_ou_none(r["support"]),
            "annee_publication": vers_int(r["annee_publication"]),
            "code_site": vide_ou_none(r["code_site"]),
            "prix_achat": vers_float(r["prix_achat"]),
        }
        for r in brutes
    ]
    sql = """
        INSERT INTO document (
            id_document, isbn, titre, auteur, genre, support,
            annee_publication, code_site, prix_achat
        ) VALUES (
            :id_document, :isbn, :titre, :auteur, :genre, :support,
            :annee_publication, :code_site, :prix_achat
        )
    """
    inseres, rejetes = inserer_par_lots(conn, sql, lignes, "document")
    duree = time.perf_counter() - debut
    logger.info(
        "document : lues=%s insérées=%s rejetées=%s durée=%.2fs",
        len(lignes),
        inseres,
        rejetes,
        duree,
    )
    return {"lues": len(lignes), "inserees": inseres, "rejetees": rejetes, "duree": duree}


def charger_adherents(conn: Connection) -> dict[str, float | int]:
    debut = time.perf_counter()
    brutes = lire_csv(SORTIES_DIR / "adherents_propre.csv")
    lignes = [
        {
            "id_adherent": vers_int(r["id_adherent"]),
            "nom": vide_ou_none(r["nom"]),
            "prenom": vide_ou_none(r["prenom"]),
            "code_postal": vers_code_postal(r["code_postal"]),
            "tranche_age": vide_ou_none(r["tranche_age"]),
            "date_inscription": vide_ou_none(r["date_inscription"]),
            "code_site": vide_ou_none(r["code_site"]),
            "abonnement_actif": vers_bool_oui_non(r["abonnement_actif"]),
        }
        for r in brutes
    ]
    sql = """
        INSERT INTO adherent (
            id_adherent, nom, prenom, code_postal, tranche_age,
            date_inscription, code_site, abonnement_actif
        ) VALUES (
            :id_adherent, :nom, :prenom, :code_postal, :tranche_age,
            :date_inscription, :code_site, :abonnement_actif
        )
    """
    inseres, rejetes = inserer_par_lots(conn, sql, lignes, "adherent")
    duree = time.perf_counter() - debut
    logger.info(
        "adherent : lues=%s insérées=%s rejetées=%s durée=%.2fs",
        len(lignes),
        inseres,
        rejetes,
        duree,
    )
    return {"lues": len(lignes), "inserees": inseres, "rejetees": rejetes, "duree": duree}


def charger_emprunts(conn: Connection) -> dict[str, float | int]:
    debut = time.perf_counter()
    brutes = lire_csv(SORTIES_DIR / "emprunts_propre.csv")
    lignes = [
        {
            "id_emprunt": vide_ou_none(r["id_emprunt"]),
            "id_document": vers_int(r["id_document"]),
            "id_adherent": vers_int(r["id_adherent"]),
            "code_site": vide_ou_none(r["code_site"]),
            "date_emprunt": vide_ou_none(r["date_emprunt"]),
            "date_retour_prevue": vide_ou_none(r["date_retour_prevue"]),
            "date_retour_reelle": vide_ou_none(r["date_retour_reelle"]),
        }
        for r in brutes
    ]
    sql = """
        INSERT INTO emprunt (
            id_emprunt, id_document, id_adherent, code_site,
            date_emprunt, date_retour_prevue, date_retour_reelle
        ) VALUES (
            :id_emprunt, :id_document, :id_adherent, :code_site,
            :date_emprunt, :date_retour_prevue, :date_retour_reelle
        )
    """
    inseres, rejetes = inserer_par_lots(conn, sql, lignes, "emprunt")
    duree = time.perf_counter() - debut
    logger.info(
        "emprunt : lues=%s insérées=%s rejetées=%s durée=%.2fs",
        len(lignes),
        inseres,
        rejetes,
        duree,
    )
    return {"lues": len(lignes), "inserees": inseres, "rejetees": rejetes, "duree": duree}


def ecrire_rejets() -> None:
    if not rejets:
        return
    chemin = SORTIES_DIR / "rejets_chargement.csv"
    champs = sorted({cle for rejet in rejets for cle in rejet})
    with chemin.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=champs)
        writer.writeheader()
        writer.writerows(rejets)
    logger.info("Rejets écrits dans %s (%s lignes)", chemin, len(rejets))


def main() -> None:
    rejets.clear()
    engine = creer_engine()
    stats: dict[str, dict[str, float | int]] = {}

    with engine.begin() as conn:
        vider_tables(conn)
        stats["mediatheque"] = charger_mediatheques(conn)
        stats["document"] = charger_documents(conn)
        stats["adherent"] = charger_adherents(conn)
        stats["emprunt"] = charger_emprunts(conn)

    ecrire_rejets()

    logger.info("=== Récapitulatif ===")
    for table, s in stats.items():
        logger.info(
            "%s : lues=%s insérées=%s rejetées=%s durée=%.2fs",
            table,
            s["lues"],
            s["inserees"],
            s["rejetees"],
            s["duree"],
        )


if __name__ == "__main__":
    main()
