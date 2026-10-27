from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Autor, Categoria, Libro, Prestamo, Socio
from ..models.libro import libro_categoria


def libros_mas_prestados(db: Session, limite: int = 5):
    total_prestamos = func.count(Prestamo.id).label("total_prestamos")
    consulta = (
        select(
            Libro.id.label("libro_id"),
            Libro.titulo,
            Autor.nombre.label("autor"),
            total_prestamos,
        )
        .join(Libro.autor)
        .join(Libro.prestamos)
        .group_by(Libro.id, Libro.titulo, Autor.nombre)
        .order_by(total_prestamos.desc())
        .limit(limite)
    )
    return db.execute(consulta).mappings().all()


def categorias(db: Session):
    total = func.count(libro_categoria.c.libro_id).label("total_libros")
    consulta = (
        select(Categoria.id.label("categoria_id"), Categoria.nombre, total)
        .outerjoin(libro_categoria, libro_categoria.c.categoria_id == Categoria.id)
        .group_by(Categoria.id, Categoria.nombre)
        .order_by(total.desc(), Categoria.nombre.asc())
    )
    return db.execute(consulta).mappings().all()


def prestamos_vencidos(db: Session):
    hoy = date.today()
    dias_retraso = (hoy - Prestamo.fecha_limite).label("dias_retraso")
    consulta = (
        select(
            Prestamo.id.label("prestamo_id"),
            Libro.titulo,
            Socio.nombre.label("socio"),
            Socio.email,
            Prestamo.fecha_limite,
            dias_retraso,
        )
        .join(Prestamo.libro)
        .join(Prestamo.socio)
        .where(Prestamo.fecha_devolucion.is_(None), Prestamo.fecha_limite < hoy)
        .order_by(dias_retraso.desc())
    )
    return db.execute(consulta).mappings().all()


def socios_con_multas(db: Session):
    consulta = (
        select(
            Socio.id.label("socio_id"),
            Socio.nombre.label("socio"),
            func.sum(Prestamo.multa).label("total_multas"),
            func.count(Prestamo.id).label("prestamos_con_multa"),
        )
        .join(Prestamo, Prestamo.socio_id == Socio.id)
        .where(Prestamo.multa > 0)
        .group_by(Socio.id, Socio.nombre)
        .having(func.sum(Prestamo.multa) > 0)
        .order_by(func.sum(Prestamo.multa).desc())
    )
    return db.execute(consulta).mappings().all()


def autores(db: Session):
    sub_libros = (
        select(
            Libro.autor_id,
            func.count(Libro.id).label("total_libros"),
            func.coalesce(func.sum(Libro.ejemplares), 0).label("total_ejemplares"),
        )
        .group_by(Libro.autor_id)
        .subquery()
    )

    sub_prestamos = (
        select(
            Libro.autor_id,
            func.count(Prestamo.id).label("total_prestamos"),
        )
        .join(Prestamo, Prestamo.libro_id == Libro.id)
        .group_by(Libro.autor_id)
        .subquery()
    )

    consulta = (
        select(
            Autor.id.label("autor_id"),
            Autor.nombre.label("autor"),
            func.coalesce(sub_libros.c.total_libros, 0).label("total_libros"),
            func.coalesce(sub_libros.c.total_ejemplares, 0).label("total_ejemplares"),
            func.coalesce(sub_prestamos.c.total_prestamos, 0).label("total_prestamos"),
        )
        .outerjoin(sub_libros, Autor.id == sub_libros.c.autor_id)
        .outerjoin(sub_prestamos, Autor.id == sub_prestamos.c.autor_id)
        .order_by(Autor.nombre.asc())
    )
    return db.execute(consulta).mappings().all()


def resumen(db: Session):
    hoy = date.today()
    consulta = select(
        select(func.count(Libro.id)).scalar_subquery().label("total_libros"),
        select(func.coalesce(func.sum(Libro.ejemplares), 0)).scalar_subquery().label("total_ejemplares"),
        select(func.count(Prestamo.id)).where(Prestamo.fecha_devolucion.is_(None)).scalar_subquery().label("total_prestados"),
        select(func.count(Socio.id)).where(Socio.activo == True).scalar_subquery().label("socios_activos"),
        select(func.count(Prestamo.id)).where(Prestamo.fecha_devolucion.is_(None), Prestamo.fecha_limite < hoy).scalar_subquery().label("prestamos_vencidos"),
        select(func.coalesce(func.sum(Prestamo.multa), 0.0)).scalar_subquery().label("total_multas"),
    )
    return db.execute(consulta).mappings().one()
