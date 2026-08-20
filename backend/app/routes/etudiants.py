from fastapi import APIRouter, Query
from app.models import obtenir_etudiants

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