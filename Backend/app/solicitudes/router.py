from typing import List, Optional
import importlib
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.solicitudes.schemas import (
    SolicitudCreate, 
    SolicitudResponse, 
    SolicitudUpdate, 
    SolicitudEstadoUpdate,
    SolicitudHabilidadCreate,
    SolicitudHabilidadResponse
)
from app.solicitudes.models import Solicitud, SolicitudHabilidad, SolicitudCandidato
from app.solicitudes.services import evaluar_candidato_cumple_excluyentes

# Cargar dinámicamente el módulo de listeners para asegurar su registro en SQLAlchemy
importlib.import_module("app.listeners.solicitud_listeners")

router = APIRouter(
    prefix="/solicitudes",
    tags=["Solicitudes"]
)

# -------------------------------------------------------------------
# 1. POST /solicitudes/ (Crear solicitud)
# -------------------------------------------------------------------
@router.post("/", response_model=SolicitudResponse, status_code=status.HTTP_201_CREATED)
def crear_solicitud(solicitud_in: SolicitudCreate, db: Session = Depends(get_db)):
    """Crea una nueva solicitud asociando el usuario creador y sus habilidades requeridas."""
																			 
    datos_solicitud = solicitud_in.model_dump(exclude={"habilidades", "sol_estado_id"})
	
    # Asignar explícitamente la llave foránea de estado
    if hasattr(solicitud_in, "sol_estado_id") and solicitud_in.sol_estado_id is not None:
        datos_solicitud["sol_estado_solicitud_id"] = solicitud_in.sol_estado_id
    elif hasattr(solicitud_in, "sol_estado_solicitud_id") and solicitud_in.sol_estado_solicitud_id is not None:
        datos_solicitud["sol_estado_solicitud_id"] = solicitud_in.sol_estado_solicitud_id

    nueva_solicitud = Solicitud(**datos_solicitud)
    
    try:
        db.add(nueva_solicitud)
        db.flush()

        if solicitud_in.habilidades:
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

    except IntegrityError as e:
        db.rollback()
        mensaje_original = str(e.orig)

        # Detectar duplicidad de código único (SOL-XXX)
        if "sol_codigo" in mensaje_original or "uq_tbl_solicitud_codigo" in mensaje_original:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una solicitud registrada con el código '{solicitud_in.sol_codigo}'."
            )
        
        # Cualquier otra restricción de llave duplicada o foránea
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en la base de datos: {mensaje_original}"
        )




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
    """Lista las solicituds permitiendo filtros opcionales y paginación."""
    query = db.query(Solicitud)

    if estado_id is not None:
        query = query.filter(Solicitud.sol_estado_solicitud_id == estado_id)
    if prioridad_id is not None:
        query = query.filter(Solicitud.sol_prioridad_id == prioridad_id)
    if cargo_id is not None:
        query = query.filter(Solicitud.sol_cargo_id == cargo_id)

    return query.offset(skip).limit(limit).all()


