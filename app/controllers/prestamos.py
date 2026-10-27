from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from ..models import Libro, Prestamo, Socio
from ..schemas.prestamos import PrestamoCrear, PrestamoDevolucion


def listar(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    estado: str | None = None,
    socio_id: int | None = None,
    libro_id: int | None = None,
):
    hoy = date.today()
    consulta = select(Prestamo).options(
        selectinload(Prestamo.libro),
        selectinload(Prestamo.socio),
    )

    if socio_id is not None:
        consulta = consulta.where(Prestamo.socio_id == socio_id)

    if libro_id is not None:
        consulta = consulta.where(Prestamo.libro_id == libro_id)

    if estado == "activo":
        consulta = consulta.where(
            Prestamo.fecha_devolucion.is_(None), Prestamo.fecha_limite >= hoy
        )
    elif estado == "vencido":
        consulta = consulta.where(
            Prestamo.fecha_devolucion.is_(None), Prestamo.fecha_limite < hoy
        )
    elif estado == "devuelto":
        consulta = consulta.where(Prestamo.fecha_devolucion.is_not(None))

    consulta = (
        consulta.order_by(Prestamo.fecha_prestamo.desc(), Prestamo.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return db.scalars(consulta).all()


def obtener(db: Session, prestamo_id: int):
    prestamo = db.scalar(
        select(Prestamo)
        .options(
            selectinload(Prestamo.libro),
            selectinload(Prestamo.socio),
        )
        .where(Prestamo.id == prestamo_id)
    )
    if prestamo is None:
        raise NoEncontrado("El préstamo no existe")
    return prestamo


def crear(db: Session, datos: PrestamoCrear):
    socio = db.get(Socio, datos.socio_id)
    if socio is None:
        raise NoEncontrado("El socio no existe")

    libro = db.get(Libro, datos.libro_id)
    if libro is None:
        raise NoEncontrado("El libro no existe")

    if not socio.activo:
        raise ReglaNegocio("El socio no está activo")

    hoy = date.today()

    prestamo_vencido = db.scalar(
        select(Prestamo.id)
        .where(
            Prestamo.socio_id == datos.socio_id,
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_limite < hoy,
        )
        .limit(1)
    )
    if prestamo_vencido is not None:
        raise ReglaNegocio("El socio tiene préstamos vencidos")

    total_sin_devolver = db.scalar(
        select(func.count(Prestamo.id))
        .where(
            Prestamo.socio_id == datos.socio_id,
            Prestamo.fecha_devolucion.is_(None),
        )
    ) or 0
    if total_sin_devolver >= 3:
        raise ReglaNegocio("Máximo de 3 préstamos")

    mismo_libro = db.scalar(
        select(Prestamo.id)
        .where(
            Prestamo.socio_id == datos.socio_id,
            Prestamo.libro_id == datos.libro_id,
            Prestamo.fecha_devolucion.is_(None),
        )
        .limit(1)
    )
    if mismo_libro is not None:
        raise Conflicto("El socio ya tiene este libro en préstamo sin devolver")

    prestados_libro = db.scalar(
        select(func.count(Prestamo.id))
        .where(
            Prestamo.libro_id == datos.libro_id,
            Prestamo.fecha_devolucion.is_(None),
        )
    ) or 0
    disponibles = libro.ejemplares - prestados_libro
    if disponibles <= 0:
        raise ReglaNegocio("No hay ejemplares disponibles")

    fecha_prestamo = datos.fecha_prestamo or hoy
    fecha_limite = fecha_prestamo + timedelta(days=datos.dias)

    prestamo = Prestamo(
        libro_id=datos.libro_id,
        socio_id=datos.socio_id,
        fecha_prestamo=fecha_prestamo,
        fecha_limite=fecha_limite,
        multa=0.0,
    )
    db.add(prestamo)
    db.commit()
    db.refresh(prestamo)
    return prestamo


def registrar_devolucion(db: Session, prestamo_id: int, datos: PrestamoDevolucion):
    prestamo = db.get(Prestamo, prestamo_id)
    if prestamo is None:
        raise NoEncontrado("El préstamo no existe")

    if prestamo.fecha_devolucion is not None:
        raise Conflicto("El préstamo ya fue devuelto previamente")

    fecha_devolucion = datos.fecha_devolucion or date.today()

    if fecha_devolucion < prestamo.fecha_prestamo:
        raise ReglaNegocio("La fecha de devolución no puede ser anterior a la fecha de préstamo")

    if fecha_devolucion > prestamo.fecha_limite:
        dias_retraso = (fecha_devolucion - prestamo.fecha_limite).days
        prestamo.multa = round(dias_retraso * 0.50, 2)
    else:
        prestamo.multa = 0.0

    prestamo.fecha_devolucion = fecha_devolucion
    db.commit()
    db.refresh(prestamo)
    return prestamo
