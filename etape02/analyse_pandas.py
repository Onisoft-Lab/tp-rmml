import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUT_DIR = Path(__file__).resolve().parent.parent / "sorties"

CSVS = {
    "mediatheques": DATA_DIR / "mediatheques.csv",
    "documents": DATA_DIR / "documents.csv",
    "adherents": DATA_DIR / "adherents.csv",
    "emprunts": DATA_DIR / "emprunts.csv",
}

df_sites = pd.read_csv(CSVS["mediatheques"])
df_documents = pd.read_csv(CSVS["documents"])
df_adherents = pd.read_csv(CSVS["adherents"])
df_emprunts = pd.read_csv(CSVS["emprunts"])

df_emprunts["date_emprunt"] = pd.to_datetime(df_emprunts["date_emprunt"])
df_emprunts["date_retour_prevue"] = pd.to_datetime(df_emprunts["date_retour_prevue"])
df_emprunts["date_retour_reelle"] = pd.to_datetime(df_emprunts["date_retour_reelle"])

# print(df_emprunts.dtypes)

documents_shape = df_documents.shape
documents_na = df_documents.isna().sum()

emprunts_shape = df_emprunts.shape
emprunts_na = df_emprunts.isna().sum()

print(f"==== Documents ==== \n\nShape: {documents_shape} \n\nNA:\n{documents_na}\n")
print(f"==== Emprunts ==== \n\nShape: {emprunts_shape} \n\nNA:\n{emprunts_na}\n")
print("\n==== Les 10 documents les plus chers ====\n")
print(df_documents.sort_values(by="prix_achat", ascending=False).head(10))

print("\n==== Le nombre de documents par genre ====\n")
print(df_documents.groupby("genre").size().sort_values(ascending=False))

print("\n==== Fusion des DataFrames ====\n")
df_complet = df_emprunts.merge(df_documents, on="id_document", how="left").merge(df_adherents, on="id_adherent", how="left")
print(df_complet.shape)
print(df_complet.isna().sum())

print("\n==== Nombre de lignes de df_complet sans document correspondant ====\n")
print(df_complet["titre"].isna().sum())

df_complet_top10 = (
    df_complet[df_complet["titre"].notna()]
    .groupby("id_document", as_index=False)
    .agg(
        titre=("titre", "first"),
        auteur=("auteur", "first"),
        nb_emprunts=("id_emprunt", "nunique"),
    )
    .sort_values("nb_emprunts", ascending=False)
    .head(10)
)
df_complet_top10.to_csv(OUT_DIR / "top10_documents.csv", index=False, encoding="utf-8")
