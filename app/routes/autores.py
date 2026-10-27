from fastapi import APIRouter, Query, status

from ..controllers import autores as controlador
from ..core.dependencies import PaginacionDep, SessionDep
from ..schemas.autores import AutorActualizar, AutorCrear, AutorLeer
from ..schemas.libros import LibroLeer

router = APIRouter(
    prefix="/autores",
    tags=["Autores"]
)


@router.get("", response_model=list[AutorLeer])
@router.get("/", response_model=list[AutorLeer], include_in_schema=False)
def listar_autores(
    paginacion: PaginacionDep,
    db: SessionDep,
    nacionalidad: str | None = Query(None, description="Filtrar por nacionalidad")
):
    return controlador.listar(
        db,
        skip=paginacion.skip,
        limit=paginacion.limit,
        nacionalidad=nacionalidad
    )


@router.get("/{autor_id}", response_model=AutorLeer)
def obtener_autor(autor_id: int, db: SessionDep):
    return controlador.obtener(db, autor_id)


@router.get("/{autor_id}/libros", response_model=list[LibroLeer])
def listar_libros_autor(autor_id: int, db: SessionDep):
    return controlador.listar_libros(db, autor_id)


@router.post("", response_model=AutorLeer, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=AutorLeer, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def crear_autor(datos: AutorCrear, db: SessionDep):
    return controlador.crear(db, datos)


@router.patch("/{autor_id}", response_model=AutorLeer)
def actualizar_autor(autor_id: int, datos: AutorActualizar, db: SessionDep):
    return controlador.actualizar(db, autor_id, datos)


@router.delete("/{autor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_autor(autor_id: int, db: SessionDep):
    controlador.eliminar(db, autor_id)
