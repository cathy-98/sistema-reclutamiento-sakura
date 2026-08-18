from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


class TipoEntrevistaAsignacion(StrictModel):
    tipo_entrevista_id: int = Field(gt=0)
    usuarios_ids: list[int] = Field(min_length=1, max_length=50)

    @field_validator("usuarios_ids")
    @classmethod
    def validar_usuarios(cls, value: list[int]) -> list[int]:
        if any(v <= 0 for v in value):
            raise ValueError("Todos los usuarios_ids deben ser mayores que cero")
        if len(value) != len(set(value)):
            raise ValueError("usuarios_ids no puede contener duplicados")
        return value


class EntrevistaCreate(StrictModel):
    solicitud_candidato_id: int = Field(gt=0)
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    titulo_evento: str = Field(min_length=1, max_length=300)
    enlace_reunion: str | None = Field(default=None, max_length=300)
    comentarios_convocatoria: str | None = Field(default=None, max_length=300)
    tipos: list[TipoEntrevistaAsignacion] = Field(min_length=1, max_length=20)

    @field_validator("titulo_evento")
    @classmethod
    def titulo_no_vacio(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("titulo_evento no puede estar vacío")
        return value

    @field_validator("enlace_reunion", "comentarios_convocatoria")
    @classmethod
    def opcionales_limpios(cls, value: str | None) -> str | None:
        return _clean(value)

    @model_validator(mode="after")
    def validar(self):
        if self.fecha_hora_inicio >= self.fecha_hora_fin:
            raise ValueError("fecha_hora_inicio debe ser anterior a fecha_hora_fin")
        tipos = [x.tipo_entrevista_id for x in self.tipos]
        if len(tipos) != len(set(tipos)):
            raise ValueError("No puede repetir un tipo de entrevista")
        return self


class EntrevistaMasivaCreate(StrictModel):
    solicitudes_candidatos_ids: list[int] = Field(min_length=1, max_length=500)
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    titulo_evento: str = Field(min_length=1, max_length=300)
    enlace_reunion: str | None = Field(default=None, max_length=300)
    comentarios_convocatoria: str | None = Field(default=None, max_length=300)
    tipos: list[TipoEntrevistaAsignacion] = Field(min_length=1, max_length=20)

    @field_validator("solicitudes_candidatos_ids")
    @classmethod
    def validar_slcd(cls, value: list[int]) -> list[int]:
        if any(v <= 0 for v in value):
            raise ValueError("Todos los solicitudes_candidatos_ids deben ser mayores que cero")
        if len(value) != len(set(value)):
            raise ValueError("solicitudes_candidatos_ids no puede contener duplicados")
        return value

    @field_validator("titulo_evento")
    @classmethod
    def titulo_no_vacio(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("titulo_evento no puede estar vacío")
        return value

    @field_validator("enlace_reunion", "comentarios_convocatoria")
    @classmethod
    def opcionales_limpios(cls, value: str | None) -> str | None:
        return _clean(value)

    @model_validator(mode="after")
    def validar(self):
        if self.fecha_hora_inicio >= self.fecha_hora_fin:
            raise ValueError("fecha_hora_inicio debe ser anterior a fecha_hora_fin")
        tipos = [x.tipo_entrevista_id for x in self.tipos]
        if len(tipos) != len(set(tipos)):
            raise ValueError("No puede repetir un tipo de entrevista")
        return self


class EntrevistaUpdate(StrictModel):
    titulo_evento: str | None = Field(default=None, min_length=1, max_length=300)
    enlace_reunion: str | None = Field(default=None, max_length=300)
    comentarios_convocatoria: str | None = Field(default=None, max_length=300)

    @field_validator("titulo_evento")
    @classmethod
    def titulo_no_vacio(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("titulo_evento no puede estar vacío")
        return value

    @field_validator("enlace_reunion", "comentarios_convocatoria")
    @classmethod
    def opcionales_limpios(cls, value: str | None) -> str | None:
        return _clean(value)

    @model_validator(mode="after")
    def not_empty(self):
        if not self.model_fields_set:
            raise ValueError("Debe informar al menos un campo")
        return self


class ParticipantesUpdate(StrictModel):
    tipos: list[TipoEntrevistaAsignacion] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def validar(self):
        ids = [x.tipo_entrevista_id for x in self.tipos]
        if len(ids) != len(set(ids)):
            raise ValueError("No puede repetir un tipo de entrevista")
        return self


class ReprogramarRequest(StrictModel):
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    motivo: str = Field(min_length=1, max_length=300)

    @field_validator("motivo")
    @classmethod
    def clean_motivo(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("motivo no puede estar vacío")
        return value

    @model_validator(mode="after")
    def validar(self):
        if self.fecha_hora_inicio >= self.fecha_hora_fin:
            raise ValueError("fecha_hora_inicio debe ser anterior a fecha_hora_fin")
        return self


class MotivoEstadoRequest(StrictModel):
    motivo: str = Field(min_length=1, max_length=300)

    @field_validator("motivo")
    @classmethod
    def clean_motivo(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("motivo no puede estar vacío")
        return value


class EvaluacionCreate(StrictModel):
    nombre_resultado_id: int = Field(gt=0)
    observacion: str | None = Field(default=None, max_length=300)

    @field_validator("observacion")
    @classmethod
    def clean_obs(cls, value: str | None) -> str | None:
        return _clean(value)


class EvaluacionUpdate(StrictModel):
    nombre_resultado_id: int | None = Field(default=None, gt=0)
    observacion: str | None = Field(default=None, max_length=300)

    @field_validator("observacion")
    @classmethod
    def clean_obs(cls, value: str | None) -> str | None:
        return _clean(value)

    @model_validator(mode="after")
    def not_empty(self):
        if not self.model_fields_set:
            raise ValueError("Debe informar al menos un campo")
        return self


class EntrevistadorRead(BaseModel):
    usuario_id: int
    nombres: str
    apellido_paterno: str
    email: str


class TipoEntrevistaRead(BaseModel):
    tipo_entrevista_id: int
    nombre: str
    descripcion: str | None = None
    entrevistadores: list[EntrevistadorRead] = Field(default_factory=list)


class EvaluacionRead(BaseModel):
    evaluacion_id: int
    entrevista_id: int
    tipo_entrevista_id: int | None = None
    tipo_entrevista_nombre: str | None = None
    usuario_id: int | None = None
    usuario_nombre: str | None = None
    resultado_id: int
    resultado_nombre: str
    observacion: str | None = None
    fecha_creacion: datetime | None = None
    fecha_actualizacion: datetime | None = None


class EntrevistaRead(BaseModel):
    entrevista_id: int
    solicitud_candidato_id: int
    solicitud_id: int
    solicitud_codigo: str | None = None
    candidato_id: int
    candidato_nombre: str
    candidato_email: str
    estado_id: int
    estado_nombre: str
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    fecha_creacion: datetime
    fecha_actualizacion: datetime | None = None
    titulo_evento: str
    enlace_reunion: str | None = None
    comentarios_convocatoria: str | None = None
    motivo_estado: str | None = None
    usuario_creador_id: int | None = None
    tipos: list[TipoEntrevistaRead] = Field(default_factory=list)
    evaluaciones: list[EvaluacionRead] = Field(default_factory=list)


class EntrevistaMasivaRead(BaseModel):
    total_solicitados: int
    total_creados: int
    entrevistas: list[EntrevistaRead] = Field(default_factory=list)


class MiEntrevistaRead(BaseModel):
    entrevista_id: int
    solicitud_candidato_id: int
    candidato_id: int
    candidato_nombre: str
    solicitud_id: int
    solicitud_codigo: str | None = None
    estado: str
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    titulo_evento: str
    enlace_reunion: str | None = None
    tipos_asignados: list[TipoEntrevistaRead] = Field(default_factory=list)


class EntrevistaCandidatoRead(BaseModel):
    entrevista_id: int
    solicitud_id: int
    solicitud_codigo: str | None = None
    estado: str
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    titulo_evento: str
    enlace_reunion: str | None = None
    comentarios_convocatoria: str | None = None
    tipos: list[str] = Field(default_factory=list)
