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

    class Config:
        from_attributes = True


# ==========================================
# ESQUEMAS DE SOLICITUD DE VACANTES (Sprint 1)
# ==========================================
class SolicitudBase(BaseModel):
    # Campos para listar todas las solicitudes
    id_solicitud: Optional[int] = None
    titulo: str = Field(..., max_length=200)
    descripcion: Optional[str] = None
    id_cargo: int
    id_prioridad: int
    cantidad_vacantes: int = Field(..., gt=0)
    id_cliente: int
    id_usuario_solicitante: int
    id_usuario_responsable: Optional[int] = None
    id_modalidad: int
    salario_minimo: Optional[Decimal] = None
    salario_maximo: Optional[Decimal] = None
    fecha_inicio_busqueda: Optional[date] = None
    fecha_cierre_busqueda: Optional[date] = None
    fecha_inicio_cliente: Optional[date] = None
    id_estado_solicitud: int
    id_area: int
    # NUEVOS CAMPOS: Formatos de tiempo (ej. "09:00:00" o "18:00:00")
    hora_inicio_jornada: Optional[time] = None
    hora_fin_jornada: Optional[time] = None

class SolicitudCreate(SolicitudBase):
    # Permite recibir la lista de habilidades requeridas en el mismo formulario
    habilidades: List[SolicitudHabilidadCreate] = []

class SolicitudResponse(SolicitudBase):
    id_solicitud: int
    fecha_creacion: datetime
    habilidades: List[SolicitudHabilidadResponse] = []

    class Config:
        from_attributes = True