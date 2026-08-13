from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from app.usuarios.schemas import UsuarioRead


Password = Annotated[str, StringConstraints(min_length=8, max_length=72)]
ResetToken = Annotated[str, StringConstraints(min_length=32, max_length=512)]


class LoginRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")

    email: EmailStr
    password: str=Field(min_length=1,max_length=72)


class TokenResponse(BaseModel):
    access_token:str
    token_type:str="bearer"
    expires_in:int
    principal_type:Literal["usuario","candidato"]="usuario"


class ChangePasswordRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")

    password_actual:str=Field(min_length=1,max_length=72)
    password_nueva:Password


class ForgotPasswordRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")

    email:EmailStr


class ForgotPasswordResponse(BaseModel): message:str
                


class ResetPasswordRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    token:ResetToken
    nueva_contrasena:Password
class AuthMeResponse(UsuarioRead): pass

                     
                              


                                  
        
