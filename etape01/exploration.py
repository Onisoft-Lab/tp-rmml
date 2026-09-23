import csv
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CSVS = {
    "mediatheques": DATA_DIR / "mediatheques.csv",
    "documents": DATA_DIR / "documents.csv",
    "adherents": DATA_DIR / "adherents.csv",
    "emprunts": DATA_DIR / "emprunts.csv",
}

class Mediatheque:
    def __init__(self, code_site: str, nom: str, commune: str, annee_ouverture: int, surface_m2: int):
        self.code_site = code_site
        self.nom = nom
        self.commune = commune
        self.annee_ouverture = annee_ouverture
        self.surface_m2 = surface_m2

    """
    @param year: year to calculate the seniority
    @return: number of years since the mediatheque was opened
    """
    def seniority(self, year: int) -> int:
        if isinstance(self.annee_ouverture, str):
            self.annee_ouverture = int(self.annee_ouverture)
        return year - self.annee_ouverture

    def __str__(self) -> str:
        return f"{self.code_site} - {self.nom} ({self.commune}), {self.surface_m2} m²"

"""
@param csv_path: path of the csv file to read
@return: list of dictionaries
"""
def read_csv(csv_path: Path) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

"""
@param lines: list of dictionaries
@param column: column to count by
@return: Counter of the column
"""
def count_by(lines: list[dict], column: str) -> Counter:
    return Counter(line[column] for line in lines)


def loans_in_progress(loans: list[dict]) -> list[dict]:
    return [loan for loan in loans if not loan["date_retour_reelle"]]

if __name__ == "__main__":
    datas = {name: read_csv(chemin) for name, chemin in CSVS.items()}

    print("==================== Nombre de lignes par fichier ====================")
    for name, csv in datas.items():
        print(len(csv))

    print("===== Mediatheques ======")
    for mediatheque in datas["mediatheques"]:
        mediatheque = Mediatheque(**mediatheque)
        print(f"{mediatheque} ({mediatheque.seniority(2026)} ans en 2026)")

    print("===== Nombre d'emprunts par code_site ======")
    for code_site, count in count_by(datas["emprunts"], "code_site").most_common():
        print(f"{code_site}: {count}")

    print("===== Nombre de documents par support ======")
    for support, count in count_by(datas["documents"], "support").most_common():
        print(f"{support}: {count}")
    
    print("===== Nombre d'adherents par tranche d'age ======")
    for age, count in count_by(datas["adherents"], "tranche_age").most_common():
        print(f"{age}: {count}")

    print("===== Nombre d'emprunts en cours ======")
    print(len(loans_in_progress(datas["emprunts"])))