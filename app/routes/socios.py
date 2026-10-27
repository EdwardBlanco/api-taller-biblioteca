from fastapi import APIRouter, Query, status

from ..controllers import socios as controlador
from ..core.dependencies import PaginacionDep, SessionDep
from ..schemas.prestamos import PrestamoLeer
from ..schemas.socios import SocioActualizar, SocioCrear, SocioLeer

router = APIRouter(
    prefix="/socios",
    tags=["Socios"]
)


@router.get("", response_model=list[SocioLeer])
@router.get("/", response_model=list[SocioLeer], include_in_schema=False)
def listar_socios(
    paginacion: PaginacionDep,
    db: SessionDep,
    activo: bool | None = Query(None, description="Filtrar por estado activo (true/false)"),
):
    return controlador.listar(
        db,
        skip=paginacion.skip,
        limit=paginacion.limit,
        activo=activo,
    )


@router.get("/{socio_id}", response_model=SocioLeer)
def obtener_socio(socio_id: int, db: SessionDep):
    return controlador.obtener(db, socio_id)


@router.get("/{socio_id}/prestamos", response_model=list[PrestamoLeer])
def listar_prestamos_socio(
    socio_id: int,
    db: SessionDep,
    estado: str | None = Query(None, pattern="^(activo|vencido|devuelto)$", description="Filtrar por estado: activo, vencido, devuelto"),
):
    return controlador.listar_prestamos_socio(db, socio_id, estado=estado)


@router.post("", response_model=SocioLeer, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=SocioLeer, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def crear_socio(datos: SocioCrear, db: SessionDep):
    return controlador.crear(db, datos)


@router.patch("/{socio_id}", response_model=SocioLeer)
def actualizar_socio(socio_id: int, datos: SocioActualizar, db: SessionDep):
    return controlador.actualizar(db, socio_id, datos)


@router.delete("/{socio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_socio(socio_id: int, db: SessionDep):
    controlador.eliminar(db, socio_id)
