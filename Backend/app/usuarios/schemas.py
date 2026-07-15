from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional

# ==========================================
# 1. Esquema Base (Campos Comunes)
# ==========================================
class UsuarioBase(BaseModel):
    usr_nombres: str = Field(..., max_length=15, description="Nombres del usuario")
    usr_apellido_paterno: str = Field(..., max_length=15, description="Apellido paterno")
    usr_apellido_materno: Optional[str] = Field(None, max_length=15, description="Apellido materno")
    usr_rut_sin_dv: Optional[str] = Field(None, max_length=15, description="RUT chileno sin dígito verificador")
    usr_dv: Optional[str] = Field(None, max_length=1, description="Dígito verificador del RUT")
    usr_telefono: Optional[str] = Field(None, max_length=15, description="Teléfono de contacto")
    usr_email: EmailStr = Field(..., max_length=30, description="Correo electrónico único")
    
    usr_rol_id: Optional[int] = Field(None, description="ID del rol asociado")
    usr_estado_usuario_id: Optional[int] = Field(None, description="ID del estado actual")
    usr_area_id: Optional[int] = Field(None, description="ID del área a la que pertenece")


# ==========================================
# 2. Esquema de Entrada (Crear Usuario)
# ==========================================
class UsuarioCreate(UsuarioBase):
    usr_contrasena: str = Field(..., min_length=6, max_length=100, description="Contraseña en texto plano")


# ==========================================
# 3. Esquema de Actualización Parcial (PATCH)
# ==========================================
class UsuarioUpdate(BaseModel):
    usr_nombres: Optional[str] = Field(None, min_length=1, max_length=15)
    usr_apellido_paterno: Optional[str] = Field(None, min_length=1, max_length=15)
    usr_apellido_materno: Optional[str] = Field(None, min_length=1, max_length=15)
    usr_rut_sin_dv: Optional[str] = Field(None, max_length=15)
    usr_dv: Optional[str] = Field(None, max_length=1)
    usr_telefono: Optional[str] = Field(None, max_length=15)
    usr_email: Optional[EmailStr] = None
    usr_contrasena: Optional[str] = Field(None, min_length=6)
    usr_rol_id: Optional[int] = None
    usr_estado_usuario_id: Optional[int] = None
    usr_area_id: Optional[int] = None

    class Config:
        from_attributes = True


# ==========================================
# 4. Esquemas de Sub-recursos (Para respuestas anidadas)
# ==========================================
class RolSimpleResponse(BaseModel):
    rol_id: int
    rol_nombre: str

    class Config:
        from_attributes = True


class AreaSimpleResponse(BaseModel):
    area_id: int
    area_nombre: Optional[str]

    class Config:
        from_attributes = True


class EstadoUsuarioResponse(BaseModel):
    esusr_id: int
    esusr_nombre: str
    esusr_descripcion: Optional[str] = None

    class Config:
        from_attributes = True


# ==========================================
# 5. Esquema de Salida (Lectura de Usuario)
# ==========================================
class UsuarioResponse(BaseModel):
    usr_id: int
    usr_nombres: str
    usr_apellido_paterno: str
    usr_apellido_materno: Optional[str] = None
    usr_rut_sin_dv: Optional[str] = None
    usr_dv: Optional[str] = None
    usr_telefono: Optional[str] = None
    usr_email: EmailStr
    
    rol: Optional[RolSimpleResponse] = None
    area: Optional[AreaSimpleResponse] = None
    estado: Optional[EstadoUsuarioResponse] = None
    
    permisos: list[str] = []

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def extraer_permisos(cls, data: any) -> any:
        if hasattr(data, "rol") and data.rol and hasattr(data.rol, "permisos"):
            data.permisos = [p.per_nombre for p in data.rol.permisos]
        elif isinstance(data, dict):
            rol = data.get("rol")
            if rol:
                if hasattr(rol, "permisos"):
                    data["permisos"] = [p.per_nombre for p in rol.permisos]
                elif isinstance(rol, dict) and "permisos" in rol:
                    data["permisos"] = [
                        p["per_nombre"] if isinstance(p, dict) else p.per_nombre 
                        for p in rol["permisos"]
                    ]
        return data


# ==========================================
# 6. Esquemas para Permisos y Roles Enriquecidos
# ==========================================
class PermisoResponse(BaseModel):
    per_id: int
    per_nombre: str
    per_descripcion: Optional[str] = None

    class Config:
        from_attributes = True


class RolWithPermisosResponse(BaseModel):
    rol_id: int
    rol_nombre: str
    rol_descripcion: Optional[str] = None
    permisos: list[PermisoResponse] = []

    class Config:
        from_attributes = True