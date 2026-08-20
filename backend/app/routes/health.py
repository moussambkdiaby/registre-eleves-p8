from fastapi import APIRouter
from app.database import get_cursor

router = APIRouter()


@router.get("/health")
def health_check():
    """Vérifie que l'API tourne et que la base de données répond."""
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        db_status = "connectée"
    except Exception as e:
        db_status = f"erreur : {str(e)}"

    return {
        "api": "en ligne",
        "base_de_donnees": db_status,
    }