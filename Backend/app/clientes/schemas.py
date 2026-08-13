from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class EmpresaCreate(StrictSchema):
    emp_nombre: str = Field(..., min_length=1, max_length=30)
    emp_identificacion: str | None = Field(default=None, min_length=1, max_length=15)


class EmpresaUpdate(StrictSchema):
    emp_nombre: str | None = Field(default=None, min_length=1, max_length=30)
    emp_identificacion: str | None = Field(default=None, min_length=1, max_length=15)


class EmpresaRead(BaseModel):
    emp_id: int
    emp_nombre: str | None = None
    emp_identificacion: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ClienteBase(StrictSchema):
    cli_nombre: str = Field(..., min_length=1, max_length=30)
    cli_cargo_empresa_id: int | None = Field(default=None, gt=0)
    cli_area_empresa_id: int | None = Field(default=None, gt=0)
    cli_empresa_id: int = Field(..., gt=0)
    cli_email: EmailStr | None = None
    cli_email2: EmailStr | None = None
    cli_telefono1: str | None = Field(default=None, min_length=1, max_length=12)
    cli_telefono2: str | None = Field(default=None, min_length=1, max_length=12)

    @model_validator(mode="after")
    def validar_contactos(self):
        if self.cli_email and self.cli_email2:
            if str(self.cli_email).casefold() == str(self.cli_email2).casefold():
                raise ValueError("cli_email y cli_email2 deben ser diferentes")
        if self.cli_telefono1 and self.cli_telefono2:
            if self.cli_telefono1 == self.cli_telefono2:
                raise ValueError("cli_telefono1 y cli_telefono2 deben ser diferentes")
        return self


class ClienteCreate(ClienteBase):
    pass


class ClienteReplace(ClienteBase):
    pass


class ClienteUpdate(StrictSchema):
    cli_nombre: str | None = Field(default=None, min_length=1, max_length=30)
    cli_cargo_empresa_id: int | None = Field(default=None, gt=0)
    cli_area_empresa_id: int | None = Field(default=None, gt=0)
    cli_empresa_id: int | None = Field(default=None, gt=0)
    cli_email: EmailStr | None = None
    cli_email2: EmailStr | None = None
    cli_telefono1: str | None = Field(default=None, min_length=1, max_length=12)
    cli_telefono2: str | None = Field(default=None, min_length=1, max_length=12)


class ClienteRead(BaseModel):
    cli_id: int
    cli_nombre: str
    cli_cargo_empresa_id: int | None = None
    cli_area_empresa_id: int | None = None
    cli_empresa_id: int | None = None
    cli_email: EmailStr | None = None
    cli_email2: EmailStr | None = None
    cli_telefono1: str | None = None
    cli_telefono2: str | None = None

    model_config = ConfigDict(from_attributes=True)
