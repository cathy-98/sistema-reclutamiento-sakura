from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator, model_validator


Password = Annotated[str, StringConstraints(min_length=8, max_length=72)]


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def normalize_semicolon_values(value: str | list[str] | None) -> str | None:
    if value is None:
        return None
    raw = value if isinstance(value, list) else value.split(";")
    result: list[str] = []
    seen: set[str] = set()
    for item in raw:
        cleaned = str(item).strip()
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key not in seen:
            seen.add(key)
            result.append(cleaned)
    return ";".join(result) or None


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DireccionCreate(StrictSchema):
    drcd_comuna_id: int | None = Field(default=None, gt=0)
    drcd_calle: str | None = Field(default=None, max_length=40)
    drcd_numero: int | None = Field(default=None, gt=0)
    drcd_dpto_oficina: str | None = Field(default=None, max_length=10)

    @field_validator("drcd_calle", "drcd_dpto_oficina")
    @classmethod
    def trim_text(cls, value):
        return _clean_optional_text(value)


class DireccionUpdate(DireccionCreate):
    pass


class DireccionResponse(DireccionCreate):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    drcd_id: int
    drcd_candidato_id: int | None = None


class HabilidadCreate(StrictSchema):
    cdhb_habilidad_id: int = Field(gt=0)
    cdhb_nivel_habilidad_id: int | None = Field(default=None, gt=0)
    cdhb_anios_experiencia: int = Field(default=0, ge=0)


class HabilidadUpdate(StrictSchema):
    cdhb_nivel_habilidad_id: int | None = Field(default=None, gt=0)
    cdhb_anios_experiencia: int | None = Field(default=None, ge=0)


class HabilidadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    cdhb_id: int
    cdhb_candidato_id: int | None
    cdhb_habilidad_id: int | None
    cdhb_nivel_habilidad_id: int | None
    cdhb_anios_experiencia: int | None


class EstudioCreate(StrictSchema):
    etcd_nivel_educacional_id: int | None = Field(default=None, gt=0)
    etcd_institucion_id: int | None = Field(default=None, gt=0)
    etcd_carrera_id: int | None = Field(default=None, gt=0)
    etcd_fecha_inicio: date | None = None
    etcd_fecha_fin: date | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.etcd_fecha_inicio and self.etcd_fecha_fin and self.etcd_fecha_inicio > self.etcd_fecha_fin:
            raise ValueError("etcd_fecha_inicio no puede ser posterior a etcd_fecha_fin")
        return self


class EstudioUpdate(EstudioCreate):
    pass


class EstudioResponse(EstudioCreate):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    etcd_id: int
    etcd_candidato_id: int | None


class ExperienciaCreate(StrictSchema):
    expl_empresa_id: int | None = Field(default=None, gt=0)
    expl_cargo_id: int | None = Field(default=None, gt=0)
    expl_descripcion_funciones: str | None = Field(default=None, max_length=300)
    expl_fecha_inicio: date | None = None
    expl_fecha_fin: date | None = None
    habilidades_ids: list[int] = Field(default_factory=list)

    @field_validator("expl_descripcion_funciones")
    @classmethod
    def trim_description(cls, value):
        return _clean_optional_text(value)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.expl_fecha_inicio and self.expl_fecha_fin and self.expl_fecha_inicio > self.expl_fecha_fin:
            raise ValueError("expl_fecha_inicio no puede ser posterior a expl_fecha_fin")
        if len(self.habilidades_ids) != len(set(self.habilidades_ids)):
            raise ValueError("habilidades_ids contiene valores duplicados")
        return self


class ExperienciaUpdate(ExperienciaCreate):
    pass


class ExperienciaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    expl_id: int
    expl_candidato_id: int | None
    expl_empresa_id: int | None
    expl_cargo_id: int | None
    expl_descripcion_funciones: str | None
    expl_fecha_inicio: date | None
    expl_fecha_fin: date | None
    habilidades_ids: list[int] = Field(default_factory=list)


class CursoCreate(StrictSchema):
    curs_nombre_curso: str = Field(min_length=1, max_length=40)
    curs_institucion_id: int | None = Field(default=None, gt=0)
    curs_es_certificado: bool | None = None
    curs_anio_curso: int | None = Field(default=None, ge=1900, le=2100)

    @field_validator("curs_nombre_curso")
    @classmethod
    def trim_name(cls, value):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("curs_nombre_curso no puede estar vacío")
        return cleaned


