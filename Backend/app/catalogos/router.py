from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Importamos la dependencia de la base de datos (ajusta la ruta según tu proyecto si es necesario)
from app.database import get_db

# Importaciones del módulo local
from app.catalogos import models, schemas

router = APIRouter(
    prefix="/catalogos",
    tags=["Catálogos Globales"]
)

# ==========================================================
# 🌍 ENDPOINTS GEOGRÁFICOS
# ==========================================================

@router.get("/paises", response_model=List[schemas.PaisResponse])
def listar_paises(db: Session = Depends(get_db)):
    return db.query(models.Pais).all()

@router.get("/regiones", response_model=List[schemas.RegionResponse])
def listar_regiones(pais_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Region)
    if pais_id:
        query = query.filter(models.Region.reg_pais_id == pais_id)
    return query.all()

@router.get("/ciudades", response_model=List[schemas.CiudadResponse])
def listar_ciudades(region_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Ciudad)
    if region_id:
        query = query.filter(models.Ciudad.ciu_region_id == region_id)
    return query.all()

@router.get("/comunas", response_model=List[schemas.ComunaResponse])
def listar_comunas(ciudad_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Comuna)
    if ciudad_id:
        query = query.filter(models.Comuna.com_ciudad_id == ciudad_id)
    return query.all()


# ==========================================================
# ⚙️ ENDPOINTS TÉCNICOS DE RECLUTAMIENTO
# ==========================================================

@router.get("/habilidades", response_model=List[schemas.HabilidadResponse])
def listar_habilidades(db: Session = Depends(get_db)):
    return db.query(models.Habilidad).all()

@router.get("/niveles-habilidad", response_model=List[schemas.NivelHabilidadResponse])
def listar_niveles_habilidad(db: Session = Depends(get_db)):
    return db.query(models.NivelHabilidad).all()

@router.get("/cargos", response_model=List[schemas.CargoResponse])
def listar_cargos(db: Session = Depends(get_db)):
    return db.query(models.Cargo).all()

@router.get("/modalidades", response_model=List[schemas.ModalidadResponse])
def listar_modalidades(db: Session = Depends(get_db)):
    return db.query(models.Modalidad).all()

@router.get("/tipos-contrato", response_model=List[schemas.TipoContratoResponse])
def listar_tipos_contrato(db: Session = Depends(get_db)):
    return db.query(models.TipoContrato).all()

@router.get("/disponibilidades", response_model=List[schemas.DisponibilidadResponse])
def listar_disponibilidades(db: Session = Depends(get_db)):
    return db.query(models.Disponibilidad).all()

@router.get("/estados-solicitud", response_model=List[schemas.EstadoSolicitudResponse])
def listar_estados_solicitud(db: Session = Depends(get_db)):
    return db.query(models.EstadoSolicitud).all()

@router.get("/prioridades-solicitud", response_model=List[schemas.PrioridadSolicitudResponse])
def listar_prioridades_solicitud(db: Session = Depends(get_db)):
    return db.query(models.PrioridadSolicitud).all()

# ==========================================================
# MÉTODOS DE ESCRITURA (POST, PUT, DELETE) - HABILIDADES
# ==========================================================

@router.post("/habilidades", response_model=schemas.HabilidadResponse, status_code=201)
def crear_habilidad(payload: schemas.HabilidadCreate, db: Session = Depends(get_db)):
    # Validar si ya existe una con el mismo nombre para evitar duplicados
    existe = db.query(models.Habilidad).filter(models.Habilidad.hab_nombre == payload.hab_nombre).first()
    if existe:
        raise HTTPException(status_code=400, detail="Esta habilidad ya se encuentra registrada")
        
    nueva_hab = models.Habilidad(**payload.model_dump())
    db.add(nueva_hab)
    db.commit()
    db.refresh(nueva_hab)
    return nueva_hab

@router.put("/habilidades/{hab_id}", response_model=schemas.HabilidadResponse)
def actualizar_habilidad(hab_id: int, payload: schemas.HabilidadCreate, db: Session = Depends(get_db)):
    db_hab = db.query(models.Habilidad).filter(models.Habilidad.hab_id == hab_id).first()
    if not db_hab:
        raise HTTPException(status_code=404, detail="Habilidad no encontrada")
        
    db_hab.hab_nombre = payload.hab_nombre
    db_hab.hab_descripcion = payload.hab_descripcion
    db.commit()
    db.refresh(db_hab)
    return db_hab

@router.delete("/habilidades/{hab_id}", status_code=204)
def eliminar_habilidad(hab_id: int, db: Session = Depends(get_db)):
    db_hab = db.query(models.Habilidad).filter(models.Habilidad.hab_id == hab_id).first()
    if not db_hab:
        raise HTTPException(status_code=404, detail="Habilidad no encontrada")
        
    db.delete(db_hab)
    db.commit()
    return None


# ==========================================================
# MÉTODOS DE ESCRITURA (POST, PUT, DELETE) - CARGOS
# ==========================================================

@router.post("/cargos", response_model=schemas.CargoResponse, status_code=201)
def crear_cargo(payload: schemas.CargoCreate, db: Session = Depends(get_db)):
    existe = db.query(models.Cargo).filter(models.Cargo.crgo_nombre == payload.crgo_nombre).first()
    if existe:
        raise HTTPException(status_code=400, detail="Este cargo ya se encuentra registrado")
        
    nuevo_cargo = models.Cargo(**payload.model_dump())
    db.add(nuevo_cargo)
    db.commit()
    db.refresh(nuevo_cargo)
    return nuevo_cargo

@router.put("/cargos/{crgo_id}", response_model=schemas.CargoResponse)
def actualizar_cargo(crgo_id: int, payload: schemas.CargoCreate, db: Session = Depends(get_db)):
    db_cargo = db.query(models.Cargo).filter(models.Cargo.crgo_id == crgo_id).first()
    if not db_cargo:
        raise HTTPException(status_code=404, detail="Cargo no encontrado")
        
    db_cargo.crgo_nombre = payload.crgo_nombre
    db_cargo.crgo_descripcion = payload.crgo_descripcion
    db.commit()
    db.refresh(db_cargo)
    return db_cargo

@router.delete("/cargos/{crgo_id}", status_code=204)
def eliminar_cargo(crgo_id: int, db: Session = Depends(get_db)):
    db_cargo = db.query(models.Cargo).filter(models.Cargo.crgo_id == crgo_id).first()
    if not db_cargo:
        raise HTTPException(status_code=404, detail="Cargo no encontrado")
        
    db.delete(db_cargo)
    db.commit()
    return None