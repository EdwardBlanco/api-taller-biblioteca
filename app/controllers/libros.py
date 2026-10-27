from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from ..models import Autor, Categoria, Libro, Prestamo
from ..schemas.libros import LibroActualizar, LibroCrear, OrdenLibro


def listar(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    buscar: str | None = None,
    autor: str | None = None,
    categoria_id: int | None = None,
    desde: int | None = None,
    hasta: int | None = None,
    orden: OrdenLibro | None = None,
):
    consulta = select(Libro).options(
        selectinload(Libro.autor),
        selectinload(Libro.categorias),
        selectinload(Libro.prestamos),
    )

    if buscar:
        consulta = consulta.where(Libro.titulo.ilike(f"%{buscar.strip()}%"))

    if autor:
        consulta = consulta.join(Libro.autor).where(Autor.nombre.ilike(f"%{autor.strip()}%"))

    if categoria_id:
        consulta = consulta.join(Libro.categorias).where(Categoria.id == categoria_id)

    if desde is not None:
        consulta = consulta.where(Libro.anio_publicacion >= desde)

    if hasta is not None:
        consulta = consulta.where(Libro.anio_publicacion <= hasta)

    if orden == OrdenLibro.titulo:
        consulta = consulta.order_by(Libro.titulo.asc())
    elif orden == OrdenLibro.anio:
        consulta = consulta.order_by(Libro.anio_publicacion.asc())
    elif orden == OrdenLibro.menos_anio:
        consulta = consulta.order_by(Libro.anio_publicacion.desc())
    else:
        consulta = consulta.order_by(Libro.titulo.asc())

    consulta = consulta.offset(skip).limit(limit)
    return db.scalars(consulta).all()


def obtener(db: Session, libro_id: int):
    libro = db.scalar(
        select(Libro)
        .options(
            selectinload(Libro.autor),
            selectinload(Libro.categorias),
            selectinload(Libro.prestamos),
        )
        .where(Libro.id == libro_id)
    )
    if libro is None:
        raise NoEncontrado("El libro no existe")
    return libro


def crear(db: Session, datos: LibroCrear):
    autor = db.get(Autor, datos.autor_id)
    if autor is None:
        raise NoEncontrado("El autor no existe")

    isbn_existente = db.scalar(select(Libro.id).where(Libro.isbn == datos.isbn))
    if isbn_existente is not None:
        raise Conflicto("Ya existe un libro con ese código ISBN")

    categorias = db.scalars(
        select(Categoria).where(Categoria.id.in_(datos.categoria_ids))
    ).all()
    if len(categorias) != len(set(datos.categoria_ids)):
        raise NoEncontrado("Una o más categorías especificadas no existen")

    libro = Libro(
        titulo=datos.titulo,
        isbn=datos.isbn,
        anio_publicacion=datos.anio_publicacion,
        ejemplares=datos.ejemplares,
        autor_id=datos.autor_id,
    )
    libro.categorias = list(categorias)

    db.add(libro)
    db.commit()
    db.refresh(libro)
    return libro


def actualizar(db: Session, libro_id: int, datos: LibroActualizar):
    libro = db.get(Libro, libro_id)
    if libro is None:
        raise NoEncontrado("El libro no existe")

    datos_dict = datos.model_dump(exclude_unset=True)

    if "autor_id" in datos_dict and datos_dict["autor_id"] is not None:
        autor = db.get(Autor, datos_dict["autor_id"])
        if autor is None:
            raise NoEncontrado("El autor especificado no existe")

    if "isbn" in datos_dict and datos_dict["isbn"] is not None:
        isbn_existente = db.scalar(
            select(Libro.id).where(Libro.isbn == datos_dict["isbn"], Libro.id != libro_id)
        )
        if isbn_existente is not None:
            raise Conflicto("El código ISBN ya está registrado para otro libro")

    if "ejemplares" in datos_dict and datos_dict["ejemplares"] is not None:
        prestamos_activos = sum(1 for p in libro.prestamos if p.fecha_devolucion is None)
        if datos_dict["ejemplares"] < prestamos_activos:
            raise ReglaNegocio("El número de ejemplares no puede ser menor a los préstamos activos")

    if "categoria_ids" in datos_dict and datos_dict["categoria_ids"] is not None:
        cat_ids = datos_dict["categoria_ids"]
        categorias = db.scalars(
            select(Categoria).where(Categoria.id.in_(cat_ids))
        ).all()
        if len(categorias) != len(set(cat_ids)):
            raise NoEncontrado("Una o más categorías especificadas no existen")
        libro.categorias = list(categorias)

    for campo in ["titulo", "isbn", "anio_publicacion", "ejemplares", "autor_id"]:
        if campo in datos_dict and datos_dict[campo] is not None:
            setattr(libro, campo, datos_dict[campo])

    db.commit()
    db.refresh(libro)
    return libro


def eliminar(db: Session, libro_id: int):
    libro = db.get(Libro, libro_id)
    if libro is None:
        raise NoEncontrado("El libro no existe")

    prestamo_activo = db.scalar(
        select(Prestamo.id)
        .where(Prestamo.libro_id == libro_id, Prestamo.fecha_devolucion.is_(None))
        .limit(1)
    )
    if prestamo_activo is not None:
        raise Conflicto("No se puede eliminar el libro porque tiene préstamos sin devolver")

    db.delete(libro)
    db.commit()
