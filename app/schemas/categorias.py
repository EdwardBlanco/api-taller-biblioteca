from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoriaCrear(BaseModel):
    nombre: str = Field(min_length=3, max_length=50, examples=["novela"])
    descripcion: str | None = Field(default=None, max_length=200, examples=["Obras narrativas de ficción"])

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        valor = valor.strip().lower()
        if len(valor) < 3 or len(valor) > 50:
            raise ValueError("El nombre debe tener entre 3 y 50 caracteres")
        return valor


class CategoriaActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=50)
    descripcion: str | None = Field(default=None, max_length=200)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str | None) -> str | None:
        if valor is not None:
            valor = valor.strip().lower()
            if len(valor) < 3 or len(valor) > 50:
                raise ValueError("El nombre debe tener entre 3 y 50 caracteres")
            return valor
        return None


class CategoriaLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None = None