# -------------------------------------------------------------------
# 3. GET /solicitudes/{id} (Detalle de solicitud)
# -------------------------------------------------------------------
@router.get("/{id}", response_model=SolicitudResponse)
def obtener_solicitud_por_id(id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle completo de una solicitud por su ID."""
    solicitud = db.query(Solicitud).filter(Solicitud.sol_id == id).first()
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"solicitud con ID {id} no encontrada."
        )
    return solicitud


# -------------------------------------------------------------------
# 4. PATCH /solicitudes/{id} (Modificación de parámetros)
# -------------------------------------------------------------------
@router.patch("/{id}", response_model=SolicitudResponse)
def actualizar_solicitud(id: int, solicitud_update: SolicitudUpdate, db: Session = Depends(get_db)):
    """Permite modificar parámetros técnicos, salarios o descripciones de la solicitud."""
    solicitud = db.query(Solicitud).filter(Solicitud.sol_id == id).first()
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"solicitud con ID {id} no encontrada."
        )

    update_data = solicitud_update.model_dump(exclude_unset=True)
    
				   
    if "sol_estado_id" in update_data:
        update_data["sol_estado_solicitud_id"] = update_data.pop("sol_estado_id")

    for field, value in update_data.items():
        setattr(solicitud, field, value)

    try:
        db.commit()
        db.refresh(solicitud)
        return solicitud
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad al actualizar: {str(e.orig)}"
        )


# -------------------------------------------------------------------
# 5. PATCH /solicitudes/{id}/estado (Cambio de estado)
# -------------------------------------------------------------------
@router.patch("/{id}/estado", response_model=SolicitudResponse)
def cambiar_estado_solicitud(id: int, estado_in: SolicitudEstadoUpdate, db: Session = Depends(get_db)):
    """Actualiza el estado de flujo de la solicitud. La traza de historial la genera el listener automáticamente."""
    solicitud = db.query(Solicitud).filter(Solicitud.sol_id == id).first()
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"solicitud con ID {id} no encontrada."
        )

    nuevo_estado = getattr(estado_in, "sol_estado_solicitud_id", getattr(estado_in, "sol_estado_id", None))
    if nuevo_estado is not None and nuevo_estado != solicitud.sol_estado_solicitud_id:
				 
        solicitud.sol_estado_solicitud_id = nuevo_estado
        
        # Inyectar observación para ser consumida por el listener audit_cambio_estado_solicitud
		  
        solicitud._observacion = getattr(estado_in, "observacion", "Cambio de estado desde API")

    db.commit()
    db.refresh(solicitud)
    return solicitud


# -------------------------------------------------------------------
# 6. PATCH /solicitudes/{id}/desactivar (Borrado Lógico)
# -------------------------------------------------------------------
@router.patch("/{id}/desactivar", response_model=SolicitudResponse)
def inactivar_solicitud(id: int, db: Session = Depends(get_db)):
    """Inactiva o archiva una solicitud (borrado lógico)."""
    solicitud = db.query(Solicitud).filter(Solicitud.sol_id == id).first()
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"solicitud con ID {id} no encontrada."
        )

					   
    solicitud.sol_estado_solicitud_id = 4
    solicitud._observacion = "Desactivación (Borrado Lógico) de la solicitud"
    
    db.commit()
    db.refresh(solicitud)
    return solicitud


# -------------------------------------------------------------------
# 7. POST /solicitudes/{id}/habilidades (Agregar Habilidades)
# -------------------------------------------------------------------
@router.post("/{id}/habilidades", response_model=List[SolicitudHabilidadResponse])
def agregar_habilidades_solicitud(id: int, habilidades: List[SolicitudHabilidadCreate], db: Session = Depends(get_db)):
    """Agrega una o más habilidades requeridas a una solicitud ya existente."""
    solicitud = db.query(Solicitud).filter(Solicitud.sol_id == id).first()
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"solicitud con ID {id} no encontrada."
        )

    # Identificar IDs de habilidades previamente asociadas a la solicitud
    habilidades_existentes = {h.solhb_habilidad_id for h in solicitud.habilidades if h.solhb_habilidad_id is not None}

    nuevas_habilidades = []
    for hab in habilidades:
																
        if hab.solhb_habilidad_id in habilidades_existentes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La habilidad con ID {hab.solhb_habilidad_id} ya se encuentra agregada a la solicitud {id}."
            )

        nueva_hab = SolicitudHabilidad(
            solhb_solicitud_id=id,
            solhb_habilidad_id=hab.solhb_habilidad_id,
            solhb_nivel_habilidad_id=hab.solhb_nivel_habilidad_id,
            solhb_anios_experiencia_req=hab.solhb_anios_experiencia_req,
            solhb_es_excluyente=hab.solhb_es_excluyente
        )
        db.add(nueva_hab)
        nuevas_habilidades.append(nueva_hab)
        habilidades_existentes.add(hab.solhb_habilidad_id)

    try:
        db.commit()
        return nuevas_habilidades
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al asociar habilidades: {str(e.orig)}"
        )


# -------------------------------------------------------------------
# 8. DELETE /solicitudes/{id}/habilidades/{habilidad_id} (Remover Habilidad)
# -------------------------------------------------------------------
@router.delete("/{id}/habilidades/{habilidad_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_habilidad_solicitud(id: int, habilidad_id: int, db: Session = Depends(get_db)):
    """Remueve una habilidad requerida específica de una solicitud."""
    relacion = db.query(SolicitudHabilidad).filter(
        SolicitudHabilidad.solhb_solicitud_id == id,
        SolicitudHabilidad.solhb_habilidad_id == habilidad_id
    ).first()

    if not relacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No se encontró la habilidad {habilidad_id} vinculada a la solicitud {id}."
        )

    db.delete(relacion)
    db.commit()
    return None


# -------------------------------------------------------------------
# 9. POST /solicitudes/{id}/evaluar-candidato (Matching de Requisitos)
# -------------------------------------------------------------------
@router.post("/{id}/evaluar-candidato")
def evaluar_candidato_solicitud(id: int, habilidades_candidato: list[dict], db: Session = Depends(get_db)):
    """Evalúa si un candidato cumple con las habilidades excluyentes de la solicitud."""
    # Normalizar las llaves del JSON recibido para soportar múltiples formatos (cdhb_*, solhb_*, habilidad_id)																											   
    habilidades_normalizadas = []
    for idx, item in enumerate(habilidades_candidato):
        hab_id = (
            item.get("habilidad_id")
            or item.get("cdhb_habilidad_id")
            or item.get("solhb_habilidad_id")
            or item.get("id")
        )
        anios = (
            item.get("anios_experiencia")
            if "anios_experiencia" in item
            else item.get("cdhb_anios_experiencia", item.get("solhb_anios_experiencia_req", item.get("anios", 0)))
        )

        if hab_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El elemento en la posición {idx} debe incluir 'habilidad_id' o 'cdhb_habilidad_id'."
            )

        habilidades_normalizadas.append({
            "habilidad_id": hab_id,
            "anios_experiencia": anios
        })

    try:
        return evaluar_candidato_cumple_excluyentes(db, id, habilidades_normalizadas)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de JSON inválido. Falta el campo requerido: {str(e)}"
        )


# -------------------------------------------------------------------
# 10. GET /solicitudes/{id}/candidatos (Listar Candidatos Postulados)
# -------------------------------------------------------------------
@router.get("/{id}/candidatos")
def listar_candidatos_solicitud(id: int, db: Session = Depends(get_db)):
    """Retorna los candidatos postulados o asignados a la solicitud."""
    solicitud = db.query(Solicitud).filter(Solicitud.sol_id == id).first()
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"solicitud con ID {id} no encontrada."
        )
    
    # Consulta directa a la tabla intermedia SolicitudCandidato
    candidatos_vinculados = db.query(SolicitudCandidato).filter(
        SolicitudCandidato.slcd_solicitud_id == id
    ).all()

    return candidatos_vinculados