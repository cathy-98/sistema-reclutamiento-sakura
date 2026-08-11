from __future__ import annotations

from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    model_validator,
)


Name15 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=15)]
Name20 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
Name50 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
Description300 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]
Password = Annotated[str, StringConstraints(min_length=8, max_length=72)]


class ReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class WriteModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


# ==========================================================
# SUBRECURSOS
# ==========================================================

class PermisoRead(ReadModel):
    per_id: int
    per_nombre: str
    per_descripcion: str | None = None


class RolSimpleRead(ReadModel):
    rol_id: int
    rol_nombre: str


class RolRead(ReadModel):
    rol_id: int
    rol_nombre: str
    rol_descripcion: str | None = None
    permisos: list[PermisoRead] = Field(default_factory=list)


class AreaRead(ReadModel):
    area_id: int
    area_nombre: str | None = None
    area_descripcion: str | None = None


class EstadoUsuarioRead(ReadModel):
    esusr_id: int
    esusr_nombre: str
    esusr_descripcion: str | None = None


# ==========================================================
# USUARIOS
# ==========================================================

class UsuarioFields(WriteModel):
    usr_nombres: Name15
    usr_apellido_paterno: Name15
    usr_apellido_materno: Name15 | None = None
    usr_rut_sin_dv: str | None = Field(default=None, max_length=15)
    usr_dv: str | None = Field(default=None, min_length=1, max_length=1)
    usr_telefono: str | None = Field(default=None, min_length=1, max_length=15)
    usr_email: EmailStr = Field(max_length=30)
    usr_rol_id: int | None = Field(default=None, ge=1)
    usr_estado_usuario_id: int | None = Field(default=None, ge=1)
    usr_area_id: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validar_rut_completo(self):
        if (self.usr_rut_sin_dv is None) != (self.usr_dv is None):
            raise ValueError("usr_rut_sin_dv y usr_dv deben informarse juntos")
        return self


class UsuarioCreate(UsuarioFields):
    usr_contrasena: Password


class UsuarioReplace(UsuarioFields):
    """PUT reemplaza todos los campos editables salvo la contraseña."""


class UsuarioUpdate(WriteModel):
    usr_nombres: Name15 | None = None
    usr_apellido_paterno: Name15 | None = None
    usr_apellido_materno: Name15 | None = None
    usr_rut_sin_dv: str | None = Field(default=None, max_length=15)
    usr_dv: str | None = Field(default=None, min_length=1, max_length=1)
    usr_telefono: str | None = Field(default=None, min_length=1, max_length=15)
    usr_email: EmailStr | None = Field(default=None, max_length=30)
    usr_rol_id: int | None = Field(default=None, ge=1)
    usr_estado_usuario_id: int | None = Field(default=None, ge=1)
    usr_area_id: int | None = Field(default=None, ge=1)


class UsuarioRead(ReadModel):
    usr_id: int
    usr_nombres: str
    usr_apellido_paterno: str
    usr_apellido_materno: str | None = None
    usr_rut_sin_dv: str | None = None
    usr_dv: str | None = None
    usr_telefono: str | None = None
    usr_email: EmailStr
    usr_rol_id: int | None = None
    usr_estado_usuario_id: int | None = None
    usr_area_id: int | None = None
    rol: RolSimpleRead | None = None
    area: AreaRead | None = None
    estado: EstadoUsuarioRead | None = None
    permisos: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def extraer_permisos(cls, data):
        if hasattr(data, "rol") and data.rol is not None:
            permiso_objs = getattr(data.rol, "permisos", []) or []
            # No mutamos el ORM; devolvemos un diccionario serializable.
            return {
                "usr_id": data.usr_id,
                "usr_nombres": data.usr_nombres,
                "usr_apellido_paterno": data.usr_apellido_paterno,
                "usr_apellido_materno": data.usr_apellido_materno,
                "usr_rut_sin_dv": data.usr_rut_sin_dv,
                "usr_dv": data.usr_dv,
                "usr_telefono": data.usr_telefono,
                "usr_email": data.usr_email,
                "usr_rol_id": data.usr_rol_id,
                "usr_estado_usuario_id": data.usr_estado_usuario_id,
                "usr_area_id": data.usr_area_id,
                "rol": data.rol,
                "area": data.area,
                "estado": data.estado,
                "permisos": [p.per_nombre for p in permiso_objs],
            }
        return data


class UsuarioPasswordReset(WriteModel):
    nueva_contrasena: Password


# ==========================================================
# ROLES
# ==========================================================

class RolCreate(WriteModel):
    rol_nombre: Name20
    rol_descripcion: Description300 | None = None


class RolUpdate(WriteModel):
    rol_nombre: Name20 | None = None
    rol_descripcion: Description300 | None = None


class RolPermisosReplace(WriteModel):
    permiso_ids: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def sin_duplicados(self):
        if len(self.permiso_ids) != len(set(self.permiso_ids)):
            raise ValueError("permiso_ids no puede contener IDs duplicados")
        if any(item_id <= 0 for item_id in self.permiso_ids):
            raise ValueError("Todos los permiso_ids deben ser mayores que cero")
        return self


# ==========================================================
# PERMISOS
# ==========================================================

class PermisoCreate(WriteModel):
    per_nombre: Name20
    per_descripcion: Description300 | None = None


class PermisoUpdate(WriteModel):
    per_nombre: Name20 | None = None
    per_descripcion: Description300 | None = None


# ==========================================================
# ÁREAS Y ESTADOS
# ==========================================================

class AreaCreate(WriteModel):
    area_nombre: Name50
    area_descripcion: Description300 | None = None


class AreaUpdate(WriteModel):
    area_nombre: Name50 | None = None
    area_descripcion: Description300 | None = None


class EstadoUsuarioCreate(WriteModel):
    esusr_nombre: Name20
    esusr_descripcion: Description300 | None = None


class EstadoUsuarioUpdate(WriteModel):
    esusr_nombre: Name20 | None = None
    esusr_descripcion: Description300 | None = None
