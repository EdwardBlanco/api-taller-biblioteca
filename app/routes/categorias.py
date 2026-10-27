from fastapi import APIRouter, status

from ..controllers import categorias as controlador
from ..core.dependencies import PaginacionDep, SessionDep
from ..schemas.categorias import CategoriaActualizar, CategoriaCrear, CategoriaLeer

router = APIRouter(
    prefix="/categorias",
    tags=["Categorías"]
)


@router.get("", response_model=list[CategoriaLeer])
@router.get("/", response_model=list[CategoriaLeer], include_in_schema=False)
def listar_categorias(paginacion: PaginacionDep, db: SessionDep):
    return controlador.listar(db, skip=paginacion.skip, limit=paginacion.limit)


@router.get("/{categoria_id}", response_model=CategoriaLeer)
def obtener_categoria(categoria_id: int, db: SessionDep):
    return controlador.obtener(db, categoria_id)


@router.post("", response_model=CategoriaLeer, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=CategoriaLeer, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def crear_categoria(datos: CategoriaCrear, db: SessionDep):
    return controlador.crear(db, datos)


@router.patch("/{categoria_id}", response_model=CategoriaLeer)
def actualizar_categoria(categoria_id: int, datos: CategoriaActualizar, db: SessionDep):
    return controlador.actualizar(db, categoria_id, datos)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(categoria_id: int, db: SessionDep):
    controlador.eliminar(db, categoria_id)
