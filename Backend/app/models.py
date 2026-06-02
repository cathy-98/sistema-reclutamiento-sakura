from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, ForeignKey, Boolean, CheckConstraint, UniqueConstraint, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# ==========================================
# TABLA DE USUARIOS (Sincronizada con el Sprint 0)
# ==========================================
# Adaptado exactamente a la estructura de la tabla 'public.usuarios'
# que nos entregó el equipo de Base de Datos.

class Usuario(Base):
    __tablename__ = "usuarios"

    # Llave primaria autoincremental
    id = Column(Integer, primary_key=True, index=True)
    
    # Campo 'usuario' (reemplaza al anterior 'nombre' para el login/identificación)
    usuario = Column(String(50), nullable=False)
    
    # Campo 'contrasena' (anteriormente password_hash, mapea directamente la columna de la BD)
    contrasena = Column(String(255), nullable=False)
    
    # Email único e indexado para las búsquedas del login
    email = Column(String(100), unique=True, index=True, nullable=False)
    
    # Rol asignado para el control de accesos (ADMIN, RECLUTADOR)
    rol = Column(String(30), nullable=False)

    # Relaciones inversas virtuales para solicitudes solicitadas o bajo responsabilidad
    solicitudes_solicitadas = relationship(
        "Solicitud", 
        foreign_keys="[Solicitud.id_usuario_solicitante]", 
        back_populates="solicitante"
    )
    solicitudes_responsables = relationship(
        "Solicitud", 
        foreign_keys="[Solicitud.id_usuario_responsable]", 
        back_populates="responsable"
    )

# ==========================================
# 1. TABLAS DE CATÁLOGOS / MAESTRAS
# ==========================================

class Cliente(Base):
    __tablename__ = "tbl_cliente"

    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    nombre_cliente = Column(String(150), nullable=False)

    # Relación inversa: Un cliente puede tener muchas solicitudes asociadas
    solicitudes = relationship("Solicitud", back_populates="cliente")


class EstadoSolicitud(Base):
    __tablename__ = "tbl_estado_solicitud"

    id_estado_solicitud = Column(Integer, primary_key=True, autoincrement=True)
    nombre_estado_solicitud = Column(String(50), nullable=False, unique=True)

    solicitudes = relationship("Solicitud", back_populates="estado")


class Prioridad(Base):
    __tablename__ = "tbl_prioridad"

    id_prioridad = Column(Integer, primary_key=True, autoincrement=True)
    nombre_prioridad = Column(String(30), nullable=False, unique=True)

    solicitudes = relationship("Solicitud", back_populates="prioridad")


class Cargo(Base):
    __tablename__ = "tbl_cargo"

    id_cargo = Column(Integer, primary_key=True, autoincrement=True)
    nombre_cargo = Column(String(100), nullable=False, unique=True)

    solicitudes = relationship("Solicitud", back_populates="cargo")


class Modalidad(Base):
    __tablename__ = "tbl_modalidad"

    id_modalidad = Column(Integer, primary_key=True, autoincrement=True)
    nombre_modalidad = Column(String(50), nullable=False, unique=True)

    solicitudes = relationship("Solicitud", back_populates="modalidad")


class Area(Base):
    __tablename__ = "tbl_area"

    id_area = Column(Integer, primary_key=True, autoincrement=True)
    nombre_area = Column(String(100), nullable=False, unique=True)

    solicitudes = relationship("Solicitud", back_populates="area")


class Habilidad(Base):
    __tablename__ = "tbl_habilidad"

    id_habilidad = Column(Integer, primary_key=True, autoincrement=True)
    nombre_habilidad = Column(String(100), nullable=False, unique=True)

    solicitud_habilidades = relationship("SolicitudHabilidad", back_populates="habilidad")


class NivelHabilidad(Base):
    __tablename__ = "tbl_nivel_habilidad"

    id_nivel_habilidad = Column(Integer, primary_key=True, autoincrement=True)
    nombre_nivel_habilidad = Column(String(50), nullable=False, unique=True)

    solicitud_habilidades = relationship("SolicitudHabilidad", back_populates="nivel")

