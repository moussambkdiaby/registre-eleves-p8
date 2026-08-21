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


def _note_valide(valeur) -> bool:
    """Une note doit être comprise entre 0 et 20 pour être considérée valide."""
    if valeur is None:
        return False
    return 0 <= valeur <= 20


def importer_etudiants(numeros_a_importer: list[str]) -> dict:
    """
    Importe en PostgreSQL les étudiants du JSON dont le numero est dans
    numeros_a_importer, en ignorant ceux déjà présents en base (doublons).
    Les notes hors de la plage 0-20 sont rejetées individuellement et
    signalées, sans bloquer l'import de l'étudiant.
    """
    donnees_json = charger_valides_json()
    numeros_existants = get_numeros_existants()
    matieres_id = get_matieres_id()

    importes = 0
    ignores = 0
    anomalies = []

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

            # 2. Insertion des notes, matière par matière, avec validation
            for nom_matiere, valeurs in etudiant["notes"].items():
                matiere_id = matieres_id.get(nom_matiere)
                if matiere_id is None:
                    continue  # matière inconnue dans la table matieres

                devoirs = valeurs.get("devoirs", [])
                examen = valeurs.get("examen")
                moyenne = valeurs.get("moyenne")

                devoirs_invalides = [d for d in devoirs if not _note_valide(d)]
                examen_invalide = not _note_valide(examen)

                if devoirs_invalides or examen_invalide:
                    anomalies.append({
                        "numero": etudiant["numero"],
                        "nom": etudiant["nom"],
                        "matiere": nom_matiere,
                        "devoirs_invalides": devoirs_invalides,
                        "examen_invalide": examen if examen_invalide else None,
                    })
                    continue  # on n'insère pas cette matière pour cet étudiant

                cur.execute(
                    """
                    INSERT INTO notes (etudiant_id, matiere_id, devoirs, examen, moyenne)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (etudiant_id, matiere_id, devoirs, examen, moyenne),
                )

        importes += 1

    return {
        "importes": importes,
        "ignores": ignores,
        "anomalies": anomalies,
    }

def rechercher_etudiants_db(numero=None, code=None, nom=None, prenom=None, classe=None) -> list[dict]:
    """Recherche les étudiants en base, avec filtres optionnels, hors archivés."""
    conditions = ["e.archive = FALSE"]
    params = []

    if numero:
        conditions.append("e.numero ILIKE %s")
        params.append(f"%{numero}%")
    if code:
        conditions.append("e.code ILIKE %s")
        params.append(f"%{code}%")
    if nom:
        conditions.append("e.nom ILIKE %s")
        params.append(f"%{nom}%")
    if prenom:
        conditions.append("e.prenom ILIKE %s")
        params.append(f"%{prenom}%")
    if classe:
        conditions.append("e.classe = %s")
        params.append(classe)

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT e.id, e.numero, e.code, e.nom, e.prenom, e.date_naissance, e.classe,
               ROUND(AVG(n.moyenne), 2) AS moyenne_generale
        FROM etudiants e
        LEFT JOIN notes n ON n.etudiant_id = e.id
        WHERE {where_clause}
        GROUP BY e.id
        ORDER BY e.id
    """

    with get_cursor() as cur:
        cur.execute(query, params)
        resultats = cur.fetchall()

    for r in resultats:
        r["source"] = "DB"
    return resultats


def rechercher_etudiants_json(numero=None, code=None, nom=None, prenom=None, classe=None) -> list[dict]:
    """Recherche dans le JSON, en excluant les étudiants déjà importés en base."""
    donnees = charger_valides_json()
    numeros_db = get_numeros_existants()

    resultats = []
    for e in donnees:
        if e["numero"] in numeros_db:
            continue  # déjà en DB, on ne le montre pas en double

        if numero and numero.lower() not in e["numero"].lower():
            continue
        if code and code.lower() not in e["code"].lower():
            continue
        if nom and nom.lower() not in e["nom"].lower():
            continue
        if prenom and prenom.lower() not in e["prenom"].lower():
            continue
        if classe and classe != e["classe"]:
            continue

        moyennes = [m["moyenne"] for m in e["notes"].values()]
        moyenne_generale = round(sum(moyennes) / len(moyennes), 2) if moyennes else None

        resultats.append({
            "id": None,
            "numero": e["numero"],
            "code": e["code"],
            "nom": e["nom"],
            "prenom": e["prenom"],
            "date_naissance": e["date_naissance"],
            "classe": e["classe"],
            "moyenne_generale": moyenne_generale,
            "source": "JSON",
        })
    return resultats


def obtenir_etudiants(page=1, limite=5, numero=None, code=None, nom=None, prenom=None, classe=None) -> dict:
    """Combine DB + JSON, applique les filtres, puis découpe selon la pagination."""
    resultats_db = rechercher_etudiants_db(numero, code, nom, prenom, classe)
    resultats_json = rechercher_etudiants_json(numero, code, nom, prenom, classe)

    combines = resultats_db + resultats_json
    total = len(combines)

    debut = (page - 1) * limite
    fin = debut + limite
    page_resultats = combines[debut:fin]

    return {
        "total": total,
        "page": page,
        "limite": limite,
        "resultats": page_resultats,
    }


def ajouter_etudiant(etudiant: dict) -> int:
    """Insère un nouvel étudiant ajouté manuellement, avec ses notes optionnelles."""
    matieres_id = get_matieres_id()

    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO etudiants (numero, code, nom, prenom, date_naissance, classe)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                etudiant["numero"],
                etudiant.get("code"),
                etudiant["nom"],
                etudiant["prenom"],
                etudiant["date_naissance"],
                etudiant["classe"],
            ),
        )
        etudiant_id = cur.fetchone()["id"]

        for nom_matiere, valeurs in etudiant.get("notes", {}).items():
            matiere_id = matieres_id.get(nom_matiere)
            if matiere_id is None:
                continue
            cur.execute(
                """
                INSERT INTO notes (etudiant_id, matiere_id, devoirs, examen, moyenne)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (etudiant_id, matiere_id, valeurs["devoirs"], valeurs["examen"], valeurs["moyenne"]),
            )

    return etudiant_id