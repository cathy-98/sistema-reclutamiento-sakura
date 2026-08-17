from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


Clasificacion = Literal["APROBADO", "PENDIENTE", "NO_APROBADO"]


class TipoResultadoResumen(StrictModel):
    nombre: str
    cantidad: int


class EvaluacionTecnicaResumen(StrictModel):
    cuestionario_id: int
    cuestionario: str
    porcentaje: float | None = None
    aprobado: bool | None = None
    estado: str | None = None


class EvaluacionEntrevistaResumen(StrictModel):
    entrevista_id: int
    tipo_id: int | None = None
    tipo: str | None = None
    entrevistador_id: int | None = None
    entrevistador: str | None = None
    resultado: str
    observacion: str | None = None


class CandidatoInformeItem(StrictModel):
    solicitud_candidato_id: int
    solicitud_id: int
    solicitud_codigo: str | None
    solicitud_titulo: str | None
    candidato_id: int
    candidato_nombre: str
    candidato_email: EmailStr
    candidato_telefono: str | None
    cargo_id: int | None
    cargo: str | None
    disponibilidad_id: int | None
    disponibilidad: str | None
    match: float | None
    estado_postulacion: str | None
    clasificacion: Clasificacion
    clasificacion_sugerida: bool
    motivo_clasificacion: list[str]
    tecnologias: list[str] = []
    tecnicas: list[EvaluacionTecnicaResumen] = []
    entrevistas: list[EvaluacionEntrevistaResumen] = []
    puede_enviar_rechazo: bool
    puede_enviar_directivos: bool


class CandidateListResponse(StrictModel):
    total: int
    items: list[CandidatoInformeItem]


class IdiomaItem(StrictModel):
    idioma_id: int
    idioma: str
    nivel: str


class IdiomaUpsert(StrictModel):
    idioma_id: int = Field(gt=0)
    nivel: Literal["Basico", "Intermedio", "Avanzado", "Nativo"]


class IdiomasReplaceRequest(StrictModel):
    idiomas: list[IdiomaUpsert]

    @field_validator("idiomas")
    @classmethod
    def unique_languages(cls, value):
        ids = [x.idioma_id for x in value]
        if len(ids) != len(set(ids)):
            raise ValueError("No se puede repetir un idioma")
        return value


class CategoriaHabilidadItem(StrictModel):
    categoria_id: int
    nombre: str
    descripcion: str | None = None


class HabilidadCategoriaUpdate(StrictModel):
    categoria_id: int | None = Field(default=None, gt=0)


class CVOverrides(StrictModel):
    perfil_profesional: str | None = Field(default=None, max_length=3000)
    resumen_ejecutivo: str | None = Field(default=None, max_length=3000)
    roles_recomendados: list[str] | None = None
    fortalezas: list[str] | None = None


class DocumentoResponse(StrictModel):
    documento_id: int
    solicitud_candidato_id: int
    tipo_documento: str
    nombre_archivo: str
    fecha_generacion: datetime
    hash_sha256: str


class MasivoRequest(StrictModel):
    solicitud_candidato_ids: list[int] = Field(min_length=1, max_length=100)

    @field_validator("solicitud_candidato_ids")
    @classmethod
    def unique_ids(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("No se pueden repetir candidatos")
        if any(x <= 0 for x in value):
            raise ValueError("Los IDs deben ser mayores que cero")
        return value


class MasivoDocumentoResponse(StrictModel):
    nombre_archivo: str
    cantidad: int
    documento_ids: list[int]


class DirectivosPrepareRequest(MasivoRequest):
    destinatarios: list[EmailStr] = Field(min_length=1, max_length=30)
    cc: list[EmailStr] = Field(default_factory=list, max_length=30)
    asunto: str | None = Field(default=None, max_length=300)
    cuerpo: str | None = Field(default=None, max_length=10000)


class DirectivosPreview(StrictModel):
    destinatarios: list[EmailStr]
    cc: list[EmailStr]
    asunto: str
    cuerpo: str
    candidatos: list[CandidatoInformeItem]
    adjuntos: list[DocumentoResponse]


class DirectivosSendRequest(DirectivosPrepareRequest):
    pass


class RechazosPrepareRequest(MasivoRequest):
    tipo: Literal["RECHAZO", "AGRADECIMIENTO"] = "RECHAZO"
    asunto_plantilla: str | None = Field(default=None, max_length=300)
    cuerpo_plantilla: str | None = Field(default=None, max_length=10000)


class RechazoPreviewItem(StrictModel):
    solicitud_candidato_id: int
    destinatario: EmailStr
    asunto: str
    cuerpo: str


class RechazosPreview(StrictModel):
    items: list[RechazoPreviewItem]


class RechazoSendItem(StrictModel):
    tipo: Literal["RECHAZO", "AGRADECIMIENTO"] = "RECHAZO"
    solicitud_candidato_id: int = Field(gt=0)
    asunto: str = Field(min_length=1, max_length=300)
    cuerpo: str = Field(min_length=1, max_length=10000)


class RechazosSendRequest(StrictModel):
    items: list[RechazoSendItem] = Field(min_length=1, max_length=100)

    @field_validator("items")
    @classmethod
    def unique_items(cls, value):
        ids = [x.solicitud_candidato_id for x in value]
        if len(ids) != len(set(ids)):
            raise ValueError("No se pueden repetir candidatos")
        return value


class NotificationResponse(StrictModel):
    notificacion_id: int
    solicitud_candidato_id: int
    tipo: str
    destinatario: str
    cc: str | None
    asunto: str
    estado: str
    fecha_creacion: datetime
    fecha_envio: datetime | None
    error: str | None


class PlantillaResponse(StrictModel):
    plantilla_id: int
    tipo: str
    nombre: str
    asunto: str
    cuerpo: str
    activa: bool


class PlantillaUpdate(StrictModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    asunto: str | None = Field(default=None, min_length=1, max_length=300)
    cuerpo: str | None = Field(default=None, min_length=1, max_length=10000)
    activa: bool | None = None

    @model_validator(mode="after")
    def non_empty(self):
        if not self.model_fields_set:
            raise ValueError("Debe informar al menos un campo")
        return self

class NotificationDetailResponse(NotificationResponse):
    cuerpo: str
