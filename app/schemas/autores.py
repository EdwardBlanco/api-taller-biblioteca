from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AutorCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100, examples=["Gabriel García Márquez"])
    nacionalidad: str | None = Field(default=None, max_length=60, examples=["Colombiana"])
    anio_nacimiento: int | None = Field(default=None, ge=1000, examples=[1927])

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        valor = valor.strip()
        if len(valor) < 2 or len(valor) > 100:
            raise ValueError("El nombre debe tener entre 2 y 100 caracteres")
        return valor.title()

    @field_validator("nacionalidad")
    @classmethod
    def validar_nacionalidad(cls, valor: str | None) -> str | None:
        if valor is not None:
            valor = valor.strip()
            return valor.title() if valor else None
        return None

    @field_validator("anio_nacimiento")
    @classmethod
    def validar_anio(cls, valor: int | None) -> int | None:
        if valor is not None:
            anio_actual = date.today().year
            if valor < 1000 or valor > anio_actual:
                raise ValueError(f"El año de nacimiento debe estar entre 1000 y {anio_actual}")
        return valor


class AutorActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    nacionalidad: str | None = Field(default=None, max_length=60)
    anio_nacimiento: int | None = Field(default=None, ge=1000)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str | None) -> str | None:
        if valor is not None:
            valor = valor.strip()
            if len(valor) < 2 or len(valor) > 100:
                raise ValueError("El nombre debe tener entre 2 y 100 caracteres")
            return valor.title()
        return None

    @field_validator("nacionalidad")
    @classmethod
    def validar_nacionalidad(cls, valor: str | None) -> str | None:
        if valor is not None:
            valor = valor.strip()
            return valor.title() if valor else None
        return None

    @field_validator("anio_nacimiento")
    @classmethod
    def validar_anio(cls, valor: int | None) -> int | None:
        if valor is not None:
            anio_actual = date.today().year
            if valor < 1000 or valor > anio_actual:
                raise ValueError(f"El año de nacimiento debe estar entre 1000 y {anio_actual}")
        return valor


class AutorLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    nacionalidad: str | None = None
    anio_nacimiento: int | None = None