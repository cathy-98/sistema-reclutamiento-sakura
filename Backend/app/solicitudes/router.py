from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.solicitudes.schemas import (
    SolicitudCreate, 
    SolicitudResponse, 
    SolicitudUpdate, 
    SolicitudEstadoUpdate,
    SolicitudHabilidadCreate,
    SolicitudHabilidadResponse
)
from app.solicitudes.models import Solicitud, SolicitudHabilidad
from app.solicitudes.services import evaluar_candidato_cumple_excluyentes

router = APIRouter(
    prefix="/solicitudes",
    tags=["Solicitudes / Vacantes"]
)

# -------------------------------------------------------------------
# 1. POST /solicitudes/ (Crear vacante)
# -------------------------------------------------------------------
@router.post("/", response_model=SolicitudResponse, status_code=status.HTTP_201_CREATED)
def crear_solicitud(solicitud_in: SolicitudCreate, db: Session = Depends(get_db)):
    """Crea una nueva vacante asociando el usuario creador y sus habilidades requeridas."""
    datos_solicitud = solicitud_in.model_dump(exclude={"habilidades"})
    nueva_solicitud = Solicitud(**datos_solicitud)
    
    db.add(nueva_solicitud)
    db.flush()

    for hab in solicitud_in.habilidades:
        nueva_habilidad = SolicitudHabilidad(
            solhb_solicitud_id=nueva_solicitud.sol_id,
            solhb_habilidad_id=hab.solhb_habilidad_id,
            solhb_nivel_habilidad_id=hab.solhb_nivel_habilidad_id,
            solhb_anios_experiencia_req=hab.solhb_anios_experiencia_req,
            solhb_es_excluyente=hab.solhb_es_excluyente
        )
        db.add(nueva_habilidad)

    db.commit()
    db.refresh(nueva_solicitud)
    return nueva_solicitud

# -------------------------------------------------------------------
# 2. GET /solicitudes/ (Listar con filtros)
# -------------------------------------------------------------------
@router.get("/", response_model=List[SolicitudResponse])
def listar_solicitudes(
    estado_id: Optional[int] = Query(None, description="Filtrar por estado"),
    prioridad_id: Optional[int] = Query(None, description="Filtrar por prioridad"),
    cargo_id: Optional[int] = Query(None, description="Filtrar por cargo"),
    skip: int = Query(0, ge=0, description="Registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Límite por página"),
    db: Session = Depends(get_db)):
    """Lista las vacantes permitiendo filtros opcionales y paginación."""
    query = db.query(Solicitud)

    if estado_id is not None:
        query = query.filter(Solicitud.sol_estado_solicitud_id == estado_id)
    if prioridad_id is not None:
        query = query.filter(Solicitud.sol_prioridad_id == prioridad_id)
    if cargo_id is not None:
        query = query.filter(Solicitud.sol_cargo_id == cargo_id)

    return query.offset(skip).limit(limit).all()


