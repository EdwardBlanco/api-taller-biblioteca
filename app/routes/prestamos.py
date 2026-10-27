from fastapi import APIRouter, Query, status

from ..controllers import prestamos as controlador
from ..core.dependencies import PaginacionDep, SessionDep
from ..schemas.prestamos import (
    PrestamoCrear,
    PrestamoDetalleLeer,
    PrestamoDevolucion,
    PrestamoLeer,
)

router = APIRouter(
    prefix="/prestamos",
    tags=["Préstamos"]
)


@router.get("", response_model=list[PrestamoLeer])
@router.get("/", response_model=list[PrestamoLeer], include_in_schema=False)
def listar_prestamos(
    paginacion: PaginacionDep,
    db: SessionDep,
    estado: str | None = Query(None, pattern="^(activo|vencido|devuelto)$", description="Filtrar por estado"),
    socio_id: int | None = Query(None, description="Filtrar por socio"),
    libro_id: int | None = Query(None, description="Filtrar por libro"),
):
    return controlador.listar(
        db,
        skip=paginacion.skip,
        limit=paginacion.limit,
        estado=estado,
        socio_id=socio_id,
        libro_id=libro_id,
    )


@router.get("/{prestamo_id}", response_model=PrestamoDetalleLeer)
def obtener_prestamo(prestamo_id: int, db: SessionDep):
    return controlador.obtener(db, prestamo_id)


@router.post("", response_model=PrestamoLeer, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=PrestamoLeer, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def crear_prestamo(datos: PrestamoCrear, db: SessionDep):
    return controlador.crear(db, datos)


@router.post("/{prestamo_id}/devolucion", response_model=PrestamoLeer)
def registrar_devolucion(
    prestamo_id: int,
    db: SessionDep,
    datos: PrestamoDevolucion | None = None,
):
    datos_devolucion = datos or PrestamoDevolucion()
    return controlador.registrar_devolucion(db, prestamo_id, datos_devolucion)
