from __future__ import annotations

from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


# ==========================================================
# BASES REUTILIZABLES
# ==========================================================

class BaseRead(BaseModel):
    """Base para respuestas construidas desde objetos SQLAlchemy."""
                                                  

    model_config = ConfigDict(from_attributes=True)


class BaseCreate(BaseModel):
    """Base para payloads de creación. Rechaza campos desconocidos."""
                                             
                                                     

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class BaseUpdate(BaseModel):
    """Base para PATCH/edición parcial. Rechaza campos desconocidos."""
                                                     
                                                    

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


Text15 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=15)]
Text20 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
Text40 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)]
Text50 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
Text100 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Text255 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
Text300 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]


# ==========================================================
# UBICACIÓN GEOGRÁFICA
# ==========================================================

class PaisBase(BaseCreate):
    pais_nombre: Text100


class PaisCreate(PaisBase):
    pass


class PaisUpdate(BaseUpdate):
    pais_nombre: Optional[Text100] = None


class PaisRead(BaseRead):
    pais_id: int
    pais_nombre: Optional[str] = None


class RegionBase(BaseCreate):
    reg_pais_id: Optional[int] = Field(default=None, ge=1)
    reg_nombre: Text100


class RegionCreate(RegionBase):
    pass


class RegionUpdate(BaseUpdate):
    reg_pais_id: Optional[int] = Field(default=None, ge=1)
    reg_nombre: Optional[Text100] = None


class RegionRead(BaseRead):
    reg_id: int
    reg_pais_id: Optional[int] = None
    reg_nombre: Optional[str] = None


class ComunaBase(BaseCreate):
    com_region_id: Optional[int] = Field(default=None, ge=1)
    com_nombre: Text100


class ComunaCreate(ComunaBase):
    pass


class ComunaUpdate(BaseUpdate):
    com_region_id: Optional[int] = Field(default=None, ge=1)
    com_nombre: Optional[Text100] = None


class ComunaRead(BaseRead):
    com_id: int
    com_region_id: Optional[int] = None
    com_nombre: Optional[str] = None


# ==========================================================
# EDUCACIÓN E INSTITUCIONES
# ==========================================================

class TipoInstitucionBase(BaseCreate):
    tint_tipo_institucion: Text40
                                                       
                                                              

                                                                                                                                                       

class TipoInstitucionCreate(TipoInstitucionBase):
    pass

                                                                                             
                                                           
                                                               
                                                                      
                                                                       
                                                                             

class TipoInstitucionUpdate(BaseUpdate):
    tint_tipo_institucion: Optional[Text40] = None


class TipoInstitucionRead(BaseRead):
    tint_id: int
    tint_tipo_institucion: Optional[str] = None
                                                         

                                                                                                                                                       

class InstitucionBase(BaseCreate):
    inst_nombre: Text40
    inst_tipo_institucion_id: Optional[int] = Field(default=None, ge=1)

                                                                                    
                                                    
                                                        
                                                               

class InstitucionCreate(InstitucionBase):
    pass


class InstitucionUpdate(BaseUpdate):
    inst_nombre: Optional[Text40] = None
    inst_tipo_institucion_id: Optional[int] = Field(default=None, ge=1)
                                                                    

                                                                                                                                                       

class InstitucionRead(BaseRead):
    inst_id: int
    inst_nombre: Optional[str] = None
    inst_tipo_institucion_id: Optional[int] = None

                                                                                          
                                                         
                           

class CarreraBase(BaseCreate):
    crra_nombre: Text255


class CarreraCreate(CarreraBase):
    pass
                                                                
                                                                       

                                                                                                                                                       

class CarreraUpdate(BaseUpdate):
    crra_nombre: Optional[Text255] = None

                                                                                                        
                                                                    
                                                                      
                                                                             

class CarreraRead(BaseRead):
    crra_id: int
    crra_nombre: Optional[str] = None


class NivelEducacionalBase(BaseCreate):
    nved_nombre: Text40


