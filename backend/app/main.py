from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, etudiants, stats

app = FastAPI(title="API Gestion Étudiants - Projet P8")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(etudiants.router)
app.include_router(stats.router)


@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API du projet P8"}