from datetime import date
from pydantic import BaseModel, Field, field_validator


class NoteMatiere(BaseModel):
    devoirs: list[float] = []
    examen: float | None = None
    moyenne: float | None = None

    @field_validator("examen")
    @classmethod
    def examen_valide(cls, v):
        if v is not None and not (0 <= v <= 20):
            raise ValueError("La note d'examen doit être comprise entre 0 et 20")
        return v

    @field_validator("devoirs")
    @classmethod
    def devoirs_valides(cls, v):
        for note in v:
            if not (0 <= note <= 20):
                raise ValueError("Chaque note de devoir doit être comprise entre 0 et 20")
        return v


class EtudiantCreate(BaseModel):
    numero: str = Field(..., min_length=1, max_length=20)
    code: str | None = Field(None, max_length=20)
    nom: str = Field(..., min_length=1, max_length=100)
    prenom: str = Field(..., min_length=1, max_length=100)
    date_naissance: date
    classe: str = Field(..., min_length=1, max_length=20)
    notes: dict[str, NoteMatiere] = {}