class NivelEducacionalCreate(NivelEducacionalBase):
    pass


class NivelEducacionalUpdate(BaseUpdate):
    nved_nombre: Optional[Text40] = None


class NivelEducacionalRead(BaseRead):
    nved_id: int
    nved_nombre: Optional[str] = None


# ==========================================================
# PUESTO, EXPERIENCIA Y CONDICIONES DE TRABAJO
# ==========================================================

class HabilidadBase(BaseCreate):
    hab_nombre: Text255
    hab_descripcion: Optional[Text300] = None


class HabilidadCreate(HabilidadBase):
    pass


class HabilidadUpdate(BaseUpdate):
    hab_nombre: Optional[Text255] = None
    hab_descripcion: Optional[Text300] = None


class HabilidadRead(BaseRead):
    hab_id: int
    hab_nombre: Optional[str] = None
    hab_descripcion: Optional[str] = None


class NivelHabilidadBase(BaseCreate):
    nvhb_nombre: Text20
    nvhb_descripcion: Optional[Text300] = None
    nvhb_puntaje_base: Optional[int] = Field(default=None, ge=0)
    nvhb_duracion: Optional[int] = Field(default=None, ge=0)


class NivelHabilidadCreate(NivelHabilidadBase):
    pass


class NivelHabilidadUpdate(BaseUpdate):
    nvhb_nombre: Optional[Text20] = None
    nvhb_descripcion: Optional[Text300] = None
    nvhb_puntaje_base: Optional[int] = Field(default=None, ge=0)
    nvhb_duracion: Optional[int] = Field(default=None, ge=0)


class NivelHabilidadRead(BaseRead):
    nvhb_id: int
    nvhb_nombre: Optional[str] = None
    nvhb_descripcion: Optional[str] = None
    nvhb_puntaje_base: Optional[int] = None
    nvhb_duracion: Optional[int] = None


class CargoBase(BaseCreate):
    crgo_nombre: Text50
    crgo_descripcion: Optional[Text300] = None


class CargoCreate(CargoBase):
    pass


class CargoUpdate(BaseUpdate):
    crgo_nombre: Optional[Text50] = None
    crgo_descripcion: Optional[Text300] = None


class CargoRead(BaseRead):
    crgo_id: int
    crgo_nombre: Optional[str] = None
    crgo_descripcion: Optional[str] = None


class ModalidadBase(BaseCreate):
    mdld_nombre: Text20
    mdld_descripcion: Optional[Text300] = None


class ModalidadCreate(ModalidadBase):
    pass


class ModalidadUpdate(BaseUpdate):
    mdld_nombre: Optional[Text20] = None
    mdld_descripcion: Optional[Text300] = None


class ModalidadRead(BaseRead):
    mdld_id: int
    mdld_nombre: Optional[str] = None
    mdld_descripcion: Optional[str] = None


class TipoContratoBase(BaseCreate):
    tpct_nombre: Text20
    tpct_descripcion: Optional[Text300] = None


class TipoContratoCreate(TipoContratoBase):
    pass


class TipoContratoUpdate(BaseUpdate):
    tpct_nombre: Optional[Text20] = None
    tpct_descripcion: Optional[Text300] = None


class TipoContratoRead(BaseRead):
    tpct_id: int
    tpct_nombre: Optional[str] = None
    tpct_descripcion: Optional[str] = None


class DisponibilidadBase(BaseCreate):
    disp_nombre: Text40


class DisponibilidadCreate(DisponibilidadBase):
    pass


class DisponibilidadUpdate(BaseUpdate):
    disp_nombre: Optional[Text40] = None


class DisponibilidadRead(BaseRead):
    disp_id: int
    disp_nombre: Optional[str] = None


# ==========================================================
# RECLUTAMIENTO, RESULTADOS Y ESTADOS
# ==========================================================

class EstadoSolicitudBase(BaseCreate):
    essl_nombre: Text20
    essl_descripcion: Optional[Text300] = None


