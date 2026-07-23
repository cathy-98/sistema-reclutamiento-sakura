from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


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

    class Config:
        from_attributes = True


# ---------------------------------------------------------
# Schemas para Solicitud (Creación y Validación)
# ---------------------------------------------------------
class SolicitudCreate(BaseModel):
    sol_codigo: str
    sol_titulo: str
    sol_descripcion: Optional[str] = None
    sol_salario_min: Optional[int] = None
    sol_salario_max: Optional[int] = None
    sol_cliente_id: int
    sol_estado_id: int
    sol_usuario_creador_id: int
    
    # Lista de habilidades a asociar
    habilidades: List[SolicitudHabilidadCreate] = []

    @model_validator(mode='after')
    def validar_al_menos_una_habilidad_excluyente(self):
        """
        Garantiza que la vacante tenga al menos 1 habilidad obligatoria/excluyente.
        """
        if self.habilidades:
            excluyentes = [h for h in self.habilidades if h.solhb_es_excluyente]
            if not excluyentes:
                raise ValueError("La solicitud debe incluir al menos una habilidad con carácter excluyente (obligatoria).")
        return self