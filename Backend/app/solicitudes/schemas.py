from datetime import datetime, time
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator


# ---------------------------------------------------------
# Schemas para SolicitudHabilidad
# ---------------------------------------------------------
class SolicitudHabilidadBase(BaseModel):
    solhb_habilidad_id: int
    solhb_nivel_habilidad_id: Optional[int] = None
    solhb_anios_experiencia_req: int = Field(default=0, ge=0)
    solhb_es_excluyente: bool = Field(
        default=False, 
        description="Flag que define si la habilidad es obligatoria (True) u opcional (False)"
    )

class SolicitudHabilidadCreate(SolicitudHabilidadBase):
    pass

class SolicitudHabilidadResponse(SolicitudHabilidadBase):
    solhb_id: int
    solhb_solicitud_id: int

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------
# Schemas para Solicitud (Creación y Validación, Edición y Lectura)
# ---------------------------------------------------------

class SolicitudCreate(BaseModel):
    sol_codigo: str = Field(..., max_length=8, description="Código con formato SOL-XXX")
    sol_titulo: str = Field(..., max_length=300)
    sol_descripcion: Optional[str] = Field(None, max_length=300)
    sol_observacion: Optional[str] = Field(None, max_length=300)
    sol_cantidad_vacantes: Optional[int] = Field(1, ge=1)
    
    sol_salario_min: Optional[int] = None
    sol_salario_max: Optional[int] = None

    # Fechas y Horarios Opcionales
    sol_fecha_creacion: Optional[datetime] = None
    sol_fecha_inicio_busqueda: Optional[datetime] = None
    sol_fecha_cierre_busqueda: Optional[datetime] = None
    sol_fecha_inicio_cliente: Optional[datetime] = None
    sol_hora_inicio_jornada: Optional[time] = None
    sol_hora_fin_jornada: Optional[time] = None

    # Foreign Keys
    sol_cargo_id: Optional[int] = None
    sol_prioridad_id: Optional[int] = None
    sol_cliente_id: int
    sol_usuario_creador_id: int
    sol_usuario_asignado_id: Optional[int] = None
    sol_modalidad_id: Optional[int] = None
    sol_estado_solicitud_id: Optional[int] = Field(None, description="ID del estado")
    sol_estado_id: Optional[int] = Field(None, description="Alias alternativo para sol_estado_solicitud_id")
    sol_tipo_contrato_id: Optional[int] = None

    # Habilidades anidadas
    habilidades: List[SolicitudHabilidadCreate] = []

    @model_validator(mode='after')
    def normalizar_y_validar(self):
        # Mapear sol_estado_id hacia sol_estado_solicitud_id si se provee
        if self.sol_estado_solicitud_id is None and self.sol_estado_id is not None:
            self.sol_estado_solicitud_id = self.sol_estado_id
        
        # Validar al menos una habilidad excluyente
        if self.habilidades:
            excluyentes = [h for h in self.habilidades if h.solhb_es_excluyente]
            if not excluyentes:
                raise ValueError("La solicitud debe incluir al menos una habilidad obligatoria/excluyente.")
        return self



class SolicitudUpdate(BaseModel):
    sol_codigo: Optional[str] = Field(None, max_length=8)
    sol_titulo: Optional[str] = Field(None, max_length=300)
    sol_descripcion: Optional[str] = Field(None, max_length=300)
    sol_observacion: Optional[str] = Field(None, max_length=300)
    sol_cantidad_vacantes: Optional[int] = Field(None, ge=1)
    sol_salario_min: Optional[int] = None
    sol_salario_max: Optional[int] = None
    
    sol_fecha_inicio_busqueda: Optional[datetime] = None
    sol_fecha_cierre_busqueda: Optional[datetime] = None
    sol_fecha_inicio_cliente: Optional[datetime] = None
    sol_hora_inicio_jornada: Optional[time] = None
    sol_hora_fin_jornada: Optional[time] = None

    sol_cargo_id: Optional[int] = None
    sol_prioridad_id: Optional[int] = None
    sol_cliente_id: Optional[int] = None
    sol_usuario_asignado_id: Optional[int] = None
    sol_modalidad_id: Optional[int] = None
    sol_estado_solicitud_id: Optional[int] = None
    sol_tipo_contrato_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class SolicitudEstadoUpdate(BaseModel):
    sol_estado_solicitud_id: int = Field(..., description="Nuevo ID de estado para la solicitud")

class SolicitudEstadoUpdate(BaseModel):
    sol_estado_solicitud_id: Optional[int] = Field(None, description="Nuevo ID de estado para la solicitud")
    sol_estado_id: Optional[int] = Field(None, description="Alias alternativo para el ID de estado")
    observacion: Optional[str] = Field("Cambio de estado desde API", description="Comentario para la auditoría")

class SolicitudResponse(BaseModel):
    sol_id: int
    sol_codigo: Optional[str] = None
    sol_titulo: Optional[str] = None
    sol_descripcion: Optional[str] = None
    sol_observacion: Optional[str] = None
    sol_cantidad_vacantes: Optional[int] = None
    sol_salario_min: Optional[int] = None
    sol_salario_max: Optional[int] = None
    
    sol_fecha_creacion: Optional[datetime] = None
    sol_fecha_inicio_busqueda: Optional[datetime] = None
    sol_fecha_cierre_busqueda: Optional[datetime] = None
    sol_fecha_inicio_cliente: Optional[datetime] = None
    sol_hora_inicio_jornada: Optional[time] = None
    sol_hora_fin_jornada: Optional[time] = None

    sol_cargo_id: Optional[int] = None
    sol_prioridad_id: Optional[int] = None
    sol_cliente_id: Optional[int] = None
    sol_usuario_creador_id: Optional[int] = None
    sol_usuario_asignado_id: Optional[int] = None
    sol_modalidad_id: Optional[int] = None
    sol_estado_solicitud_id: Optional[int] = None
    sol_tipo_contrato_id: Optional[int] = None

    habilidades: List[SolicitudHabilidadResponse] = []

    model_config = ConfigDict(from_attributes=True)