class EstadoSolicitudCreate(EstadoSolicitudBase):
    pass


class EstadoSolicitudUpdate(BaseUpdate):
    essl_nombre: Optional[Text20] = None
    essl_descripcion: Optional[Text300] = None


class EstadoSolicitudRead(BaseRead):
    essl_id: int
    essl_nombre: Optional[str] = None
    essl_descripcion: Optional[str] = None


class PrioridadSolicitudBase(BaseCreate):
    prsol_nombre: Text15
    prsol_descripcion: Optional[Text300] = None


class PrioridadSolicitudCreate(PrioridadSolicitudBase):
    pass


class PrioridadSolicitudUpdate(BaseUpdate):
    prsol_nombre: Optional[Text15] = None
    prsol_descripcion: Optional[Text300] = None


class PrioridadSolicitudRead(BaseRead):
    prsol_id: int
    prsol_nombre: Optional[str] = None
    prsol_descripcion: Optional[str] = None


class EstadoSolicitudCandidatoBase(BaseCreate):
    essc_nombre: Text40
    essc_descripcion: Optional[Text300] = None


class EstadoSolicitudCandidatoCreate(EstadoSolicitudCandidatoBase):
    pass


class EstadoSolicitudCandidatoUpdate(BaseUpdate):
    essc_nombre: Optional[Text40] = None
    essc_descripcion: Optional[Text300] = None


class EstadoSolicitudCandidatoRead(BaseRead):
    essc_id: int
    essc_nombre: Optional[str] = None
    essc_descripcion: Optional[str] = None


class MotivoRechazoBase(BaseCreate):
    mtrc_nombre: Text40
    mtrc_descripcion: Optional[Text300] = None


class MotivoRechazoCreate(MotivoRechazoBase):
    pass


class MotivoRechazoUpdate(BaseUpdate):
    mtrc_nombre: Optional[Text40] = None
    mtrc_descripcion: Optional[Text300] = None


class MotivoRechazoRead(BaseRead):
    mtrc_id: int
    mtrc_nombre: Optional[str] = None
    mtrc_descripcion: Optional[str] = None


class EstadoCuestionarioCandidatoBase(BaseCreate):
    escc_nombre: Text40


class EstadoCuestionarioCandidatoCreate(EstadoCuestionarioCandidatoBase):
    pass


class EstadoCuestionarioCandidatoUpdate(BaseUpdate):
    escc_nombre: Optional[Text40] = None


class EstadoCuestionarioCandidatoRead(BaseRead):
    escc_id: int
    escc_nombre: Optional[str] = None


class EstadoEntrevistaBase(BaseCreate):
    esev_nombre: Text40
    esev_descripcion: Optional[Text300] = None


class EstadoEntrevistaCreate(EstadoEntrevistaBase):
    pass


class EstadoEntrevistaUpdate(BaseUpdate):
    esev_nombre: Optional[Text40] = None
    esev_descripcion: Optional[Text300] = None


class EstadoEntrevistaRead(BaseRead):
    esev_id: int
    esev_nombre: Optional[str] = None
    esev_descripcion: Optional[str] = None


class TipoEntrevistaBase(BaseCreate):
    tpet_nombre: Text40
    tpet_descripcion: Optional[Text300] = None


class TipoEntrevistaCreate(TipoEntrevistaBase):
    pass


class TipoEntrevistaUpdate(BaseUpdate):
    tpet_nombre: Optional[Text40] = None
    tpet_descripcion: Optional[Text300] = None


class TipoEntrevistaRead(BaseRead):
    tpet_id: int
    tpet_nombre: Optional[str] = None
    tpet_descripcion: Optional[str] = None


class NombreResultadoBase(BaseCreate):
    nore_nombre: Text40


class NombreResultadoCreate(NombreResultadoBase):
    pass


class NombreResultadoUpdate(BaseUpdate):
    nore_nombre: Optional[Text40] = None


class NombreResultadoRead(BaseRead):
    nore_id: int
    nore_nombre: Optional[str] = None
