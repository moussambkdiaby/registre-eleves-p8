import json
from pathlib import Path
from app.database import get_cursor
from datetime import datetime

# Chemin absolu vers data/valides.json, peu importe d'où on lance Python
BASE_DIR = Path(__file__).resolve().parent.parent.parent
JSON_PATH = BASE_DIR / "data" / "valides.json"


def charger_valides_json() -> list[dict]:
    """Lit le fichier valides.json et renvoie la liste des étudiants."""
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_numeros_existants() -> set[str]:
    """Renvoie l'ensemble des numéros d'étudiants déjà présents en base."""
    with get_cursor() as cur:
        cur.execute("SELECT numero FROM etudiants")
        resultats = cur.fetchall()
    return {row["numero"] for row in resultats}


def marquer_origine_json(donnees_json: list[dict]) -> list[dict]:
    """
    Ajoute à chaque étudiant du JSON une info indiquant s'il est déjà
    importé en base (doublon) ou non.
    """
    numeros_db = get_numeros_existants()
    for etudiant in donnees_json:
        etudiant["deja_importe"] = etudiant["numero"] in numeros_db
        etudiant["source"] = "JSON"
    return donnees_json   




def _convertir_date(date_str: str) -> str:
    """Convertit une date JJ/MM/AAAA (format JSON) en AAAA-MM-JJ (format PostgreSQL)."""
    return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")


def get_matieres_id() -> dict[str, int]:
    """Renvoie un dictionnaire {nom_matiere: id} pour retrouver l'id d'une matière par son nom."""
    with get_cursor() as cur:
        cur.execute("SELECT id, nom FROM matieres")
        resultats = cur.fetchall()
    return {row["nom"]: row["id"] for row in resultats}


def importer_etudiants(numeros_a_importer: list[str]) -> dict:
    """
    Importe en PostgreSQL les étudiants du JSON dont le numero est dans
    numeros_a_importer, en ignorant ceux déjà présents en base (doublons).
    Renvoie un résumé : combien importés, combien ignorés.
    """
    donnees_json = charger_valides_json()
    numeros_existants = get_numeros_existants()
    matieres_id = get_matieres_id()

    importes = 0
    ignores = 0

    for etudiant in donnees_json:
        if etudiant["numero"] not in numeros_a_importer:
            continue

        if etudiant["numero"] in numeros_existants:
            ignores += 1
            continue

        with get_cursor(commit=True) as cur:
            # 1. Insertion de l'étudiant
            cur.execute(
                """
                INSERT INTO etudiants (numero, code, nom, prenom, date_naissance, classe)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    etudiant["numero"],
                    etudiant["code"],
                    etudiant["nom"],
                    etudiant["prenom"],
                    _convertir_date(etudiant["date_naissance"]),
                    etudiant["classe"],
                ),
            )
            etudiant_id = cur.fetchone()["id"]

            # 2. Insertion des notes, matière par matière
            for nom_matiere, valeurs in etudiant["notes"].items():
                matiere_id = matieres_id.get(nom_matiere)
                if matiere_id is None:
                    continue  # matière inconnue dans la table matieres, on ignore

                cur.execute(
                    """
                    INSERT INTO notes (etudiant_id, matiere_id, devoirs, examen, moyenne)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        etudiant_id,
                        matiere_id,
                        valeurs["devoirs"],
                        valeurs["examen"],
                        valeurs["moyenne"],
                    ),
                )

        importes += 1

    return {"importes": importes, "ignores": ignores}