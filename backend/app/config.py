from pathlib import Path
from pydantic_settings import BaseSettings

# Chemin absolu vers la racine du projet (2 niveaux au-dessus de ce fichier :
# app/config.py -> backend/ -> racine du projet)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    class Config:
        env_file = str(ENV_PATH)


settings = Settings()