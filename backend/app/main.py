from fastapi import FastAPI
from app.routes import health, etudiants, stats

app = FastAPI(title="API Gestion Étudiants - Projet P8")

app.include_router(health.router)
app.include_router(etudiants.router)
app.include_router(stats.router)


@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API du projet P8"}