# -------------------------------------------------------------------
# 3. GET /solicitudes/{id} (Detalle de vacante)
# -------------------------------------------------------------------
@router.get("/{id}", response_model=SolicitudResponse)
def obtener_solicitud_por_id(id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle completo de una vacante por su ID."""
    solicitud = db.query(Solicitud).filter(Solicitud.sol_id == id).first()
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Vacante con ID {id} no encontrada."
        )
    return solicitud


# -------------------------------------------------------------------
# 4. PATCH /solicitudes/{id} (Modificación de parámetros)
# -------------------------------------------------------------------
@router.patch("/{id}", response_model=SolicitudResponse)
def actualizar_solicitud(id: int, solicitud_update: SolicitudUpdate, db: Session = Depends(get_db)):
    """Permite modificar parámetros técnicos, salarios o descripciones de la vacante."""
    solicitud = db.query(Solicitud).filter(Solicitud.sol_id == id).first()
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Vacante con ID {id} no encontrada."
        )

    update_data = solicitud_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(solicitud, field, value)

    db.commit()
    db.refresh(solicitud)
    return solicitud


# -------------------------------------------------------------------
# 5. PATCH /solicitudes/{id}/estado (Cambio de estado)
# -------------------------------------------------------------------
@router.patch("/{id}/estado", response_model=SolicitudResponse)
def cambiar_estado_solicitud(id: int,estado_in: SolicitudEstadoUpdate,db: Session = Depends(get_db)):
    """Actualiza de forma directa el estado de flujo de la vacante."""
    solicitud = db.query(Solicitud).filter(Solicitud.sol_id == id).first()
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Vacante con ID {id} no encontrada."
        )

    solicitud.sol_estado_solicitud_id = estado_in.sol_estado_solicitud_id
    db.commit()
    db.refresh(solicitud)
    return solicitud


# -------------------------------------------------------------------
# 6. PATCH /solicitudes/{id}/desactivar (Borrado Lógico)
# -------------------------------------------------------------------
@router.patch("/{id}/desactivar", response_model=SolicitudResponse)
def inactivar_solicitud(id: int, db: Session = Depends(get_db)):
    """Inactiva o archiva una vacante (borrado lógico) sin eliminar datos históricos."""
    solicitud = db.query(Solicitud).filter(Solicitud.sol_id == id).first()
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Vacante con ID {id} no encontrada."
        )

    # Asume ID de estado inactivo/inactivada (ejemplo: 99 u otro configurado)
    solicitud.sol_estado_solicitud_id = 99
    db.commit()
    db.refresh(solicitud)
    return solicitud


# -------------------------------------------------------------------
# 7. POST /solicitudes/{id}/habilidades (Agregar Habilidades)
# -------------------------------------------------------------------
@router.post("/{id}/habilidades", response_model=List[SolicitudHabilidadResponse])
def agregar_habilidades_solicitud(id: int, habilidades: List[SolicitudHabilidadCreate], db: Session = Depends(get_db)):
    """Agrega una o más habilidades requeridas a una vacante ya existente."""
    solicitud = db.query(Solicitud).filter(Solicitud.sol_id == id).first()
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Vacante con ID {id} no encontrada."
        )

    nuevas_habilidades = []
    for hab in habilidades:
        nueva_hab = SolicitudHabilidad(
            solhb_solicitud_id=id,
            solhb_habilidad_id=hab.solhb_habilidad_id,
            solhb_nivel_habilidad_id=hab.solhb_nivel_habilidad_id,
            solhb_anios_experiencia_req=hab.solhb_anios_experiencia_req,
            solhb_es_excluyente=hab.solhb_es_excluyente
        )
        db.add(nueva_hab)
        nuevas_habilidades.append(nueva_hab)

    db.commit()
    return nuevas_habilidades


# -------------------------------------------------------------------
# 8. DELETE /solicitudes/{id}/habilidades/{habilidad_id} (Remover Habilidad)
# -------------------------------------------------------------------
@router.delete("/{id}/habilidades/{habilidad_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_habilidad_solicitud(id: int, habilidad_id: int, db: Session = Depends(get_db)):
    """Remueve una habilidad requerida específica de una vacante."""
    relacion = db.query(SolicitudHabilidad).filter(
        SolicitudHabilidad.solhb_solicitud_id == id,
        SolicitudHabilidad.solhb_habilidad_id == habilidad_id
    ).first()

    if not relacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No se encontró la habilidad {habilidad_id} vinculada a la vacante {id}."
        )

    db.delete(relacion)
    db.commit()
    return None
# -------------------------------------------------------------------
# 9. POST /solicitudes/{id}/evaluar-candidato (Matching de Requisitos)
# -------------------------------------------------------------------
@router.post("/{id}/evaluar-candidato")
def evaluar_candidato_solicitud(id: int, habilidades_candidato: list[dict],db: Session = Depends(get_db)):
    """Evalúa si un candidato cumple con las habilidades excluyentes de la vacante."""
    try:
        return evaluar_candidato_cumple_excluyentes(db, id, habilidades_candidato)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# -------------------------------------------------------------------
# 10. GET /solicitudes/{id}/candidatos (Listar Candidatos Postulados)
# -------------------------------------------------------------------
@router.get("/{id}/candidatos")
def listar_candidatos_solicitud(id: int, db: Session = Depends(get_db)):
    """Retorna los candidatos postulados o asignados a la vacante."""
    solicitud = db.query(Solicitud).filter(Solicitud.sol_id == id).first()
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Vacante con ID {id} no encontrada."
        )
    
    # Retorna la lista de postulaciones asociadas
    return getattr(solicitud, "postulaciones", [])
