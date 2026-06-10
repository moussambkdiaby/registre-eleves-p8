# ============================================
# IMPORT DES DONNÉES valides.json → PostgreSQL
# Projet DEV DATA P8
# ============================================

import json
import os
import psycopg2
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis .env
load_dotenv()

# ============================================
# NORMALISATION DES MATIÈRES
# Gère les variantes d'écriture du JSON
# ============================================
MATIERES_NORMALISEES = {
    "math":      "Math",
    "maths":     "Math",
    "francais":  "Francais",
    "français":  "Francais",
    "françcais": "Francais",
    "anglais":   "Anglais",
    "pc":        "PC",
    "svt":       "SVT",
    "hg":        "HG"
}

def normaliser_matiere(nom):
    """Normalise le nom d'une matière."""
    return MATIERES_NORMALISEES.get(nom.lower().strip(), nom.strip())

def normaliser_classe(classe):
    """Normalise le nom d'une classe. Ex: 6emeA → 6EME_A"""
    return classe.strip().upper().replace("EME", "EME_")

def calculer_moyenne_matiere(devoirs, examen):
    """Calcule la moyenne selon la formule : (moy_devoirs + 2×examen) / 3"""
    if not devoirs:
        return round(examen, 2)
    moyenne_devoirs = sum(devoirs) / len(devoirs)
    return round((moyenne_devoirs + 2 * examen) / 3, 2)

def calculer_moyenne_generale(moyennes):
    """Calcule la moyenne générale à partir des moyennes par matière."""
    if not moyennes:
        return 0
    return round(sum(moyennes) / len(moyennes), 2)

# ============================================
# CONNEXION À POSTGRESQL
# ============================================
def get_connexion():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

# ============================================
# FONCTIONS D'INSERTION
# ============================================
def get_ou_creer_classe(cursor, libelle):
    """Récupère l'id d'une classe ou la crée si elle n'existe pas."""
    libelle_norm = normaliser_classe(libelle)
    
    # Vérifie si la classe existe
    cursor.execute(
        "SELECT id_classe FROM classe WHERE libelle = %s",
        (libelle_norm,)
    )
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    # Sinon on la crée
    cursor.execute(
        "INSERT INTO classe (libelle) VALUES (%s) RETURNING id_classe",
        (libelle_norm,)
    )
    return cursor.fetchone()[0]

def etudiant_existe(cursor, numero):
    """Vérifie si un étudiant existe déjà via son numéro."""
    cursor.execute(
        "SELECT id_etudiant FROM etudiant WHERE numero = %s",
        (numero,)
    )
    return cursor.fetchone() is not None

def inserer_etudiant(cursor, etudiant, id_classe, moyenne_generale):
    """Insère un étudiant et retourne son id."""
    cursor.execute("""
        INSERT INTO etudiant 
            (code, numero, nom, prenom, date_naissance, moyenne_generale, id_classe)
        VALUES 
            (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id_etudiant
    """, (
        etudiant["code"],
        etudiant["numero"],
        etudiant["nom"],
        etudiant["prenom"],
        etudiant["date"],
        moyenne_generale,
        id_classe
    ))
    return cursor.fetchone()[0]

def inserer_resultat_matiere(cursor, id_etudiant, id_matiere, note_examen, moyenne):
    """Insère un résultat matière et retourne son id."""
    cursor.execute("""
        INSERT INTO resultat_matiere 
            (note_examen, moyenne_matiere, id_etudiant, id_matiere)
        VALUES (%s, %s, %s, %s)
        RETURNING id_resultat
    """, (note_examen, moyenne, id_etudiant, id_matiere))
    return cursor.fetchone()[0]

def inserer_devoirs(cursor, id_resultat, devoirs):
    """Insère les notes de devoir."""
    for note in devoirs:
        cursor.execute(
            "INSERT INTO devoir (note_devoir, id_resultat) VALUES (%s, %s)",
            (note, id_resultat)
        )

# ============================================
# FONCTION PRINCIPALE D'IMPORT
# ============================================
def importer_json():
    chemin_json = os.path.join(
        os.path.dirname(__file__), "..", "data", "valides.json"
    )

    # Lecture du fichier JSON
    with open(chemin_json, "r", encoding="utf-8") as f:
        etudiants = json.load(f)

    print(f"📂 {len(etudiants)} étudiants trouvés dans le fichier JSON")

    conn = get_connexion()
    cursor = conn.cursor()

    # Récupération des matières existantes en base
    cursor.execute("SELECT id_matiere, libelle FROM matiere")
    matieres_db = {row[1]: row[0] for row in cursor.fetchall()}

    compteurs = {"importes": 0, "doublons": 0, "erreurs": 0}

    for etudiant in etudiants:
        try:
            # Vérification doublon
            if etudiant_existe(cursor, etudiant["numero"]):
                print(f"  ⚠️  Doublon ignoré : {etudiant['numero']}")
                compteurs["doublons"] += 1
                continue

            # Récupération/création de la classe
            id_classe = get_ou_creer_classe(cursor, etudiant["classe"])

            # Calcul des moyennes par matière
            moyennes = []
            matieres_a_inserer = []

            for nom_matiere, data in etudiant["matieres"].items():
                nom_norm = normaliser_matiere(nom_matiere)

                if nom_norm not in matieres_db:
                    print(f"  ⚠️  Matière inconnue ignorée : {nom_matiere}")
                    continue

                devoirs  = data.get("devoirs", [])
                examen   = data.get("examen", 0)
                moyenne  = calculer_moyenne_matiere(devoirs, examen)
                moyennes.append(moyenne)

                matieres_a_inserer.append({
                    "id_matiere": matieres_db[nom_norm],
                    "examen":     examen,
                    "moyenne":    moyenne,
                    "devoirs":    devoirs
                })

            # Calcul moyenne générale
            moyenne_generale = calculer_moyenne_generale(moyennes)

            # Insertion étudiant
            id_etudiant = inserer_etudiant(
                cursor, etudiant, id_classe, moyenne_generale
            )

            # Insertion matières et devoirs
            for m in matieres_a_inserer:
                id_resultat = inserer_resultat_matiere(
                    cursor, id_etudiant,
                    m["id_matiere"], m["examen"], m["moyenne"]
                )
                inserer_devoirs(cursor, id_resultat, m["devoirs"])

            compteurs["importes"] += 1
            print(f"  ✅ Importé : {etudiant['prenom']} {etudiant['nom']}")

        except Exception as e:
            conn.rollback()
            print(f"  ❌ Erreur pour {etudiant.get('numero')} : {e}")
            compteurs["erreurs"] += 1
            continue

        conn.commit()

    cursor.close()
    conn.close()

    print("\n" + "="*40)
    print(f"✅ Importés  : {compteurs['importes']}")
    print(f"⚠️  Doublons  : {compteurs['doublons']}")
    print(f"❌ Erreurs   : {compteurs['erreurs']}")
    print("="*40)

# ============================================
# POINT D'ENTRÉE
# ============================================
if __name__ == "__main__":
    importer_json()