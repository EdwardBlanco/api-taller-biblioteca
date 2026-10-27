from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OrdenLibro(str, Enum):
    titulo = "titulo"
    anio = "anio"
    menos_anio = "-anio"


class AutorResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class CategoriaResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class LibroCrear(BaseModel):
    titulo: str = Field(min_length=1, max_length=150, examples=["Cien Años De Soledad"])
    isbn: str = Field(pattern=r"^\d{13}$", examples=["9788437604947"])
    anio_publicacion: int = Field(ge=1450, examples=[1967])
    ejemplares: int = Field(ge=1, le=50, examples=[2])
    autor_id: int = Field(gt=0, examples=[1])
    categoria_ids: list[int] = Field(min_length=1, max_length=5, examples=[[1, 2]])

    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("El título no puede estar vacío")
        return valor.title()

    @field_validator("anio_publicacion")
    @classmethod
    def validar_anio(cls, valor: int) -> int:
        anio_actual = date.today().year
        if valor < 1450 or valor > anio_actual:
            raise ValueError(f"El año de publicación debe estar entre 1450 y {anio_actual}")
        return valor

    @field_validator("categoria_ids")
    @classmethod
    def validar_categorias(cls, valor: list[int]) -> list[int]:
        if len(valor) != len(set(valor)):
            raise ValueError("Las categorías no pueden contener duplicados")
        return valor


class LibroActualizar(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=150)
    isbn: str | None = Field(default=None, pattern=r"^\d{13}$")
    anio_publicacion: int | None = Field(default=None, ge=1450)
    ejemplares: int | None = Field(default=None, ge=1, le=50)
    autor_id: int | None = Field(default=None, gt=0)
    categoria_ids: list[int] | None = Field(default=None, min_length=1, max_length=5)

    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, valor: str | None) -> str | None:
        if valor is not None:
            valor = valor.strip()
            if not valor:
                raise ValueError("El título no puede estar vacío")
            return valor.title()
        return None

    @field_validator("anio_publicacion")
    @classmethod
    def validar_anio(cls, valor: int | None) -> int | None:
        if valor is not None:
            anio_actual = date.today().year
            if valor < 1450 or valor > anio_actual:
                raise ValueError(f"El año de publicación debe estar entre 1450 y {anio_actual}")
        return valor

    @field_validator("categoria_ids")
    @classmethod
    def validar_categorias(cls, valor: list[int] | None) -> list[int] | None:
        if valor is not None:
            if len(valor) != len(set(valor)):
                raise ValueError("Las categorías no pueden contener duplicados")
        return valor


class LibroLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    isbn: str
    anio_publicacion: int
    ejemplares: int
    disponibles: int
    autor: AutorResumen
    categorias: list[CategoriaResumen] = []
