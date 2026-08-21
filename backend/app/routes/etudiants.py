from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from psycopg2 import errors as pg_errors

from app.schemas import EtudiantCreate, EtudiantUpdate, NoteUpdate
from app.models import (
    obtenir_etudiants,
    importer_etudiants,
    ajouter_etudiant,
    modifier_etudiant,
    modifier_note,
    archiver_etudiant,
    restaurer_etudiant,
    get_etudiants_archives,
)

router = APIRouter()


@router.get("/etudiants")
def liste_etudiants(
    page: int = Query(1, ge=1),
    limite: int = Query(5, ge=1, le=100),
    numero: str | None = None,
    code: str | None = None,
    nom: str | None = None,
    prenom: str | None = None,
    classe: str | None = None,
):
    """Liste paginée des étudiants, fusion PostgreSQL + JSON, avec filtres optionnels."""
    return obtenir_etudiants(
        page=page, limite=limite,
        numero=numero, code=code, nom=nom, prenom=prenom, classe=classe,
    )


class ImportRequest(BaseModel):
    numeros: list[str]


@router.post("/etudiants/importer")
def importer(donnees: ImportRequest):
    """Importe en PostgreSQL les étudiants JSON dont les numéros sont fournis."""
    resultat = importer_etudiants(donnees.numeros)
    return resultat


@router.post("/etudiants", status_code=201)
def creer_etudiant(etudiant: EtudiantCreate):
    """Ajoute un nouvel étudiant en base, avec validation complète."""
    try:
        etudiant_id = ajouter_etudiant(etudiant.model_dump())
    except pg_errors.UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail=f"Un étudiant avec le numero '{etudiant.numero}' existe déjà.",
        )
    return {"id": etudiant_id, "message": "Étudiant ajouté avec succès"}


@router.patch("/etudiants/{etudiant_id}")
def editer_etudiant(etudiant_id: int, champs: EtudiantUpdate):
    """Modifie un ou plusieurs champs d'un étudiant existant (données DB uniquement)."""
    succes = modifier_etudiant(etudiant_id, champs.model_dump())
    if not succes:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    return {"message": "Étudiant mis à jour"}


@router.patch("/etudiants/{etudiant_id}/notes/{matiere}")
def editer_note(etudiant_id: int, matiere: str, champs: NoteUpdate):
    """Modifie (ou crée) la note d'une matière pour un étudiant (données DB uniquement)."""
    succes = modifier_note(etudiant_id, matiere, champs.model_dump())
    if not succes:
        raise HTTPException(status_code=404, detail="Étudiant ou matière introuvable")
    return {"message": "Note mise à jour"}


@router.patch("/etudiants/{etudiant_id}/archiver")
def archiver(etudiant_id: int):
    """Archive un étudiant (ne le supprime pas, juste le masque des listes principales)."""
    succes = archiver_etudiant(etudiant_id)
    if not succes:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    return {"message": "Étudiant archivé"}


@router.patch("/etudiants/{etudiant_id}/restaurer")
def restaurer(etudiant_id: int):
    """Restaure un étudiant précédemment archivé."""
    succes = restaurer_etudiant(etudiant_id)
    if not succes:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    return {"message": "Étudiant restauré"}


@router.get("/etudiants/archives")
def liste_archives():
    """Liste tous les étudiants archivés."""
    return {"resultats": get_etudiants_archives()}