from pydantic import BaseModel , ConfigDict # ConfigDict es para que Pydantic pueda convertir los datos de la base de datos a un objeto Python

# ==========================================================
# ESQUEMAS GEOGRÁFICOS
# ==========================================================

class PaisResponse(BaseModel): # Esquema para la respuesta de un país       
    pais_id: int                # ID del país
    pais_nombre: str | None     # Nombre del país

    model_config = ConfigDict(from_attributes=True) # Configuración para que Pydantic pueda convertir los datos de la base de datos a un objeto Python


class RegionResponse(BaseModel): # Esquema para la respuesta de una región  
    reg_id: int                # ID de la región
    reg_pais_id: int | None    # ID del país
    reg_nombre: str | None     # Nombre de la región

    model_config = ConfigDict(from_attributes=True) # Configuración para que Pydantic pueda convertir los datos de la base de datos a un objeto Python


class CiudadResponse(BaseModel): # Esquema para la respuesta de una ciudad  
    ciu_id: int                # ID de la ciudad
    ciu_region_id: int | None    # ID de la región  
    ciu_nombre: str | None     # Nombre de la ciudad

    model_config = ConfigDict(from_attributes=True) # Configuración para que Pydantic pueda convertir los datos de la base de datos a un objeto Python


class ComunaResponse(BaseModel): # Esquema para la respuesta de una comuna  
    com_id: int                # ID de la comuna            
    com_ciudad_id: int | None  # ID de la ciudad
    com_nombre: str | None     # Nombre de la comuna

    model_config = ConfigDict(from_attributes=True) # Configuración para que Pydantic pueda convertir los datos de la base de datos a un objeto Python


# ==========================================================
# ESQUEMAS TÉCNICOS DE RECLUTAMIENTO
# ==========================================================

class HabilidadResponse(BaseModel): # Esquema para la respuesta de una habilidad    
    hab_id: int                # ID de la habilidad
    hab_nombre: str | None     # Nombre de la habilidad
    hab_descripcion: str | None # Descripción de la habilidad

    model_config = ConfigDict(from_attributes=True) # Configuración para que Pydantic pueda convertir los datos de la base de datos a un objeto Python


class NivelHabilidadResponse(BaseModel): # Esquema para la respuesta de un nivel de habilidad
    nvhb_id: int                # ID del nivel de habilidad
    nvhb_nombre: str | None     # Nombre del nivel de habilidad
    nvhb_descripcion: str | None # Descripción del nivel de habilidad
    nvhb_puntaje_base: int | None # Puntaje base del nivel de habilidad
    nvhb_duracion: int | None     # Duración del nivel de habilidad en meses

    model_config = ConfigDict(from_attributes=True) # Configuración para que Pydantic pueda convertir los datos de la base de datos a un objeto Python


class CargoResponse(BaseModel): # Esquema para la respuesta de un cargo
    crgo_id: int                # ID del cargo
    crgo_nombre: str | None     # Nombre del cargo
    crgo_descripcion: str | None # Descripción del cargo

    model_config = ConfigDict(from_attributes=True) # Configuración para que Pydantic pueda convertir los datos de la base de datos a un objeto Python


class ModalidadResponse(BaseModel): # Esquema para la respuesta de una modalidad    
    mdld_id: int                # ID de la modalidad
    mdld_nombre: str | None     # Nombre de la modalidad
    mdld_descripcion: str | None # Descripción de la modalidad

    model_config = ConfigDict(from_attributes=True) # Configuración para que Pydantic pueda convertir los datos de la base de datos a un objeto Python


class TipoContratoResponse(BaseModel): # Esquema para la respuesta de un tipo de contrato   
    tpct_id: int                # ID del tipo de contrato
    tpct_nombre: str | None     # Nombre del tipo de contrato
    tpct_descripcion: str | None # Descripción del tipo de contrato

    model_config = ConfigDict(from_attributes=True) # Configuración para que Pydantic pueda convertir los datos de la base de datos a un objeto Python


class DisponibilidadResponse(BaseModel): # Esquema para la respuesta de una disponibilidad
    disp_id: int                # ID de la disponibilidad
    disp_nombre: str | None

    model_config = ConfigDict(from_attributes=True) # Configuración para que Pydantic pueda convertir los datos de la base de datos a un objeto Python


class EstadoSolicitudResponse(BaseModel): # Esquema para la respuesta de un estado de solicitud
    essl_id: int                # ID del estado de solicitud
    essl_nombre: str | None     # Nombre del estado de solicitud
    essl_descripcion: str | None # Descripción del estado de solicitud

    model_config = ConfigDict(from_attributes=True) # Configuración para que Pydantic pueda convertir los datos de la base de datos a un objeto Python


class PrioridadSolicitudResponse(BaseModel): # Esquema para la respuesta de una prioridad de solicitud  
    prsol_id: int                # ID de la prioridad de solicitud  
    prsol_nombre: str | None     # Nombre de la prioridad de solicitud
    prsol_descripcion: str | None # Descripción de la prioridad de solicitud

    model_config = ConfigDict(from_attributes=True) # Configuración para que Pydantic pueda convertir los datos de la base de datos a un objeto Python

# ==========================================================
# ESQUEMAS DE ENTRADA (CREACIÓN / EDICIÓN)
# ==========================================================

class HabilidadCreate(BaseModel): 
    hab_nombre: str 
    hab_descripcion: str | None = None


class CargoCreate(BaseModel):
    crgo_nombre: str
    crgo_descripcion: str | None = None