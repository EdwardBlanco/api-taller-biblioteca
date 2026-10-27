from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator


class LibroResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    isbn: str


class SocioResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str


class PrestamoCrear(BaseModel):
    libro_id: int = Field(gt=0, examples=[1])
    socio_id: int = Field(gt=0, examples=[1])
    fecha_prestamo: date | None = Field(default=None, examples=["2026-10-07"])
    dias: int = Field(default=14, ge=1, le=30, examples=[14])

    @field_validator("fecha_prestamo")
    @classmethod
    def validar_fecha_no_futura(cls, valor: date | None) -> date:
        hoy = date.today()
        if valor is not None:
            if valor > hoy:
                raise ValueError("La fecha de préstamo no puede ser futura")
            return valor
        return hoy


class PrestamoDevolucion(BaseModel):
    fecha_devolucion: date | None = Field(default=None, examples=["2026-10-27"])

    @field_validator("fecha_devolucion")
    @classmethod
    def asignar_fecha_por_defecto(cls, valor: date | None) -> date:
        return valor if valor is not None else date.today()


class PrestamoLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    libro_id: int
    socio_id: int
    fecha_prestamo: date
    fecha_limite: date
    fecha_devolucion: date | None = None
    multa: float
    estado: str


class PrestamoDetalleLeer(PrestamoLeer):
    libro: LibroResumen
    socio: SocioResumen
