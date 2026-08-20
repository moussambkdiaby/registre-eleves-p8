import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

from app.config import settings


def get_connection():
    """Ouvre une nouvelle connexion à PostgreSQL."""
    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )


@contextmanager
def get_cursor(commit: bool = False):
    """
    Fournit un curseur prêt à l'emploi, avec fermeture automatique
    de la connexion et du curseur, même en cas d'erreur.

    Utilisation :
        with get_cursor() as cur:
            cur.execute("SELECT * FROM etudiants")
            resultats = cur.fetchall()

        with get_cursor(commit=True) as cur:
            cur.execute("INSERT INTO etudiants (...) VALUES (...)")
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()