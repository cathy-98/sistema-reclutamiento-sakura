from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PreguntaCreate(StrictModel):
    preg_texto_pregunta: str = Field(min_length=1, max_length=300)
    preg_habilidad_id: int = Field(gt=0)
    preg_nivel_habilidad_id: int = Field(gt=0)

    @field_validator("preg_texto_pregunta")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("La pregunta no puede estar vacía")
        return value


class PreguntaUpdate(StrictModel):
    preg_texto_pregunta: str | None = Field(default=None, min_length=1, max_length=300)
    preg_habilidad_id: int | None = Field(default=None, gt=0)
    preg_nivel_habilidad_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def not_empty(self):
        if not self.model_fields_set:
            raise ValueError("Debe informar al menos un campo")
        return self


class OpcionCreate(StrictModel):
    opcr_texto_opcion: str = Field(min_length=1, max_length=300)
    opcr_es_correcta: bool = False


class OpcionUpdate(StrictModel):
    opcr_texto_opcion: str | None = Field(default=None, min_length=1, max_length=300)
    opcr_es_correcta: bool | None = None

    @model_validator(mode="after")
    def not_empty(self):
        if not self.model_fields_set:
            raise ValueError("Debe informar al menos un campo")
        return self


class OpcionAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    opcr_id: int
    opcr_pregunta_id: int
    opcr_texto_opcion: str
    opcr_es_correcta: bool


class OpcionCandidateRead(BaseModel):
    opcr_id: int
    opcr_texto_opcion: str


class PreguntaAdminRead(BaseModel):
    preg_id: int
    preg_texto_pregunta: str
    preg_habilidad_id: int
    habilidad_nombre: str | None = None
    preg_nivel_habilidad_id: int
    nivel_nombre: str | None = None
    puntaje_base: int
    duracion_minutos: int
    preg_fecha_creacion: datetime
    opciones: list[OpcionAdminRead] = Field(default_factory=list)


class PreguntaCandidateRead(BaseModel):
    prcu_id: int
    preg_id: int
    preg_texto_pregunta: str
    habilidad_nombre: str | None = None
    nivel_nombre: str | None = None
    puntaje_base: int
    opciones: list[OpcionCandidateRead] = Field(default_factory=list)
    respuesta_seleccionada_id: int | None = None


class CuestionarioCreate(StrictModel):
    cues_nombre: str = Field(min_length=1, max_length=300)
    cues_descripcion: str | None = Field(default=None, max_length=300)
    cues_porcentaje_aprobacion: Decimal = Field(ge=0, le=100)
    cues_solicitud_id: int = Field(gt=0)


class CuestionarioUpdate(StrictModel):
    cues_nombre: str | None = Field(default=None, min_length=1, max_length=300)
    cues_descripcion: str | None = Field(default=None, max_length=300)
    cues_porcentaje_aprobacion: Decimal | None = Field(default=None, ge=0, le=100)
    cues_solicitud_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def not_empty(self):
        if not self.model_fields_set:
            raise ValueError("Debe informar al menos un campo")
        return self


class CuestionarioRead(BaseModel):
    cues_id: int
    cues_nombre: str
    cues_descripcion: str | None = None
    cues_porcentaje_aprobacion: Decimal
    cues_solicitud_id: int
    solicitud_codigo: str | None = None
    cantidad_preguntas: int
    puntaje_maximo: int
    duracion_minutos: int


class AsignacionCreate(StrictModel):
    candidato_id: int = Field(gt=0)
    fecha_vencimiento: datetime


class AsignacionMasivaCreate(StrictModel):
    candidato_ids: list[int] = Field(min_length=1, max_length=1000)
    fecha_vencimiento: datetime

    @field_validator("candidato_ids")
    @classmethod
    def validar_candidatos(cls, value: list[int]) -> list[int]:
        if any(candidate_id <= 0 for candidate_id in value):
            raise ValueError("Todos los candidato_ids deben ser mayores que cero")
        if len(value) != len(set(value)):
            raise ValueError("candidato_ids no puede contener duplicados")
        return value


class AsignarTodosCreate(StrictModel):
    fecha_vencimiento: datetime


class CandidatoDisponibleRead(BaseModel):
    cand_id: int
    cand_email: str
    cand_nombres: str | None = None
    cand_apellido_paterno: str | None = None
    cand_apellido_materno: str | None = None
    solicitud_candidato_id: int
    estado_postulacion_id: int | None = None
    estado_postulacion_nombre: str | None = None
    cuestionario_asignado: bool
    asignacion_id: int | None = None
    estado_cuestionario: str | None = None


class AsignacionRead(BaseModel):
    cdcu_id: int
    cdcu_candidato_id: int
    candidato_email: str | None = None
    cdcu_cuestionario_id: int
    cuestionario_nombre: str | None = None
    cdcu_fecha_asignacion: datetime
    cdcu_fecha_inicio: datetime | None = None
    cdcu_fecha_vencimiento: datetime
    cdcu_fecha_resolucion: datetime | None = None
    cdcu_porcentaje_obtenido: Decimal | None = None
    estado_id: int
    estado_nombre: str
    cdcu_tiempo_utilizado: int | None = None
    cdcu_permitir_reintento: bool
    cdcu_aprobado: bool | None = None
    cantidad_preguntas: int
    puntaje_maximo: int
    duracion_minutos: int


class AsignacionMasivaRead(BaseModel):
    cuestionario_id: int
    solicitud_id: int
    fecha_vencimiento: datetime
    total_candidatos_solicitud: int
    total_solicitados: int
    total_asignados: int
    total_omitidos_ya_asignados: int
    asignaciones: list[AsignacionRead] = Field(default_factory=list)


class AsignacionCandidateRead(BaseModel):
    cdcu_id: int
    cuestionario_id: int
    cuestionario_nombre: str
    cuestionario_descripcion: str | None = None
    porcentaje_aprobacion: Decimal
    solicitud_id: int
    solicitud_codigo: str | None = None
    fecha_asignacion: datetime
    fecha_inicio: datetime | None = None
    fecha_vencimiento: datetime
    fecha_resolucion: datetime | None = None
    estado: str
    cantidad_preguntas: int
    puntaje_maximo: int
    duracion_minutos: int
    porcentaje_obtenido: Decimal | None = None
    aprobado: bool | None = None
    tiempo_utilizado: int | None = None


class RespuestaSave(StrictModel):
    pregunta_cuestionario_id: int = Field(gt=0)
    opcion_respuesta_id: int = Field(gt=0)


class RespuestaRead(BaseModel):
    rspr_id: int
    pregunta_cuestionario_id: int
    opcion_respuesta_id: int


class FinalizarRead(BaseModel):
    asignacion_id: int
    estado: str
    puntaje_obtenido: int
    puntaje_maximo: int
    porcentaje_obtenido: Decimal
    porcentaje_aprobacion: Decimal
    aprobado: bool
    tiempo_utilizado: int
    respondidas: int
    preguntas_totales: int


class RespuestaResultadoInterno(BaseModel):
    pregunta: str
    opcion_seleccionada: str
    opcion_correcta: str
    es_correcta: bool
    puntaje_obtenido: int
    puntaje_maximo: int


class ResultadoInternoRead(BaseModel):
    asignacion: AsignacionRead
    respuestas: list[RespuestaResultadoInterno] = Field(default_factory=list)


class ReintentoEnable(StrictModel):
    fecha_vencimiento: datetime
