from fastapi import APIRouter, Query, status

from ..controllers import libros as controlador
from ..core.dependencies import PaginacionDep, SessionDep
from ..schemas.libros import LibroActualizar, LibroCrear, LibroLeer, OrdenLibro

router = APIRouter(
    prefix="/libros",
    tags=["Libros"]
)


@router.get("", response_model=list[LibroLeer])
@router.get("/", response_model=list[LibroLeer], include_in_schema=False)
def listar_libros(
    paginacion: PaginacionDep,
    db: SessionDep,
    buscar: str | None = Query(None, description="Título que contenga el texto"),
    autor: str | None = Query(None, description="Nombre del autor que contenga el texto"),
    categoria_id: int | None = Query(None, description="Libros de esa categoría"),
    desde: int | None = Query(None, description="Año mínimo de publicación"),
    hasta: int | None = Query(None, description="Año máximo de publicación"),
    orden: OrdenLibro | None = Query(None, description="Criterio de ordenamiento: titulo, anio o -anio"),
):
    return controlador.listar(
        db,
        skip=paginacion.skip,
        limit=paginacion.limit,
        buscar=buscar,
        autor=autor,
        categoria_id=categoria_id,
        desde=desde,
        hasta=hasta,
        orden=orden,
    )


@router.get("/{libro_id}", response_model=LibroLeer)
def obtener_libro(libro_id: int, db: SessionDep):
    return controlador.obtener(db, libro_id)


@router.post("", response_model=LibroLeer, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=LibroLeer, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def crear_libro(datos: LibroCrear, db: SessionDep):
    return controlador.crear(db, datos)


@router.patch("/{libro_id}", response_model=LibroLeer)
def actualizar_libro(libro_id: int, datos: LibroActualizar, db: SessionDep):
    return controlador.actualizar(db, libro_id, datos)


@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_libro(libro_id: int, db: SessionDep):
    controlador.eliminar(db, libro_id)
