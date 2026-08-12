from __future__ import annotations

from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SolicitudHabilidadBase(StrictSchema):
    solhb_habilidad_id: int = Field(..., gt=0)
    solhb_nivel_habilidad_id: int | None = Field(default=None, gt=0)
    solhb_anios_experiencia_req: int = Field(default=0, ge=0)
    solhb_es_excluyente: bool = Field(default=False)


class SolicitudHabilidadCreate(SolicitudHabilidadBase):
    pass


class SolicitudHabilidadUpdate(StrictSchema):
    solhb_nivel_habilidad_id: int | None = Field(default=None, gt=0)
    solhb_anios_experiencia_req: int | None = Field(default=None, ge=0)
    solhb_es_excluyente: bool | None = None


class SolicitudHabilidadResponse(SolicitudHabilidadBase):
    solhb_id: int
    solhb_solicitud_id: int

    model_config = ConfigDict(from_attributes=True)


class SolicitudBase(StrictSchema):
    sol_titulo: str = Field(..., min_length=1, max_length=300)
    sol_descripcion: str | None = Field(default=None, min_length=1, max_length=300)
    sol_observacion: str | None = Field(default=None, min_length=1, max_length=300)
    sol_cantidad_vacantes: int = Field(default=1, ge=1)
    sol_salario_min: int | None = Field(default=None, ge=0)
    sol_salario_max: int | None = Field(default=None, ge=0)
    sol_fecha_inicio_busqueda: datetime | None = None
    sol_fecha_cierre_busqueda: datetime | None = None
    sol_fecha_inicio_cliente: datetime | None = None
    sol_hora_inicio_jornada: time | None = None
    sol_hora_fin_jornada: time | None = None
    sol_cargo_id: int | None = Field(default=None, gt=0)
    sol_prioridad_id: int | None = Field(default=None, gt=0)
    sol_cliente_id: int = Field(..., gt=0)
    sol_usuario_asignado_id: int | None = Field(default=None, gt=0)
    sol_modalidad_id: int | None = Field(default=None, gt=0)
    sol_tipo_contrato_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validar_rangos(self):
        if self.sol_salario_min is not None and self.sol_salario_max is not None:
            if self.sol_salario_min > self.sol_salario_max:
                raise ValueError("sol_salario_min no puede ser mayor que sol_salario_max")
        if self.sol_hora_inicio_jornada and self.sol_hora_fin_jornada:
            if self.sol_hora_inicio_jornada >= self.sol_hora_fin_jornada:
                raise ValueError("La hora de inicio de jornada debe ser anterior a la hora de fin")
        if self.sol_fecha_inicio_busqueda and self.sol_fecha_cierre_busqueda:
            if self.sol_fecha_cierre_busqueda < self.sol_fecha_inicio_busqueda:
                raise ValueError("La fecha de cierre de búsqueda no puede ser anterior a la fecha de inicio")
        return self


class SolicitudCreate(SolicitudBase):
    habilidades: list[SolicitudHabilidadCreate] = Field(default_factory=list, min_length=1)

    @model_validator(mode="after")
    def validar_habilidades(self):
        ids = [h.solhb_habilidad_id for h in self.habilidades]
        if len(ids) != len(set(ids)):
            raise ValueError("No se puede repetir una habilidad dentro de la solicitud")
        if not any(h.solhb_es_excluyente for h in self.habilidades):
            raise ValueError("Toda solicitud debe incluir al menos una habilidad excluyente")
        return self


class SolicitudReplace(SolicitudBase):
    pass


class SolicitudUpdate(StrictSchema):
    sol_titulo: str | None = Field(default=None, min_length=1, max_length=300)
    sol_descripcion: str | None = Field(default=None, min_length=1, max_length=300)
    sol_observacion: str | None = Field(default=None, min_length=1, max_length=300)
    sol_cantidad_vacantes: int | None = Field(default=None, ge=1)
    sol_salario_min: int | None = Field(default=None, ge=0)
    sol_salario_max: int | None = Field(default=None, ge=0)
    sol_fecha_inicio_busqueda: datetime | None = None
    sol_fecha_cierre_busqueda: datetime | None = None
    sol_fecha_inicio_cliente: datetime | None = None
    sol_hora_inicio_jornada: time | None = None
    sol_hora_fin_jornada: time | None = None
    sol_cargo_id: int | None = Field(default=None, gt=0)
    sol_prioridad_id: int | None = Field(default=None, gt=0)
    sol_cliente_id: int | None = Field(default=None, gt=0)
    sol_usuario_asignado_id: int | None = Field(default=None, gt=0)
    sol_modalidad_id: int | None = Field(default=None, gt=0)
    sol_tipo_contrato_id: int | None = Field(default=None, gt=0)


class SolicitudEstadoUpdate(StrictSchema):
    sol_estado_solicitud_id: int = Field(..., gt=0)
    observacion: str | None = Field(default=None, min_length=1, max_length=300)


class SolicitudResponse(BaseModel):
    sol_id: int
    sol_codigo: str | None = None
    sol_titulo: str | None = None
    sol_descripcion: str | None = None
    sol_observacion: str | None = None
    sol_cantidad_vacantes: int | None = None
    sol_salario_min: int | None = None
    sol_salario_max: int | None = None
    sol_fecha_creacion: datetime | None = None
    sol_fecha_inicio_busqueda: datetime | None = None
    sol_fecha_cierre_busqueda: datetime | None = None
    sol_fecha_inicio_cliente: datetime | None = None
    sol_hora_inicio_jornada: time | None = None
    sol_hora_fin_jornada: time | None = None
    sol_cargo_id: int | None = None
    sol_prioridad_id: int | None = None
    sol_cliente_id: int | None = None
    sol_usuario_creador_id: int | None = None
    sol_usuario_asignado_id: int | None = None
    sol_modalidad_id: int | None = None
    sol_estado_solicitud_id: int | None = None
    sol_tipo_contrato_id: int | None = None
    habilidades: list[SolicitudHabilidadResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class HistorialSolicitudResponse(BaseModel):
    hsol_id: int
    hsol_solicitud_id: int | None = None
    hsol_estado_anterior_id: int | None = None
    hsol_estado_actual_id: int | None = None
    hsol_fecha_cambio: datetime | None = None
    hsol_usuario_id: int | None = None
    hsol_comentario: str | None = None

    model_config = ConfigDict(from_attributes=True)


class HabilidadCandidatoInput(StrictSchema):
    habilidad_id: int = Field(..., gt=0)
    anios_experiencia: int = Field(default=0, ge=0)
