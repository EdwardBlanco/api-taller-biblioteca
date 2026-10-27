from datetime import date

from pydantic import BaseModel, ConfigDict


class ReporteLibroMasPrestado(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    libro_id: int
    titulo: str
    autor: str
    total_prestamos: int


class ReporteCategoria(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    categoria_id: int
    nombre: str
    total_libros: int


class ReportePrestamoVencido(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prestamo_id: int
    titulo: str
    socio: str
    email: str
    fecha_limite: date
    dias_retraso: int


class ReporteSocioConMultas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    socio_id: int
    socio: str
    total_multas: float
    prestamos_con_multa: int


class ReporteAutor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    autor_id: int
    autor: str
    total_libros: int
    total_ejemplares: int
    total_prestamos: int


class ReporteResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_libros: int
    total_ejemplares: int
    total_prestados: int
    socios_activos: int
    prestamos_vencidos: int
    total_multas: float