class CursoUpdate(StrictSchema):
    curs_nombre_curso: str | None = Field(default=None, min_length=1, max_length=40)
    curs_institucion_id: int | None = Field(default=None, gt=0)
    curs_es_certificado: bool | None = None
    curs_anio_curso: int | None = Field(default=None, ge=1900, le=2100)


class CursoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    curs_id: int
    curs_candidato_id: int | None
    curs_nombre_curso: str | None
    curs_institucion_id: int | None
    curs_es_certificado: bool | None
    curs_anio_curso: int | None


class CandidatoBase(StrictSchema):
    cand_email: EmailStr
    cand_nombres: str = Field(min_length=1, max_length=20)
    cand_apellido_paterno: str = Field(min_length=1, max_length=20)
    cand_apellido_materno: str | None = Field(default=None, max_length=20)
    cand_fecha_nacimiento: date | None = None
    cand_telefono: str | None = Field(default=None, max_length=20)
    cand_rut_sin_dv: int | None = Field(default=None, gt=0)
    cand_dv: int | str | None = None
    cand_disponibilidad_id: int | None = Field(default=None, gt=0)
    cand_resumen_profesional: str | None = Field(default=None, max_length=300)
    cand_url_1: str | list[str] | None = None
    cand_titulo: str | None = Field(default=None, max_length=300)
    cand_cv_urls: str | list[str] | None = None

    @field_validator(
        "cand_nombres",
        "cand_apellido_paterno",
        "cand_apellido_materno",
        "cand_telefono",
        "cand_resumen_profesional",
        "cand_titulo",
    )
    @classmethod
    def trim_fields(cls, value):
        return _clean_optional_text(value)

    @field_validator("cand_dv")
    @classmethod
    def normalize_dv(cls, value):
        if value is None:
            return None
        if isinstance(value, int):
            if 0 <= value <= 10:
                return value
            raise ValueError("cand_dv debe estar entre 0 y 10")
        text = str(value).strip().upper()
        if text == "K":
            return 10
        if text.isdigit() and 0 <= int(text) <= 9:
            return int(text)
        raise ValueError("cand_dv debe ser 0-9 o K")

    @field_validator("cand_url_1", "cand_cv_urls")
    @classmethod
    def normalize_urls(cls, value):
        normalized = normalize_semicolon_values(value)
        return normalized

    @model_validator(mode="after")
    def validate_rut_pair(self):
        if (self.cand_rut_sin_dv is None) != (self.cand_dv is None):
            raise ValueError("cand_rut_sin_dv y cand_dv deben informarse juntos")
        if self.cand_fecha_nacimiento and self.cand_fecha_nacimiento > date.today():
            raise ValueError("cand_fecha_nacimiento no puede estar en el futuro")
        return self


class CandidatoCreate(CandidatoBase):
    password_inicial: Password | None = None
    direccion: DireccionCreate | None = None
    habilidades: list[HabilidadCreate] = Field(default_factory=list)
    estudios: list[EstudioCreate] = Field(default_factory=list)
    experiencias: list[ExperienciaCreate] = Field(default_factory=list)
    cursos: list[CursoCreate] = Field(default_factory=list)


class CandidatoReplace(CandidatoBase):
    pass


class CandidatoUpdate(StrictSchema):
    cand_email: EmailStr | None = None
    cand_nombres: str | None = Field(default=None, min_length=1, max_length=20)
    cand_apellido_paterno: str | None = Field(default=None, min_length=1, max_length=20)
    cand_apellido_materno: str | None = Field(default=None, max_length=20)
    cand_fecha_nacimiento: date | None = None
    cand_telefono: str | None = Field(default=None, max_length=20)
    cand_rut_sin_dv: int | None = Field(default=None, gt=0)
    cand_dv: int | str | None = None
    cand_disponibilidad_id: int | None = Field(default=None, gt=0)
    cand_resumen_profesional: str | None = Field(default=None, max_length=300)
    cand_url_1: str | list[str] | None = None
    cand_titulo: str | None = Field(default=None, max_length=300)
    cand_cv_urls: str | list[str] | None = None

    @field_validator("cand_dv")
    @classmethod
    def normalize_dv(cls, value):
        return CandidatoBase.normalize_dv(value)

    @field_validator("cand_url_1", "cand_cv_urls")
    @classmethod
    def normalize_urls(cls, value):
        return normalize_semicolon_values(value)


