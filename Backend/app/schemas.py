from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date, datetime, time
from decimal import Decimal


# ==========================================
# ESQUEMAS DE AUTENTICACIÓN (Sprint 0)
# ==========================================
# Esquema para recibir los datos de inicio de sesión 
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Esquema para responderle al frontend con el Token JWT
# Se cambia la clave 'nombre' por 'usuario' para ir en perfecta sintonía con la base de datos
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: str  # Adaptado de 'nombre' a 'usuario'
    rol: str

# ==========================================
# ESQUEMAS DE CATÁLOGOS MAESTROS (Salida)(Sprint 1)
# ==========================================
class ClienteResponse(BaseModel):
    id_cliente: int
    nombre_cliente: str

    class Config:
        from_attributes = True


class EstadoSolicitudResponse(BaseModel):
    id_estado_solicitud: int
    nombre_estado_solicitud: str

    class Config:
        from_attributes = True


class PrioridadResponse(BaseModel):
    id_prioridad: int
    nombre_prioridad: str

    class Config:
        from_attributes = True


class CargoResponse(BaseModel):
    id_cargo: int
    nombre_cargo: str

    class Config:
        from_attributes = True


class ModalidadResponse(BaseModel):
    id_modalidad: int
    nombre_modalidad: str

    class Config:
        from_attributes = True


class AreaResponse(BaseModel):
    id_area: int
    nombre_area: str

    class Config:
        from_attributes = True


class HabilidadResponse(BaseModel):
    id_habilidad: int
    nombre_habilidad: str

    class Config:
        from_attributes = True


class NivelHabilidadResponse(BaseModel):
    id_nivel_habilidad: int
    nombre_nivel_habilidad: str

    class Config:
        from_attributes = True


class UsuarioSimpleResponse(BaseModel):
    id: int
    usuario: str
    email: EmailStr
    rol: str

    class Config:
        from_attributes = True


# ==========================================
# ESQUEMAS DE DETALLE: SOLICITUD HABILIDAD (Sprint 1)
# ==========================================
class SolicitudHabilidadBase(BaseModel):
    id_habilidad: int
    id_nivel_habilidad: int
    anios_experiencia: int = Field(default=0, ge=0)

class SolicitudHabilidadCreate(SolicitudHabilidadBase):
    pass

class SolicitudHabilidadResponse(SolicitudHabilidadBase):
    id_solicitud_habilidad: int
    id_solicitud: int
    
    habilidad: Optional[HabilidadResponse] = None
    nivel: Optional[NivelHabilidadResponse] = None

    class Config:
        from_attributes = True



# ==========================================
# ESQUEMAS DE SOLICITUD DE VACANTES
# ==========================================
class SolicitudBase(BaseModel):
    titulo: str = Field(..., max_length=200)
    descripcion: Optional[str] = None
    cantidad_vacantes: int = Field(..., gt=0)
    salario_minimo: Optional[Decimal] = None
    salario_maximo: Optional[Decimal] = None
    fecha_inicio_busqueda: Optional[date] = None
    fecha_cierre_busqueda: Optional[date] = None
    fecha_inicio_cliente: Optional[date] = None
    hora_inicio_jornada: Optional[time] = None
    hora_fin_jornada: Optional[time] = None

class SolicitudCreate(SolicitudBase):
    id_cargo: int
    id_prioridad: int
    id_cliente: int
    id_usuario_solicitante: int
    id_usuario_responsable: Optional[int] = None
    id_modalidad: int
    id_estado_solicitud: int
    id_area: int
    habilidades: List[SolicitudHabilidadCreate] = []

class SolicitudResponse(SolicitudBase):
    id_solicitud: int
    fecha_creacion: datetime
    
    id_cargo: int
    id_prioridad: int
    id_cliente: int
    id_usuario_solicitante: int
    id_usuario_responsable: Optional[int] = None
    id_modalidad: int
    id_estado_solicitud: int
    id_area: int

    cargo: Optional[CargoResponse] = None
    prioridad: Optional[PrioridadResponse] = None
    cliente: Optional[ClienteResponse] = None
    solicitante: Optional[UsuarioSimpleResponse] = None
    responsable: Optional[UsuarioSimpleResponse] = None
    modalidad: Optional[ModalidadResponse] = None
    estado: Optional[EstadoSolicitudResponse] = None
    area: Optional[AreaResponse] = None
    habilidades: List[SolicitudHabilidadResponse] = []

    class Config:
        from_attributes = True


# ==========================================
# NUEVO: ESQUEMAS PARA GESTIÓN DE CANDIDATOS (Sprint 1)
# ==========================================
class CandidatoBase(BaseModel):
    nombres: str = Field(..., max_length=100)
    apellido_paterno: str = Field(..., max_length=100)
    apellido_materno: Optional[str] = Field(None, max_length=100)
    correo_electronico: EmailStr
    telefono_contacto: Optional[str] = Field(None, max_length=30)
    rut_candidato: Optional[str] = Field(None, max_length=20)
    fecha_nacimiento: Optional[date] = None
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    pretension_renta: Optional[Decimal] = None
    disponibilidad: Optional[str] = Field(None, max_length=100)
    resumen_profesional: Optional[str] = None

class CandidatoCreate(CandidatoBase):
    pass

class CandidatoResponse(CandidatoBase):
    id_candidato: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ==========================================
# NUEVO: ESQUEMAS PARA LA POSTULACIÓN (MATCH)
# ==========================================
class SolicitudCandidatoResponse(BaseModel):
    id_solicitud_candidato: int
    id_solicitud: int
    id_candidato: int
    match_score: Optional[Decimal] = None
    color_semaforo: Optional[str] = None
    estado_postulacion: str
    fecha_postulacion: datetime
    
    # Trae la información del candidato enlazado
    candidato: Optional[CandidatoResponse] = None

    class Config:
        from_attributes = True