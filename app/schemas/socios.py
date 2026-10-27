import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class SocioCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100, examples=["Ana Torres"])
    email: EmailStr = Field(examples=["ana@example.com"])
    telefono: str | None = Field(default=None, examples=["+57 3001234567"])
    activo: bool = True

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre no puede estar vacío")
        return valor.title()

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, valor: str) -> str:
        return valor.strip().lower()

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, valor: str | None) -> str | None:
        if valor is not None:
            valor = valor.strip()
            if not valor:
                return None
            if not re.match(r"^[\d\s\+]{7,15}$", valor):
                raise ValueError("El teléfono debe tener entre 7 y 15 caracteres y solo contener dígitos, espacios o +")
            return valor
        return None


class SocioActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    telefono: str | None = None
    activo: bool | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str | None) -> str | None:
        if valor is not None:
            valor = valor.strip()
            if not valor:
                raise ValueError("El nombre no puede estar vacío")
            return valor.title()
        return None

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, valor: str | None) -> str | None:
        if valor is not None:
            return valor.strip().lower()
        return None

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, valor: str | None) -> str | None:
        if valor is not None:
            valor = valor.strip()
            if not valor:
                return None
            if not re.match(r"^[\d\s\+]{7,15}$", valor):
                raise ValueError("El teléfono debe tener entre 7 y 15 caracteres y solo contener dígitos, espacios o +")
            return valor
        return None


class SocioLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: EmailStr
    telefono: str | None = None
    activo: bool
    fecha_alta: datetime
