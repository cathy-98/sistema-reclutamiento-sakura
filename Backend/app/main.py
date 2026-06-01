from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

# Importaciones locales adaptadas de forma precisa
from app.database import obtener_db
from app.models import Usuario, Solicitud, SolicitudHabilidad
from app.schemas import (
    LoginRequest, TokenResponse, 
    SolicitudCreate, SolicitudResponse
)
from app.security import verificar_password, crear_token_acceso

app = FastAPI(
    title="P&E Platform - Core API",
    description="Servidor de servicios backend adaptado a la base de datos física normalizada del Sprint 1",
    version="1.4.0"
)

# ==========================================
# CONFIGURACIÓN DE CORS
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# ENDPOINTS
# ==========================================
# ==========================================
# MÓDULO DE AUTENTICACIÓN (Sprint 0)
# ==========================================

# 1. Endpoint de Prueba (GET /)
@app.get("/", tags=["Pruebas"])
def verificar_conexion_db(db: Session = Depends(obtener_db)):
    """
    Realiza una consulta de prueba rápida a PostgreSQL en Docker.
    """
    try:
        db.execute(text("SELECT 1"))
        return {
            "estado": "¡Al abordaje! Backend activo y conectado a PostgreSQL",
            "puerto_db": 5432,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al conectar con la base de datos de Docker: {str(e)}"
        )


# 2. Endpoint de Login (POST /api/auth/login)
@app.post(
    "/api/auth/login", 
    response_model=TokenResponse, 
    tags=["Autenticación"]
)
def login(
    solicitud: LoginRequest, 
    db: Session = Depends(obtener_db)
):
    """
    Valida las credenciales de los usuarios comparando la contraseña hash 
    con la nueva columna 'contrasena' de PostgreSQL.
    """
    # 1. Buscamos al usuario en la base de datos por su email
    usuario = db.query(Usuario).filter(Usuario.email == solicitud.email).first()
    
    # 2. Validamos que exista y que la contraseña coincida con 'usuario.contrasena'
    if not usuario or not verificar_password(solicitud.password, usuario.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    # 3. Datos que viajarán en el Token (Se utiliza 'usuario.usuario' en vez de nombre)
    datos_token = {
        "sub": usuario.email,
        "rol": usuario.rol,
        "usuario": usuario.usuario
    }
    
    # 4. Generamos el JWT firmado
    token_jwt = crear_token_acceso(datos_token)
    
    # 5. Respondemos al frontend con el TokenResponse adaptado
    return TokenResponse(
        access_token=token_jwt,
        token_type="bearer",
        usuario=usuario.usuario,
        rol=usuario.rol
    )

# ==========================================
# MÓDULO DE SOLICITUDES (Sprint 1)
# ==========================================

@app.post("/api/solicitudes", response_model=SolicitudResponse, status_code=201, tags=["Solicitudes"])
def crear_solicitud(solicitud_in: SolicitudCreate, db: Session = Depends(obtener_db)):
    """
    Registra una nueva solicitud en tbl_solicitud y mapea de forma transaccional 
    todas sus tecnologías vinculadas dentro de la tabla intermedia tbl_solicitud_habilidad.
    """
    # 1. Validar coherencia salarial desde la lógica de negocio del Backend
    if (solicitud_in.salario_minimo is not None and 
            solicitud_in.salario_maximo is not None and 
            solicitud_in.salario_minimo > solicitud_in.salario_maximo):
        raise HTTPException(
            status_code=400,
            detail="El salario mínimo no puede ser superior al salario máximo."
        )

    # 2. Creación de la instancia principal de la solicitud
    nueva_solicitud = Solicitud(
        titulo=solicitud_in.titulo,
        descripcion=solicitud_in.descripcion,
        id_cargo=solicitud_in.id_cargo,
        id_prioridad=solicitud_in.id_prioridad,
        cantidad_vacantes=solicitud_in.cantidad_vacantes,
        id_cliente=solicitud_in.id_cliente,
        id_usuario_solicitante=solicitud_in.id_usuario_solicitante,
        id_usuario_responsable=solicitud_in.id_usuario_responsable,
        id_modalidad=solicitud_in.id_modalidad,
        salario_minimo=solicitud_in.salario_minimo,
        salario_maximo=solicitud_in.salario_maximo,
        fecha_inicio_busqueda=solicitud_in.fecha_inicio_busqueda,
        fecha_cierre_busqueda=solicitud_in.fecha_cierre_busqueda,
        fecha_inicio_cliente=solicitud_in.fecha_inicio_cliente,
        id_estado_solicitud=solicitud_in.id_estado_solicitud,
        id_area=solicitud_in.id_area
    )
    
    try:
        # Añadir cabecera de la solicitud en la base de datos
        db.add(nueva_solicitud)
        db.commit()
        db.refresh(nueva_solicitud)

        # 3. Insertar las habilidades técnicas asociadas en la tabla intermedia relacional
        for hab in solicitud_in.habilidades:
            nueva_habilidad = SolicitudHabilidad(
                id_solicitud=nueva_solicitud.id_solicitud,
                id_habilidad=hab.id_habilidad,
                id_nivel_habilidad=hab.id_nivel_habilidad,
                anios_experiencia=hab.anios_experiencia
            )
            db.add(nueva_habilidad)
        
        db.commit()
        db.refresh(nueva_solicitud)
        return nueva_solicitud
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error transaccional al registrar la solicitud: {str(e)}"
        )


