from fastapi import APIRouter

from app.models import (
    get_kpis,
    get_repartition_par_classe,
    get_repartition_par_source,
    get_moyenne_par_classe,
    get_moyenne_par_classe_globale,
    get_top10_meilleures_moyennes,
)

router = APIRouter()


@router.get("/stats/kpis")
def kpis():
    """Indicateurs globaux pour le dashboard."""
    return get_kpis()


@router.get("/stats/repartition-classe")
def repartition_classe():
    """Nombre d'étudiants par classe."""
    return {"resultats": get_repartition_par_classe()}


@router.get("/stats/repartition-source")
def repartition_source():
    """Nombre d'étudiants par source (DB / JSON)."""
    return {"resultats": get_repartition_par_source()}


@router.get("/stats/moyenne-classe")
def moyenne_classe():
    """Moyenne générale par classe."""
    return {"resultats": get_moyenne_par_classe()}


@router.get("/stats/top10")
def top10():
    """Top 10 des meilleures moyennes générales."""
    return {"resultats": get_top10_meilleures_moyennes()}

@router.get("/stats/moyenne-classe-globale")
def moyenne_classe_globale():
    """Moyenne générale par classe, DB + JSON combinés."""
    return {"resultats": get_moyenne_par_classe_globale()}