class CandidatoSelfUpdate(StrictSchema):
    """Campos que el candidato puede mantener por autoservicio.

    Deliberadamente NO incluye email, nombres, RUT/DV, fecha de nacimiento,
    estado, fecha de creación ni cand_cv_urls. Esos campos requieren flujo
    administrativo o de carga de CV y no pueden alterarse desde el portal.
    """

    cand_telefono: str | None = Field(default=None, max_length=20)
    cand_disponibilidad_id: int | None = Field(default=None, gt=0)
    cand_resumen_profesional: str | None = Field(default=None, max_length=300)
    cand_url_1: str | list[str] | None = None
    cand_titulo: str | None = Field(default=None, max_length=300)

    @field_validator(
        "cand_telefono",
        "cand_resumen_profesional",
        "cand_titulo",
    )
    @classmethod
    def trim_fields(cls, value):
        return _clean_optional_text(value)

    @field_validator("cand_url_1")
    @classmethod
    def normalize_urls(cls, value):
        return normalize_semicolon_values(value)


class CandidatoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cand_id: int
    cand_email: EmailStr
    cand_nombres: str
    cand_apellido_paterno: str
    cand_apellido_materno: str | None
    cand_fecha_nacimiento: date | None
    cand_telefono: str | None
    cand_rut_sin_dv: int | None
    cand_dv: int | None
    cand_disponibilidad_id: int | None
    cand_resumen_profesional: str | None
    cand_fecha_creacion: datetime | None
    cand_url_1: str | None
    cand_titulo: str | None
    cand_estado_usuario_id: int | None
    cand_cv_urls: str | None


class CandidatoPerfilResponse(CandidatoResponse):
    direccion: DireccionResponse | None = None
    habilidades: list[HabilidadResponse] = Field(default_factory=list)
    estudios: list[EstudioResponse] = Field(default_factory=list)
    experiencias: list[ExperienciaResponse] = Field(default_factory=list)
    cursos: list[CursoResponse] = Field(default_factory=list)


class CandidatoPerfilCompletoResponse(CandidatoPerfilResponse):
    """Vista completa del candidato con todos los bloques del CV estructurado."""
    pass


class CandidatoCreationResponse(BaseModel):
    candidato: CandidatoPerfilResponse
    password_temporal: str | None = Field(
        default=None,
        description="Solo se entrega una vez cuando el backend generó una contraseña inicial.",
    )


class ImportCvResponse(BaseModel):
    candidato: CandidatoPerfilResponse
    creado: bool
    actualizado: bool
    password_temporal: str | None = None
    cv_ruta_guardada: str
    advertencias: list[str] = Field(default_factory=list)


class PostulacionCreate(StrictSchema):
    slcd_pretension_renta: int | None = Field(default=None, ge=0)
    slcd_puntaje_compatibilidad: Decimal | None = Field(default=None, ge=0, le=100)
    slcd_observaciones: str | None = Field(default=None, max_length=300)


class PostulacionUpdate(StrictSchema):
    slcd_pretension_renta: int | None = Field(default=None, ge=0)
    slcd_puntaje_compatibilidad: Decimal | None = Field(default=None, ge=0, le=100)
    slcd_observaciones: str | None = Field(default=None, max_length=300)


class PostulacionEstadoUpdate(StrictSchema):
    estado_id: int = Field(gt=0)
    motivo_rechazo_id: int | None = Field(default=None, gt=0)
    observaciones: str | None = Field(default=None, max_length=300)


class PostulacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slcd_id: int
    slcd_candidato_id: int | None
    slcd_solicitud_id: int | None
    slcd_pretension_renta: int | None
    slcd_puntaje_compatibilidad: Decimal | None
    slcd_estado_solicitud_candidato_id: int | None
    slcd_fecha_postulacion: datetime | None
    slcd_observaciones: str | None
    slcd_motivo_rechazo_id: int | None


class EvaluacionExcluyentes(BaseModel):
    cumple_excluyentes: bool
    habilidades_faltantes: list[dict] = Field(default_factory=list)
    advertencia: str | None = None


class PostulacionConEvaluacionResponse(BaseModel):
    postulacion: PostulacionResponse
    evaluacion: EvaluacionExcluyentes


class CandidatoSolicitudItem(BaseModel):
    postulacion: PostulacionResponse
    candidato: CandidatoResponse


class PrincipalTypeResponse(BaseModel):
    principal_type: Literal["candidato"] = "candidato"
    candidato: CandidatoPerfilResponse
