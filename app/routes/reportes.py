from fastapi import APIRouter, Query

from ..controllers import reportes as controlador
from ..core.dependencies import SessionDep
from ..schemas.reportes import (
    ReporteAutor,
    ReporteCategoria,
    ReporteLibroMasPrestado,
    ReportePrestamoVencido,
    ReporteResumen,
    ReporteSocioConMultas,
)

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"]
)


@router.get("/libros-mas-prestados", response_model=list[ReporteLibroMasPrestado])
def reporte_libros_mas_prestados(
    db: SessionDep,
    limite: int = Query(5, ge=1, le=50, description="Cantidad máxima de libros a mostrar"),
):
    return controlador.libros_mas_prestados(db, limite=limite)


@router.get("/categorias", response_model=list[ReporteCategoria])
def reporte_categorias(db: SessionDep):
    return controlador.categorias(db)


@router.get("/prestamos-vencidos", response_model=list[ReportePrestamoVencido])
def reporte_prestamos_vencidos(db: SessionDep):
    return controlador.prestamos_vencidos(db)


@router.get("/socios-con-multas", response_model=list[ReporteSocioConMultas])
def reporte_socios_con_multas(db: SessionDep):
    return controlador.socios_con_multas(db)


@router.get("/autores", response_model=list[ReporteAutor])
def reporte_autores(db: SessionDep):
    return controlador.autores(db)


@router.get("/resumen", response_model=ReporteResumen)
def reporte_resumen(db: SessionDep):
    return controlador.resumen(db)
