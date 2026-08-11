from datetime import date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, AliasChoices


# Catálogo Genérico Flexible para Mapear Diversos Modelos de Catálogo
class CatalogoBaseResponse(BaseModel):
    id: Optional[int] = Field(
        None, 
        validation_alias=AliasChoices("id", "cmn_id", "crg_id", "inst_id", "crra_id", "nves_id", "eces_id", "nvhb_id", "hbd_id", "dsp_id")
    )
    nombre: Optional[str] = Field(
        None, 
        validation_alias=AliasChoices("nombre", "cmn_nombre", "crg_nombre", "inst_nombre", "crra_nombre", "nves_nombre", "eces_nombre", "nvhb_nombre", "hbd_nombre", "dsp_nombre")
    )    
    model_config = ConfigDict(from_attributes=True)


# --- Schemas de Dirección ---
class DireccionCandidatoCreate(BaseModel):
    drcd_comuna_id: Optional[int] = None
    drcd_calle: Optional[str] = None
    drcd_numero: Optional[str] = None
    drcd_depto_oficina: Optional[str] = None

class DireccionCandidatoResponse(DireccionCandidatoCreate):
    drcd_id: int
    comuna: Optional[CatalogoBaseResponse] = None
    model_config = ConfigDict(from_attributes=True)


# --- Schemas de Habilidades del Candidato ---
class CandidatoHabilidadCreate(BaseModel):
    cdhb_habilidad_id: int
    cdhb_nivel_habilidad_id: Optional[int] = None
    cdhb_anios_experiencia: int = Field(default=0, ge=0)

class CandidatoHabilidadResponse(CandidatoHabilidadCreate):
    cdhb_id: int
    habilidad: Optional[CatalogoBaseResponse] = None
    nivel_habilidad: Optional[CatalogoBaseResponse] = None
    model_config = ConfigDict(from_attributes=True)


# --- Schemas de Experiencia Laboral ---
class ExperienciaLaboralCreate(BaseModel):
    expl_empresa: str
    expl_cargo_id: Optional[int] = None
    expl_cargo_nombre_custom: Optional[str] = None
    expl_fecha_inicio: date
    expl_fecha_fin: Optional[date] = None
    expl_trabaja_actualmente: bool = False
    expl_descripcion_funciones: Optional[str] = None
    habilidades_ids: List[int] = Field(default=[], description="IDs de habilidades aplicadas en este trabajo")

class ExperienciaLaboralHabilidadResponse(BaseModel):
    exhb_id: int
    habilidad: Optional[CatalogoBaseResponse] = None
    model_config = ConfigDict(from_attributes=True)

class ExperienciaLaboralResponse(BaseModel):
    expl_id: int
    expl_empresa: str
    expl_cargo_nombre_custom: Optional[str] = None
    expl_fecha_inicio: date
    expl_fecha_fin: Optional[date] = None
    expl_trabaja_actualmente: bool
    expl_descripcion_funciones: Optional[str] = None
    cargo: Optional[CatalogoBaseResponse] = None
    habilidades_asociadas: List[ExperienciaLaboralHabilidadResponse] = []                                                                         
    model_config = ConfigDict(from_attributes=True)


# --- Schemas de Estudios ---
class EstudioCandidatoCreate(BaseModel):
    estc_institucion_id: Optional[int] = None
    estc_carrera_id: Optional[int] = None
    estc_nivel_estudio_id: Optional[int] = None
    estc_estado_estudio_id: Optional[int] = None
    estc_fecha_inicio: Optional[date] = None
    estc_fecha_fin: Optional[date] = None

class EstudioCandidatoResponse(EstudioCandidatoCreate):
    estc_id: int
    institucion: Optional[CatalogoBaseResponse] = None
    carrera: Optional[CatalogoBaseResponse] = None
    nivel_estudio: Optional[CatalogoBaseResponse] = None
    estado_estudio: Optional[CatalogoBaseResponse] = None
    model_config = ConfigDict(from_attributes=True)


# --- Schemas de Cursos ---
class CursoCreate(BaseModel):
    crs_nombre: str
    crs_institucion_id: Optional[int] = None
    crs_horas_duracion: Optional[int] = None
    crs_fecha_obtencion: Optional[date] = None
    crs_tiene_certificado: bool = False

class CursoResponse(CursoCreate):
    crs_id: int
    institucion: Optional[CatalogoBaseResponse] = None
    model_config = ConfigDict(from_attributes=True)


# --- Schemas Principales de Candidato ---
class CandidatoCreate(BaseModel):
    cand_rut_sin_dv: int = Field(..., description="RUT sin puntos ni dígito verificador")
    cand_dv: str = Field(..., max_length=1, description="Dígito verificador (0-9 o K)")
    cand_nombres: str
    cand_apellidos: str
    cand_email: EmailStr
    cand_telefono: Optional[str] = None
    cand_fecha_nacimiento: Optional[date] = None
    cand_resumen_profesional: Optional[str] = None
    cand_disponibilidad_id: Optional[int] = None

    # Objetos anidados en el ingreso de CV
    direccion: Optional[DireccionCandidatoCreate] = None
    habilidades: List[CandidatoHabilidadCreate] = []
    experiencias: List[ExperienciaLaboralCreate] = []
    estudios: List[EstudioCandidatoCreate] = []
    cursos: List[CursoCreate] = []


class CandidatoPerfilResponse(BaseModel):
    cand_id: int
    cand_rut_sin_dv: int
    cand_dv: str
    cand_nombres: str
    cand_apellidos: str
    cand_email: EmailStr
    cand_telefono: Optional[str] = None
    cand_fecha_nacimiento: Optional[date] = None
    cand_resumen_profesional: Optional[str] = None

    disponibilidad: Optional[CatalogoBaseResponse] = None
    direccion: Optional[DireccionCandidatoResponse] = None
    habilidades: List[CandidatoHabilidadResponse] = []
    experiencias: List[ExperienciaLaboralResponse] = []
    estudios: List[EstudioCandidatoResponse] = []
    cursos: List[CursoResponse] = []

    model_config = ConfigDict(from_attributes=True)