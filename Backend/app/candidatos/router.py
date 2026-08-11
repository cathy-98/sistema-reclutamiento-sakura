from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.candidatos.schemas import CandidatoCreate, CandidatoPerfilResponse
from app.candidatos.services import crear_candidato_completo
from app.candidatos.models import Candidato

router = APIRouter(prefix="/candidatos", tags=["Candidatos"])

@router.post("/", response_model=CandidatoPerfilResponse, status_code=status.HTTP_201_CREATED)
def registrar_candidato(candidato_in: CandidatoCreate, db: Session = Depends(get_db)):
    """Crea un candidato completo con su trayectoria laboral, estudios y habilidades."""
    # Verificar unicidad por RUT o Email
    existente = db.query(Candidato).filter(
        (Candidato.cand_rut_sin_dv == candidato_in.cand_rut_sin_dv) |
        (Candidato.cand_email == candidato_in.cand_email)
    ).first()
    
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un candidato registrado con el mismo RUT o Correo Electrónico."
        )
        
    return crear_candidato_completo(db, candidato_in)

@router.get("/{id}", response_model=CandidatoPerfilResponse)
def obtener_perfil_candidato(id: int, db: Session = Depends(get_db)):
    """Obtiene la hoja de vida / perfil completo del candidato."""
    candidato = db.query(Candidato).filter(Candidato.cand_id == id).first()
    if not candidato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidato con ID {id} no encontrado."
        )
    return candidato
