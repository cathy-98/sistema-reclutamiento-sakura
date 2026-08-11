from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from typing import Annotated

from app.usuarios.schemas import UsuarioRead


Password = Annotated[str, StringConstraints(min_length=8, max_length=72)]


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    password_actual: str = Field(min_length=1, max_length=72)
    password_nueva: Password


class AuthMeResponse(UsuarioRead):
    pass
