from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text

# Importaciones locales
from app.database import obtener_db
from app.models import (
    Usuario, Solicitud, SolicitudHabilidad, Candidato, SolicitudCandidato, 
    Cliente, EstadoSolicitud, Prioridad, Cargo, Modalidad, Area, Habilidad, NivelHabilidad
)
from app.schemas import (
    LoginRequest, TokenResponse, 
    SolicitudCreate, SolicitudResponse,
    ClienteResponse, EstadoSolicitudResponse, PrioridadResponse,
    CargoResponse, ModalidadResponse, AreaResponse, HabilidadResponse, NivelHabilidadResponse,
    CandidatoCreate, CandidatoResponse, SolicitudCandidatoResponse
)
from app.security import verificar_password, crear_token_acceso

app = FastAPI(
    title="Sakura Platform - Core API",
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
# MÓDULO DE CATÁLOGOS MAESTROS
# ==========================================

@app.get("/api/catalogos/clientes", response_model=List[ClienteResponse], tags=["Catálogos"])
def listar_clientes(db: Session = Depends(obtener_db)):
    return db.query(Cliente).all()

@app.get("/api/catalogos/estados-solicitud", response_model=List[EstadoSolicitudResponse], tags=["Catálogos"])
def listar_estados_solicitud(db: Session = Depends(obtener_db)):
    return db.query(EstadoSolicitud).all()

@app.get("/api/catalogos/prioridades", response_model=List[PrioridadResponse], tags=["Catálogos"])
def listar_prioridades(db: Session = Depends(obtener_db)):
    return db.query(Prioridad).all()

@app.get("/api/catalogos/cargos", response_model=List[CargoResponse], tags=["Catálogos"])
def listar_cargos(db: Session = Depends(obtener_db)):
    return db.query(Cargo).all()

@app.get("/api/catalogos/modalidades", response_model=List[ModalidadResponse], tags=["Catálogos"])
def listar_modalidades(db: Session = Depends(obtener_db)):
    return db.query(Modalidad).all()

@app.get("/api/catalogos/areas", response_model=List[AreaResponse], tags=["Catálogos"])
def listar_areas(db: Session = Depends(obtener_db)):
    return db.query(Area).all()

@app.get("/api/catalogos/habilidades", response_model=List[HabilidadResponse], tags=["Catálogos"])
def listar_habilidades(db: Session = Depends(obtener_db)):
    return db.query(Habilidad).all()

@app.get("/api/catalogos/niveles-habilidad", response_model=List[NivelHabilidadResponse], tags=["Catálogos"])
def listar_niveles_habilidad(db: Session = Depends(obtener_db)):
    return db.query(NivelHabilidad).all()

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

    # 2. NUEVA VALIDACIÓN: Validar coherencia de horario laboral
    if (solicitud_in.hora_inicio_jornada is not None and 
            solicitud_in.hora_fin_jornada is not None and 
            solicitud_in.hora_inicio_jornada >= solicitud_in.hora_fin_jornada):
        raise HTTPException(
            status_code=400,
            detail="La hora de inicio de la jornada debe ser estrictamente anterior a la hora de término."
        )

    # 3. Creación de la instancia principal de la solicitud
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
        id_area=solicitud_in.id_area,
        # Inyección de las nuevas columnas
        hora_inicio_jornada=solicitud_in.hora_inicio_jornada,
        hora_fin_jornada=solicitud_in.hora_fin_jornada
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
    Retorna el listado completo de solicitudes resolviendo todos sus catálogos
    de forma ansiosa (joinedload) en una sola llamada SQL para alta performance.
    """
    return db.query(Solicitud).options(
        joinedload(Solicitud.cargo),
        joinedload(Solicitud.prioridad),
        joinedload(Solicitud.cliente),
        joinedload(Solicitud.solicitante),
        joinedload(Solicitud.responsable),
        joinedload(Solicitud.modalidad),
        joinedload(Solicitud.estado),
        joinedload(Solicitud.area),
        joinedload(Solicitud.habilidades).joinedload(SolicitudHabilidad.habilidad),
        joinedload(Solicitud.habilidades).joinedload(SolicitudHabilidad.nivel)
    ).order_by(Solicitud.id_solicitud.desc()).all()


@app.get("/api/solicitudes/{id}", response_model=SolicitudResponse, tags=["Solicitudes"])
def obtener_solicitud(id: int, db: Session = Depends(obtener_db)):
    """
    Busca los datos y relaciones de una única solicitud por su ID.
    """
    solicitud = db.query(Solicitud).options(
        joinedload(Solicitud.cargo),
        joinedload(Solicitud.prioridad),
        joinedload(Solicitud.cliente),
        joinedload(Solicitud.solicitante),
        joinedload(Solicitud.responsable),
        joinedload(Solicitud.modalidad),
        joinedload(Solicitud.estado),
        joinedload(Solicitud.area),
        joinedload(Solicitud.habilidades).joinedload(SolicitudHabilidad.habilidad),
        joinedload(Solicitud.habilidades).joinedload(SolicitudHabilidad.nivel)
    ).filter(Solicitud.id_solicitud == id).first()
    
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
    
    # NUEVA VALIDACIÓN: Validar coherencia de horario laboral en actualización
    if (solicitud_in.hora_inicio_jornada is not None and 
            solicitud_in.hora_fin_jornada is not None and 
            solicitud_in.hora_inicio_jornada >= solicitud_in.hora_fin_jornada):
        raise HTTPException(
            status_code=400,
            detail="La hora de inicio de la jornada debe ser estrictamente anterior a la hora de término."
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

# ==========================================
# MÓDULO DE CANDIDATOS (Sprint 1 )
# ==========================================

@app.post("/api/candidatos", response_model=CandidatoResponse, status_code=201, tags=["Candidatos"])
def crear_candidato(candidato_in: CandidatoCreate, db: Session = Depends(obtener_db)):
    """
    Registra de forma permanente la ficha de un candidato nuevo.
    """
    # Validamos que el correo electrónico no esté registrado ya en el sistema
    existente = db.query(Candidato).filter(Candidato.correo_electronico == candidato_in.correo_electronico).first()
    if existente:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un candidato registrado con el correo electrónico '{candidato_in.correo_electronico}'."
        )

    nuevo_candidato = Candidato(**candidato_in.model_dump())
    try:
        db.add(nuevo_candidato)
        db.commit()
        db.refresh(nuevo_candidato)
        return nuevo_candidato
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error de base de datos al guardar el candidato: {str(e)}"
        )


@app.get("/api/candidatos", response_model=List[CandidatoResponse], tags=["Candidatos"])
def listar_candidatos(db: Session = Depends(obtener_db)):
    """
    Retorna el listado completo de candidatos registrados en el sistema.
    """
    return db.query(Candidato).order_by(Candidato.id_candidato.desc()).all()


@app.get("/api/candidatos/{id}", response_model=CandidatoResponse, tags=["Candidatos"])
def obtener_candidato(id: int, db: Session = Depends(obtener_db)):
    """
    Recupera la ficha de datos de un candidato por su ID.
    """
    candidato = db.query(Candidato).filter(Candidato.id_candidato == id).first()
    if not candidato:
        raise HTTPException(
            status_code=404,
            detail="El candidato solicitado no existe en el sistema."
        )
    return candidato


@app.put("/api/candidatos/{id}", response_model=CandidatoResponse, tags=["Candidatos"])
def actualizar_candidato(id: int, candidato_in: CandidatoCreate, db: Session = Depends(obtener_db)):
    """
    Modifica las propiedades de un candidato registrado.
    """
    candidato_db = db.query(Candidato).filter(Candidato.id_candidato == id).first()
    if not candidato_db:
        raise HTTPException(
            status_code=404,
            detail="Candidato no encontrado para actualización."
        )
    
    # Validamos que al cambiar el correo, no colisione con el de otro candidato existente
    if candidato_in.correo_electronico != candidato_db.correo_electronico:
        existente = db.query(Candidato).filter(Candidato.correo_electronico == candidato_in.correo_electronico).first()
        if existente:
            raise HTTPException(
                status_code=400,
                detail="El correo electrónico ingresado ya se encuentra registrado por otro candidato."
            )

    for clave, valor in candidato_in.model_dump().items():
        setattr(candidato_db, clave, valor)

    try:
        db.commit()
        db.refresh(candidato_db)
        return candidato_db
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error transaccional al actualizar la ficha del candidato: {str(e)}"
        )


@app.delete("/api/candidatos/{id}", tags=["Candidatos"])
def eliminar_candidato(id: int, db: Session = Depends(obtener_db)):
    """
    Elimina físicamente a un candidato y limpia de forma automática todas sus postulaciones por CASCADE.
    """
    candidato_db = db.query(Candidato).filter(Candidato.id_candidato == id).first()
    if not candidato_db:
        raise HTTPException(
            status_code=404,
            detail="El candidato solicitado no existe o ya fue eliminado."
        )
    
    try:
        db.delete(candidato_db)
        db.commit()
        return {
            "status": "success",
            "detail": f"Candidato con ID {id} y su historial de postulaciones eliminados correctamente."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar candidato: {str(e)}"
        )


# ==========================================
# MÓDULO DE POSTULACIONES Y MATCHING (N:M)
# ==========================================

@app.post("/api/solicitudes/{id_solicitud}/postular/{id_candidato}", response_model=SolicitudCandidatoResponse, status_code=201, tags=["Postulaciones y Match"])
def asociar_postulacion(
    id_solicitud: int, 
    id_candidato: int, 
    match_score: float = None, 
    color_semaforo: str = "Gris", 
    estado_postulacion: str = "Nuevo",
    db: Session = Depends(obtener_db)
):
    """
    Crea el vínculo de postulación entre un candidato y una solicitud (vacante).
    Permite inyectar de forma directa el match score y el color semáforo (calculados por n8n e IA).
    """
    # 1. Validar existencia previa de ambos extremos
    solicitud = db.query(Solicitud).filter(Solicitud.id_solicitud == id_solicitud).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="La solicitud no existe.")
        
    candidato = db.query(Candidato).filter(Candidato.id_candidato == id_candidato).first()
    if not candidato:
        raise HTTPException(status_code=404, detail="El candidato no existe.")

    # 2. Validar que no se postule dos veces a la misma vacante (Constraint UNIQUE)
    postulacion_existente = db.query(SolicitudCandidato).filter(
        SolicitudCandidato.id_solicitud == id_solicitud,
        SolicitudCandidato.id_candidato == id_candidato
    ).first()
    
    if postulacion_existente:
        raise HTTPException(
            status_code=400,
            detail="Este candidato ya se encuentra postulado y calificado en esta solicitud."
        )

    nueva_postulacion = SolicitudCandidato(
        id_solicitud=id_solicitud,
        id_candidato=id_candidato,
        match_score=match_score,
        color_semaforo=color_semaforo,
        estado_postulacion=estado_postulacion
    )
    
    try:
        db.add(nueva_postulacion)
        db.commit()
        db.refresh(nueva_postulacion)
        return nueva_postulacion
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error transaccional al asociar postulación: {str(e)}"
        )


@app.get("/api/solicitudes/{id_solicitud}/postulaciones", response_model=List[SolicitudCandidatoResponse], tags=["Postulaciones y Match"])
def obtener_postulantes_de_solicitud(id_solicitud: int, db: Session = Depends(obtener_db)):
    """
    Retorna el listado de postulantes asociados a una solicitud específica,
    ordenados estrictamente de mejor a peor por su 'match_score' de forma descendente.
    """
    # Validamos existencia de la solicitud
    solicitud = db.query(Solicitud).filter(Solicitud.id_solicitud == id_solicitud).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")

    # Buscamos las vinculaciones cargando el perfil del candidato de forma ansiosa
    return db.query(SolicitudCandidato).options(
        joinedload(SolicitudCandidato.candidato)
    ).filter(
        SolicitudCandidato.id_solicitud == id_solicitud
    ).order_by(
        SolicitudCandidato.match_score.desc()
    ).all()