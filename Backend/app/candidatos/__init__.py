# app/candidatos/__init__.py
"""
Módulo de Candidatos e Ingreso de CV (Postulaciones)
"""
from app.candidatos.models import Candidato, DireccionCandidato, CandidatoHabilidad
from app.candidatos.schemas import CandidatoCreate, CandidatoPerfilResponse
#from app.candidatos.services import crear_candidato_completo

__all__ = [
    "Candidato",
    "DireccionCandidato",
    "CandidatoHabilidad",
    "CandidatoCreate",
    "CandidatoPerfilResponse",
    "crear_candidato_completo",
]