@app.get("/api/solicitudes", response_model=List[SolicitudResponse], tags=["Solicitudes"])
def listar_solicitudes(db: Session = Depends(obtener_db)):
    """
    Retorna el listado completo de solicitudes guardadas en la base de datos PostgreSQL,
    ordenadas desde la más nueva (ID descendente).
    """
    return db.query(Solicitud).order_by(Solicitud.id_solicitud.desc()).all()


@app.get("/api/solicitudes/{id}", response_model=SolicitudResponse, tags=["Solicitudes"])
def obtener_solicitud(id: int, db: Session = Depends(obtener_db)):
    """
    Busca de forma exacta los datos y las relaciones de una única solicitud por su ID.
    """
    solicitud = db.query(Solicitud).filter(Solicitud.id_solicitud == id).first()
    if not solicitud:
        raise HTTPException(
            status_code=404, 
            detail="La solicitud buscada no existe en el sistema."
        )
    return solicitud


@app.put("/api/solicitudes/{id}", response_model=SolicitudResponse, tags=["Solicitudes"])
def actualizar_solicitud(id: int, solicitud_in: SolicitudCreate, db: Session = Depends(obtener_db)):
    """
    Modifica la cabecera del registro en tbl_solicitud y limpia/reemplaza 
    sus habilidades asociadas en tbl_solicitud_habilidad de forma transaccional.
    """
    solicitud_db = db.query(Solicitud).filter(Solicitud.id_solicitud == id).first()
    if not solicitud_db:
        raise HTTPException(
            status_code=404, 
            detail="Solicitud no encontrada en los registros."
        )
    
    # Validar coherencia de los montos salariales
    if (solicitud_in.salario_minimo is not None and 
            solicitud_in.salario_maximo is not None and 
            solicitud_in.salario_minimo > solicitud_in.salario_maximo):
        raise HTTPException(
            status_code=400,
            detail="El salario mínimo no puede ser superior al salario máximo."
        )

    # Actualizar campos de la cabecera, utilizando model_dump de Pydantic v2
    datos_actualizados = solicitud_in.model_dump(exclude={"habilidades"})
    for clave, valor in datos_actualizados.items():
        setattr(solicitud_db, clave, valor)

    try:
        # Borrar en cascada las habilidades anteriores asociadas a este ID de solicitud
        db.query(SolicitudHabilidad).filter(SolicitudHabilidad.id_solicitud == id).delete()
        
        # Insertar el nuevo listado de requerimientos técnicos en la tabla intermedia
        for hab in solicitud_in.habilidades:
            nueva_hab = SolicitudHabilidad(
                id_solicitud=id,
                id_habilidad=hab.id_habilidad,
                id_nivel_habilidad=hab.id_nivel_habilidad,
                anios_experiencia=hab.anios_experiencia
            )
            db.add(nueva_hab)
        
        db.commit()
        db.refresh(solicitud_db)
        return solicitud_db
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error transaccional al intentar actualizar la solicitud: {str(e)}"
        )


@app.delete("/api/solicitudes/{id}", tags=["Solicitudes"])
def eliminar_solicitud(id: int, db: Session = Depends(obtener_db)):
    """
    Elimina físicamente una vacante de la tabla tbl_solicitud.
    Las filas en tbl_solicitud_habilidad se borran de forma automática gracias al Cascade Delete.
    """
    solicitud_db = db.query(Solicitud).filter(Solicitud.id_solicitud == id).first()
    if not solicitud_db:
        raise HTTPException(
            status_code=404, 
            detail="La solicitud indicada no existe o ya fue eliminada."
        )
    
    try:
        db.delete(solicitud_db)
        db.commit()
        return {
            "status": "success", 
            "detail": f"Solicitud con ID {id} y sus habilidades asociadas han sido removidas con éxito."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error al intentar eliminar la solicitud de la Base de Datos: {str(e)}"
        )