# ==========================================
# 3. TABLA PRINCIPAL DE SOLICITUDES
# ==========================================
class Solicitud(Base):
    __tablename__ = "tbl_solicitud"

    id_solicitud = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    cantidad_vacantes = Column(Integer, nullable=False)
    salario_minimo = Column(Numeric(12, 2), nullable=True)
    salario_maximo = Column(Numeric(12, 2), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_inicio_busqueda = Column(Date, nullable=True)
    fecha_cierre_busqueda = Column(Date, nullable=True)
    fecha_inicio_cliente = Column(Date, nullable=True)
    # NUEVOS CAMPOS: Columnas de hora de inicio y fin de jornada laboral
    hora_inicio_jornada = Column(Time, nullable=True)
    hora_fin_jornada = Column(Time, nullable=True)

    # Claves Foráneas de Catálogos y Relacionales
    id_cargo = Column(Integer, ForeignKey("tbl_cargo.id_cargo"), nullable=False)
    id_prioridad = Column(Integer, ForeignKey("tbl_prioridad.id_prioridad"), nullable=False)
    id_cliente = Column(Integer, ForeignKey("tbl_cliente.id_cliente"), nullable=False)
    id_usuario_solicitante = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    id_usuario_responsable = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    id_modalidad = Column(Integer, ForeignKey("tbl_modalidad.id_modalidad"), nullable=False)
    id_estado_solicitud = Column(Integer, ForeignKey("tbl_estado_solicitud.id_estado_solicitud"), nullable=False)
    id_area = Column(Integer, ForeignKey("tbl_area.id_area"), nullable=False)

    # Restricciones de integridad a nivel físico (Database constraints)
    __table_args__ = (
        CheckConstraint("cantidad_vacantes > 0", name="chk_cantidad_vacantes"),
        CheckConstraint(
            "salario_minimo IS NULL OR salario_maximo IS NULL OR salario_minimo <= salario_maximo",
            name="chk_salarios"
        ),
        # NUEVO CONSTRAINT: Valida que la hora de inicio sea anterior a la de fin si ambas están definidas
        CheckConstraint(
            "hora_inicio_jornada IS NULL OR hora_fin_jornada IS NULL OR hora_inicio_jornada < hora_fin_jornada",
            name="chk_horario_jornada"
        ),
    )

    # Relaciones de navegación ORM
    cargo = relationship("Cargo", back_populates="solicitudes")
    prioridad = relationship("Prioridad", back_populates="solicitudes")
    cliente = relationship("Cliente", back_populates="solicitudes")
    solicitante = relationship("Usuario", foreign_keys=[id_usuario_solicitante], back_populates="solicitudes_solicitadas")
    responsable = relationship("Usuario", foreign_keys=[id_usuario_responsable], back_populates="solicitudes_responsables")
    modalidad = relationship("Modalidad", back_populates="solicitudes")
    estado = relationship("EstadoSolicitud", back_populates="solicitudes")
    area = relationship("Area", back_populates="solicitudes")

    # Relación uno a muchos con la tabla intermedia de habilidades requeridas (borrado en cascada)
    habilidades = relationship(
        "SolicitudHabilidad",
        back_populates="solicitud",
        cascade="all, delete-orphan"
    )


# ==========================================
# 4. TABLA INTERMEDIA: SOLICITUD HABILIDADES
# ==========================================
class SolicitudHabilidad(Base):
    __tablename__ = "tbl_solicitud_habilidad"

    id_solicitud_habilidad = Column(Integer, primary_key=True, autoincrement=True)
    id_solicitud = Column(Integer, ForeignKey("tbl_solicitud.id_solicitud", ondelete="CASCADE"), nullable=False)
    id_habilidad = Column(Integer, ForeignKey("tbl_habilidad.id_habilidad"), nullable=False)
    id_nivel_habilidad = Column(Integer, ForeignKey("tbl_nivel_habilidad.id_nivel_habilidad"), nullable=False)
    anios_experiencia = Column(Integer, nullable=False, default=0)

    # Clave compuesta única para evitar asociar la misma tecnología dos veces a una sola vacante
    __table_args__ = (
        UniqueConstraint("id_solicitud", "id_habilidad", name="uq_solicitud_habilidad"),
    )

    # Relaciones de navegación de retorno
    solicitud = relationship("Solicitud", back_populates="habilidades")
    habilidad = relationship("Habilidad", back_populates="solicitud_habilidades")
    nivel = relationship("NivelHabilidad", back_populates="solicitud_habilidades")